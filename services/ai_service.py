import requests
import json
import os

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "llama3.2:latest"

PROMPTS = {
    "resume": """Você é um especialista em recursos humanos e currículos profissionais.
Com base nas informações fornecidas abaixo, gere um currículo profissional completo, bem estruturado e formatado em HTML.
O currículo deve seguir os padrões do mercado brasileiro, com linguagem formal e objetiva.
Use tags HTML para estruturar o conteúdo (h1, h2, h3, p, ul, li, etc). NÃO inclua tags <html>, <head> ou <body>.
Retorne APENAS o HTML do conteúdo do currículo, sem explicações adicionais.

Informações do candidato:
{user_data}""",

    "contract": """Você é um advogado especialista em contratos empresariais e civis.
Com base nas informações fornecidas abaixo, gere um contrato profissional completo, bem estruturado e formatado em HTML.
O contrato deve seguir os padrões legais brasileiros, com cláusulas claras e linguagem jurídica adequada.
Inclua todas as cláusulas essenciais: objeto, obrigações das partes, prazo, valor, rescisão, foro, etc.
Use tags HTML para estruturar o conteúdo (h1, h2, h3, p, ul, li, etc). NÃO inclua tags <html>, <head> ou <body>.
Retorne APENAS o HTML do conteúdo do contrato, sem explicações adicionais.

Informações do contrato:
{user_data}""",

    "report": """Você é um analista profissional especializado em relatórios corporativos.
Com base nas informações fornecidas abaixo, gere um relatório profissional completo, bem estruturado e formatado em HTML.
O relatório deve seguir os padrões corporativos, com linguagem formal, dados organizados e conclusões claras.
Use tags HTML para estruturar o conteúdo (h1, h2, h3, p, ul, li, table, etc). NÃO inclua tags <html>, <head> ou <body>.
Retorne APENAS o HTML do conteúdo do relatório, sem explicações adicionais.

Informações do relatório:
{user_data}"""
}

def generate_content(doc_type, user_data):
    """Generate professional HTML content using Gemini API if configured, otherwise fallback to Ollama."""
    prompt_template = PROMPTS.get(doc_type)
    if not prompt_template:
        raise ValueError(f"Tipo de documento inválido: {doc_type}")

    prompt = prompt_template.format(user_data=user_data)
    
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            # Remove markdown block enclosures if Gemini returns them
            text = response.text.strip()
            if text.startswith("```html"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            return text.strip()
        except Exception as e:
            # If Gemini fails, log or fall through to Ollama fallback
            print(f"Erro ao usar Gemini, tentando Ollama: {e}")

    # Fallback to Ollama
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 4096
            }
        }, timeout=120)

        if response.status_code == 200:
            result = response.json()
            return result.get("response", "")
        else:
            raise Exception(f"Ollama error: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        raise Exception("Não foi possível conectar ao Gemini (sem chave GEMINI_API_KEY) ou ao Ollama. Verifique se o Ollama está rodando ou defina GEMINI_API_KEY.")

