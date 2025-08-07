web: cd backend && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
worker: cd backend && celery -A app.workers.celery_app worker --loglevel=info
release: cd backend && alembic upgrade head