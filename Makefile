start:
	sudo docker compose up --build --force-recreate --remove-orphans

start-silent:
	sudo docker compose up -d --build --force-recreate --remove-orphans

delete:
	sudo docker compose down -v --remove-orphans
	sudo docker rm -f fastapi-clean-architecture-ddd-template