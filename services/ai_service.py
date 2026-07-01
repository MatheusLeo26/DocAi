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
3. Todos os links devem ser clicáveis usando la tag <a> com target="_blank".
4. Organize a seção de contato horizontalmente ou em lista elegante logo abaixo do nome.

Use tags HTML para estruturar o conteúdo (h1, h2, h3, p, ul, li, etc). NÃO inclua tags <html>, <head> ou <body>.
IMPORTANTE: NÃO use formatação Markdown (como **texto**). Se precisar destacar algo, use as tags HTML apropriadas (como <strong>texto</strong>).
Retorne APENAS o HTML do conteúdo do currículo, sem explicações adicionais.

Informações do candidato:
{user_data}""",

    "resume_es": """Usted es un reclutador profesional y experto en recursos humanos. Su misión es actuar como un filtro riguroso, extrayendo, resumiendo y organizando la información proporcionada para crear el currículum ideal (enfocado en un máximo de 1.5 a 2 páginas).
Con base en la información proporcionada a continuación, genere un currículum profesional completo, bien estructurado, conciso y formateado en HTML EN ESPAÑOL.
El currículum debe seguir los estándares del mercado internacional, destacando únicamente lo que aporta valor real para el área del candidato.

DIRECTRICES DE OPTIMIZACIÓN Y FILTRADO (OBLIGATORIO):
1. Compactación de espacio: Formatee los títulos para ahorrar espacio vertical. Ejemplo: coloque el Cargo y la Empresa en la misma línea (ej: <strong>Cargo</strong> | Empresa).
2. Habilidades como etiquetas (tags): Transforme la sección de "Habilidades" en una lista de palabras clave cortas agrupadas por categoría (ej: Backend: Python, SQL; Herramientas: Playwright, Git). NUNCA use párrafos explicativos en las Habilidades para no repetir lo que ya está descrito en la experiencia profesional.
3. Orden de valor: Posicione la sección de "Proyectos" justo después de "Experiencia profesional". Los proyectos son fundamentales y deben tener prioridad antes de las certificaciones.
4. Filtro de relevancia (Cursos y Certificaciones): Actúe como un juez crítico. Mantenga ÚNICAMENTE las 4 o 5 certificaciones más relevantes, complejas o de mayor peso que validen las competencias del candidato. Elimine cursos genéricos, de muy corta duración o que parezcan estar allí solo para "hacer volumen".
5. Fusión de secciones menores: Combine las "Certificaciones" (ya filtradas) e "Idiomas" en una sola sección llamada "Información adicional" al final del currículum.

Si el usuario proporciona preferencias, directrices o datos adicionales en el campo "Sugerencias/Información adicional", asegúrese de incorporarlos y seguirlos fielmente en el currículum generado.

REGLAS OBLIGATORIAS PARA LA SECCIÓN DE CONTACTO:
1. Use iconos de FontAwesome antes de cada información de contacto. Ejemplos:
   - Correo electrónico: <i class="fas fa-envelope"></i> correo@ejemplo.com
   - Teléfono: <i class="fas fa-phone"></i> +55 11 99999-9999
   - LinkedIn: <i class="fab fa-linkedin"></i> <a href="URL_COMPLETA">URL_COMPLETA</a>
   - GitHub: <i class="fab fa-github"></i> <a href="URL_COMPLETA">URL_COMPLETA</a>
   - Portfólio/Sitio: <i class="fas fa-globe"></i> <a href="URL_COMPLETA">URL_COMPLETA</a>
   - Ciudad: <i class="fas fa-map-marker-alt"></i> Ciudad - Estado/País
2. NUNCA acorte ni resuma los enlaces. Muestre siempre la URL COMPLETA y EXACTA proporcionada por el usuario, tanto en el texto visible del enlace como en el atributo href.
3. Todos los enlaces deben ser cliqueables usando la etiqueta <a> con target="_blank".
4. Organice la sección de contacto horizontalmente o en una lista elegante justo debajo del nombre.

Use etiquetas HTML para estructurar el contenido (h1, h2, h3, p, ul, li, etc). NO incluya etiquetas <html>, <head> o <body>.
IMPORTANTE: NO use formato Markdown (como **texto**). Si necesita resaltar algo, use las etiquetas HTML apropiadas (como <strong>texto</strong>).
Devuelva ÚNICAMENTE el HTML del contenido del currículum, sin explicaciones adicionales. Todo el texto generado debe estar en español.

Información del candidato:
{user_data}""",

    "contract": """Você é um advogado especialista em contratos empresariais e civis.
Com base nas informações altamente estruturadas fornecidas abaixo, gere um contrato profissional completo, robusto, bem estruturado e formatado em HTML.
O contrato deve seguir os padrões legais brasileiros, com linguagem jurídica adequada.

DIRETRIZES OBRIGATÓRIAS:
1. Siga exatamente o "Modelo de Contrato" especificado no topo das informações (ex: Prestação de Serviços, CLT, Freelancer, Sociedade).
2. Utilize PRECISAMENTE os dados de Contratante e Contratada fornecidos. Se uma parte for Pessoa Jurídica (PJ), insira os dados do Representante Legal e seu cargo na qualificação das partes. NÃO invente nomes ou documentos.
3. Se um "Foro de Eleição" for fornecido, crie a cláusula de Foro especificando essa cidade para dirimir quaisquer disputas judiciais.
4. ATENÇÃO ÀS CLÁUSULAS PADRONIZADAS: Se existirem "Cláusulas Padronizadas Selecionadas" nas informações (como Multa, IPCA, IGP-M, Non-compete, NDA), você DEVE redigir parágrafos jurídicos detalhados incorporando cada uma delas no corpo do contrato.
5. DETECÇÃO DE PEJOTIZAÇÃO (MITIGAÇÃO DE RISCO TRABALHISTA): Se você detectar que o contrato estabelece uma relação de prestação de serviços ou freelancer com características que possam assemelhar-se a um emprego tradicional (habitualidade, subordinação, dependência econômica) ou se a parte contratada for explicitamente qualificada como MEI (Microempreendedor Individual) ou Pessoa Física autônoma, você DEVE incluir automaticamente uma cláusula/seção robusta de "Declaração de Autonomia e Termo de Responsabilidade/Indenização Trabalhista". Esta cláusula deve isentar a Contratante de qualquer responsabilidade previdenciária ou trabalhista e estabelecer direito de regresso absoluto contra a Contratada caso a Contratante seja acionada na Justiça do Trabalho.
6. Incorpore também quaisquer orientações de "Sugestões Adicionais".

Use tags HTML para estruturar o conteúdo (h1, h2, h3, p, ul, li, etc). NÃO inclua tags <html>, <head> ou <body>.
IMPORTANTE: NÃO use formatação Markdown (como **texto**). Se precisar destacar algo, use as tags HTML apropriadas (como <strong>texto</strong>).
Retorne APENAS o HTML do conteúdo do contrato pronto para impressão, sem explicações adicionais.

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
{user_data}""",

    "resume_en": """You are a professional recruiter and human resources expert. Your mission is to act as a strict filter, extracting, summarizing, and organizing the provided information to create the ideal resume (focused on a maximum of 1.5 to 2 pages).
Based on the information provided below, generate a complete, well-structured, lean, and HTML-formatted professional resume IN ENGLISH.
The resume should follow international market standards, highlighting only what adds real value to the candidate's field.

OPTIMIZATION AND FILTERING GUIDELINES (MANDATORY):
1. Space Compaction: Format titles to save vertical space. Example: put Title and Company on the same line (e.g., <strong>Title</strong> | Company).
2. Skills as Tags: Transform the "Skills" section into a list of short keywords grouped by category (e.g., Backend: Python, SQL; Tools: Playwright, Git). NEVER use explanatory paragraphs in Skills to avoid repeating what is already described in professional experience.
3. Value Ordering: Position the "Projects" section right after "Professional Experience". Projects are fundamental and should have prominence before certifications.
4. Relevance Filter (Courses and Certifications): Act as a critical judge. Keep ONLY the 4 or 5 most relevant, complex, or weighty certifications that validate the candidate's competencies. Remove generic, very short-duration courses or those that seem to be there just to "make volume".
5. Fusion of Smaller Sections: Combine "Certifications" (already filtered) and "Languages" into a single section called "Additional Information" at the end of the resume.

If the user provides preferences, guidelines, or extra data in the "Suggestions/Additional Information" field, be sure to incorporate and follow them faithfully in the generated resume.

MANDATORY RULES FOR THE CONTACT SECTION:
1. Use FontAwesome icons before each contact information. Examples:
   - Email: <i class="fas fa-envelope"></i> email@example.com
   - Phone: <i class="fas fa-phone"></i> +55 11 99999-9999
   - LinkedIn: <i class="fab fa-linkedin"></i> <a href="FULL_URL">FULL_URL</a>
   - GitHub: <i class="fab fa-github"></i> <a href="FULL_URL">FULL_URL</a>
   - Portfolio/Website: <i class="fas fa-globe"></i> <a href="FULL_URL">FULL_URL</a>
   - City: <i class="fas fa-map-marker-alt"></i> City - State/Country
2. NEVER shorten or summarize links. Always display the EXACT FULL URL provided by the user, both in the visible link text and in the href attribute.
3. All links must be clickable using the <a> tag with target="_blank".
4. Organize the contact section horizontally or in an elegant list just below the name.

Use HTML tags to structure the content (h1, h2, h3, p, ul, li, etc). DO NOT include <html>, <head> or <body> tags.
IMPORTANT: DO NOT use Markdown formatting (like **text**). If you need to highlight something, use the appropriate HTML tags (like <strong>text</strong>).
Return ONLY the HTML of the resume content, without additional explanations. All generated text must be in English.

Candidate information:
{user_data}"""
}

def generate_content(doc_type, user_data, image_paths=None):
    """Generate professional HTML content using Gemini API if configured, otherwise fallback to Ollama."""
    mapped_type = doc_type
    if doc_type in ['resume_modern', 'resume_minimalist']:
        mapped_type = 'resume'
    elif doc_type in ['resume_modern_en', 'resume_minimalist_en']:
        mapped_type = 'resume_en'
    elif doc_type in ['resume_modern_es', 'resume_minimalist_es']:
        mapped_type = 'resume_es'

    prompt_template = PROMPTS.get(mapped_type)
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

