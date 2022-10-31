export PIPENV_VERBOSITY=-1

# Dev utilities
develop:
	docker-compose up -d

deps:
	docker-compose build

docker_clean_build:
	docker-compose build --no-cache runserver

clean_locks:
	rm -f Pipfile.lock || true
	pipenv lock --clear --verbose

fix-file-ownership: # Fix docker-created files that are owned by root user
	@echo "When running docker, files created by the application are owned by the root user."
	@echo "This task fixes file ownership by resetting the owner of the directory to the current user."
	@echo "SUDO permission is required to fix this, you may be prompted for your password..."
	find . -uid 0 &>/dev/null && sudo chown -R ${USER}:${USER} .

format:
	make fix-file-ownership
	make black
	make isort
	make autoflake

precommit:
	make format
	make test

migrations:
ifndef NAME
	$(error NAME is undefined)
endif
	bin/dev aerich migrate --name $(NAME)
	@make fix-file-ownership
	bin/dev aerich upgrade

migrate:
	bin/dev aerich upgrade

# Docker homeasssistant management
ha_clean:
	dc kill homeassistant
	dc rm -f homeassistant
	docker volume rm -f plantassistant_homeassistant

ha_shell:
	dc up -d homeassistant
	dc exec homeassistant bash

ha_extract_fixtures:
	dc up -d homeassistant
	docker cp plantassistant_homeassistant_1:/config/.storage/ docker/homeassistant

ha_install_fixture:
	dc up -d homeassistant
	docker cp docker/homeassistant/$(FIXTURE) plantassistant_homeassistant_1:/tmp
	dc exec homeassistant rm -rf /config/.storage
	dc exec homeassistant cp -r /tmp/$(FIXTURE) /config/.storage
	dc kill homeassistant
	dc rm -f homeassistant
	dc up -d homeassistant

ha_install_fixture_empty_instance:
	make ha_install_fixture FIXTURE=empty_instance

ha_read_token:
	dc exec homeassistant cat /config/.storage/auth | jq -r '.data.refresh_tokens[] | select(.token_type == "long_lived_access_token")'

# CI Pipeline & Tests

pytest: # Base pytest command, plus any arguments
	pytest

docker_test: # Run tests in docker
	dc run devcontainer make pytest

test: # Shortcut for clearing HA docker data and running pytest in docker
	make ha_install_fixture_empty_instance
	make docker_test

test_backend_coverage:
	pytest --cov=plantassistant/app/ --cov-config=.coveragerc --cov-report html --cov-report term
	echo "View coverage report: file://${PWD}/htmlcov/index.html"
docker_test_backend_coverage:
	dc run devcontainer make test

# Codebase Linting & Cleanup
clean:
	find . -name '*.pyc' -delete

isort:
	isort plantassistant/

flake8:
	flake8

autoflake:
	autoflake -r -i --expand-star-imports --remove-all-unused-imports --remove-duplicate-keys --remove-unused-variables --ignore-init-module-imports plantassistant/

black:
	black plantassistant/

lint:
	black --check plantassistant/
