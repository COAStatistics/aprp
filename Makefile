# Makefile - common commands for development.

DJANGO_CONTAINER_NAME = web
DJANGO_SERVICE_NAME = web
DATABASE_SERVICE_NAME = postgres
REDIS_SERVICE_NAME = redis

## -- docker targets --

init:
	docker exec -it ${DJANGO_CONTAINER_NAME} ./scripts/init_data.sh

ps:
	docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}'

attach:
	docker exec -it ${DJANGO_CONTAINER_NAME} bash

shell:
	docker exec -it ${DJANGO_CONTAINER_NAME} python manage.py shell

test:
	docker exec ${DJANGO_CONTAINER_NAME} pytest -m "not secret"


## -- docker-compose targets --

## validate file
config:
	docker-compose config

## run db service
up-db:
	docker-compose -f docker-compose.dev.yml up ${DATABASE_SERVICE_NAME} -d

## run redis service
up-redis:
	docker-compose -f docker-compose.dev.yml up ${REDIS_SERVICE_NAME} -d

## docker compose up in development and background
up-dev:
	docker-compose -f docker-compose.dev.yml up -d

down-dev:
	docker-compose down -f docker-compose.dev.yml

## make migrations in web service
migrate:
	docker-compose run ${DJANGO_SERVICE_NAME} python manage.py makemigrations && python manage.py migrate

## jupyter notebook
jupyter:
	docker-compose run ${DJANGO_SERVICE_NAME} -c "cd notebooks && ../manage.py shell_plus --notebook"

## run pytest-cov with web service
pytest-cov:
	docker-compose run ${DJANGO_SERVICE_NAME} pytest --cov-report html --cov=.

## Check to see if the local postgres service service is running
pg-is-ready:
	docker-compose exec ${DATABASE_SERVICE_NAME} pg_isready

## Check to see if the local redis service is running
redis-ping:
	docker-compose exec ${REDIS_SERVICE_NAME} redis-cli ping
