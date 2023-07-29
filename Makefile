COMPOSE := docker-compose -f docker-compose.yml

.PHONY: up
up:
	$(COMPOSE) up --build -d

down:
	$(COMPOSE) down -v

ps:
	$(COMPOSE) ps

bash:
	$(COMPOSE) exec backend bash

logs:
	$(COMPOSE) logs -f --tail 100 backend