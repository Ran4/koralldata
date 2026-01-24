.PHONY: run

run:
	uv run python serve.py &
	firefox http://localhost:7123
