import os
from flask import current_app
from docx import Document as DocxDocument
from services.pdf_service import generate_pdf_sync


def _docx_to_html(docx_path: str) -> str:
    """Convert a .docx file to a simple HTML representation.
    Only extracts paragraphs and headings; complex formatting is ignored.
    """
    doc = DocxDocument(docx_path)
    html_parts = []
    for para in doc.paragraphs:
        style = para.style.name.lower()
        text = para.text.replace('\n', '<br>')
        if 'heading' in style:
            level = ''.join(filter(str.isdigit, style)) or '1'
            html_parts.append(f'<h{level}>{text}</h{level}>')
        else:
            html_parts.append(f'<p>{text}</p>')
    return '\n'.join(html_parts)


def convert_docx_to_pdf(input_path: str) -> str:
    """Convert a .docx file to PDF and return the PDF file path.
    The PDF is generated using the existing Playwright PDF service.
    """
    # Create temporary HTML content
    html_content = f"<!DOCTYPE html><html><head><meta charset='UTF-8'></head><body>{_docx_to_html(input_path)}</body></html>"
    # Prepare output path
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_dir = os.path.join(current_app.instance_path, 'uploads')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{base_name}.pdf")
    # Generate PDF using existing utility
    generate_pdf_sync(html_content, output_path)
    return output_path
