import os
import json
from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from services.image_converter import convert_image
from services.doc_converter import convert_docx_to_pdf, convert_pdf_to_docx
from services.pdf_modifiers import reorder_pdf, compress_pdf, split_pdf_interval, split_pdf_all, merge_pdfs, convert_to_pdfa

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
        convert_to_pdfa(input_path, output_path)
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@conversion_bp.route('/pdf-to-docx', methods=['POST'])
def convert_pdf_to_docx_route():
    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400
    file = request.files['file']
    filename = secure_filename(file.filename)
    if not filename.lower().endswith('.pdf'):
        return jsonify({'message': 'Only .pdf files supported'}), 400
    input_path = os.path.join(current_app.instance_path, 'uploads', filename)
    os.makedirs(os.path.dirname(input_path), exist_ok=True)
    file.save(input_path)
    try:
        docx_path = convert_pdf_to_docx(input_path)
        return send_file(docx_path, as_attachment=True)
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
        reorder_pdf(input_path, output_path, page_order)
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@conversion_bp.route('/compress-pdf', methods=['POST'])
def compress_pdf_route():
    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400
    file = request.files['file']
    filename = secure_filename(file.filename)
    level = request.form.get('level', 'medium')
    
    input_path = os.path.join(current_app.instance_path, 'uploads', filename)
    os.makedirs(os.path.dirname(input_path), exist_ok=True)
    file.save(input_path)
    
    base, _ = os.path.splitext(filename)
    output_filename = f"{base}_compressed.pdf"
    output_path = os.path.join(current_app.instance_path, 'uploads', output_filename)
    
    try:
        compress_pdf(input_path, output_path, level)
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@conversion_bp.route('/split-pdf', methods=['POST'])
def split_pdf_route():
    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400
    file = request.files['file']
    filename = secure_filename(file.filename)
    mode = request.form.get('mode', 'all')
    page_range = request.form.get('range', '')
    
    input_path = os.path.join(current_app.instance_path, 'uploads', filename)
    os.makedirs(os.path.dirname(input_path), exist_ok=True)
    file.save(input_path)
    
    base, _ = os.path.splitext(filename)
    
    try:
        if mode == 'interval' and page_range:
            output_filename = f"{base}_interval.pdf"
            output_path = os.path.join(current_app.instance_path, 'uploads', output_filename)
            split_pdf_interval(input_path, output_path, page_range)
            return send_file(output_path, as_attachment=True)
            
        elif mode == 'all':
            memory_file = split_pdf_all(input_path, base)
            return send_file(memory_file, download_name=f"{base}_dividido.zip", as_attachment=True)
            
        else:
            return jsonify({'message': 'Modo de divisão inválido'}), 400
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@conversion_bp.route('/merge-pdfs', methods=['POST'])
def merge_pdfs_route():
    files = request.files.getlist('files')
    if not files or len(files) < 2:
        return jsonify({'message': 'Forneça pelo menos 2 arquivos PDF'}), 400
        
    try:
        input_paths = []
        for file in files:
            filename = secure_filename(file.filename)
            if filename.lower().endswith('.pdf'):
                input_path = os.path.join(current_app.instance_path, 'uploads', filename)
                os.makedirs(os.path.dirname(input_path), exist_ok=True)
                file.save(input_path)
                input_paths.append(input_path)
                
        output_filename = "merged_temp.pdf"
        output_path = os.path.join(current_app.instance_path, 'uploads', output_filename)
        merge_pdfs(input_paths, output_path)
        
        return send_file(output_path, download_name="merged_temp.pdf", as_attachment=True)
    except Exception as e:
        return jsonify({'message': str(e)}), 500
