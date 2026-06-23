import os
import asyncio
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
    h1, h2, h3, p, ul, li, div, span { text-align: left !important; }

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Inter', sans-serif;
        color: #1e293b !important;
        padding: 50px 60px;
        line-height: 1.8;
        background: white;
    }
    h1 { font-size: 22px !important; color: #0f172a !important; text-align: center !important; margin-bottom: 30px; text-transform: uppercase; letter-spacing: 2px; }
    h2 { font-size: 14px !important; color: #0f172a !important; margin-top: 20px; margin-bottom: 8px; text-transform: uppercase; }
    h3 { font-size: 13px !important; color: #334155 !important; margin-top: 10px; font-weight: 600; }
    p { font-size: 13px !important; color: #334155 !important; margin-bottom: 10px; text-align: justify !important; }
    ul { padding-left: 25px; margin-bottom: 10px; }
    li { font-size: 13px !important; color: #334155 !important; margin-bottom: 4px; }
    .signatures { margin-top: 60px; display: flex; justify-content: space-between; }
    .signature-line { width: 200px; border-top: 1px solid #0f172a; padding-top: 5px; text-align: center !important; font-size: 12px !important; }
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


def generate_pdf_sync(html_content, output_path):
    """Generate a PDF from HTML content using Playwright (sync wrapper)."""
    asyncio.run(_generate_pdf(html_content, output_path))


async def _generate_pdf(html_content, output_path):
    """Generate a PDF from HTML content using Playwright."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html_content, wait_until="networkidle", timeout=60000)
        # Wait a brief moment for fonts to load, but don't block forever
        await page.wait_for_timeout(1000)
        await page.pdf(
            path=output_path,
            format="A4",
            margin={"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"},
            print_background=True
        )
        await browser.close()


def create_document_pdf(doc_type, ai_content, output_path):
    """Wrap AI-generated content into a styled HTML template and generate PDF."""
    template = PDF_TEMPLATES.get(doc_type)
    if not template:
        raise ValueError(f"Template não encontrado para tipo: {doc_type}")

    full_html = template.replace("{content}", ai_content)
    generate_pdf_sync(full_html, output_path)
    return output_path
