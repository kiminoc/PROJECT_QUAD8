# models/subscription.py
from db_connection import get_cursor
from datetime import datetime, timedelta

class Subscription:
    @staticmethod
    def create(customer_id, plan_id, start_date, end_date):
        with get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO subscriptions 
                (customer_id, plan_id, start_date, end_date, status)
                VALUES (%s, %s, %s, %s, 'active')
            """, (customer_id, plan_id, start_date, end_date))
            return cursor.lastrowid

    @staticmethod
    def get_active_by_customer(customer_id):
        today = datetime.now().strftime('%Y-%m-%d')
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT s.*, p.plan_name 
                FROM subscriptions s
                JOIN plans p ON s.plan_id = p.plan_id
                WHERE s.customer_id = %s 
                  AND s.status = 'active' 
                  AND s.end_date >= %s
                ORDER BY s.end_date DESC
                LIMIT 1
            """, (customer_id, today))
            return cursor.fetchone()

    @staticmethod
    def get_expired_by_customer(customer_id):
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT s.*, p.plan_name 
                FROM subscriptions s
                JOIN plans p ON s.plan_id = p.plan_id
                WHERE s.customer_id = %s AND s.status = 'expired'
                ORDER BY s.end_date DESC
                LIMIT 1
            """, (customer_id,))
            return cursor.fetchone()

    @staticmethod
    def expire_old(customer_id):
        with get_cursor() as cursor:
            cursor.execute("""
                UPDATE subscriptions 
                SET status = 'expired' 
                WHERE customer_id = %s AND status = 'active'
            """, (customer_id,))

    @staticmethod
    def get_active_count():
        today = datetime.now().strftime('%Y-%m-%d')
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) as count FROM subscriptions
                WHERE status = 'active' AND end_date >= %s
            """, (today,))
            row = cursor.fetchone()
            return row['count'] if row else 0

    @staticmethod
    def get_all():
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT s.*, c.full_name, c.customer_code, p.plan_name
                FROM subscriptions s
                JOIN customers c ON s.customer_id = c.customer_id
                JOIN plans p ON s.plan_id = p.plan_id
                WHERE c.is_deleted = 0
                ORDER BY s.start_date DESC
            """)
            return cursor.fetchall()

    @staticmethod
    def get_expiring_soon(days=3):
        today = datetime.now().strftime('%Y-%m-%d')
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT s.*, c.full_name, c.customer_code, p.plan_name
                FROM subscriptions s
                JOIN customers c ON s.customer_id = c.customer_id
                JOIN plans p ON s.plan_id = p.plan_id
                WHERE s.status = 'active' 
                  AND s.end_date BETWEEN %s AND DATE_ADD(%s, INTERVAL %s DAY)
                  AND c.is_deleted = 0
            """, (today, today, days))
            return cursor.fetchall()
