# models/setting.py
from db_connection import get_cursor

class Setting:
    @staticmethod
    def get(key, default=None):
        with get_cursor() as cursor:
            cursor.execute("SELECT setting_value FROM settings WHERE setting_key = %s", (key,))
            row = cursor.fetchone()
            return row['setting_value'] if row else default

    @staticmethod
    def set(key, value):
        with get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO settings (setting_key, setting_value)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE setting_value = %s
            """, (key, str(value), str(value)))

    @staticmethod
    def get_all():
        with get_cursor() as cursor:
            cursor.execute("SELECT setting_key, setting_value FROM settings")
            rows = cursor.fetchall()
            return {row['setting_key']: row['setting_value'] for row in rows} if rows else {}

    @staticmethod
    def get_gym_settings():
        settings = Setting.get_all()
        return {
            'gym_name':            settings.get('gym_name', 'Quad8 Gym'),
            'gym_address':         settings.get('gym_address', ''),
            'gym_contact':         settings.get('gym_contact', ''),
            'gym_email':           settings.get('gym_email', ''),
            'day_pass_fee':        float(settings.get('day_pass_fee', 25)),
            'low_stock_threshold': int(settings.get('low_stock_threshold', 5)),
            'expiring_plan_days':  int(settings.get('expiring_plan_days', 3)),
            'weekly_plan_price':   float(settings.get('weekly_plan_price', 110)),
            'monthly_plan_price':  float(settings.get('monthly_plan_price', 375)),
        }
