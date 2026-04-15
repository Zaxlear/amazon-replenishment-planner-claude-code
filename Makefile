.PHONY: dev-services dev-backend dev-frontend migrate test

dev-services:
	docker compose -f docker/docker-compose.dev.yml up -d

dev-services-down:
	docker compose -f docker/docker-compose.dev.yml down

dev-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

migrate:
	cd backend && alembic upgrade head

migrate-new:
	cd backend && alembic revision --autogenerate -m "$(msg)"

test:
	cd backend && python -m pytest -v

seed:
	cd backend && python -m scripts.seed_data
