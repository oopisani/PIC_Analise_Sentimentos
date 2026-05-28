# Arquitetura do Sistema: Análise de Sentimentos em Redes Sociais

Este documento detalha as decisões arquiteturais, padrões de design e o fluxo de dados do projeto de Análise de Sentimentos em Redes Sociais. O objetivo é fornecer aos desenvolvedores e mantenedores uma visão de como as diferentes camadas da aplicação interagem e onde cada responsabilidade reside.

## 1. Princípios e Visão Geral

A arquitetura foi projetada com foco em **Modularidade**, **Desacoplamento** e **Forte Tipagem**. Baseia-se em conceitos de Clean Architecture e separação em camadas estruturais, garantindo que as mudanças em uma biblioteca de terceiros (como a troca da API do Reddit ou do gerador de Nuvem de Palavras) não afetem as lógicas fundamentais do domínio e do processamento léxico (NLP).

## 2. Mapa Estrutural (Camadas)

O projeto é dividido fundamentalmente em duas grandes macro-áreas: os **Entrypoints (Scripts)** e o **Core Analysis (`src/sa`)**.

```text
reddit-sentiment-analysis/
├── scripts/                  <-- Entrypoints CLI (Apresentação / Invocação)
│   ├── reddit.py             (Dispara Coleta)
│   ├── view.py               (Dispara Visualização/NLP)
│   └── convert.py            (Dispara Conversão de Arquivos)
│
└── src/sa/                   <-- Core Domain & Infrastructure
    ├── client/               (Adaptadores de Infra: API Externa)
    ├── collector/            (Orquestração e Regras de Extração)
    ├── common/               (Contratos/Interfaces Base)
    ├── file/                 (Infraestrutura de Persistência)
    ├── logger/               (Cross-cutting: Telemetria e Eventos)
    ├── model/                (Enums, TypedDicts, Tipos Base)
    ├── nlp/                  (Motor Analítico Lexical)
    ├── parser/               (Infraestrutura de CLI)
    └── visualization/        (Motores de Renderização)
```

### 2.1. Diagrama de Relacionamentos (Grafo de Dependências)

O seguinte diagrama ilustra o fluxo de dependências entre as camadas, organizado da esquerda para a direita. As dependências fluem sempre em direção ao domínio central (`common/`, `model/`), respeitando os princípios de Clean Architecture — camadas externas dependem das internas, nunca o contrário:

```mermaid
flowchart LR
    subgraph L1 ["Entrypoints"]
        REDDIT["scripts/reddit.py\n━━━━━━━━━━━━━━\nColeta Reddit"]
        VIEW["scripts/view.py\n━━━━━━━━━━━━━━\nVisualização"]
        CONVERT["scripts/convert.py\n━━━━━━━━━━━━━━\nConversão"]
    end

    subgraph L2 ["CLI Infrastructure"]
        PARSER["sa/parser/\n━━━━━━━━━━━━━━\nArgparse + Validators"]
    end

    subgraph L3 ["Orchestration"]
        COLLECTOR["sa/collector/\n━━━━━━━━━━━━━━\nRedditCollector"]
        NLP["sa/nlp/\n━━━━━━━━━━━━━━\nLemmatizer / Stopwords"]
        VIS["sa/visualization/\n━━━━━━━━━━━━━━\nWordCloud / Barchart"]
    end

    subgraph L4 ["Adapters"]
        CLIENT["sa/client/\n━━━━━━━━━━━━━━\nPRAW OAuth Client"]
        FILE["sa/file/\n━━━━━━━━━━━━━━\nCSV / XLSX Savers"]
    end

    subgraph L5 ["Domain Core"]
        COMMON["sa/common/\n━━━━━━━━━━━━━━\nABCs & Contracts"]
        MODEL["sa/model/\n━━━━━━━━━━━━━━\nEnums & Data Types"]
        LOGGER["sa/logger/\n━━━━━━━━━━━━━━\nTelemetry & Events"]
    end

    %% Entrypoints → CLI + Orchestrators + Adapters
    REDDIT --> PARSER
    REDDIT --> COLLECTOR
    REDDIT --> CLIENT
    REDDIT --> FILE

    VIEW --> PARSER
    VIEW --> NLP
    VIEW --> VIS
    VIEW --> FILE

    CONVERT --> PARSER
    CONVERT --> FILE

    %% Parser → Core
    PARSER --> COMMON
    PARSER --> MODEL

    %% Orchestration → Adapters + Core
    COLLECTOR --> CLIENT
    COLLECTOR --> COMMON
    COLLECTOR --> MODEL
    COLLECTOR --> LOGGER

    NLP --> MODEL

    VIS --> COMMON
    VIS --> MODEL
    VIS --> LOGGER

    %% Adapters → Core
    CLIENT --> COMMON
    CLIENT --> MODEL

    FILE --> COMMON
    FILE --> MODEL

    %% Core internal
    COMMON --> MODEL
    COMMON --> LOGGER
```

## 3. Descrição Detalhada dos Componentes

### 3.1. CLI e Argument Parsers (`scripts/` & `src/sa/parser/`)

Os scripts localizados em `scripts/` funcionam estritamente como montadores de dependências (_Composition Roots_). Eles leem as variáveis de ambiente, invocam o `parser/` para transformar simples strings do terminal em instâncias de forte tipagem (`Path`, `FileFormat`, `Language`), instanciam classes concretas e engatilham os objetos orquestradores. A inteligência e regras de validação CLI vivem no `parser/`, isolando os scripts em `scripts` do resto do domínio.

### 3.2. Models e Core Domain (`model/`)

A espinha dorsal de dados. Fornece tipos como `Language`, `Polarity`, `PostRecord`. Tudo no sistema flui ao redor destas estruturas. Elas não dependem de ninguém, mas todos dependem delas.

### 3.3. Contratos e Interfaces (`common/`)

Centraliza os contratos formais do sistema por meio de Classes Base Abstratas (ABCs), definindo explicitamente o "quê" deve ser executado, sem impor detalhes de implementação. Essa camada estabelece fronteiras claras entre domínio e infraestrutura, garantindo baixo acoplamento, substituibilidade e previsibilidade comportamental nas operações de leitura e escrita.

#### 3.3.1. Adaptadores de Infraestrutura Externa (`client/`)

Esta é a camada anti-corrupção (ACL) contra ferramentas externas. Esse pacote encobre a comunicação com os serviços de redes sociais, autenticações e paginações pesadas da web, entregando ao resto do sistema uma sessão agnóstica e autenticada.

#### 3.3.2. Orquestração de Coleta (`collector/`)

Recebe a instância de cliente já configurada e autenticada, as regras de busca (palavras-chave definidas por dicionário estrito, limite total de requisições e idioma alvo) e coordena integralmente o fluxo de paginação, respeitando limites e critérios de encerramento. Realiza validação prévia para garantir idempotência, prevenir duplicidade e manter rastreabilidade. Atua como um funil orgânico de extração bruta, consolidando apenas dados válidos e estruturalmente íntegros para as camadas subsequentes, sem incorporar regras de negócio ou enriquecimento semântico.

#### 3.5.3. Implementações de Arquivo (`file/`)

Responsável pelo "como" da persistência. Implementa os contratos de arquivo definidos em `common/` para manipulação tabular, leitura e escrita de metadados e planilhas estruturadas.

### 3.4. Motor Natural Language Processing (`nlp/`)

Representa o núcleo matemático de destilação semântica do sistema, responsável por transformar texto bruto e ruidoso (ex.: `Hoje eu estou mto feliz kk #dia`) em estrutura linguística normalizada e analiticamente útil.

Executa um pipeline monolítico de higienização que remove ruídos sintáticos (como repetições informais do tipo `kk`), elimina numerais irrelevantes, normaliza símbolos e converte emojis em suas descrições textuais equivalentes, reduzindo ambiguidade semântica. Em seguida, invoca operações para realizar **tokenização** e **lematização** agressivas, garantindo redução morfológica consistente.

O tratamento de **stop words** ocorre em duas camadas complementares: uma dinâmica, configurável pelo analista via `.csv`, e outra estrutural, herdada das bibliotecas gramaticais externas, assegurando flexibilidade sem comprometer rigor linguístico.

### 3.5. Renderização e View (`visualization/`)

É um consumidor terminal (Sincronizado via subgrupos de CLI). Não afeta o percurso natural dos DataFrames. Recebe uma contagem purificada já processada pelo pacote NLP e injeta instâncias dentro do back-end "Agg" do `matplotlib` (Headless/sem janelas interativas gráficas). Delega a geração final de nuvens para instâncias customizadas de interface WordCloud e gráficos barchart para eixos em disco (`.png`).

## 4. Fluxo de Execução Simplificado (Data Flow)

Um exemplo clássico do percurso percorrido quando o script de Coleta Inicia a extração:

1. **Invocação (CLI):** O usuário invoca `python ./scripts/reddit ...`. O Parser valida e retorna um Namespace.
2. **Setup:** O Factory instancia o Client (`client`) do Reddit a partir das variáveis de ambiente.
3. **Extração:** O `RedditCollector` é atrelado e assume a transação. Iterará sobre Subreddits listados.
4. **Verificação (Sub-Rotina NLP):** Enquanto colhe os dados puros, testa estocásticamente o conteúdo usando o avaliador natural de Idioma de NLP. O ignorado morre aqui.
5. **Estruturação:** Informações extraídas via generator preenchem o modelo de domínio (`sa.model`) purificado.
6. **Persistência I/O:** Baseado na Flag, o construtor instancia um Driver de Disco (ex: `XLSXPostSaver`) que absorve todos itens e conclui extrações pro disco.
