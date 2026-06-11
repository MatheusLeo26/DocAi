import os
import asyncio
from playwright.async_api import async_playwright

PDF_TEMPLATES = {
    "resume": """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Inter', sans-serif;
        color: #1e293b;
        padding: 40px 50px;
        line-height: 1.6;
        background: white;
    }
    h1 { font-size: 28px; color: #0f172a; margin-bottom: 5px; border-bottom: 3px solid #3b82f6; padding-bottom: 10px; }
    h2 { font-size: 16px; color: #3b82f6; margin-top: 25px; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px; }
    h3 { font-size: 14px; color: #334155; margin-top: 10px; }
    p { font-size: 13px; color: #475569; margin-bottom: 8px; }
    ul { padding-left: 20px; margin-bottom: 10px; }
    li { font-size: 13px; color: #475569; margin-bottom: 4px; }
    .contact-info { font-size: 12px; color: #64748b; margin-bottom: 20px; }
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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Inter', sans-serif;
        color: #1e293b;
        padding: 50px 60px;
        line-height: 1.8;
        background: white;
    }
    h1 { font-size: 22px; color: #0f172a; text-align: center; margin-bottom: 30px; text-transform: uppercase; letter-spacing: 2px; }
    h2 { font-size: 14px; color: #0f172a; margin-top: 20px; margin-bottom: 8px; text-transform: uppercase; }
    h3 { font-size: 13px; color: #334155; margin-top: 10px; font-weight: 600; }
    p { font-size: 13px; color: #334155; margin-bottom: 10px; text-align: justify; }
    ul { padding-left: 25px; margin-bottom: 10px; }
    li { font-size: 13px; color: #334155; margin-bottom: 4px; }
    .signatures { margin-top: 60px; display: flex; justify-content: space-between; }
    .signature-line { width: 200px; border-top: 1px solid #0f172a; padding-top: 5px; text-align: center; font-size: 12px; }
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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Inter', sans-serif;
        color: #1e293b;
        padding: 40px 50px;
        line-height: 1.7;
        background: white;
    }
    h1 { font-size: 24px; color: #0f172a; margin-bottom: 5px; }
    .report-meta { font-size: 12px; color: #64748b; margin-bottom: 30px; border-bottom: 2px solid #3b82f6; padding-bottom: 15px; }
    h2 { font-size: 16px; color: #1e40af; margin-top: 25px; margin-bottom: 10px; }
    h3 { font-size: 14px; color: #334155; margin-top: 12px; }
    p { font-size: 13px; color: #475569; margin-bottom: 10px; text-align: justify; }
    ul { padding-left: 20px; margin-bottom: 10px; }
    li { font-size: 13px; color: #475569; margin-bottom: 4px; }
    table { width: 100%; border-collapse: collapse; margin: 15px 0; }
    th { background: #1e40af; color: white; padding: 10px; font-size: 12px; text-align: left; }
    td { border: 1px solid #e2e8f0; padding: 8px; font-size: 12px; color: #475569; }
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
        await page.set_content(html_content, wait_until="domcontentloaded", timeout=60000)
        # Wait a brief moment for fonts to load, but don't block forever
        await page.wait_for_timeout(2000)
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
