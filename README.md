# Глоссарий терминов ВКР


![Приложение](https://sun9-9.userapi.com/impg/O5LVMQUiEsdmd8M-TGuvXtbnAy2SuVrMA_o5FQ/XqThJZKtt_c.jpg?size=1275x601&quality=95&sign=d1fee034cbe151da588e061551a2313c&type=album)
![Mindmap](https://sun9-56.userapi.com/impg/5E8kiMoszzMU9epTvg3LpnHP6mV3JX8vtDPqog/chxmJIvtrsk.jpg?size=1280x601&quality=95&sign=cff9a45c86c8613405f1528235874c8c&type=album)

## 1. Цель и задачи лабораторной работы

В ходе выполнения лабораторной работы необходимо было создать сервис на базе **FastAPI** для управления словарём терминов по теме ВКР. Основные задачи:

1. Создание полного глоссария употребляемых терминов с хранением в Базе Данных.
2. Поиск связей между употребляемыми терминами.
3. Построение семантического графа (MindMap) понятий и обеспечение визуализации терминов и связей между ними.
4. Создать контейнер для обеспечения возможности развертывания на произвольной платформе.

## 2. Структура проекта

1. **main.py**  
   Создание приложения FastApi, работа с базой данных, работа с MindMap
2. **Dockerfile**  
   Cценарный файл, который используется для создания образа Docker
3. **graph.json**
   Json файл, содержащий связи между терминами
4. **templates/index.html**  
   html файл главная страницы сайта
5. **templates/mindmap.html**  
   html файл страницы Mindmap
6. **requirements.txt**  
   Зависимости проекта

## 3. Используемые технологии

- **Python 3.10**, фреймворк **FastAPI**
- **SQLite** для хранения терминов и связей между ними
- **Pydantic** для описания и валидации схем
- **Uvicorn** для запуска FastAPI
- **Docker** для контейнеризации
- **sklearn** для поиска и создания связей между терминами
- **[vis.js](https://visjs.github.io/vis-network/docs/network/)** для визуализации Mindmap

## 4. База данных
В проекте используется две таблицы: terms и relations

![Таблицы БД](https://sun9-11.userapi.com/s/v1/ig2/K_0stisdQPrVwjk14j69rJMJGvqbfvw3lnV3dy_2eEwY0Pm30vH8cVHcLCSvFN9ow2VQZyxT2atgU3JCTGx029NQ.jpg?quality=95&as=32x13,48x20,72x30,108x45,160x67,240x100,360x151,361x151&from=bu&u=4IoMTVtgdqltBH3Sp_N26F8_HGWsoXLZI9f8CB3dYkw&cs=361x151)

## 5. Запуск в Docker
Для запуска приложения в докере необходимо:  
1. Собрать образ:
   ```bash
   docker build -t my-app .
   ```
2. Запустить контейнер:
   ```bash
   docker run -p 8000:8000 my-app
   ```
3. Приложение станет доступно на `http://127.0.0.1:8000`.


## P.S. MindMap
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
