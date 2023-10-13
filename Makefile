install-packages:
	pip install -r requirements.txt

prepare-init-project:
	cp .env.example .env
	pip install -r requirements.txt
	mkdir static staticfiles log media
	python manage.py collectstatic --noinput
	python manage.py migrate
	make load-fixtures

run:
	python manage.py runserver

run-sockets:
	daphne -b 0.0.0.0 -p 8001 app.asgi:application

makemigrations:
	python manage.py makemigrations -n $(argument)

migrate:
	python manage.py migrate

collect:
	python manage.py collectstatic --noinput

shell:
	python manage.py shell

celery:
	celery -A app worker -l info

celery-beat:
	celery -A app beat -l info

load-fixtures:
	python manage.py loaddata fixtures/users/user_type.json
	python manage.py loaddata fixtures/users/users.json

tests-clusters:
	python manage.py test core.cluster

tests-machines:
	python manage.py test core.machine

tests-devices:
	python manage.py test core.device
