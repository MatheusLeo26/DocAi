from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import FernetEngine
import os

ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or '0I6iUvDq9hVf0T3M9h7bL_wzR-H92bN7h1iH_jG4b3A='

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    documents = db.relationship('Document', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False) # e.g. 'resume', 'contract', 'report'
    title = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    content_html = db.Column(StringEncryptedType(db.Text, ENCRYPTION_KEY, FernetEngine), nullable=True) # Stores the raw generated AI content (HTML)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_id: int, type: str, title: str, file_path: str, content_html: str = None, **kwargs):
        self.user_id = user_id
        self.type = type
        self.title = title
        self.file_path = file_path
        self.content_html = content_html
        super().__init__(**kwargs)

class Draft(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False) # e.g. 'resume', 'contract', 'report'
    title = db.Column(db.String(255), nullable=False)
    content_json = db.Column(StringEncryptedType(db.Text, ENCRYPTION_KEY, FernetEngine), nullable=False) # Stores stringified form fields JSON
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, user_id: int, type: str, title: str, content_json: str, **kwargs):
        self.user_id = user_id
        self.type = type
        self.title = title
        self.content_json = content_json
        super().__init__(**kwargs)

