#!/usr/bin/env python3
import sqlite3
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


# Global in-memory database connection
db_conn = None


def load_database_to_memory():
    """Load the SQLite database from disk into memory."""
    # Create in-memory database
    memory_conn = sqlite3.connect(":memory:", check_same_thread=False)
    memory_conn.row_factory = sqlite3.Row

    # Load from disk
    disk_conn = sqlite3.connect("tire_data.db")
    disk_conn.backup(memory_conn)
    disk_conn.close()

    print("Database loaded into memory")
    return memory_conn


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global db_conn
    db_conn = load_database_to_memory()

    # Get count
    cursor = db_conn.execute("SELECT COUNT(*) FROM tires")
    count = cursor.fetchone()[0]
    print(f"Loaded {count:} tires into memory")

    yield

    # Cleanup
    db_conn.close()


app = FastAPI(title="Tire Data API", lifespan=lifespan)


@app.get("/api/tires")
def search_tires(
    width: Optional[int] = Query(None, description="Tire width in mm"),
    profile: Optional[int] = Query(None, description="Tire profile/aspect ratio"),
    diameter: Optional[int] = Query(None, description="Wheel diameter in inches"),
    search: Optional[str] = Query(None, description="Search in tire name"),
    hide_all_season: bool = Query(True, description="Hide all-season tires"),
):
    """Search for tires based on query parameters."""

    # Build query
    query = "SELECT width, profile, diameter, full_name FROM tires WHERE 1=1"
    params = []

    if width is not None:
        query += " AND width = ?"
        params.append(width)

    if profile is not None:
        query += " AND profile = ?"
        params.append(profile)

    if diameter is not None:
        query += " AND diameter = ?"
        params.append(diameter)

    if search:
        query += " AND full_name LIKE ?"
        params.append(f"%{search}%")

    if hide_all_season:
        query += (
            " AND full_name NOT LIKE '%allseas%' AND full_name NOT LIKE '%all season%'"
        )

    query += " ORDER BY width, profile, diameter, full_name"

    # Execute query
    cursor = db_conn.execute(query, params)
    rows = cursor.fetchall()

    # Convert to list of dicts
    results = [
        {
            "width": row["width"],
            "profile": row["profile"],
            "diameter": row["diameter"],
            "full_name": row["full_name"],
        }
        for row in rows
    ]

    return results


@app.get("/")
def read_root():
    """Serve the main HTML page."""
    return FileResponse("tire_data.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7123)
