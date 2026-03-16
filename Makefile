start:
	sudo docker compose up --build --force-recreate --remove-orphans

start-silent:
	sudo docker compose up -d --build --force-recreate --remove-orphans

view-processes:
	sudo docker ps -a

delete:
	sudo docker compose down -v --remove-orphans
	sudo docker rm -f fastapi-clean-architecture-ddd-template-api fastapi-clean-architecture-ddd-template-database fastapi-clean-architecture-ddd-template-database-admin

dependencies-up:
	sudo docker compose -f docker-compose.yaml up --build --force-recreate --remove-orphans database database-admin

dependencies-up-silent:
	sudo docker compose -f docker-compose.yaml up -d --build --force-recreate --remove-orphans database database-admin

dependencies-down:
	sudo docker compose -f docker-compose.yaml down -v --remove-orphans