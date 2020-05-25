web: gunicorn application:app
worker: celery -A tasks worker --loglevel info
