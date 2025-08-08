web: bash -c "cd frontend && npm ci && npm run build && cd ../backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT"
worker: cd backend && celery -A app.workers.celery_app worker --loglevel=info
release: cd backend && python scripts/init_postgis.py && alembic upgrade head