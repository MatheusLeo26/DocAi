from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models import Document, db
from services.ai_service import generate_content
from services.pdf_service import create_document_pdf
import os
import uuid
from datetime import datetime

docs_bp = Blueprint('docs', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')


@docs_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_document():
    """Receive user data, generate content with AI, create PDF, save to DB."""
    user_id = get_jwt_identity()
    
    # Handle both JSON and multipart form data
    if request.is_json:
        data = request.get_json()
        doc_type = data.get('type')
        user_data = data.get('data')
        title = data.get('title')
        files = []
    else:
        doc_type = request.form.get('type')
        user_data = request.form.get('data')
        title = request.form.get('title')
        files = request.files.getlist('images')

    title = title or f'Documento {datetime.now().strftime("%d/%m/%Y %H:%M")}'

    if not doc_type or not user_data:
        return jsonify({'message': 'Tipo de documento e dados são obrigatórios'}), 400

    if doc_type not in ['resume', 'contract', 'report']:
        return jsonify({'message': 'Tipo inválido. Use: resume, contract ou report'}), 400

    temp_image_paths = []
    try:
        # Save uploaded images temporarily
        if files:
            temp_dir = os.path.join(UPLOAD_FOLDER, str(user_id), 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            for f in files:
                if f and f.filename:
                    filename = secure_filename(f.filename)
                    unique_name = f"{uuid.uuid4().hex[:8]}_{filename}"
                    path = os.path.join(temp_dir, unique_name)
                    f.save(path)
                    temp_image_paths.append(path)

        # Step 1: Generate professional content with AI
        ai_content = generate_content(doc_type, user_data, temp_image_paths)

        # Step 2: Generate PDF with Playwright
        filename = f"{doc_type}_{uuid.uuid4().hex[:8]}.pdf"
        user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))
        os.makedirs(user_folder, exist_ok=True)
        output_path = os.path.join(user_folder, filename)

        create_document_pdf(doc_type, ai_content, output_path)

        # Step 3: Save document metadata to database
        doc = Document(
            user_id=int(user_id),
            type=doc_type,
            title=title,
            file_path=output_path
        )
        db.session.add(doc)
        db.session.commit()

        # Clean up temporary images
        for path in temp_image_paths:
            if os.path.exists(path):
                os.remove(path)

        return jsonify({
            'message': 'Documento gerado com sucesso!',
            'document': {
                'id': doc.id,
                'type': doc.type,
                'title': doc.title,
                'created_at': doc.created_at.isoformat()
            }
        }), 201

    except Exception as e:
        for path in temp_image_paths:
            if os.path.exists(path):
                os.remove(path)
        return jsonify({'message': f'Erro ao gerar documento: {str(e)}'}), 500


@docs_bp.route('/list', methods=['GET'])
@jwt_required()
def list_documents():
    """List all documents for the logged-in user."""
    user_id = get_jwt_identity()
    doc_type = request.args.get('type')

    query = Document.query.filter_by(user_id=int(user_id))
    if doc_type:
        query = query.filter_by(type=doc_type)

    docs = query.order_by(Document.created_at.desc()).all()

    return jsonify({
        'documents': [{
            'id': d.id,
            'type': d.type,
            'title': d.title,
            'created_at': d.created_at.isoformat()
        } for d in docs]
    }), 200


@docs_bp.route('/download/<int:doc_id>', methods=['GET'])
@jwt_required()
def download_document(doc_id):
    """Download a generated PDF document."""
    user_id = get_jwt_identity()
    doc = Document.query.filter_by(id=doc_id, user_id=int(user_id)).first()

    if not doc:
        return jsonify({'message': 'Documento não encontrado'}), 404

    if not os.path.exists(doc.file_path):
        return jsonify({'message': 'Arquivo não encontrado no servidor'}), 404

    return send_file(doc.file_path, as_attachment=True, download_name=f"{doc.title}.pdf")


@docs_bp.route('/delete/<int:doc_id>', methods=['DELETE'])
@jwt_required()
def delete_document(doc_id):
    """Delete a document."""
    user_id = get_jwt_identity()
    doc = Document.query.filter_by(id=doc_id, user_id=int(user_id)).first()

    if not doc:
        return jsonify({'message': 'Documento não encontrado'}), 404

    # Delete file from disk
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    db.session.delete(doc)
    db.session.commit()

    return jsonify({'message': 'Documento excluído com sucesso'}), 200
