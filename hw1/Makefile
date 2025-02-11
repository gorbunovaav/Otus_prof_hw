# Установка зависимостей
install: pip install -r requirements.txt

# Запуск тестов
test: pytest

# Проверка стиля кода
lint: flake8 .

# Форматирование кода
format: black .

# Очистка сгенерированных файлов
clean: find . -type f -name "*.pyc" -delete find . -type d -name "__pycache__" -delete

# Запуск приложения
run: python main.py

# Комбинированная задача: установка зависимостей и запуск тестов
setup: install test