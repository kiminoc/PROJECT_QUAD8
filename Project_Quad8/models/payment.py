# models/payment.py
from db_connection import get_cursor
from datetime import datetime

class Payment:
    @staticmethod
    def create(customer_id, amount, payment_type='cash'):
        """Create a new payment record"""
        with get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO payments (customer_id, amount, payment_type, payment_date)
                VALUES (%s, %s, %s, NOW())
            """, (customer_id, amount, payment_type))
            return cursor.lastrowid

    @staticmethod
    def get_all(limit=9999):
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM payments
                ORDER BY payment_date DESC
                LIMIT %s
            """, (limit,))
            return cursor.fetchall()

    @staticmethod
    def get_today_total():
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0) as total 
                FROM payments 
                WHERE DATE(payment_date) = CURDATE()
            """)
            row = cursor.fetchone()
            return float(row['total']) if row else 0.0
