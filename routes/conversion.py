import os
from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from services.image_converter import convert_image
from services.doc_converter import convert_docx_to_pdf

conversion_bp = Blueprint('conversion_bp', __name__)

@conversion_bp.route('/image', methods=['POST'])
def convert_image_route():
    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400
    file = request.files['file']
    target_format = request.form.get('target_format')
    if not target_format:
        return jsonify({'message': 'target_format required'}), 400
    filename = secure_filename(file.filename)
    input_path = os.path.join(current_app.instance_path, 'uploads', filename)
    os.makedirs(os.path.dirname(input_path), exist_ok=True)
    file.save(input_path)
    base, _ = os.path.splitext(filename)
    output_filename = f"{base}.{target_format.lower()}"
    output_path = os.path.join(current_app.instance_path, 'uploads', output_filename)
    try:
        convert_image(input_path, output_path, target_format)
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@conversion_bp.route('/document', methods=['POST'])
def convert_document_route():
    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400
    file = request.files['file']
    filename = secure_filename(file.filename)
    if not filename.lower().endswith('.docx'):
        return jsonify({'message': 'Only .docx files supported'}), 400
    input_path = os.path.join(current_app.instance_path, 'uploads', filename)
    os.makedirs(os.path.dirname(input_path), exist_ok=True)
    file.save(input_path)
    try:
        pdf_path = convert_docx_to_pdf(input_path)
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@conversion_bp.route('/pdf', methods=['POST'])
def convert_pdf_route():
    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400
    file = request.files['file']
    filename = secure_filename(file.filename)
    if not filename.lower().endswith('.pdf'):
        return jsonify({'message': 'Only .pdf files supported'}), 400
    input_path = os.path.join(current_app.instance_path, 'uploads', filename)
    os.makedirs(os.path.dirname(input_path), exist_ok=True)
    file.save(input_path)
    base, _ = os.path.splitext(filename)
    output_filename = f"{base}_pdfa.pdf"
    output_path = os.path.join(current_app.instance_path, 'uploads', output_filename)
    try:
        from pathlib import Path
        import pdftopdfa
        result = pdftopdfa.convert_to_pdfa(Path(input_path), Path(output_path), level='3b')
        if not result.success:
            return jsonify({'message': result.error or 'Falha ao converter para PDF/A'}), 500
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@conversion_bp.route('/reorder-pdf', methods=['POST'])
def reorder_pdf_route():
    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400
    file = request.files['file']
    filename = secure_filename(file.filename)
    if not filename.lower().endswith('.pdf'):
        return jsonify({'message': 'Only .pdf files supported'}), 400
    
    page_order_str = request.form.get('page_order')
    if not page_order_str:
        return jsonify({'message': 'No page order specified'}), 400
    
    import json
    try:
        page_order = json.loads(page_order_str)
    except Exception:
        return jsonify({'message': 'Invalid page order format'}), 400
        
    input_path = os.path.join(current_app.instance_path, 'uploads', filename)
    os.makedirs(os.path.dirname(input_path), exist_ok=True)
    file.save(input_path)
    
    base, _ = os.path.splitext(filename)
    output_filename = f"{base}_reordered.pdf"
    output_path = os.path.join(current_app.instance_path, 'uploads', output_filename)
    
    try:
        import fitz
        doc = fitz.open(input_path)
        new_doc = fitz.open()
        for index in page_order:
            if 0 <= index < len(doc):
                new_doc.insert_pdf(doc, from_page=index, to_page=index)
        new_doc.save(output_path)
        new_doc.close()
        doc.close()
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({'message': str(e)}), 500


