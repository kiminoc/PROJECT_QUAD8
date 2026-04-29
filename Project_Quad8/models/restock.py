# models/restock.py
from db_connection import get_cursor

class Restock:
    @staticmethod
    def create(product_id, quantity_added):
        with get_cursor() as cursor:
            # Update stock in inventory
            cursor.execute("""
                UPDATE inventory 
                SET stock = stock + %s 
                WHERE product_id = %s
            """, (quantity_added, product_id))

            # Record the restock
            cursor.execute("""
                INSERT INTO restocks (product_id, quantity_added)
                VALUES (%s, %s)
            """, (product_id, quantity_added))
            return True

    @staticmethod
    def get_history(limit=50):
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT r.*, i.product_name, i.sku 
                FROM restocks r
                JOIN inventory i ON r.product_id = i.product_id
                ORDER BY r.restocked_at DESC 
                LIMIT %s
            """, (limit,))
            return cursor.fetchall()
