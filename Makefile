.PHONY: setup test build run clean

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements-dev.txt

test:
	. .venv/bin/activate && pytest -v

build:
	docker build -t eexperts-test-api .

run:
	docker run -p 8080:8080 eexperts-test-api

clean:
	docker rm -f $$(docker ps -aq --filter ancestor=eexperts-test-api) 2>/dev/null || true
	docker rmi eexperts-test-api 2>/dev/null || true