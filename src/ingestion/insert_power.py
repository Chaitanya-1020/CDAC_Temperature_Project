import os
import sys
import json

# ------------------------------------------------------------------
# Add project root
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
JSON_FILE = "data/raw/power.json"

# ------------------------------------------------------------------
# SQL Query
# ------------------------------------------------------------------
INSERT_QUERY = """
INSERT INTO power
(timestamp, node, socket, cpu_power, memory_power, node_power)
VALUES (%s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
cpu_power=VALUES(cpu_power),
memory_power=VALUES(memory_power),
node_power=VALUES(node_power)
"""

# ------------------------------------------------------------------
# Read concatenated JSON objects
# ------------------------------------------------------------------
def read_json_objects(file_path):

    with open(file_path, "r", encoding="utf-8") as f:

        buffer = ""
        braces = 0

        for line in f:

            buffer += line

            braces += line.count("{")
            braces -= line.count("}")

            if braces == 0 and buffer.strip():

                yield json.loads(buffer)

                buffer = ""

# ------------------------------------------------------------------
# Insert Power Data
# ------------------------------------------------------------------
def insert_power():

    print("========== START ==========")

    conn = get_connection()
    cursor = conn.cursor()

    rows = []

    for obj in read_json_objects(JSON_FILE):

        timestamp = obj["timestamp"]

        data = obj["data"]

        for node, node_data in data.items():

            node_power = float(node_data["power_node_watts"])

            for socket in [0, 1]:

                socket_key = f"socket_{socket}"

                socket_data = node_data[socket_key]

                cpu_power = float(socket_data["power_cpu_watts"])
                memory_power = float(socket_data["power_mem_watts"])

                rows.append(
                    (
                        timestamp,
                        node,
                        socket,
                        cpu_power,
                        memory_power,
                        node_power
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
    insert_power()