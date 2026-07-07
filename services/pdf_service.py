import os
import asyncio
import re
from playwright.async_api import async_playwright

PDF_TEMPLATES = {
    "resume": """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
    h1, h2, h3, p, ul, li, div, span { text-align: left !important; }

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Inter', sans-serif;
        color: #1e293b !important;
        padding: 40px 50px;
        line-height: 1.6;
        background: white;
    }
    h1 { font-size: 28px !important; color: #0f172a !important; margin-bottom: 5px; border-bottom: 3px solid #3b82f6; padding-bottom: 10px; }
    h2 { font-size: 16px !important; color: #3b82f6 !important; margin-top: 25px; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px; }
    h3 { font-size: 14px !important; color: #334155 !important; margin-top: 10px; }
    p { font-size: 13px !important; color: #475569 !important; margin-bottom: 8px; }
    ul { padding-left: 20px; margin-bottom: 10px; }
    li { font-size: 13px !important; color: #475569 !important; margin-bottom: 4px; }
    h1 + p, h1 + div, .contact-info { font-size: 12px !important; color: #64748b !important; margin-bottom: 20px; }
    .contact-info i { color: #3b82f6 !important; margin-right: 6px; width: 16px; text-align: center !important; }
    .contact-info a { color: #3b82f6 !important; text-decoration: none; }
    .contact-info a:hover { text-decoration: underline; }
    i.fab, i.fas { color: #3b82f6 !important; margin-right: 6px; font-size: 13px !important; }
    a { color: #3b82f6 !important; text-decoration: none; }
</style>
</head>
<body>
{content}
</body>
</html>""",

    "resume_en": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
    h1, h2, h3, p, ul, li, div, span { text-align: left !important; }

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Inter', sans-serif;
        color: #1e293b !important;
        padding: 40px 50px;
        line-height: 1.6;
        background: white;
    }
    h1 { font-size: 28px !important; color: #0f172a !important; margin-bottom: 5px; border-bottom: 3px solid #3b82f6; padding-bottom: 10px; }
    h2 { font-size: 16px !important; color: #3b82f6 !important; margin-top: 25px; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px; }
    h3 { font-size: 14px !important; color: #334155 !important; margin-top: 10px; }
    p { font-size: 13px !important; color: #475569 !important; margin-bottom: 8px; }
    ul { padding-left: 20px; margin-bottom: 10px; }
    li { font-size: 13px !important; color: #475569 !important; margin-bottom: 4px; }
    h1 + p, h1 + div, .contact-info { font-size: 12px !important; color: #64748b !important; margin-bottom: 20px; }
    .contact-info i { color: #3b82f6 !important; margin-right: 6px; width: 16px; text-align: center !important; }
    .contact-info a { color: #3b82f6 !important; text-decoration: none; }
    .contact-info a:hover { text-decoration: underline; }
    i.fab, i.fas { color: #3b82f6 !important; margin-right: 6px; font-size: 13px !important; }
    a { color: #3b82f6 !important; text-decoration: none; }
</style>
</head>
<body>
{content}
</body>
</html>""",

    "resume_modern": """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
    h1, h2, h3, p, ul, li, div, span { text-align: left !important; }

    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Poppins', sans-serif;
        color: #334155 !important;
        padding: 40px 45px;
        line-height: 1.6;
        background: white;
    }
    h1 { font-size: 26px !important; color: #0f172a !important; font-weight: 700; margin-bottom: 5px; }
    h2 { font-size: 14px !important; color: #0d9488 !important; font-weight: 600; margin-top: 25px; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1.5px; border-left: 4px solid #0d9488; padding-left: 10px; }
    h3 { font-size: 13px !important; color: #1e293b !important; font-weight: 600; margin-top: 8px; }
    p { font-size: 12px !important; color: #475569 !important; margin-bottom: 6px; }
    ul { padding-left: 18px; margin-bottom: 8px; }
    li { font-size: 12px !important; color: #475569 !important; margin-bottom: 3px; }
    h1 + p, h1 + div, .contact-info { font-size: 11px !important; color: #64748b !important; margin-top: 10px; margin-bottom: 20px; background: #f8fafc; padding: 12px 15px; border-radius: 8px; }
    .contact-info i { color: #0d9488 !important; margin-right: 4px; }
    .contact-info a { color: #0d9488 !important; text-decoration: none; }
    i.fab, i.fas { color: #0d9488 !important; margin-right: 4px; }
    a { color: #0d9488 !important; text-decoration: none; }
</style>
</head>
<body>
{content}
</body>
</html>""",

    "resume_modern_en": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
    h1, h2, h3, p, ul, li, div, span { text-align: left !important; }

    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Poppins', sans-serif;
        color: #334155 !important;
        padding: 40px 45px;
        line-height: 1.6;
        background: white;
    }
    h1 { font-size: 26px !important; color: #0f172a !important; font-weight: 700; margin-bottom: 5px; }
    h2 { font-size: 14px !important; color: #0d9488 !important; font-weight: 600; margin-top: 25px; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1.5px; border-left: 4px solid #0d9488; padding-left: 10px; }
    h3 { font-size: 13px !important; color: #1e293b !important; font-weight: 600; margin-top: 8px; }
    p { font-size: 12px !important; color: #475569 !important; margin-bottom: 6px; }
    ul { padding-left: 18px; margin-bottom: 8px; }
    li { font-size: 12px !important; color: #475569 !important; margin-bottom: 3px; }
    h1 + p, h1 + div, .contact-info { font-size: 11px !important; color: #64748b !important; margin-top: 10px; margin-bottom: 20px; background: #f8fafc; padding: 12px 15px; border-radius: 8px; }
    .contact-info i { color: #0d9488 !important; margin-right: 4px; }
    .contact-info a { color: #0d9488 !important; text-decoration: none; }
    i.fab, i.fas { color: #0d9488 !important; margin-right: 4px; }
    a { color: #0d9488 !important; text-decoration: none; }
</style>
</head>
<body>
{content}
</body>
</html>""",

    "resume_minimalist": """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
    h1, h2, h3, p, ul, li, div, span { text-align: center !important; }

    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Lora:ital,wght@0,400;0,500;1,400&display=swap');
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Lora', serif;
        color: #111827 !important;
        padding: 50px 55px;
        line-height: 1.7;
        background: white;
    }
    h1 { font-family: 'Playfair Display', serif; font-size: 30px !important; color: #111827 !important; text-align: center !important; font-weight: 600; margin-bottom: 15px; }
    h2 { font-family: 'Playfair Display', serif; font-size: 13px !important; color: #111827 !important; font-weight: 600; margin-top: 30px; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 2px; text-align: center !important; border: none; padding-bottom: 3px; border-bottom: 1px solid #111827; }
    h3 { font-size: 13px !important; color: #111827 !important; font-weight: 600; margin-top: 10px; }
    p { font-size: 12px !important; color: #374151 !important; margin-bottom: 6px; }
    ul { padding-left: 20px; margin-bottom: 8px; }
    li { font-size: 12px !important; color: #374151 !important; margin-bottom: 3px; }
    i.fab, i.fas { display: none; }
    h1 + p, h1 + div, .contact-info { font-size: 11px !important; text-align: center !important; color: #4b5563 !important; margin-bottom: 25px; }
    a { color: #111827 !important; text-decoration: underline; }
</style>
</head>
<body>
{content}
</body>
</html>""",

    "resume_minimalist_en": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
    h1, h2, h3, p, ul, li, div, span { text-align: center !important; }

    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Lora:ital,wght@0,400;0,500;1,400&display=swap');
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Lora', serif;
        color: #111827 !important;
        padding: 50px 55px;
        line-height: 1.7;
        background: white;
    }
    h1 { font-family: 'Playfair Display', serif; font-size: 30px !important; color: #111827 !important; text-align: center !important; font-weight: 600; margin-bottom: 15px; }
    h2 { font-family: 'Playfair Display', serif; font-size: 13px !important; color: #111827 !important; font-weight: 600; margin-top: 30px; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 2px; text-align: center !important; border: none; padding-bottom: 3px; border-bottom: 1px solid #111827; }
    h3 { font-size: 13px !important; color: #111827 !important; font-weight: 600; margin-top: 10px; }
    p { font-size: 12px !important; color: #374151 !important; margin-bottom: 6px; }
    ul { padding-left: 20px; margin-bottom: 8px; }
    li { font-size: 12px !important; color: #374151 !important; margin-bottom: 3px; }
    i.fab, i.fas { display: none; }
    h1 + p, h1 + div, .contact-info { font-size: 11px !important; text-align: center !important; color: #4b5563 !important; margin-bottom: 25px; }
    a { color: #111827 !important; text-decoration: underline; }
</style>
</head>
<body>
{content}
</body>
</html>""",

    "resume_es": """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
    h1, h2, h3, p, ul, li, div, span { text-align: left !important; }

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Inter', sans-serif;
        color: #1e293b !important;
        padding: 40px 50px;
        line-height: 1.6;
        background: white;
    }
    h1 { font-size: 28px !important; color: #0f172a !important; margin-bottom: 5px; border-bottom: 3px solid #3b82f6; padding-bottom: 10px; }
    h2 { font-size: 16px !important; color: #3b82f6 !important; margin-top: 25px; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px; }
    h3 { font-size: 14px !important; color: #334155 !important; margin-top: 10px; }
    p { font-size: 13px !important; color: #475569 !important; margin-bottom: 8px; }
    ul { padding-left: 20px; margin-bottom: 10px; }
    li { font-size: 13px !important; color: #475569 !important; margin-bottom: 4px; }
    h1 + p, h1 + div, .contact-info { font-size: 12px !important; color: #64748b !important; margin-bottom: 20px; }
    .contact-info i { color: #3b82f6 !important; margin-right: 6px; width: 16px; text-align: center !important; }
    .contact-info a { color: #3b82f6 !important; text-decoration: none; }
    .contact-info a:hover { text-decoration: underline; }
    i.fab, i.fas { color: #3b82f6 !important; margin-right: 6px; font-size: 13px !important; }
    a { color: #3b82f6 !important; text-decoration: none; }
</style>
</head>
<body>
{content}
</body>
</html>""",

    "resume_modern_es": """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
    h1, h2, h3, p, ul, li, div, span { text-align: left !important; }

    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Poppins', sans-serif;
        color: #334155 !important;
        padding: 40px 45px;
        line-height: 1.6;
        background: white;
    }
    h1 { font-size: 26px !important; color: #0f172a !important; font-weight: 700; margin-bottom: 5px; }
    h2 { font-size: 14px !important; color: #0d9488 !important; font-weight: 600; margin-top: 25px; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1.5px; border-left: 4px solid #0d9488; padding-left: 10px; }
    h3 { font-size: 13px !important; color: #1e293b !important; font-weight: 600; margin-top: 8px; }
    p { font-size: 12px !important; color: #475569 !important; margin-bottom: 6px; }
    ul { padding-left: 18px; margin-bottom: 8px; }
    li { font-size: 12px !important; color: #475569 !important; margin-bottom: 3px; }
    h1 + p, h1 + div, .contact-info { font-size: 11px !important; color: #64748b !important; margin-top: 10px; margin-bottom: 20px; background: #f8fafc; padding: 12px 15px; border-radius: 8px; }
    .contact-info i { color: #0d9488 !important; margin-right: 4px; }
    .contact-info a { color: #0d9488 !important; text-decoration: none; }
    i.fab, i.fas { color: #0d9488 !important; margin-right: 4px; }
    a { color: #0d9488 !important; text-decoration: none; }
</style>
</head>
<body>
{content}
</body>
</html>""",

    "resume_minimalist_es": """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<style>
    h1, h2, h3, p, ul, li, div, span { text-align: center !important; }

    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Lora:ital,wght@0,400;0,500;1,400&display=swap');
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Lora', serif;
        color: #111827 !important;
        padding: 50px 55px;
        line-height: 1.7;
        background: white;
    }
    h1 { font-family: 'Playfair Display', serif; font-size: 30px !important; color: #111827 !important; text-align: center !important; font-weight: 600; margin-bottom: 15px; }
    h2 { font-family: 'Playfair Display', serif; font-size: 13px !important; color: #111827 !important; font-weight: 600; margin-top: 30px; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 2px; text-align: center !important; border: none; padding-bottom: 3px; border-bottom: 1px solid #111827; }
    h3 { font-size: 13px !important; color: #111827 !important; font-weight: 600; margin-top: 10px; }
    p { font-size: 12px !important; color: #374151 !important; margin-bottom: 6px; }
    ul { padding-left: 20px; margin-bottom: 8px; }
    li { font-size: 12px !important; color: #374151 !important; margin-bottom: 3px; }
    i.fab, i.fas { display: none; }
    h1 + p, h1 + div, .contact-info { font-size: 11px !important; text-align: center !important; color: #4b5563 !important; margin-bottom: 25px; }
    a { color: #111827 !important; text-decoration: underline; }
</style>
</head>
<body>
{content}
</body>
</html>""",

    "contract": """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: Arial, "Times New Roman", sans-serif;
        color: #000000 !important;
        padding: 0;
        line-height: 1.5;
        background: white;
    }
    h1 { font-size: 12pt !important; color: #000000 !important; text-align: center; margin-bottom: 20px; text-transform: uppercase; font-weight: bold; }
    h2 { font-size: 12pt !important; color: #000000 !important; margin-top: 15px; margin-bottom: 10px; text-transform: uppercase; font-weight: bold; text-align: left; }
    h3 { font-size: 12pt !important; color: #000000 !important; margin-top: 10px; font-weight: bold; text-align: left; }
    p { font-size: 12pt !important; color: #000000 !important; margin-bottom: 10px; text-align: justify; }
    ul { padding-left: 25px; margin-bottom: 10px; }
    li { font-size: 12pt !important; color: #000000 !important; margin-bottom: 10px; text-align: justify; }
    div, span { text-align: justify; font-size: 12pt; color: #000000; }

    /* ── Signature Block (ABNT) ── */
    .closing-block {
        page-break-inside: avoid;
        margin-top: 50px;
    }
    .local-data {
        text-align: left;
        margin-bottom: 60px;
        font-size: 12pt;
        color: #000000;
    }
    .signatures-container {
        display: flex;
        justify-content: space-between;
        gap: 40px;
        page-break-inside: avoid;
    }
    .signature-party {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        flex: 1;
        page-break-inside: avoid;
    }
    .signature-line {
        width: 280px;
        border-top: 1px solid #000000;
        margin-top: 80px;
        margin-bottom: 6px;
    }
    .signature-party .sig-name {
        font-size: 12pt;
        font-weight: bold;
        color: #000000;
        margin-bottom: 2px;
    }
    .signature-party .sig-doc {
        font-size: 11pt;
        color: #000000;
        margin-bottom: 2px;
    }
    .signature-party .sig-role {
        font-size: 11pt;
        font-weight: bold;
        color: #000000;
        text-transform: uppercase;
    }
    .witnesses-section {
        margin-top: 60px;
        page-break-inside: avoid;
    }
    .witnesses-section h3 {
        text-align: left;
        margin-bottom: 30px;
    }
</style>
</head>
<body>
{content}
</body>
</html>""",

    "report": """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
    h1, h2, h3, p, ul, li, div, span { text-align: left !important; }

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Inter', sans-serif;
        color: #1e293b !important;
        padding: 40px 50px;
        line-height: 1.7;
        background: white;
    }
    h1 { font-size: 24px !important; color: #0f172a !important; margin-bottom: 5px; }
    .report-meta { font-size: 12px !important; color: #64748b !important; margin-bottom: 30px; border-bottom: 2px solid #3b82f6; padding-bottom: 15px; }
    h2 { font-size: 16px !important; color: #1e40af !important; margin-top: 25px; margin-bottom: 10px; }
    h3 { font-size: 14px !important; color: #334155 !important; margin-top: 12px; }
    p { font-size: 13px !important; color: #475569 !important; margin-bottom: 10px; text-align: justify !important; }
    ul { padding-left: 20px; margin-bottom: 10px; }
    li { font-size: 13px !important; color: #475569 !important; margin-bottom: 4px; }
    table { width: 100%; border-collapse: collapse; margin: 15px 0; }
    th { background: #1e40af; color: white; padding: 10px; font-size: 12px !important; text-align: left !important; }
    td { border: 1px solid #e2e8f0; padding: 8px; font-size: 12px !important; color: #475569 !important; }
    tr:nth-child(even) { background: #f8fafc; }
</style>
</head>
<body>
{content}
</body>
</html>"""
}


def generate_pdf_sync(html_content, output_path, margins=None):
    """Generate a PDF from HTML content using Playwright (sync wrapper)."""
    asyncio.run(_generate_pdf(html_content, output_path, margins))


async def _generate_pdf(html_content, output_path, margins=None):
    """Generate a PDF from HTML content using Playwright."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    if margins is None:
        margins = {"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"}

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html_content, wait_until="networkidle", timeout=60000)
        # Wait a brief moment for fonts to load, but don't block forever
        await page.wait_for_timeout(1000)
        await page.pdf(
            path=output_path,
            format="A4",
            margin=margins,
            print_background=True
        )
        await browser.close()


def create_document_pdf(doc_type, ai_content, output_path):
    """Wrap AI-generated content into a styled HTML template and generate PDF."""
    template = PDF_TEMPLATES.get(doc_type)
    if not template:
        raise ValueError(f"Template não encontrado para tipo: {doc_type}")

    margins = None
    if doc_type == "contract":
        # ABNT margins: Top 3cm, Left 3cm, Bottom 2cm, Right 2cm
        margins = {"top": "30mm", "bottom": "20mm", "left": "30mm", "right": "20mm"}
        
        # ── CONTRACT HTML SANITIZATION ──
        # The LLM and contenteditable editor wrap every ~80 char line in its own
        # <p> tag, which the PDF renderer treats as separate block elements,
        # creating hard visual line breaks mid-sentence. We need to merge
        # consecutive <p> tags that belong to the same logical paragraph.
        
        # Step 1: Remove inline styles that leak dark-theme colors into the PDF
        #         (e.g. color: var(--text-color), color: rgb(226, 232, 240))
        ai_content = re.sub(r'color:\s*var\(--[^)]+\);?', '', ai_content, flags=re.IGNORECASE)
        ai_content = re.sub(r'color:\s*rgb\([^)]+\);?', '', ai_content, flags=re.IGNORECASE)
        ai_content = re.sub(r'font-size:\s*1\.2rem;?', '', ai_content, flags=re.IGNORECASE)
        
        # Step 2: Clean up empty style attributes left behind
        ai_content = re.sub(r'\s*style\s*=\s*"\s*"', '', ai_content, flags=re.IGNORECASE)
        
        # Step 3: Remove <span> wrappers that now have no useful attributes
        ai_content = re.sub(r'<span\s*>(.*?)</span>', r'\1', ai_content, flags=re.IGNORECASE | re.DOTALL)
        
        # Step 4: Merge consecutive <p> tags into single paragraphs.
        # The key insight: </p><p> between lines of the SAME paragraph must be
        # replaced with a space. But </p> before a heading (<h1-h6>) or before
        # a paragraph that starts with structural keywords (CLÁUSULA, PARÁGRAFO, etc.)
        # should be PRESERVED as a real paragraph break.
        
        # 4a: First, normalize whitespace between closing and opening tags
        ai_content = re.sub(r'</p>\s*<p', '</p><p', ai_content, flags=re.IGNORECASE)
        
        # 4b: Protect paragraph boundaries that are REAL (before headings,
        #     or before paragraphs starting with structural contract keywords)
        structural_keywords = (
            r'CLÁUSULA|CLAUSULA|PARÁGRAFO|PARAGRAFO|'
            r'CONTRATANTE:|CONTRATADA:|CONTRATADO:|'
            r'TESTEMUNHAS:|'
            r'E,? por estarem|'
            r'Representad[ao] por:|'
            r'Nome:|CPF:|RG:|CNPJ:|'
            r'_{5,}|'                         # Signature lines (5+ underscores)
            r'\d+\.\s*_{3,}'                  # Numbered signature lines (1. ___)
        )
        # Protect </p><p> where the new <p> starts with a structural keyword
        ai_content = re.sub(
            r'</p><p([^>]*)>\s*(' + structural_keywords + r')',
            r'[[PARA_BREAK]]\1[[\2]]',
            ai_content,
            flags=re.IGNORECASE
        )
        
        # 4c: Now merge ALL remaining consecutive </p><p> into a single space
        #     This is the core fix: these are the fake line breaks
        ai_content = re.sub(
            r'</p>\s*<p[^>]*>',
            ' ',
            ai_content,
            flags=re.IGNORECASE
        )
        
        # 4d: Restore protected paragraph boundaries
        ai_content = re.sub(
            r'\[\[PARA_BREAK\]\]([^\[]*)\[\[([^\]]+)\]\]',
            r'</p><p style="text-align: justify;">\2',
            ai_content
        )
        
        # Step 5: Handle <div> wrappers that also create unwanted breaks
        #         Empty divs with just <br> are intentional spacing — keep them
        ai_content = re.sub(r'<div[^>]*>\s*<br\s*/?>\s*</div>', '<br>', ai_content, flags=re.IGNORECASE)
        #         Other consecutive divs that aren't structural: merge them
        ai_content = re.sub(r'</div>\s*<div[^>]*>', ' ', ai_content, flags=re.IGNORECASE)
        
        # Step 6: Clean up remaining stray <br> and newlines
        ai_content = re.sub(r'<br\s*/?>', ' ', ai_content, flags=re.IGNORECASE)
        ai_content = ai_content.replace("\n", " ").replace("\r", "")
        
        # Step 7: Normalize whitespace
        ai_content = re.sub(r'&nbsp;\s*', ' ', ai_content)
        ai_content = re.sub(r'\s{2,}', ' ', ai_content)
        ai_content = re.sub(r'>\s+<', '><', ai_content)
        
        # Step 8: Convert underscore signature lines into proper HTML signature blocks
        #         This replaces ___ patterns with CSS-based signature lines
        
        # 8a: Remove all standalone underscore lines (they will be replaced by the signature block)
        ai_content = re.sub(
            r'<(?:p|h\d|div)[^>]*>\s*(?:<br\s*/?>)?\s*_{3,}\s*</(?:p|h\d|div)>',
            '',
            ai_content,
            flags=re.IGNORECASE
        )
        # Also remove inline underscores within paragraphs
        ai_content = re.sub(r'_{5,}', '', ai_content)
        
        # 8b: Separate "Local e Data" from the closing paragraph ("E, por estarem...")
        #     Look for patterns like: "... testemunhas abaixo. Cidade, DD de Mês de AAAA"
        ai_content = re.sub(
            r'((?:testemunhas|assinam)[^<]*?)'
            r'\s*([A-ZÀ-Ú][a-zà-ú]+(?:\s+–\s*|\s*[-,]\s*|,\s+)\s*\d{1,2}\s+de\s+\w+\s+de\s+\d{4})',
            r'\1</p><div class="closing-block"><div class="local-data">\2</div>',
            ai_content,
            flags=re.IGNORECASE
        )
        
        # Helper function to strip HTML tags inside groups
        def clean_html_text(html_string):
            text = re.sub(r'<[^>]+>', '', html_string)
            text = text.replace('&nbsp;', ' ').replace('&nbsp', ' ')
            return text.strip()

        # 8c: Build proper signature blocks from detected party info
        def build_signature_html(match):
            name = clean_html_text(match.group('name'))
            doc_line = clean_html_text(match.group('doc_line'))
            role = clean_html_text(match.group('role'))
            rep_info = clean_html_text(match.group('rep')) if match.group('rep') else ''
            
            html = '<div class="signature-party">'
            html += '<div class="signature-line"></div>'
            html += f'<div class="sig-name">{name}</div>'
            html += f'<div class="sig-doc">{doc_line}</div>'
            if rep_info:
                html += f'<div class="sig-doc">{rep_info}</div>'
            html += f'<div class="sig-role">{role}</div>'
            html += '</div>'
            return html
        
        # Match signature blocks: Name on its own line, then optional CPF/CNPJ, then optional representation, then role
        # We allow p, div or h1-h6 tags. Using proper backreferences (\1, \3, \5, \7) prevents crossing tags.
        sig_pattern = re.compile(
            r'<(p|h\d|div)[^>]*>(?P<name>(?:(?!</\1>).)*?)</\1>\s*'
            r'<(p|h\d|div)[^>]*>(?P<doc_line>(?:(?!</\3>).)*?(?:CPF|CNPJ)(?:(?!</\3>).)*?)</\3>\s*'
            r'(?:<(p|h\d|div)[^>]*>(?P<rep>(?:(?!</\5>).)*?Representad[ao]\s+por(?:(?!</\5>).)*?)</\5>\s*)?'
            r'<(p|h\d|div)[^>]*>(?P<role>(?:(?!</\7>).)*?(?:CONTRATANT[E]|CONTRATAD[AOa]|LOCADOR[Aa]?|LOCATÁRI[Oo]|PARTE\s+\w+)(?:(?!</\7>).)*?)</\7>',
            re.IGNORECASE | re.DOTALL
        )
        
        # Find all signature blocks and replace them
        sig_matches = list(sig_pattern.finditer(ai_content))
        valid_matches = []
        for m in sig_matches:
            name_text = clean_html_text(m.group('name'))
            role_text = clean_html_text(m.group('role'))
            doc_text = clean_html_text(m.group('doc_line'))
            
            # Filter out false positives from preamble
            if len(name_text) > 80 or role_text.strip().endswith(':') or 'portador' in doc_text.lower():
                continue
            valid_matches.append(m)

        if valid_matches:
            # Build the signatures container
            sig_html_parts = []
            for m in valid_matches:
                sig_html_parts.append(build_signature_html(m))
            
            # Remove all matched signature blocks from content
            for m in reversed(valid_matches):
                ai_content = ai_content[:m.start()] + ai_content[m.end():]
            
            # Build the full closing signature section
            closing_html = '<div class="signatures-container">'
            closing_html += ''.join(sig_html_parts)
            closing_html += '</div></div>'  # close signatures-container and closing-block
            
            # Append before closing </p> or at the end
            ai_content = ai_content.rstrip() + closing_html
        
        # 8d: If no structured signatures were found but we have the closing-block open, close it
        if '<div class="closing-block">' in ai_content and '</div></div>' not in ai_content:
            ai_content += '</div>'

    full_html = template.replace("{content}", ai_content)
    generate_pdf_sync(full_html, output_path, margins)
    return output_path
