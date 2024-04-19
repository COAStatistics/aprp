# Makefile - common commands for development.

DJANGO_CONTAINER_NAME = web
DJANGO_SERVICE_NAME = web
DATABASE_SERVICE_NAME = postgres
PGADMIN_SERVICE_NAME = pgadmin
REDIS_SERVICE_NAME = redis
REDIS_COMMANDER_SERVICE_NAME = redis-commander
JUPYTER_NOTEBOOK_SERVICE_NAME = notebook
MAIL_HOG_SERVICE_NAME = mailhog
BEAT_SERVICE_NAME = beat
WORKER_SERVICE_NAME = worker

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

## run postgres service
up-postgres:
	docker-compose -f docker-compose.dev.yml up ${DATABASE_SERVICE_NAME} -d

## run pgadmin service
up-pgadmin:
	docker-compose -f docker-compose.dev.yml up ${PGADMIN_SERVICE_NAME} -d

## run redis service
up-redis:
	docker-compose -f docker-compose.dev.yml up ${REDIS_SERVICE_NAME} -d

## run web service
up-redis-commander:
	docker-compose -f docker-compose.dev.yml up ${REDIS_COMMANDER_SERVICE_NAME} -d

## run web service
up-web:
	docker-compose -f docker-compose.dev.yml up ${DJANGO_SERVICE_NAME} -d


## run beat service
up-beat:
	docker-compose -f docker-compose.dev.yml up ${BEAT_SERVICE_NAME} -d

## run worker service
up-worker:
	docker-compose -f docker-compose.dev.yml up ${WORKER_SERVICE_NAME} -d

## run jupyter service
up-jupyter:
	docker-compose -f docker-compose.dev.yml up ${JUPYTER_NOTEBOOK_SERVICE_NAME} -d

## run mail service
up-mail:
	docker-compose -f docker-compose.dev.yml up ${MAIL_HOG_SERVICE_NAME} -d

## build and run web service, if image source is updated
build-web:
	docker-compose -f docker-compose.dev.yml up --build ${DJANGO_SERVICE_NAME} -d

## docker compose up in development and background
up-dev:
	docker-compose -f docker-compose.dev.yml up -d

down-dev:
	docker-compose -f docker-compose.dev.yml down

## make migrations in web service
migrate:
	docker-compose -f docker-compose.dev.yml exec ${DJANGO_SERVICE_NAME} python manage.py makemigrations
	docker-compose -f docker-compose.dev.yml exec ${DJANGO_SERVICE_NAME} python manage.py migrate

## run pytest-cov with web service
pytest-cov:
	docker-compose run ${DJANGO_SERVICE_NAME} pytest --cov-report html --cov=.

## Check to see if the local postgres service service is running
pg-is-ready:
	docker-compose exec ${DATABASE_SERVICE_NAME} pg_isready

## Check to see if the local redis service is running
redis-ping:
	docker-compose exec ${REDIS_SERVICE_NAME} redis-cli ping
