# Отчет

![Приложение](https://sun9-9.userapi.com/impg/O5LVMQUiEsdmd8M-TGuvXtbnAy2SuVrMA_o5FQ/XqThJZKtt_c.jpg?size=1275x601&quality=95&sign=d1fee034cbe151da588e061551a2313c&type=album)
### Получение списка всех терминов.
@app.get("/", response_class=HTMLResponse)
также выполняется почти в каждой другой функции
### Получение информации о конкретном термине по ключевому слову.
@app.get("/search/")
### Добавление нового термина с описанием.
@app.post("/add-term/", response_class=HTMLResponse)
### Обновление существующего термина.
@app.post("/update-term/")
### Удаление термина из глоссария.
@app.post('/delete-term/{term_id}')

## База данных
В проекте используется две таблицы: terms и relations

![Таблицы БД](https://sun9-11.userapi.com/s/v1/ig2/K_0stisdQPrVwjk14j69rJMJGvqbfvw3lnV3dy_2eEwY0Pm30vH8cVHcLCSvFN9ow2VQZyxT2atgU3JCTGx029NQ.jpg?quality=95&as=32x13,48x20,72x30,108x45,160x67,240x100,360x151,361x151&from=bu&u=4IoMTVtgdqltBH3Sp_N26F8_HGWsoXLZI9f8CB3dYkw&cs=361x151)

## MindMap
![Mindmap](https://sun9-56.userapi.com/impg/5E8kiMoszzMU9epTvg3LpnHP6mV3JX8vtDPqog/chxmJIvtrsk.jpg?size=1280x601&quality=95&sign=cff9a45c86c8613405f1528235874c8c&type=album)
### find_related_terms()
Функция вызывается при добавлении нового термина и ищет ему связанный термин. Это выполняется при помощи библиотеки sklearn.
Используется класс TfidfVectorizer для создания матрицы TF-IDF. Эта матрица будет содержать взвешенные значения каждого слова в каждом определении. 
Функция cosine_similarity вычисляет косинусную меру схожести между последним элементом матрицы TF-IDF (текущим определением) и всеми остальными элементами (определениями других терминов).
Проходимся по каждому элементу списка косинусных мер схожести. Если значение больше установленного порога (в данном случае 0.049 - выяснил путем проб и ошибок), то соответствующий термин добавляется в список related_terms.

### generate_graph()
создает json с узлами графа и связями между узлами

### mindmap.html
Была использована библиотека [vis.js](https://visjs.github.io/vis-network/docs/network/). Библиотека представляет возможность создания визуализации графов. Для проекта была отключена physics для того, чтобы при перетягивании графов другие графы как резинкой не перетягивались.

![Mindmap without physics](https://sun9-25.userapi.com/impg/g5E-FPzzx3mrujZzkZZZ9qtN3sCVzl7IxRMI-Q/AZW1uX4Ta64.jpg?size=1280x589&quality=95&sign=336ff599ab51fcabf119a1fef611a9d3&type=album)

### Dockerfile
Копируются все файлы репозитория
Устанавливаются необходимые библиотеки из requirements.txt 
Далее сборка и запуск контейнера через команды:
docker build -t my-app .
docker run -p 8000:8000 my-app
