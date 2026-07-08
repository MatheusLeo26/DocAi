from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models import Document, Draft, db
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

    if doc_type not in ['resume', 'resume_en', 'resume_es', 'resume_modern', 'resume_modern_en', 'resume_modern_es', 'resume_minimalist', 'resume_minimalist_en', 'resume_minimalist_es', 'contract', 'report']:
        return jsonify({'message': 'Tipo inválido. Use: resume, resume_en, resume_es, resume_modern, resume_modern_en, resume_modern_es, resume_minimalist, resume_minimalist_en, resume_minimalist_es, contract ou report'}), 400

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

        # Step 1: Generate professional content with AI or use edited_content
        edited_content = request.form.get('edited_content') if not request.is_json else data.get('edited_content')
        if edited_content:
            ai_content = edited_content
        else:
            ai_content = generate_content(doc_type, user_data, temp_image_paths)

        doc_id = request.form.get('doc_id') if not request.is_json else data.get('doc_id')
        doc = None
        if doc_id:
            doc = Document.query.filter_by(id=int(doc_id), user_id=int(user_id)).first()

        # Step 2: Generate PDF with Playwright
        if doc:
            output_path = doc.file_path
        else:
            filename = f"{doc_type}_{uuid.uuid4().hex[:8]}.pdf"
            user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))
            os.makedirs(user_folder, exist_ok=True)
            output_path = os.path.join(user_folder, filename)

        create_document_pdf(doc_type, ai_content, output_path)

        # Step 3: Save or update document metadata in database
        if doc:
            doc.title = title
            doc.content_html = ai_content
        else:
            doc = Document(
                user_id=int(user_id),
                type=doc_type,
                title=title,
                file_path=output_path,
                content_html=ai_content
            )
            db.session.add(doc)
        
        # If a draft ID was provided, delete the draft upon successful PDF generation
        draft_id = request.form.get('draft_id') if not request.is_json else data.get('draft_id')
        if draft_id:
            draft = Draft.query.filter_by(id=int(draft_id), user_id=int(user_id)).first()
            if draft:
                db.session.delete(draft)

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
                'created_at': doc.created_at.isoformat() + 'Z'
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
            'created_at': d.created_at.isoformat() + 'Z'
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


@docs_bp.route('/view/<int:doc_id>', methods=['GET'])
@jwt_required()
def view_document(doc_id):
    """View a generated PDF document without forcing download."""
    user_id = get_jwt_identity()
    doc = Document.query.filter_by(id=doc_id, user_id=int(user_id)).first()

    if not doc:
        return jsonify({'message': 'Documento não encontrado'}), 404

    if not os.path.exists(doc.file_path):
        return jsonify({'message': 'Arquivo não encontrado no servidor'}), 404

    return send_file(doc.file_path, mimetype='application/pdf')


@docs_bp.route('/content/<int:doc_id>', methods=['GET'])
@jwt_required()
def get_document_content(doc_id):
    """Retrieve the raw HTML content of a generated document."""
    user_id = get_jwt_identity()
    doc = Document.query.filter_by(id=doc_id, user_id=int(user_id)).first()

    if not doc:
        return jsonify({'message': 'Documento não encontrado'}), 404

    content = doc.content_html
    if not content:
        # Fallback: Extract text from PDF file if content_html is not stored yet
        if os.path.exists(doc.file_path):
            try:
                import fitz
                pdf = fitz.open(doc.file_path)
                text_blocks = []
                for page in pdf:
                    text_blocks.append(page.get_text("text"))
                pdf.close()
                
                raw_text = "\n".join(text_blocks)
                # Convert plain text to simple paragraphs/headings HTML
                paragraphs = raw_text.split('\n')
                html_parts = []
                for p in paragraphs:
                    p_clean = p.strip()
                    if not p_clean:
                        continue
                    if p_clean.isupper() and len(p_clean) < 100:
                        html_parts.append(f"<h3>{p_clean}</h3>")
                    else:
                        html_parts.append(f"<p>{p_clean}</p>")
                content = "".join(html_parts)
            except Exception as e:
                print(f"Erro ao extrair texto do PDF: {e}")
                content = "<p>Erro ao ler o documento original do PDF. Por favor, redija ou gere novamente.</p>"
        else:
            content = "<p>O arquivo PDF não foi encontrado no servidor e não possui conteúdo em cache.</p>"

    return jsonify({
        'document': {
            'id': doc.id,
            'type': doc.type,
            'title': doc.title,
            'content_html': content
        }
    }), 200


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


@docs_bp.route('/draft/save', methods=['POST'])
@jwt_required()
def save_draft():
    """Save or update a document draft."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    draft_id = data.get('id')
    doc_type = data.get('type')
    title = data.get('title')
    content = data.get('content')
    
    if not doc_type or not title or content is None:
        return jsonify({'message': 'Tipo de documento, título e conteúdo são obrigatórios'}), 400
        
    import json
    content_str = json.dumps(content) if isinstance(content, (dict, list)) else str(content)
    
    if draft_id:
        draft = Draft.query.filter_by(id=draft_id, user_id=int(user_id)).first()
        if not draft:
            return jsonify({'message': 'Rascunho não encontrado'}), 404
        draft.title = title
        draft.content_json = content_str
        draft.type = doc_type
    else:
        draft = Draft(
            user_id=int(user_id),
            type=doc_type,
            title=title,
            content_json=content_str
        )
        db.session.add(draft)
        
    db.session.commit()
    
    return jsonify({
        'message': 'Rascunho salvo com sucesso!',
        'draft': {
            'id': draft.id,
            'type': draft.type,
            'title': draft.title,
            'updated_at': draft.updated_at.isoformat() + 'Z'
        }
    }), 200


@docs_bp.route('/draft/list', methods=['GET'])
@jwt_required()
def list_drafts():
    """List all drafts for the logged-in user."""
    user_id = get_jwt_identity()
    drafts = Draft.query.filter_by(user_id=int(user_id)).order_by(Draft.updated_at.desc()).all()
    
    return jsonify({
        'drafts': [{
            'id': d.id,
            'type': d.type,
            'title': d.title,
            'updated_at': d.updated_at.isoformat() + 'Z'
        } for d in drafts]
    }), 200


@docs_bp.route('/draft/<int:draft_id>', methods=['GET'])
@jwt_required()
def get_draft(draft_id):
    """Retrieve a specific draft's content."""
    user_id = get_jwt_identity()
    draft = Draft.query.filter_by(id=draft_id, user_id=int(user_id)).first()
    
    if not draft:
        return jsonify({'message': 'Rascunho não encontrado'}), 404
        
    import json
    try:
        content_dict = json.loads(draft.content_json)
    except Exception:
        content_dict = draft.content_json
        
    return jsonify({
        'draft': {
            'id': draft.id,
            'type': draft.type,
            'title': draft.title,
            'content': content_dict,
            'updated_at': draft.updated_at.isoformat() + 'Z'
        }
    }), 200


@docs_bp.route('/draft/delete/<int:draft_id>', methods=['DELETE'])
@jwt_required()
def delete_draft(draft_id):
    """Delete a specific draft."""
    user_id = get_jwt_identity()
    draft = Draft.query.filter_by(id=draft_id, user_id=int(user_id)).first()
    
    if not draft:
        return jsonify({'message': 'Rascunho não encontrado'}), 404
        
    db.session.delete(draft)
    db.session.commit()
    
    return jsonify({'message': 'Rascunho excluído com sucesso'}), 200


@docs_bp.route('/generate-content', methods=['POST'])
@jwt_required()
def generate_raw_content():
    """Receive user data, generate content with AI, and return the raw generated text (HTML)."""
    user_id = get_jwt_identity()
    
    # Handle both JSON and multipart form data
    if request.is_json:
        data = request.get_json()
        doc_type = data.get('type')
        user_data = data.get('data')
        files = []
    else:
        doc_type = request.form.get('type')
        user_data = request.form.get('data')
        files = request.files.getlist('images')

    if not doc_type or not user_data:
        return jsonify({'message': 'Tipo de documento e dados são obrigatórios'}), 400

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

        # Generate professional content with AI
        ai_content = generate_content(doc_type, user_data, temp_image_paths)

        # Clean up temporary images
        for path in temp_image_paths:
            if os.path.exists(path):
                os.remove(path)

        return jsonify({
            'message': 'Conteúdo gerado com sucesso!',
            'content': ai_content
        }), 200

    except Exception as e:
        for path in temp_image_paths:
            if os.path.exists(path):
                os.remove(path)
        return jsonify({'message': f'Erro ao gerar conteúdo: {str(e)}'}), 500


@docs_bp.route('/smart-edit', methods=['POST'])
@jwt_required()
def smart_edit():
    """Recebe o HTML atual e um prompt do usuário, retornando o HTML modificado pela IA."""
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Dados inválidos'}), 400
        
    html_content = data.get('content')
    prompt = data.get('prompt')
    
    if not html_content or not prompt:
        return jsonify({'message': 'Conteúdo e instrução são obrigatórios'}), 400
        
    try:
        from services.ai_service import smart_edit_content
        updated_html = smart_edit_content(html_content, prompt)
        
        return jsonify({
            'message': 'Edição aplicada com sucesso!',
            'content': updated_html
        }), 200
    except Exception as e:
        return jsonify({'message': f'Erro ao processar edição inteligente: {str(e)}'}), 500
