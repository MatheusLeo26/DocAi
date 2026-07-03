from flask import Flask
from config import Config
from extensions import db, jwt

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)

    # Register blueprints
    from routes.pages import pages_bp
    from routes.auth import auth_bp
    from routes.documents import docs_bp
    from routes.conversion import conversion_bp
    
    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(docs_bp, url_prefix='/api/docs')
    app.register_blueprint(conversion_bp, url_prefix='/api/convert')

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        import models
        db.create_all()
        try:
            db.session.execute(db.text("ALTER TABLE document ADD COLUMN content_html TEXT;"))
            db.session.commit()
        except Exception:
            db.session.rollback()
    app.run(host='0.0.0.0', port=5000, debug=True)
