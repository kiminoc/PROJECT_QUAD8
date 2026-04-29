# models/product_sales.py
from db_connection import get_cursor

class ProductSale:
    @staticmethod
    def create(product_id, customer_id, quantity, total_amount, payment_type='cash'):
        with get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO product_sales 
                (product_id, customer_id, quantity, total_amount, payment_type)
                VALUES (%s, %s, %s, %s, %s)
            """, (product_id, customer_id, quantity, total_amount, payment_type))
            return cursor.lastrowid

    @staticmethod
    def get_recent(limit=20):
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT ps.sale_id, ps.product_id, ps.customer_id, ps.quantity,
                       ps.total_amount, ps.payment_type,
                       ps.sold_at as sale_date,
                       i.product_name, i.sku 
                FROM product_sales ps
                JOIN inventory i ON ps.product_id = i.product_id
                ORDER BY ps.sold_at DESC 
                LIMIT %s
            """, (limit,))
            return cursor.fetchall()

    @staticmethod
    def get_by_product(product_id):
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM product_sales 
                WHERE product_id = %s 
                ORDER BY sold_at DESC
            """, (product_id,))
            return cursor.fetchall()

    @staticmethod
    def get_today_total():
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT COALESCE(SUM(total_amount), 0) as total 
                FROM product_sales 
                WHERE DATE(sold_at) = CURDATE()
            """)
            row = cursor.fetchone()
            return float(row['total']) if row else 0.0
