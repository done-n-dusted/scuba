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
	@echo "Setting up frontend... (Assuming package.json framework in future)"
	cd apps/frontend && echo "Install command (e.g. npm install) goes here"

setup: setup-backend setup-frontend

start-backend:
	cd apps/backend/python && poetry run uvicorn main:app --reload

start-frontend:
	@echo "Starting frontend... (Assuming npm run dev in future)"
	cd apps/frontend && echo "Run command (e.g. npm run dev) goes here"

start: start-backend start-frontend
