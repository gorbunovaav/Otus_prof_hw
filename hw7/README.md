Start server
python httpd.py -r ./www -p 8000

Проверка:
curl -i http://localhost:8000/ → 200

curl -I http://localhost:8000/forbidden → 403

curl -i http://localhost:8000/unknown → 404

curl -X POST http://localhost:8000/ → 405



Парсинг аргументов командной строки (-r, -w) 

Обработка запросов (GET, HEAD — 200/403/404, остальные — 405) 

Возврат файлов из DOCUMENT_ROOT

Обработка index.html для директорий

Корректные заголовки: Date, Server, Content-Length, Content-Type, Connection

Content-Type для: .html, .css, .js, .jpg, .jpeg, .png, .gif, .swf

Декодирование URL (%XX, пробелы)

Опционально: многопроцессная обработка с помощью multiprocessing