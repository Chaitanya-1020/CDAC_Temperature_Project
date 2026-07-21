import os
from platform import node
import sys
import json
import re

# ------------------------------------------------------------------
# Add project root to Python path
# ------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.mysql_connection import get_connection

# ------------------------------------------------------------------
# JSON File
# ------------------------------------------------------------------
JSON_FILE = "data/raw/cpu_usage.json"

# ------------------------------------------------------------------
# SQL Query
# ------------------------------------------------------------------
INSERT_QUERY = """
INSERT INTO cpu_usage
(timestamp, node, socket, core, cpu_usage)
VALUES (%s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
cpu_usage = VALUES(cpu_usage)
"""

# ------------------------------------------------------------------
# Read concatenated JSON
# ------------------------------------------------------------------
def read_json_objects(file_path):
    """
    Reads concatenated JSON objects.
    Repairs malformed values like:
        "core": 12:40:21
    by converting them to:
        "core": "12:40:21"
    """

    with open(file_path, "r", encoding="utf-8") as file:

        buffer = ""
        braces = 0

        for line in file:

            # Repair invalid JSON
            line = re.sub(
                r'"core"\s*:\s*([0-9]{2}:[0-9]{2}:[0-9]{2})',
                r'"core":"\1"',
                line
            )

            buffer += line

            braces += line.count("{")
            braces -= line.count("}")

            if braces == 0 and buffer.strip():

                yield json.loads(buffer)

                buffer = ""
# ------------------------------------------------------------------
# Insert CPU Usage
# ------------------------------------------------------------------
def insert_cpu_usage():

    print("========== START ==========")

    conn = get_connection()
    cursor = conn.cursor()

    rows = []

    for obj in read_json_objects(JSON_FILE):
        timestamp = obj["timestamp"]
        data = obj["data"]

        node = data["node"]
        cores = data["cores"]

        # Remove overall CPU usage
        core_values = cores[1:49]

        if len(core_values) != 48:
            print(f"{timestamp} -> Expected 48 cores, got {len(core_values)}")
            continue

        for idx, core_data in enumerate(core_values):
            cpu_usage = float(core_data["cpu_usage"])

            if idx < 24:
                socket = 0
                core = idx
            else:
                socket = 1
                core = idx - 24

            rows.append(
                (
                    timestamp,
                    node,
                    socket,
                    core,
                    cpu_usage
                )
            )

    print(f"Prepared {len(rows)} rows")

    cursor.executemany(INSERT_QUERY, rows)

    conn.commit()

    print(f"Inserted {cursor.rowcount} rows successfully.")

    cursor.close()
    conn.close()

    print("=========== END ===========")
# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
if __name__ == "__main__":
    insert_cpu_usage()