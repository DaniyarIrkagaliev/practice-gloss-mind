from fastapi import FastAPI, Request, Form, HTTPException, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import sqlite3
import networkx as nx
import json

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# import logging

# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Переменные для подключения к базе данных
_db_conn = None
_cursor = None


class Term(BaseModel):
    term: str
    definition: str


def connect_to_db():
    global _db_conn, _cursor
    _db_conn = sqlite3.connect('database.db', check_same_thread=False)
    _cursor = _db_conn.cursor()
    create_terms_table_if_not_exists()


def close_db_connection():
    global _db_conn, _cursor
    if _db_conn:
        _db_conn.close()


def create_terms_table_if_not_exists():
    # _cursor.execute('''
    #     drop table terms;
    #     ''')
    # _db_conn.commit()
    # _cursor.execute('''
    #         drop table relations;
    #         ''')
    # _db_conn.commit()
    _cursor.execute('''
    CREATE TABLE IF NOT EXISTS terms (
        id INTEGER  PRIMARY KEY AUTOINCREMENT,
        term VARCHAR(255),
        definition TEXT
    );
    ''')
    _db_conn.commit()

    _cursor.execute('''
       CREATE TABLE IF NOT EXISTS relations (
        id INTEGER  PRIMARY KEY AUTOINCREMENT,
        term_id INT REFERENCES terms(id),
        related_term_id INT REFERENCES terms(id),
        relation_type VARCHAR(50)
    );
        ''')
    _db_conn.commit()


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    connect_to_db()
    try:
        response = await call_next(request)
    finally:
        close_db_connection()
    return response


@app.post("/add-term/", response_class=HTMLResponse)
async def add_term(request: Request, term: str = Form(...), definition: str = Form(...)):
    term_data = Term(term=term, definition=definition)

    try:
        _cursor.execute(
            "INSERT INTO terms (term, definition) VALUES (:term, :definition)",
            {'term': term, 'definition': definition}
        )
        _db_conn.commit()
        message = f"Термин '{term}' успешно добавлен!"
    except sqlite3.IntegrityError as e:
        message = f"Произошла ошибка: термин '{term}' уже существует."

    _cursor.execute(f'SELECT COUNT(*) FROM terms')
    row_count = _cursor.fetchone()[0]
    # print(row_count)
    if row_count > 1:
        related_terms = find_related_terms(term, definition)

        _cursor.execute('''
                SELECT id
                FROM terms
                WHERE term = ?
            ''', (term,))

        term_id = _cursor.fetchone()[0]

        for related_term in related_terms:
            _cursor.execute('''
                    SELECT id
                    FROM terms
                    WHERE term = ?
                ''', (related_term,))

            related_term_id = _cursor.fetchone()[0]

            _cursor.execute('''
                    INSERT INTO relations (term_id, related_term_id, relation_type)
                    VALUES (?, ?, 'is_related_to')
                ''', (term_id, related_term_id))

        _db_conn.commit()
        # print("Больше одного")

    generate_graph()
    _cursor.execute("SELECT * FROM relations")
    relations = _cursor.fetchall()
    # print("relations")
    # print(relations)
    _cursor.execute("SELECT id, term, definition FROM terms")
    terms = _cursor.fetchall()

    return templates.TemplateResponse("index.html",
                                      {"request": request, "message": message, "terms": terms})


def find_related_terms(term, definition):
    _cursor.execute('''
        SELECT term, definition
        FROM terms
        WHERE term != ?
    ''', (term,))

    existing_terms = _cursor.fetchall()
    texts = [existing_term[1] for existing_term in existing_terms]
    texts.append(definition)
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(texts)

    cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    # print('cosine_similarities')
    # print(cosine_similarities[0])
    related_terms = []
    for index, score in enumerate(cosine_similarities[0]):
        # print("index, score, existing_terms")
        # print(index, score, existing_terms[index])
        if score > 0.049:  # Устанавливаем порог для фильтрации слабых связей
            # print(existing_terms[index][0])
            related_terms.append(existing_terms[index][0])  # Добавляем связанный термин
    # print("related_terms")
    # print(related_terms)
    return related_terms


@app.get("/glossary/{id}", response_model=Term)
async def get_term_by_name(id: str):
    _cursor.execute("SELECT * FROM terms WHERE id = ?", (id,))
    result = _cursor.fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail=f"Term {id} not found")
    return Term(term=result[1], definition=result[2])


@app.post("/update-term/")
async def update_term(term_id: int = Form(...),
                      new_term: str = Form(...),
                      new_definition: str = Form(...)):
    # Обновление записи в базе данных
    _cursor.execute("UPDATE terms SET term = ?, definition = ? WHERE id = ?",
                    (new_term, new_definition, term_id))

    _db_conn.commit()  # Сохранение изменений

    return {"message": f"Термин с ID '{term_id}' обновлен"}


@app.post('/delete-term/{term_id}')
async def delete_term(request: Request, term_id: str, method: str = Form(None)):
    if method == 'DELETE':
        try:
            _cursor.execute("DELETE FROM terms WHERE id = ?", (term_id,))
            _db_conn.commit()
            return {"message": f"Термин с ID '{term_id}' удалён"}
        except Exception as e:
            return {"error": str(e)}
    else:
        return {"error": "Неверный метод запроса."}


@app.get("/search/")
async def search_term_by_definition(request: Request, keyword: str = Query(...)):
    # logger.debug(f"/search/")
    # logger.debug(f"Получен запрос на получение термина: {keyword}")
    # Поиск терминов, содержащие указанный keyword
    query = f"""
            SELECT * FROM terms
            WHERE term LIKE '%{keyword}%'
               OR definition LIKE '%{keyword}%'
        """
    _cursor.execute(query)
    results = _cursor.fetchall()

    if not results:
        raise HTTPException(status_code=404,
                            detail=f"No terms found with the keyword '{keyword}' in their definitions.")

    terms = [[result[0], result[1], result[2]] for result in results]

    return templates.TemplateResponse("index.html", {"request": request, "terms": terms})


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    _cursor.execute("SELECT id, term, definition FROM terms")
    terms = _cursor.fetchall()
    # print(terms)
    _cursor.execute("SELECT * FROM relations")
    relations = _cursor.fetchall()
    # print(relations)
    return templates.TemplateResponse("index.html", {"request": request, "terms": terms})


with open('graph.json', 'r') as f:
    gexf_data = json.load(f)


@app.get("/mindmap", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("mindmap.html", {"request": request, "gexf_data": gexf_data})


def generate_graph():
    _cursor.execute('''
        SELECT id, term, definition
        FROM terms
    ''')

    nodes = _cursor.fetchall()

    _cursor.execute('''
        SELECT term_id, related_term_id
        FROM relations
    ''')

    edges = _cursor.fetchall()

    G = nx.DiGraph()

    for node in nodes:
        G.add_node(node[0], label=node[1], definition=node[2])

    for edge in edges:
        G.add_edge(edge[0], edge[1])

    graph_json = nx.node_link_data(G)
    with open('graph.json', 'w') as outfile:
        json.dump(graph_json, outfile)

    return True
