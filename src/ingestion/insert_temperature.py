print("SCRIPT STARTED")
import os
import sys
import json
import traceback

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.mysql_connection import get_connection

JSON_FILE = r"data/raw/temp.json"

INSERT_QUERY = """
INSERT INTO temperature
(timestamp,node,socket,core,temperature)
VALUES (%s,%s,%s,%s,%s)
ON DUPLICATE KEY UPDATE
temperature=VALUES(temperature)
"""


def insert_temperature():

    print("========== START ==========")

    conn = get_connection()
    cursor = conn.cursor()

    rows = []

    try:

        with open(JSON_FILE, "r", encoding="utf-8") as file:

            buffer = ""
            braces = 0

            for line in file:

                buffer += line

                braces += line.count("{")
                braces -= line.count("}")

                if braces == 0 and buffer.strip():

                    obj = json.loads(buffer)

                    buffer = ""

                    timestamp = obj["timestamp"]

                    for node, node_data in obj["data"].items():

                        for socket_name, socket_data in node_data.items():

                            if not socket_name.startswith("socket_"):
                                continue

                            socket = int(socket_name.split("_")[1])

                            cores = socket_data["CPU"]["Core"]

                            for core_name, temp in cores.items():

                                core = int(
                                    core_name.replace(
                                        "temp_celsius_core_",
                                        ""
                                    )
                                )

                                rows.append(
                                    (
                                        timestamp,
                                        node,
                                        socket,
                                        core,
                                        float(temp),
                                    )
                                )

        print(f"Prepared {len(rows)} rows")

        cursor.executemany(INSERT_QUERY, rows)

        conn.commit()

        print(f"Inserted {cursor.rowcount} rows successfully.")

    except Exception:

        conn.rollback()

        traceback.print_exc()

    finally:

        cursor.close()
        conn.close()

        print("========== END ==========")


print("__name__ =", __name__)

if __name__ == "__main__":
    print("Calling insert_temperature()")
    insert_temperature()