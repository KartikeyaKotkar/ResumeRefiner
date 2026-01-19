
# Variables
IMAGE_NAME = resume-refiner
CONTAINER_NAME = resume-refiner-app
PORT = 5000

# Colors
GREEN = \033[0;32m
NC = \033[0m # No Color

.PHONY: help build run stop clean test lint

help:
	@echo "$(GREEN)Available commands:$(NC)"
	@echo "  make build    - Build the Docker image"
	@echo "  make run      - Run the container (detached)"
	@echo "  make stop     - Stop and remove the container"
	@echo "  make logs     - View container logs"
	@echo "  make clean    - Remove image and container"
	@echo "  make test     - Run tests locally"
	@echo "  make lint     - Run linting checks"

build:
	@echo "$(GREEN)Building Docker image...$(NC)"
	docker build -t $(IMAGE_NAME) .

run:
	@echo "$(GREEN)Starting container...$(NC)"
	@if [ ! -f .env ]; then echo "Error: .env file not found. Copy .env.example to .env"; exit 1; fi
	docker run -d --name $(CONTAINER_NAME) -p $(PORT):$(PORT) --env-file .env $(IMAGE_NAME)
	@echo "App running on http://localhost:$(PORT)"

stop:
	@echo "$(GREEN)Stopping container...$(NC)"
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

logs:
	docker logs -f $(CONTAINER_NAME)

clean: stop
	@echo "$(GREEN)Cleaning up...$(NC)"
	docker rmi $(IMAGE_NAME) || true

test:
	@echo "$(GREEN)Running tests...$(NC)"
	# Ensure PYTHONPATH includes current directory
	export PYTHONPATH=.:$$PYTHONPATH && pytest

lint:
	@echo "$(GREEN)Running linting...$(NC)"
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
