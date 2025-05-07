Start server
python httpd.py -r ./www -p 8000

Проверка:
http://localhost:8000/ → возвращает index.html
http://localhost:8000/page → возвращает page.html
http://localhost:8000/forbidden.html → 403, ошибка
http://localhost:8000/unknown.html → 404, ошибка
curl -X POST http://localhost:8000/ → 405


В сервере реализовано следующее:

Парсинг аргументов командной строки (-r, -w) 

Обработка запросов (GET, HEAD — 200/403/404, остальные — 405) 

Возврат файлов из DOCUMENT_ROOT

Обработка index.html для директорий

Корректные заголовки: Date, Server, Content-Length, Content-Type, Connection

Content-Type для: .html, .css, .js, .jpg, .jpeg, .png, .gif, .swf

Декодирование URL (%XX, пробелы)

