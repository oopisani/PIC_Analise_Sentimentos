# Projeto de Iniciação Científica: Análise de Sentimentos em Redes Sociais

Este projeto consiste em um pipeline de extração, processamento e análise de textos provenientes da rede social Reddit, focado em categorizar e gerar métricas e recursos visuais sobre opiniões de usuários a respeito de tópicos pré-determinados.

A arquitetura foi pensada para ser modular, desacoplada e estrita, fornecendo forte tipagem, organização de dependências e previsibilidade desde a chamada na interface de terminal (CLI) até o momento da geração visual dos gráficos analisados.

## Executáveis CLI

Este projeto possui scripts de entrada estruturados na pasta `scripts/` que operam como o ponto inicial de contato para os analistas operacionais usarem as diversas vertentes criadas sob a infraestrutura. Consultar suas instruções individuais provê uma visão ampla dos comportamentos e restrições:

- [Conversor de Extensões (`scripts/convert.py`)](scripts/convert.md)
- [Crawler de Coleta NLP (`scripts/reddit.py`)](scripts/reddit.md)
- [Renderizador Gráfico de Sentimentos (`scripts/view.py`)](scripts/view.md)

## Instalação e Configuração

Para configurar o ambiente de desenvolvimento e preparar a extração e as plotagens localmente, siga os passos a seguir:

1. **Clone o repositório:**

   ```bash
   git clone https://github.com/brunapisanidev/PIC_Analise_Sentimentos.git
   cd PIC_Analise_Sentimentos
   ```

2. **Crie e ative um ambiente virtual (recomendado):**

   ```bash
   python3 -m venv .venv

   # No Linux/macOS
   source .venv/bin/activate

   # No Windows:
   .venv\Scripts\activate
   ```

3. **Instale as dependências essenciais e o pacote local:**
   O ecossistema utiliza bibliotecas pesadas de mineração, PRAW (Reddit API), NLP e plotagem de gráficos. A instalação do pacote local registrará os comandos executáveis (`sa-reddit`, `sa-view`, `sa-convert`) na sua interface:

   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

4. **Baixe o modelo do spaCy:**
   Por lidar ativamente com o idioma português (`pt_core_news_lg`) durante as limpezas de Lexo, o modelo neural deve ser baixado explicitamente:

   ```bash
   python3 -m spacy download pt_core_news_lg
   ```

5. **Ajuste de Variáveis de Ambiente:**
   Instancie o arquivo de variáveis copiando do modelo de exemplo:

   ```bash
   cp .env.example .env
   ```

   Abra o arquivo `.env` gerado e preencha as variáveis de acesso `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET` e `REDDIT_CLIENT_USERNAME` com seus tokens do Reddit Apps.\*

   Alternativamente, você pode exportar essas variáveis de ambiente diretamente no seu terminal ou ambiente de execução, sem a necessidade de criar o arquivo `.env` localmente:\*

   ```bash
   export REDDIT_CLIENT_ID='seu_client_id'
   export REDDIT_CLIENT_SECRET='seu_client_secret'
   export REDDIT_CLIENT_USERNAME='seu_client_username'
   ```
