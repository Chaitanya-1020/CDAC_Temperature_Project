import os
import sys
import pandas as pd

# ----------------------------------------------------------
# Add Project Root
# ----------------------------------------------------------
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.mysql_connection import get_connection

OUTPUT_DIR = "data/processed"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "merged_dataset.csv")


def merge_tables():

    print("=" * 70)
    print("MERGING DATASETS")
    print("=" * 70)

    conn = get_connection()

    # ------------------------------------------------------
    # Read Tables
    # ------------------------------------------------------
    temperature = pd.read_sql("SELECT * FROM temperature", conn)
    frequency = pd.read_sql("SELECT * FROM frequency", conn)
    cpu_usage = pd.read_sql("SELECT * FROM cpu_usage", conn)
    power = pd.read_sql("SELECT * FROM power", conn)
    energy = pd.read_sql("SELECT * FROM energy", conn)

    print(f"Temperature : {len(temperature)}")
    print(f"Frequency   : {len(frequency)}")
    print(f"CPU Usage   : {len(cpu_usage)}")
    print(f"Power       : {len(power)}")
    print(f"Energy      : {len(energy)}")

    # ------------------------------------------------------
    # Remove id columns
    # ------------------------------------------------------
    temperature = temperature.drop(columns=["id"])
    frequency = frequency.drop(columns=["id"])
    cpu_usage = cpu_usage.drop(columns=["id"])
    power = power.drop(columns=["id"])
    energy = energy.drop(columns=["id"])

    # ------------------------------------------------------
    # Merge Temperature + Frequency
    # ------------------------------------------------------
    merged = pd.merge(
        temperature,
        frequency,
        on=["timestamp", "node", "socket", "core"],
        how="inner",
    )

    print(f"\nAfter Temperature + Frequency : {len(merged)}")

    # ------------------------------------------------------
    # Merge CPU Usage
    # ------------------------------------------------------
    merged = pd.merge(
        merged,
        cpu_usage,
        on=["timestamp", "node", "socket", "core"],
        how="inner",
    )

    print(f"After CPU Usage              : {len(merged)}")

    # ------------------------------------------------------
    # Merge Power
    # ------------------------------------------------------
    merged = pd.merge(
        merged,
        power,
        on=["timestamp", "node", "socket"],
        how="left",
    )

    print(f"After Power                  : {len(merged)}")

    # ------------------------------------------------------
    # Merge Energy
    # ------------------------------------------------------
    merged = pd.merge(
        merged,
        energy,
        on=["timestamp", "node", "socket"],
        how="left",
    )

    print(f"After Energy                 : {len(merged)}")

    # ------------------------------------------------------
    # Rename Column
    # ------------------------------------------------------
    # merged.rename(
    #     columns={
    #         "cpu_usage": "usage"
    #     },
    #     inplace=True
    # )

    # ------------------------------------------------------
    # Keep only required columns
    # ------------------------------------------------------
    merged = merged[
        [
    "timestamp",
    "node",
    "socket",
    "core",
    "temperature",
    "frequency",
    "cpu_usage",
    "cpu_power",
    "cpu_energy"
]
    ]

    # ------------------------------------------------------
    # Save CSV
    # ------------------------------------------------------
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    merged.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(f"\nCSV Saved : {OUTPUT_FILE}")

    # ------------------------------------------------------
    # Create MySQL Table
    # ------------------------------------------------------
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS merged_dataset")

    cursor.execute("""
CREATE TABLE merged_dataset(
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    node VARCHAR(50) NOT NULL,
    socket INT NOT NULL,
    core INT NOT NULL,
    temperature FLOAT,
    frequency FLOAT,
    cpu_usage FLOAT,
    cpu_power FLOAT,
    cpu_energy DOUBLE
)
""")

    # ------------------------------------------------------
    # Prepare Data
    # ------------------------------------------------------
    records = []

    for row in merged.itertuples(index=False):

        records.append(
            (
                row.timestamp,
                row.node,
                int(row.socket),
                int(row.core),
                float(row.temperature),
                float(row.frequency),
                float(row.cpu_usage),
                float(row.cpu_power)
                if pd.notna(row.cpu_power)
                else None,
                float(row.cpu_energy)
                if pd.notna(row.cpu_energy)
                else None,
            )
        )

    # ------------------------------------------------------
    # Insert
    # ------------------------------------------------------
    insert_query = """
        INSERT INTO merged_dataset(
timestamp,
node,
socket,
core,
temperature,
frequency,
cpu_usage,
cpu_power,
cpu_energy
)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    cursor.executemany(insert_query, records)

    conn.commit()

    print(f"MySQL Rows Inserted : {cursor.rowcount}")

    cursor.close()
    conn.close()

    print("\nFinal Shape :", merged.shape)

    print("=" * 70)
    print("MERGE COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    merge_tables()