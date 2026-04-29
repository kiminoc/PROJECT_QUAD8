# controllers/controller.py
"""
Consolidated controller module containing all application controllers.
"""

from models.admin import Admin
from models.audit_log import AuditLog
from models.customer import Customer
from models.subscription import Subscription
from models.checkin import CheckIn
from models.payment import Payment
from models.plan import Plan
from models.setting import Setting
from models.inventory import Inventory
from models.product_sales import ProductSale
from models.restock import Restock
from datetime import datetime, timedelta


class AuthController:
    """Handle authentication and login operations"""

    @staticmethod
    def login(username: str, password: str):
        """Returns (success: bool, data or error_message)"""
        success, result = Admin.login(username, password)
        if success:
            try:
                AuditLog.create(result['admin_id'], 'LOGIN', 'admins', result['admin_id'])
            except:
                pass  # audit log can fail for now
            return True, result
        return False, result


class CheckInController:
    """Handle customer check-in operations"""

    @staticmethod
    def validate(code):
        """Validate customer code and return status"""
        customer = Customer.get_by_code(code)
        if not customer:
            return False, "not_found", "Customer not found"

        active_sub = Subscription.get_active_by_customer(customer['customer_id'])

        if active_sub:
            CheckIn.create(customer['customer_id'], 'plan')
            return True, "active", {
                'customer_id': customer['customer_id'],
                'name': customer['full_name'],
                'code': customer['customer_code'],
                'plan': active_sub['plan_name'],
                'end_date': str(active_sub['end_date']),
                'checkin_time': datetime.now().strftime('%H:%M')
            }

        expired_sub = Subscription.get_expired_by_customer(customer['customer_id'])
        if expired_sub:
            return True, "expired", {
                'customer_id': customer['customer_id'],
                'name': customer['full_name'],
                'code': customer['customer_code'],
                'expired_date': str(expired_sub['end_date'])
            }

        return True, "no_plan", {
            'customer_id': customer['customer_id'],
                'name': customer['full_name'],
                'code': customer['customer_code']
            }

    @staticmethod
    def renew_plan(customer_id, plan_id, payment_type='cash', admin_id=None):
        """Renew subscription for a customer"""
        try:
            Subscription.expire_old(customer_id)

            plan = Plan.get_by_id(plan_id)
            if not plan:
                return False, "Invalid plan"

            settings = Setting.get_gym_settings()
            if plan['plan_name'].lower() == 'weekly':
                price = settings.get('weekly_plan_price', 110)
            else:
                price = settings.get('monthly_plan_price', 375)

            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=plan['duration_days'])

            Subscription.create(customer_id, plan_id, start_date, end_date)
            Payment.create(customer_id, float(price), payment_type)
            CheckIn.create(customer_id, 'plan')

            if admin_id:
                AuditLog.create(admin_id, 'PLAN_RENEWAL', 'subscriptions', customer_id)

            return True, {
                'end_date': end_date.strftime('%Y-%m-%d'),
                'checkin_time': datetime.now().strftime('%H:%M')
            }
        except Exception as e:
            return False, str(e)


class CustomerController:
    """Handle customer-related operations"""

    @staticmethod
    def get_all():
        return Customer.get_all()

    @staticmethod
    def search(keyword, customer_type=None):
        return Customer.search(keyword, customer_type)

    @staticmethod
    def get_by_id(customer_id):
        return Customer.get_by_id(customer_id)

    @staticmethod
    def update(customer_id, name, gender, address, contact_info):
        return Customer.update(customer_id, name, gender, address, contact_info)

    @staticmethod
    def soft_delete(customer_id):
        return Customer.soft_delete(customer_id)

    @staticmethod
    def restore(customer_id):
        return Customer.restore(customer_id)


class DashboardController:
    """Handle dashboard and analytics operations"""

    @staticmethod
    def get_dashboard_data():
        settings = Setting.get_gym_settings()

        today_checkins_count = CheckIn.get_today_count()
        active_plans = Subscription.get_active_count()

        # Revenue = all payments today (memberships + product sales)
        today_revenue = Payment.get_today_total()

        low_stock_count = len(Inventory.get_low_stock(
            int(settings.get('low_stock_threshold', 5))
        ))
        expiring_count = len(Subscription.get_expiring_soon(
            int(settings.get('expiring_plan_days', 3))
        ))
        recent_checkins = CheckIn.get_recent(limit=10)

        return {
            'today_checkins_count': today_checkins_count,
            'active_plans_count': active_plans,
            'today_revenue': today_revenue,
            'low_stock_count': low_stock_count,
            'expiring_count': expiring_count,
            'recent_checkins': recent_checkins
        }


class DayPassController:
    """Handle day pass operations"""

    @staticmethod
    def create_daypass(name: str, gender: str, address: str, payment_type: str = 'cash', admin_id=None):
        try:
            settings = Setting.get_gym_settings()
            fee = float(settings.get('day_pass_fee', 25))

            code = Customer.generate_code('DAY')

            customer_id = Customer.create(
                code=code,
                name=name,
                gender=gender,
                address=address,
                contact_info=None,
                customer_type='day-pass'
            )

            CheckIn.create(customer_id, 'day-pass')
            Payment.create(customer_id, fee, payment_type)

            if admin_id:
                AuditLog.create(admin_id, 'DAY_PASS_ENTRY', 'customers', customer_id)

            return True, {
                'customer': {
                    'name': name,
                    'code': code,
                    'fee': fee,
                    'time': datetime.now().strftime('%H:%M')
                }
            }
        except Exception as e:
            return False, str(e)


class InventoryController:
    """Handle inventory and product management"""

    @staticmethod
    def get_all():
        return Inventory.get_all()

    @staticmethod
    def get_low_stock():
        settings = Setting.get_gym_settings()
        threshold = int(settings.get('low_stock_threshold', 5))
        return Inventory.get_low_stock(threshold)

    @staticmethod
    def create(sku, product_name, category, price, stock=0):
        try:
            if not sku or not product_name:
                return False, "SKU and product name are required"
            product_id = Inventory.create(sku, product_name, category, price, stock)
            return True, {'product_id': product_id, 'product_name': product_name}
        except Exception as e:
            err = str(e)
            if 'Duplicate entry' in err and 'sku' in err:
                return False, f"SKU '{sku}' already exists. Please use a unique SKU."
            return False, err

    @staticmethod
    def update(product_id, product_name, category, price):
        return Inventory.update(product_id, product_name, category, price)

    @staticmethod
    def update_stock(product_id, new_stock):
        return Inventory.update_stock(product_id, new_stock)

    @staticmethod
    def soft_delete(product_id):
        return Inventory.soft_delete(product_id)

    @staticmethod
    def restore(product_id):
        return Inventory.restore(product_id)


class PlanRegController:
    """Handle plan registration operations"""

    @staticmethod
    def get_plans():
        return Plan.get_weekly_monthly()

    @staticmethod
    def register_plan(name, gender, address, contact_info, plan_id, payment_type='cash', admin_id=None):
        try:
            plan = Plan.get_by_id(plan_id)
            if not plan:
                return False, "Invalid plan selected"

            settings = Setting.get_gym_settings()
            if plan['plan_name'].lower() == 'weekly':
                price = settings.get('weekly_plan_price', 110)
            else:
                price = settings.get('monthly_plan_price', 375)

            code = Customer.generate_code('PLAN')

            customer_id = Customer.create(
                code=code,
                name=name,
                gender=gender,
                address=address,
                contact_info=contact_info,
                customer_type='plan'
            )

            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=plan['duration_days'])

            Subscription.create(customer_id, plan_id, start_date, end_date)
            Payment.create(customer_id, float(price), payment_type)

            if admin_id:
                AuditLog.create(admin_id, 'PLAN_REGISTRATION', 'subscriptions', customer_id)

            return True, {
                'customer_name': name,
                'customer_code': code,
                'plan_name': plan['plan_name'],
                'end_date': end_date.strftime('%Y-%m-%d'),
                'price': price
            }
        except Exception as e:
            return False, str(e)


class ProductSalesController:
    """Handle product sales operations"""

    @staticmethod
    def sell_product(product_id, quantity, customer_id=None, payment_type='cash'):
        """Sell a product and update stock"""
        product = Inventory.get_by_id(product_id)
        if not product:
            return False, "Product not found"

        if product['stock'] < quantity:
            return False, f"Insufficient stock. Only {product['stock']} available."

        total_amount = product['price'] * quantity

        # Record the sale
        sale_id = ProductSale.create(
            product_id=product_id,
            customer_id=customer_id,
            quantity=quantity,
            total_amount=total_amount,
            payment_type=payment_type
        )

        # Deduct from stock
        new_stock = product['stock'] - quantity
        Inventory.update_stock(product_id, new_stock)

        return True, {
            'sale_id': sale_id,
            'total_amount': total_amount,
            'product_name': product['product_name'],
            'quantity': quantity
        }

    @staticmethod
    def get_recent(limit=20):
        return ProductSale.get_recent(limit)


class RestockController:
    """Handle product restocking operations"""

    @staticmethod
    def restock(product_id, quantity_added):
        """Add stock to a product (alias for restock_product)"""
        return RestockController.restock_product(product_id, quantity_added)

    @staticmethod
    def restock_product(product_id, quantity_added):
        if quantity_added <= 0:
            return False, "Quantity must be greater than zero"
        product = Inventory.get_by_id(product_id)
        if not product:
            return False, "Product not found"
        Restock.create(product_id, quantity_added)
        return True, f"Successfully added {quantity_added} units to {product['product_name']}"


class SettingController:
    """Handle application settings"""

    @staticmethod
    def get_gym_settings():
        """Return all gym settings as dict"""
        return Setting.get_gym_settings()

    @staticmethod
    def update_settings(data):
        """data is a dict of setting_key -> value"""
        for key, value in data.items():
            Setting.set(key, value)
        return True, "Settings updated successfully"


class AuditLogController:
    """Handle audit logging operations"""

    @staticmethod
    def log_action(admin_id, action, table_name, record_id=None):
        return AuditLog.create(admin_id, action, table_name, record_id)

    @staticmethod
    def get_recent(limit=100):
        return AuditLog.get_all(limit)

    # Legacy alias
    @staticmethod
    def get_recent_logs(limit=100):
        return AuditLog.get_all(limit)
