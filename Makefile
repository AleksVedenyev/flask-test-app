install:
	uv sync

start:
	uv run flask --app example --debug run --port 8000

build:
	uv run --env-file .env ./build.sh