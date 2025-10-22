release: python manage.py migrate
web: gunicorn string_analyser_service.wsgi --bind 0.0.0.0:$PORT
