import requests
import json
import os
import re

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "llama3.2:latest"

PROMPTS = {
    "resume": """Você é um recrutador profissional e especialista em recursos humanos. Sua missão é atuar como um filtro rigoroso, extraindo, resumindo e organizando as informações fornecidas para criar o currículo ideal (focado no máximo em 1.5 a 2 páginas).
Com base nas informações fornecidas abaixo, gere um currículo profissional completo, bem estruturado, enxuto e formatado em HTML.
O currículo deve seguir os padrões do mercado brasileiro, destacando apenas o que agrega real valor para a área do candidato.

DIRETRIZES DE OTIMIZAÇÃO E FILTRAGEM (OBRIGATÓRIO):
1. Compactação de Espaço: Formate títulos para economizar espaço vertical. Exemplo: coloque Cargo e Empresa na mesma linha (ex: <strong>Cargo</strong> | Empresa).
2. Habilidades como Tags: Transforme a seção de "Habilidades" em uma lista de palavras-chave curtas agrupadas por categoria (ex: Backend: Python, SQL; Ferramentas: Playwright, Git). NUNCA use parágrafos explicativos nas Habilidades para não repetir o que já está descrito na experiência profissional.
3. Ordenação de Valor: Posicione a seção de "Projetos" logo após a "Experiência Profissional". Projetos são fundamentais e devem ter destaque antes das certificações.
4. Filtro de Relevância (Cursos e Certificações): Atue como um julgador crítico. Mantenha APENAS as 4 ou 5 certificações mais relevantes, complexas ou de maior peso que validam as competências do candidato. Remova cursos genéricos, de curtíssima duração ou que parecem estar ali apenas para "fazer volume".
5. Fusão de Seções Menores: Combine as "Certificações" (já filtradas) e "Idiomas" em uma seção única chamada "Informações Adicionais" no final do currículo.

Se o usuário fornecer preferências, diretrizes ou dados extras no campo "Sugestões/Informações Adicionais", certifique-se de incorporá-los e segui-los fielmente no currículo gerado.

REGRAS OBRIGATÓRIAS PARA A SEÇÃO DE CONTATO:
1. Use ícones FontAwesome antes de cada informação de contato. Exemplos:
   - Email: <i class="fas fa-envelope"></i> email@exemplo.com
   - Telefone: <i class="fas fa-phone"></i> (11) 99999-9999
   - LinkedIn: <i class="fab fa-linkedin"></i> <a href="URL_COMPLETA">URL_COMPLETA</a>
   - GitHub: <i class="fab fa-github"></i> <a href="URL_COMPLETA">URL_COMPLETA</a>
   - Portfólio/Site: <i class="fas fa-globe"></i> <a href="URL_COMPLETA">URL_COMPLETA</a>
   - Cidade: <i class="fas fa-map-marker-alt"></i> Cidade - UF
2. NUNCA encurte ou resuma links. Sempre exiba a URL COMPLETA e EXATA fornecida pelo usuário, tanto no texto visível do link quanto no atributo href.
3. Todos os links devem ser clicáveis usando a tag <a> com target="_blank".
4. Organize a seção de contato horizontalmente ou em lista elegante logo abaixo do nome.

Use tags HTML para estruturar o conteúdo (h1, h2, h3, p, ul, li, etc). NÃO inclua tags <html>, <head> ou <body>.
IMPORTANTE: NÃO use formatação Markdown (como **texto**). Se precisar destacar algo, use as tags HTML apropriadas (como <strong>texto</strong>).
Retorne APENAS o HTML do conteúdo do currículo, sem explicações adicionais.

Informações do candidato:
{user_data}""",

    "contract": """Você é um advogado especialista em contratos empresariais e civis.
Com base nas informações fornecidas abaixo, gere um contrato profissional completo, bem estruturado e formatado em HTML.
O contrato deve seguir os padrões legais brasileiros, com cláusulas claras e linguagem jurídica adequada.
Inclua todas as cláusulas essenciais: objeto, obrigações das partes, prazo, valor, rescisão, foro, etc.

Se o usuário fornecer preferências, cláusulas específicas ou diretrizes extras no campo "Sugestões/Informações Adicionais", certifique-se de incorporá-las e segui-los fielmente no contrato gerado.

Use tags HTML para estruturar o conteúdo (h1, h2, h3, p, ul, li, etc). NÃO inclua tags <html>, <head> ou <body>.
IMPORTANTE: NÃO use formatação Markdown (como **texto**). Se precisar destacar algo, use as tags HTML apropriadas (como <strong>texto</strong>).
Retorne APENAS o HTML do conteúdo do contrato, sem explicações adicionais.

Informações do contrato:
{user_data}""",

    "report": """Você é um analista profissional especializado em relatórios corporativos.
Com base nas informações fornecidas abaixo, gere um relatório profissional completo, bem estruturado e formatado em HTML.
O relatório deve seguir os padrões corporativos, com linguagem formal, dados organizados e conclusões claras.

Se o usuário fornecer preferências, diretrizes de análise ou dados extras no campo "Sugestões/Informações Adicionais", certifique-se de incorporá-los e segui-los fielmente no relatório gerado.

Use tags HTML para estruturar o conteúdo (h1, h2, h3, p, ul, li, table, etc). NÃO inclua tags <html>, <head> ou <body>.
IMPORTANTE: NÃO use formatação Markdown (como **texto**). Se precisar destacar algo, use as tags HTML apropriadas (como <strong>texto</strong>).
Retorne APENAS o HTML do conteúdo do relatório, sem explicações adicionais.

Informações do relatório:
{user_data}"""
}

def generate_content(doc_type, user_data, image_paths=None):
    """Generate professional HTML content using Gemini API if configured, otherwise fallback to Ollama."""
    prompt_template = PROMPTS.get(doc_type)
    if not prompt_template:
        raise ValueError(f"Tipo de documento inválido: {doc_type}")

    prompt = prompt_template.format(user_data=user_data)
    
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        try:
            import google.generativeai as genai
            from PIL import Image
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            contents = []
            if image_paths:
                contents.append("Por favor, leia atentamente as imagens anexadas e utilize as informações contidas nelas para complementar, preencher e aprimorar os dados textuais fornecidos abaixo.\n\n")
                for img_path in image_paths:
                    if os.path.exists(img_path):
                        contents.append(Image.open(img_path))
            
            contents.append(prompt)
            
            response = model.generate_content(contents)
            # Remove markdown block enclosures if Gemini returns them
            text = response.text.strip()
            if text.startswith("```html"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            
            # Remove possible Markdown formatting
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
            
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
            text = result.get("response", "")
            
            # Remove possible Markdown formatting
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
            
            return text.strip()
        else:
            raise Exception(f"Ollama error: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        raise Exception("Não foi possível conectar ao Gemini (sem chave GEMINI_API_KEY) ou ao Ollama. Verifique se o Ollama está rodando ou defina GEMINI_API_KEY.")

