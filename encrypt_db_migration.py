import os
import sys
from cryptography.fernet import Fernet
from app import create_app
from extensions import db
from models import Document, Draft

# Chave gerada para esta migração e que ficará no env
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or b'0I6iUvDq9hVf0T3M9h7bL_wzR-H92bN7h1iH_jG4b3A='
fernet = Fernet(ENCRYPTION_KEY)

app = create_app()
with app.app_context():
    docs = Document.query.all()
    for doc in docs:
        if doc.content_html and not doc.content_html.startswith('gAAAAAB'): # Fernet tokens always start with gAAAAAB
            try:
                encrypted = fernet.encrypt(doc.content_html.encode('utf-8')).decode('utf-8')
                # we update using raw sql to bypass any potential getters/setters we might add
                db.session.execute(db.text("UPDATE document SET content_html = :enc WHERE id = :id"), {"enc": encrypted, "id": doc.id})
            except Exception as e:
                print(f"Erro doc {doc.id}: {e}")
                
    drafts = Draft.query.all()
    for draft in drafts:
        if draft.content_json and not draft.content_json.startswith('gAAAAAB'):
            try:
                encrypted = fernet.encrypt(draft.content_json.encode('utf-8')).decode('utf-8')
                db.session.execute(db.text("UPDATE draft SET content_json = :enc WHERE id = :id"), {"enc": encrypted, "id": draft.id})
            except Exception as e:
                print(f"Erro draft {draft.id}: {e}")

    db.session.commit()
    print("Migration (Encryption) successful")
