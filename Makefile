.PHONY: up test

up:
	set -a; . deploy/.env; set +a; \
	docker compose -f deploy/docker-compose.yml up --build

test:
	cd backend && . .venv/bin/activate && pytest
	cd frontend && yarn test
