# models/plan.py
from db_connection import get_cursor
from models.setting import Setting

class Plan:
    @staticmethod
    def get_all():
        with get_cursor() as cursor:
            cursor.execute("SELECT * FROM plans ORDER BY plan_id")
            return cursor.fetchall()

    @staticmethod
    def get_by_id(plan_id):
        with get_cursor() as cursor:
            cursor.execute("SELECT * FROM plans WHERE plan_id = %s", (plan_id,))
            return cursor.fetchone()

    @staticmethod
    def get_weekly_monthly():
        """Return one Weekly and one Monthly plan with prices from settings"""
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT MIN(plan_id) as plan_id, plan_name, duration_days 
                FROM plans 
                WHERE plan_name IN ('Weekly', 'Monthly')
                GROUP BY plan_name, duration_days
                ORDER BY duration_days ASC
            """)
            plans = cursor.fetchall()

        # Attach prices from settings
        settings = Setting.get_all()
        result = []
        for p in plans:
            p = dict(p)
            if p['plan_name'].lower() == 'weekly':
                p['price'] = float(settings.get('weekly_plan_price', 110))
            else:
                p['price'] = float(settings.get('monthly_plan_price', 375))
            result.append(p)
        return result
