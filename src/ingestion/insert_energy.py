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
JSON_FILE = "data/raw/energy.json"

# ------------------------------------------------------------------
# SQL Query
# ------------------------------------------------------------------
INSERT_QUERY = """
INSERT INTO energy
(timestamp, node, socket, cpu_energy, memory_energy, node_energy)
VALUES (%s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
cpu_energy = VALUES(cpu_energy),
memory_energy = VALUES(memory_energy),
node_energy = VALUES(node_energy)
"""

# ------------------------------------------------------------------
# Read concatenated JSON objects
# ------------------------------------------------------------------
def read_json_objects(file_path):

    with open(file_path, "r", encoding="utf-8") as file:

        buffer = ""
        braces = 0

        for line in file:

            buffer += line

            braces += line.count("{")
            braces -= line.count("}")

            if braces == 0 and buffer.strip():

                yield json.loads(buffer)

                buffer = ""


# ------------------------------------------------------------------
# Insert Energy Data
# ------------------------------------------------------------------
def insert_energy():

    print("========== START ==========")

    conn = get_connection()
    cursor = conn.cursor()

    rows = []

    for obj in read_json_objects(JSON_FILE):

        timestamp = obj["timestamp"]

        data = obj["data"]

        for node, node_data in data.items():

            node_energy = float(node_data["energy_node_joules"])

            for socket in [0, 1]:

                socket_key = f"socket_{socket}"

                socket_data = node_data[socket_key]

                cpu_energy = float(socket_data["energy_cpu_joules"])
                memory_energy = float(socket_data["energy_mem_joules"])

                rows.append(
                    (
                        timestamp,
                        node,
                        socket,
                        cpu_energy,
                        memory_energy,
                        node_energy
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
    insert_energy()