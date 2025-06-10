import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="pencarikerja",
        charset='utf8mb4',
        autocommit=True
    )
