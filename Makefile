.PHONY: run raw_tire_data.json tire_data.db

run:
	uv run python serve.py &
	firefox http://localhost:7123

# Fetch a fresh dump from Koralldata into data/. Always re-runs.
raw_tire_data.json:
	uv run python -m get_tire_data_json_from_koralldata

# Build the SQLite DB from the dump already in data/ (does NOT re-fetch).
# For a full refresh run: make raw_tire_data.json && make tire_data.db
tire_data.db:
	uv run python create_db_from_tire_data_json.py
