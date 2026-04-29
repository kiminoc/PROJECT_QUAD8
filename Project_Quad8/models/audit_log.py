# models/audit_log.py
from db_connection import get_cursor
from datetime import datetime

class AuditLog:
    @staticmethod
    def create(admin_id, action, table_name, record_id=None):
        with get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO audit_logs (admin_id, action, table_name, record_id, created_at)
                VALUES (%s, %s, %s, %s, NOW())
            """, (admin_id, action, table_name, record_id))

    @staticmethod
    def get_all(limit=100):
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT a.*, adm.full_name as admin_name
                FROM audit_logs a
                LEFT JOIN admins adm ON a.admin_id = adm.admin_id
                ORDER BY a.created_at DESC 
                LIMIT %s
            """, (limit,))
            return cursor.fetchall()

    # Alias so both get_recent(100) and get_all(100) work
    @staticmethod
    def get_recent(limit=100):
        return AuditLog.get_all(limit)
