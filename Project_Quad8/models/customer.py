# models/customer.py
from db_connection import get_cursor

class Customer:
    @staticmethod
    def generate_code(prefix):
        with get_cursor() as cursor:
            if prefix == 'DAY':
                cursor.execute("""
                    SELECT MAX(CAST(SUBSTRING(customer_code, 5) AS UNSIGNED)) as max_num 
                    FROM customers 
                    WHERE customer_code LIKE 'DAY-%'
                """)
            else:
                cursor.execute("""
                    SELECT MAX(CAST(SUBSTRING(customer_code, 6) AS UNSIGNED)) as max_num 
                    FROM customers 
                    WHERE customer_code LIKE 'PLAN-%'
                """)
            result = cursor.fetchone()
            next_num = (result['max_num'] or 0) + 1
            if prefix == 'DAY':
                return f"DAY-{str(next_num).zfill(5)}"
            else:
                return f"PLAN-{str(next_num).zfill(5)}"

    @staticmethod
    def create(code, name, gender, address, contact_info, customer_type):
        with get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO customers 
                (customer_code, full_name, gender, address, contact_info, customer_type)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (code, name, gender, address, contact_info, customer_type))
            return cursor.lastrowid

    @staticmethod
    def get_by_code(code):
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM customers 
                WHERE customer_code = %s AND is_deleted = 0
            """, (code,))
            return cursor.fetchone()

    @staticmethod
    def get_by_id(customer_id):
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM customers 
                WHERE customer_id = %s AND is_deleted = 0
            """, (customer_id,))
            return cursor.fetchone()

    @staticmethod
    def get_all():
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT c.*,
                    CASE WHEN EXISTS (
                        SELECT 1 FROM subscriptions s 
                        WHERE s.customer_id = c.customer_id 
                          AND s.status = 'active' 
                          AND s.end_date >= CURDATE()
                    ) THEN 1 ELSE 0 END as has_active_sub
                FROM customers c
                WHERE c.is_deleted = 0 
                ORDER BY c.customer_id DESC
            """)
            return cursor.fetchall()

    @staticmethod
    def search(keyword, customer_type=None):
        with get_cursor() as cursor:
            q = f"%{keyword}%"
            if customer_type:
                cursor.execute("""
                    SELECT * FROM customers 
                    WHERE is_deleted = 0 
                      AND (full_name LIKE %s OR customer_code LIKE %s)
                      AND customer_type = %s
                    ORDER BY customer_id DESC
                """, (q, q, customer_type))
            else:
                cursor.execute("""
                    SELECT * FROM customers 
                    WHERE is_deleted = 0 
                      AND (full_name LIKE %s OR customer_code LIKE %s)
                    ORDER BY customer_id DESC
                """, (q, q))
            return cursor.fetchall()

    @staticmethod
    def update(customer_id, name, gender, address, contact_info):
        with get_cursor() as cursor:
            cursor.execute("""
                UPDATE customers 
                SET full_name = %s, gender = %s, address = %s, contact_info = %s
                WHERE customer_id = %s
            """, (name, gender, address, contact_info, customer_id))

    @staticmethod
    def soft_delete(customer_id):
        with get_cursor() as cursor:
            cursor.execute("""
                UPDATE customers 
                SET is_deleted = 1, deleted_at = NOW() 
                WHERE customer_id = %s
            """, (customer_id,))

    @staticmethod
    def restore(customer_id):
        with get_cursor() as cursor:
            cursor.execute("""
                UPDATE customers 
                SET is_deleted = 0, deleted_at = NULL 
                WHERE customer_id = %s
            """, (customer_id,))

    @staticmethod
    def get_deleted():
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM customers 
                WHERE is_deleted = 1 
                ORDER BY deleted_at DESC
            """)
            return cursor.fetchall()
