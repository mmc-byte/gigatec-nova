import os
from dotenv import load_dotenv

import mysql.connector
from mysql.connector import Error

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3308")),
        database=os.getenv("MYSQL_DATABASE"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
    )


def test_connection():
    connection = None

    try:
        connection = get_connection()

        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()

        return result[0] == 1

    except Error as error:
        print(f"Database connection error: {error}")
        return False

    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()