import pymysql


def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="#Chaitanya102005#",
        database="hpc_temperature_prediction",
        autocommit=False,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.Cursor
    )