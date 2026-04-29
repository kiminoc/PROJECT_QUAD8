# db_connection.py
import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'gym_management',
    'port': 3306,
    'charset': 'utf8mb4',
    'autocommit': True,
    'buffered': True,
}

@contextmanager
def get_connection():
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        yield conn
    except Error as e:
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()

@contextmanager
def get_cursor():
    """Returns a dictionary cursor. autocommit=True so writes commit instantly."""
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        yield cursor
    except Error as e:
        raise
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn and conn.is_connected():
            conn.close()

def test_connection():
    try:
        with get_cursor() as cursor:
            cursor.execute("SELECT VERSION() as version")
            print(f"✅ MySQL Connected! Version: {cursor.fetchone()['version']}")
            cursor.execute("SHOW TABLES")
            tables = [list(row.values())[0] for row in cursor.fetchall()]
            print(f"Tables found: {len(tables)} → {tables}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_connection()
