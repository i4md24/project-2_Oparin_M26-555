# primitive_db Makefile: install / run / lint

.PHONY: install run lint

install:
	uv sync

run:
	uv run database

lint:
	uv run ruff check .
