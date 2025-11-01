#!/usr/bin/env python3
import json
import re
import sqlite3
from typing import Optional

def extract_tire_dimensions(tire_name: str) -> Optional[dict]:
    """Extract width, profile, and diameter from tire name."""
    # Pattern: width/profile R diameter (e.g., "235/35 R19")
    pattern = r'(\d{2,3})/(\d{2})\s*[RD]\s*(\d{2})'
    match = re.search(pattern, tire_name)

    if match:
        return {
            "width": int(match.group(1)),
            "profile": int(match.group(2)),
            "diameter": int(match.group(3)),
            "full_name": tire_name.strip()
        }
    return None

def extract_tire_strings(obj, results=None):
    """Recursively extract all strings that look like tire names from JSON structure."""
    if results is None:
        results = []

    if isinstance(obj, dict):
        # Check if this is a "v" field with tire data
        if "v" in obj and isinstance(obj["v"], str):
            v = obj["v"].strip()
            # Check if it looks like a tire name (contains width/profile pattern)
            if re.search(r'\d{2,3}/\d{2}\s*[RD]\s*\d{2}', v):
                results.append(v)

        # Recurse into all values
        for value in obj.values():
            extract_tire_strings(value, results)

    elif isinstance(obj, list):
        for item in obj:
            extract_tire_strings(item, results)

    return results

def main():
    print("Loading raw_tire_data.json...")
    with open('raw_tire_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("Extracting tire names...")
    tire_names = extract_tire_strings(data)
    print(f"Found {len(tire_names)} tire name entries")

    print("Parsing tire dimensions...")
    tire_list = []
    seen = set()  # Track unique combinations

    for tire_name in tire_names:
        tire_info = extract_tire_dimensions(tire_name)
        if tire_info:
            # Create a unique key to avoid duplicates
            key = (tire_info["width"], tire_info["profile"], tire_info["diameter"], tire_info["full_name"])
            if key not in seen:
                seen.add(key)
                tire_list.append(tire_info)

    print(f"Parsed {len(tire_list)} unique tires")

    # Sort by width, profile, diameter
    tire_list.sort(key=lambda x: (x["width"], x["profile"], x["diameter"], x["full_name"]))

    # Save to SQLite database
    print("\nSaving to SQLite database...")
    conn = sqlite3.connect('tire_data.db')
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tires (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            width INTEGER NOT NULL,
            profile INTEGER NOT NULL,
            diameter INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            UNIQUE(width, profile, diameter, full_name)
        )
    ''')

    # Insert data
    cursor.executemany(
        'INSERT OR IGNORE INTO tires (width, profile, diameter, full_name) VALUES (?, ?, ?, ?)',
        [(t['width'], t['profile'], t['diameter'], t['full_name']) for t in tire_list]
    )

    conn.commit()
    print(f"Saved {cursor.rowcount} tires to tire_data.db")

    # Show some stats
    cursor.execute('SELECT COUNT(*) FROM tires')
    total = cursor.fetchone()[0]
    print(f"Total tires in database: {total}")

    conn.close()

    # Show some examples
    print("\nFirst 5 examples:")
    for tire in tire_list[:5]:
        print(tire)

if __name__ == "__main__":
    main()
