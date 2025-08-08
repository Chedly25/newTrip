web: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
worker: cd backend && celery -A app.workers.celery_app worker --loglevel=info
release: npm run build && cd backend && python scripts/init_postgis.py && alembic upgrade head