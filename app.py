from flask import Flask, render_template
from config import Config
from extensions import db, jwt
from models import User, Document

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.documents import docs_bp
    from routes.conversion import conversion_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(docs_bp, url_prefix='/api/docs')
    app.register_blueprint(conversion_bp, url_prefix='/api/convert')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login')
    def login():
        return render_template('login.html')

    @app.route('/register')
    def register():
        return render_template('register.html')

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/create/<doc_type>')
    def create_document(doc_type):
        return render_template('create_document.html', doc_type=doc_type)

    @app.route('/converter')
    def converter():
        return render_template('converter.html')

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        pass
    app.run(debug=True)
