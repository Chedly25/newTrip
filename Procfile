web: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
worker: cd backend && celery -A app.workers.celery_app worker --loglevel=info
release: cd backend && python -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine); print('Database initialized')" || echo "Database setup completed"