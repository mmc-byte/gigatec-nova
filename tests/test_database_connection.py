from app.db.connection import test_connection as check_database_connection


def test_database_connection():
    assert check_database_connection()