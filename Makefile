.PHONY: run

run:
	uv run python serve.py &
	firefox http://localhost:8000/tire_data.html
