import os
import io
import zipfile
import fitz
from pathlib import Path
import pdftopdfa

def reorder_pdf(input_path: str, output_path: str, page_order: list) -> str:
    """Reorder pages in a PDF based on the provided list of indices."""
    doc = fitz.open(input_path)
    new_doc = fitz.open()
    for index in page_order:
        if 0 <= index < len(doc):
            new_doc.insert_pdf(doc, from_page=index, to_page=index)
    new_doc.save(output_path)
    new_doc.close()
    doc.close()
    return output_path

def compress_pdf(input_path: str, output_path: str, level: str = 'medium') -> str:
    """Compress a PDF file with a specific compression level."""
    doc = fitz.open(input_path)
    if level == 'low':
        doc.save(output_path, garbage=3, deflate=True)
    elif level == 'high':
        doc.save(output_path, garbage=4, deflate=True, clean=True, linear=True)
    else:
        doc.save(output_path, garbage=4, deflate=True, clean=True)
    doc.close()
    return output_path

def split_pdf_interval(input_path: str, output_path: str, page_range: str) -> str:
    """Split a PDF file and return only the specified interval."""
    doc = fitz.open(input_path)
    pages_to_keep = set()
    parts = page_range.replace(' ', '').split(',')
    
    for part in parts:
        if '-' in part:
            start, end = part.split('-')
            if start.isdigit() and end.isdigit():
                pages_to_keep.update(range(int(start)-1, int(end)))
        elif part.isdigit():
            pages_to_keep.add(int(part)-1)
            
    pages_list = sorted(list(pages_to_keep))
    pages_list = [p for p in pages_list if 0 <= p < len(doc)]
    
    if not pages_list:
        doc.close()
        raise ValueError('Intervalo inválido')
        
    new_doc = fitz.open()
    for p in pages_list:
        new_doc.insert_pdf(doc, from_page=p, to_page=p)
        
    new_doc.save(output_path)
    new_doc.close()
    doc.close()
    return output_path

def split_pdf_all(input_path: str, base_name: str) -> io.BytesIO:
    """Split a PDF file into individual pages and return them as a ZIP stream."""
    doc = fitz.open(input_path)
    memory_file = io.BytesIO()
    
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for i in range(len(doc)):
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=i, to_page=i)
            pdf_bytes = new_doc.write()
            zf.writestr(f"{base_name}_pag_{i+1}.pdf", pdf_bytes)
            new_doc.close()
            
    doc.close()
    memory_file.seek(0)
    return memory_file

def merge_pdfs(input_paths: list, output_path: str) -> str:
    """Merge multiple PDF files into one."""
    merged_doc = fitz.open()
    for path in input_paths:
        doc = fitz.open(path)
        merged_doc.insert_pdf(doc)
        doc.close()
    merged_doc.save(output_path)
    merged_doc.close()
    return output_path

def convert_to_pdfa(input_path: str, output_path: str) -> str:
    """Convert standard PDF to PDF/A."""
    result = pdftopdfa.convert_to_pdfa(Path(input_path), Path(output_path), level='3b')
    if not result.success:
        raise Exception(result.error or 'Falha ao converter para PDF/A')
    return output_path
