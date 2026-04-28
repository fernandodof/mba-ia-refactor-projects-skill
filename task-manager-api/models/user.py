from database import db
from datetime import datetime
import hashlib
import os


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at)
        }

    def set_password(self, pwd):
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', pwd.encode(), salt, 100_000)
        self.password = salt.hex() + ':' + key.hex()

    def check_password(self, pwd):
        try:
            salt_hex, key_hex = self.password.split(':')
            salt = bytes.fromhex(salt_hex)
            key = hashlib.pbkdf2_hmac('sha256', pwd.encode(), salt, 100_000)
            return key.hex() == key_hex
        except Exception:
            return False

    def is_admin(self):
        return self.role == 'admin'
