# Executáveis CLI (script/)

Este diretório comporta os pontos de entrada (entrypoints) projetados para inicializar o sistema através do terminal ou console interativo.

## Comportamento Esperado

O propósito arquitetural absoluto desta camada é orquestrar a junção entre a interface com o usuário (CLI) e a infraestrutura subjacente do Core (`src/sa`). 
Espera-se que nenhum script aqui retenha regras lógicas, processamento matemático de linguagem ou regras rígidas sobre formatação tabular. 

A responsabilidade das execuções repousa puramente na:
- Capitação das diretrizes pelo usuário ("flags" como *--total*, *--idioma*).
- Inicialização dos conectores autênticos do fluxo (carregar `.env`, APIs, NLP).
- Tratamentos superficiais dos encerramentos ou interrupções.
- Delegação do processamento ao respectivo construtor interno.

## Scripts Disponíveis

Nesta pasta, estão os executáveis que movimentam todo o ecossistema. Consulte a documentação específica de cada script para conhecer suas flags, parâmetros obrigatórios e como invocar cada um corretamente via linha de comando:

- **[Conversor de Extensões (`convert.py`)](convert.md)**: Ferramenta de apoio para conversão de arquivos delimitados de texto e tabulares (`CSV` <-> `XLSX`).
- **[Crawler Coletor do Reddit (`reddit.py`)](reddit.md)**: Script principal para raspar os textos da plataforma usando APIs. Captura as sentenças em lotes padronizados e gera o Dataset original em base tabular para a análise.
- **[Renderizador Gráfico (`view.py`)](view.md)**: Consome as tabelas consolidadas, submete o texto final às bibliotecas de inteligência neural computacional (NLP/SpaCy) para retirar palavras inúteis e, finalmente gera Barcharts e Nuvens lexicais interativas no terminal.

## Instrução Geral
Todos os CLI interativos devem respeitar e ser invocados sob uma rotina que utilize a pasta raiz do repositório como principal Path para que o interpretador resolva o módulo nativo (`python -m script.NOME_SCRIPT`). Respeite as tags `--help` fornecidas caso faltem mais detalhes durante o uso.
