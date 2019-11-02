DJANGO_CONTAINER_NAME = web

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