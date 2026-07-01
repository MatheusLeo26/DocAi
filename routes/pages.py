from flask import Blueprint, render_template

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/')
def index():
    return render_template('index.html')

@pages_bp.route('/login')
def login():
    return render_template('login.html')

@pages_bp.route('/register')
def register():
    return render_template('register.html')

@pages_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@pages_bp.route('/create/<doc_type>')
def create_document(doc_type):
    return render_template('create_document.html', doc_type=doc_type)

@pages_bp.route('/converter')
def converter():
    return render_template('converter.html')
