# models/checkin.py
from db_connection import get_cursor
from datetime import datetime

class CheckIn:
    @staticmethod
    def create(customer_id, check_type):
        with get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO check_ins (customer_id, type, check_in_time)
                VALUES (%s, %s, NOW())
            """, (customer_id, check_type))
            return cursor.lastrowid

    @staticmethod
    def get_today_count():
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM check_ins 
                WHERE DATE(check_in_time) = CURDATE()
            """)
            row = cursor.fetchone()
            return row['count'] if row else 0

    @staticmethod
    def get_recent(limit=10):
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT c.check_in_id, c.customer_id, c.type as checkin_type,
                       c.check_in_time, cust.full_name, cust.customer_code 
                FROM check_ins c
                JOIN customers cust ON c.customer_id = cust.customer_id
                WHERE cust.is_deleted = 0
                ORDER BY c.check_in_time DESC 
                LIMIT %s
            """, (limit,))
            return cursor.fetchall()
