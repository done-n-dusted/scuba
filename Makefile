.PHONY: help setup-backend setup-frontend setup start-backend start-frontend start

help:
	@echo "Available commands:"
	@echo "  make setup           - Install dependencies for both backend and frontend"
	@echo "  make setup-backend   - Install backend Python dependencies via Poetry"
	@echo "  make setup-frontend  - Install frontend dependencies"
	@echo "  make start           - Start both backend and frontend servers sequentially"
	@echo "  make start-backend   - Start the FastAPI backend server"
	@echo "  make start-frontend  - Start the frontend development server"

setup-backend:
	cd apps/backend/python && poetry install

setup-frontend:
	npm install

setup: setup-backend setup-frontend

start-backend:
	cd apps/backend/python && poetry run uvicorn main:app --reload

start-frontend:
	npm run dev

start: start-backend start-frontend

status:
	@python3 scripts/status.py

get-status: status
