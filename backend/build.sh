#!/usr/bin/env bash
# Скрипт сборки бэкенда для Render.
# Останавливаемся при первой ошибке.
set -o errexit

pip install -r requirements.txt

# Собрать статику (для админки Django).
python manage.py collectstatic --no-input

# Применить миграции.
python manage.py migrate

# Наполнить демонстрационными данными (идемпотентно).
python manage.py seed_data
python manage.py seed_users
python manage.py seed_reviews
