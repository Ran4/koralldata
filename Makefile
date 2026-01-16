.PHONY: run

run:
	uv run python serve.py &
	firefox http://localhost:7123/tire_data.html
