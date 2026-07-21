import os
import sys

# ------------------------------------------------------------------
# Add project root to Python path
# ------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.mysql_connection import get_connection


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    # ==============================================================
    # Temperature Table
    # ==============================================================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS temperature (
        id INT AUTO_INCREMENT PRIMARY KEY,
        timestamp BIGINT NOT NULL,
        node VARCHAR(50) NOT NULL,
        socket INT NOT NULL,
        core INT NOT NULL,
        temperature FLOAT NOT NULL,
        UNIQUE(timestamp, node, socket, core)
    );
    """)

    # ==============================================================
    # Frequency Table
    # ==============================================================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS frequency (
        id INT AUTO_INCREMENT PRIMARY KEY,
        timestamp BIGINT NOT NULL,
        node VARCHAR(50) NOT NULL,
        socket INT NOT NULL,
        core INT NOT NULL,
        frequency FLOAT NOT NULL,
        UNIQUE(timestamp, node, socket, core)
    );
    """)

    # ==============================================================
    # CPU Usage Table
    # ==============================================================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cpu_usage (
        id INT AUTO_INCREMENT PRIMARY KEY,
        timestamp BIGINT NOT NULL,
        node VARCHAR(50) NOT NULL,
        socket INT NOT NULL,
        core INT NOT NULL,
        cpu_usage FLOAT NOT NULL,
        UNIQUE(timestamp, node, socket, core)
    );
    """)

    # ==============================================================
    # Power Table
    # ==============================================================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS power (
        id INT AUTO_INCREMENT PRIMARY KEY,
        timestamp BIGINT NOT NULL,
        node VARCHAR(50) NOT NULL,
        socket INT NOT NULL,
        power FLOAT NOT NULL,
        UNIQUE(timestamp, node, socket)
    );
    """)

    # ==============================================================
    # Energy Table
    # ==============================================================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS energy (
        id INT AUTO_INCREMENT PRIMARY KEY,
        timestamp BIGINT NOT NULL,
        node VARCHAR(50) NOT NULL,
        socket INT NOT NULL,
        energy FLOAT NOT NULL,
        UNIQUE(timestamp, node, socket)
    );
    """)

    # ==============================================================
    # Prediction Table
    # ==============================================================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS temperature_predictions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        timestamp BIGINT NOT NULL,
        node VARCHAR(50) NOT NULL,
        socket INT NOT NULL,
        core INT NOT NULL,
        actual_temperature FLOAT,
        predicted_temperature FLOAT NOT NULL,
        model_name VARCHAR(100),
        prediction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()

    print("======================================")
    print("All tables created successfully.")
    print("======================================")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    create_tables()