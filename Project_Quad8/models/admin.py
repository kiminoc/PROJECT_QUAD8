# models/admin.py
from db_connection import get_cursor
import bcrypt

class Admin:
    @staticmethod
    def get_by_username(username):
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT admin_id, username, full_name, password 
                FROM admins 
                WHERE username = %s
            """, (username,))
            return cursor.fetchone()

    @staticmethod
    def login(username, password):
        admin = Admin.get_by_username(username)
        if not admin:
            return False, "Invalid username or password"

        try:
            # admin['password'] is stored as a string in the database,
            # need to encode both to bytes for bcrypt verification
            hashed = admin['password']
            if isinstance(hashed, bytes):
                hashed_bytes = hashed
            else:
                hashed_bytes = hashed.encode('latin1') if isinstance(hashed, str) else hashed
            
            if not hashed_bytes:
                return False, "Invalid username or password"
            
            if bcrypt.checkpw(password.encode('utf-8'), hashed_bytes):
                admin_data = {
                    'admin_id': admin['admin_id'],
                    'username': admin['username'],
                    'full_name': admin.get('full_name', username)
                }
                return True, admin_data
        except Exception as e:
            return False, f"Authentication error: {str(e)}"

        return False, "Invalid username or password"

    @staticmethod
    def change_password(admin_id, current_password, new_password):
        """Change admin password after verifying current password"""
        with get_cursor() as cursor:
            cursor.execute("SELECT password FROM admins WHERE admin_id = %s", (admin_id,))
            row = cursor.fetchone()
            if not row:
                return False
            if not bcrypt.checkpw(current_password.encode('utf-8'), row['password']):
                return False
            hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute(
                "UPDATE admins SET password = %s WHERE admin_id = %s",
                (hashed, admin_id)
            )
            return True

    @staticmethod
    def update_full_name(admin_id, full_name):
        with get_cursor() as cursor:
            cursor.execute(
                "UPDATE admins SET full_name = %s WHERE admin_id = %s",
                (full_name, admin_id)
            )
            return True
