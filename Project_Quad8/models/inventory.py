# models/inventory.py
from db_connection import get_cursor

class Inventory:
    @staticmethod
    def get_all():
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM inventory 
                WHERE is_deleted = 0 
                ORDER BY product_id DESC
            """)
            return cursor.fetchall()

    @staticmethod
    def get_by_id(product_id):
        with get_cursor() as cursor:
            cursor.execute("SELECT * FROM inventory WHERE product_id = %s", (product_id,))
            return cursor.fetchone()

    @staticmethod
    def create(sku, product_name, category, price, stock=0):
        with get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO inventory (sku, product_name, category, price, stock)
                VALUES (%s, %s, %s, %s, %s)
            """, (sku, product_name, category, price, stock))
            return cursor.lastrowid

    @staticmethod
    def update(product_id, product_name, category, price):
        with get_cursor() as cursor:
            cursor.execute("""
                UPDATE inventory 
                SET product_name = %s, category = %s, price = %s 
                WHERE product_id = %s
            """, (product_name, category, price, product_id))

    @staticmethod
    def update_stock(product_id, new_stock):
        with get_cursor() as cursor:
            cursor.execute(
                "UPDATE inventory SET stock = %s WHERE product_id = %s",
                (new_stock, product_id)
            )

    @staticmethod
    def soft_delete(product_id):
        with get_cursor() as cursor:
            cursor.execute("""
                UPDATE inventory 
                SET is_deleted = 1, deleted_at = NOW() 
                WHERE product_id = %s
            """, (product_id,))

    @staticmethod
    def restore(product_id):
        with get_cursor() as cursor:
            cursor.execute("""
                UPDATE inventory 
                SET is_deleted = 0, deleted_at = NULL 
                WHERE product_id = %s
            """, (product_id,))

    @staticmethod
    def get_low_stock(threshold=5):
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM inventory 
                WHERE is_deleted = 0 AND stock <= %s
                ORDER BY stock ASC
            """, (threshold,))
            return cursor.fetchall()
