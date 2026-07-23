# DocAi 

DocAi é um ecossistema completo para geração inteligente de documentos assistida por Inteligência Artificial (Ollama - Llama 3.2) e conversão de arquivos em múltiplos formatos (incluindo conversão profissional para o padrão arquivístico **PDF/A**). 

Este projeto é composto por:
1. **DocAi Server & Web**: API e interface web desenvolvida em Flask (Python).
2. **DocAi Mobile**: Aplicativo para dispositivos móveis desenvolvido em Dart/Flutter com menu retrátil e interface adaptativa.

---

##  Funcionalidades

###  Geração de Documentos por IA
Gere documentos profissionais estruturados em segundos. O ecossistema envia dados brutos à IA local (Ollama) ou Gemini para a redação formal e gera PDFs diagramados via Playwright.
*   **Currículos (Resumes)**: Agora com **Filtro e Otimização Inteligente de Recrutamento (ATS/Recruiter Friendly)** que compacta o layout vertical, remove excesso de cursos de baixo impacto (limita às 4-5 certificações mais relevantes), agrupa habilidades em formato de tags categorizadas (sem repetir conteúdo da experiência) e prioriza a seção de projetos e portfólio no topo.
*   **Contratos Empresariais (Contracts)**
*   **Relatórios Corporativos (Reports)**

###  Visualização Nativa e Biblioteca
*   **Biblioteca de Arquivos**: Gerencie seus documentos gerados (baixar ou excluir de forma dinâmica sem necessidade de recarregar a página, com interface SweetAlert2).
*   **Pré-visualização**: Visualize os PDFs gerados diretamente na página da aplicação web através de um modal integrado, sem precisar fazer o download prévio do arquivo.

###  Conversor de Arquivos Inteligente
Converta arquivos de forma local no servidor ou aplicativo móvel.
*   **DOCX** ➔ **PDF** (mantendo cabeçalhos e formatações).
*   **Imagens** (PNG, JPG, JFIF) ➔ Múltiplos formatos alternativos.
*   **PDF** ➔ **PDF/A-3b** (Conformidade com os padrões ISO de arquivamento de longo prazo).

---

##  Tecnologias Utilizadas

### Backend & Web
*   **Python 3**
*   **Flask** (Gerenciamento de API e Rotas)
*   **SQLAlchemy & SQLite** (Persistência de Metadados)
*   **Flask-JWT-Extended** (Autenticação Segura)
*   **Playwright** (Renderização HTML para PDF síncrona/assíncrona)
*   **pdftopdfa & pikepdf** (Conversão estrutural para o padrão PDF/A)
*   **Ollama (Llama 3.2)** (Geração de Conteúdo Inteligente)

### Mobile Application
*   **Dart & Flutter**
*   **Navigation Side Drawer** (Menu retrátil responsivo para otimização de tela)
*   **Http Client** (Integração com a API Flask)
*   **File Picker** (Interface nativa de seleção de arquivos do celular)

---

##  Como Executar o Projeto

### 1. Requisitos Prévios
*   [Python 3.10+](https://www.python.org/)
*   [Flutter SDK](https://flutter.dev/)
*   [Ollama](https://ollama.com/) instalado com o modelo `llama3.2:latest`.

---

### 2. Configurando o Servidor (Backend)
Entre na raiz do projeto e execute os passos a seguir:

1. Crie e ative seu ambiente virtual:
   ```bash
   python -m venv venv
   # No Windows:
   .\venv\Scripts\activate
   # No Linux/macOS:
   source venv/bin/activate
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
   *Nota: Caso precise instalar manualmente as dependências principais:*
   ```bash
   pip install Flask Flask-SQLAlchemy Flask-JWT-Extended python-docx requests playwright pdftopdfa PyMuPDF
   ```
3. Inicialize os navegadores do Playwright (necessário para a renderização de PDF):
   ```bash
   playwright install
   ```
4. Certifique-se de que o Ollama está rodando localmente com o modelo correto:
   ```bash
   ollama run llama3.2
   ```
5. Inicie o servidor:
   ```bash
   python app.py
   ```
   O servidor estará disponível em `http://127.0.0.1:5000`.

---

### 3. Configurando o Aplicativo Mobile (Flutter)
Acesse a pasta `mobile/`:

1. Instale os pacotes e dependências:
   ```bash
   flutter pub get
   ```
2. Execute o app em um emulador ou dispositivo conectado:
   ```bash
   flutter run
   ```
   *Nota: Por padrão, o app conecta-se ao IP `http://10.0.2.2:5000` para compatibilidade com o emulador Android. Para testar em dispositivos físicos, altere a variável `baseUrl` em `mobile/lib/services/api_service.dart` para o IP da sua máquina.*

---

##  Segurança (JWT & Cookies)
O ecossistema implementa boas práticas de segurança para o tráfego e armazenamento de credenciais de acordo com o cliente utilizado:

*   **Versão Web (Navegador)**: A autenticação utiliza **Cookies HttpOnly e Secure** (`access_token_cookie`). Os tokens JWT de sessão não são expostos nem armazenados no `LocalStorage`, mitigando vulnerabilidades de roubo de sessão via XSS (Cross-Site Scripting).
*   **Versão Mobile (Flutter)**: Utiliza autenticação do tipo `Bearer Token` fornecido no cabeçalho HTTP (`Authorization: Bearer <JWT>`) para as requisições REST, permitindo o armazenamento seguro local no dispositivo.
*   **Segredos de Ambiente**: Credenciais sensíveis e chaves de API nunca ficam expostas no código client-side.
