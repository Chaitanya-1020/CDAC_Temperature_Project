import os
import sys
import pandas as pd

# --------------------------------------------------------
# Project Root
# --------------------------------------------------------
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.mysql_connection import get_connection

# --------------------------------------------------------
# Tables
# --------------------------------------------------------
TABLES = [
    "temperature",
    "frequency",
    "cpu_usage",
    "power",
    "energy"
]

# --------------------------------------------------------
# Validate One Table
# --------------------------------------------------------
def validate_table(conn, table):

    print("=" * 70)
    print(f"TABLE : {table}")
    print("=" * 70)

    df = pd.read_sql(f"SELECT * FROM {table}", conn)

    print(f"Rows : {len(df)}")

    print("\nMissing Values")
    print(df.isnull().sum())

    print("\nDuplicate Rows :", df.duplicated().sum())

    if "timestamp" in df.columns:

        print("\nTimestamp Range")

        print(df["timestamp"].min())

        print(df["timestamp"].max())

    if "node" in df.columns:

        print("\nNodes")

        print(df["node"].unique())

    if "socket" in df.columns:

        print("\nSockets")

        print(sorted(df["socket"].unique()))

    if "core" in df.columns:

        print("\nCores")

        print(df["core"].min(), "-", df["core"].max())

    print("\nStatistics")

    print(df.describe(include="all"))

    print()

# --------------------------------------------------------
# Main
# --------------------------------------------------------
def main():

    conn = get_connection()

    for table in TABLES:

        validate_table(conn, table)

    conn.close()

if __name__ == "__main__":
    main()