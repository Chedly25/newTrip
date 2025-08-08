web: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
worker: cd backend && celery -A app.workers.celery_app worker --loglevel=info
release: bash build_frontend.sh && cd backend && python scripts/init_postgis.py && alembic upgrade head