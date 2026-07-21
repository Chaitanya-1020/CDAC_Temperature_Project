import os
import sys
import json

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
# JSON File Path
# ------------------------------------------------------------------
JSON_FILE = "data/raw/frequency.json"

# ------------------------------------------------------------------
# SQL Query
# ------------------------------------------------------------------
INSERT_QUERY = """
INSERT INTO frequency
(timestamp, node, socket, core, frequency)
VALUES (%s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
frequency = VALUES(frequency)
"""

# ------------------------------------------------------------------
# Read Concatenated JSON Objects
# ------------------------------------------------------------------
def read_json_objects(file_path):

    with open(file_path, "r", encoding="utf-8") as file:

        buffer = ""
        brace_count = 0

        for line in file:

            buffer += line

            brace_count += line.count("{")
            brace_count -= line.count("}")

            if brace_count == 0 and buffer.strip():

                yield json.loads(buffer)

                buffer = ""


# ------------------------------------------------------------------
# Insert Frequency Data
# ------------------------------------------------------------------
def insert_frequency():

    print("========== START ==========")

    conn = get_connection()
    cursor = conn.cursor()

    rows = []

    for obj in read_json_objects(JSON_FILE):

        timestamp = obj["timestamp"]

        for node_name, node_data in obj["data"].items():

            for socket_name, socket_data in node_data.items():

                if not socket_name.startswith("socket_"):
                    continue

                socket_number = int(socket_name.split("_")[1])

                cpu = socket_data.get("CPU", {})

                core_data = cpu.get("core", {})

                for key, value in core_data.items():

                    if not key.startswith("core_"):
                        continue

                    if not key.endswith("_avg_freq_mhz"):
                        continue

                    core_number = int(
                        key.replace("core_", "").replace("_avg_freq_mhz", "")
                    )

                    rows.append(
                        (
                            timestamp,
                            node_name,
                            socket_number,
                            core_number,
                            float(value),
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
    insert_frequency()