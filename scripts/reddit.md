# Reddit Crawler (`reddit.py`)

Script responsável por instanciar a "Raspagem Web" ou Crawler e alocar autenticações OAuth via credenciais para iterar ativamente em subcomunidades abertas da biblioteca externa PRAW extraindo os lexos e sentenças em lotes padronizados.

## Papel no Sistema

Ele é a mola motriz de aquisição dos dados em fase zero. Age centralizando conexões e atuando no disparo de extração subjacente (`collector`). O script se apoia e coordena bibliotecas inteiras do backend para iniciar a mineração web dos Lexos, enviando diretivas como Idioma obrigatório e limites alocados para impedir furos de paginação do provedor da rede social. Trata-se do disparador fundamental da Engine de Engenharia de Dados antes do processamento de base estatística ocorrer.

## Comportamento

Captura variáveis sensíveis ambientais (`.env`) secretamente protegidas, passa adiante a injeção do token restrito aos construtores `Client`, abre comunicações rastreadas em sistema com a injeção dos "Loggers" estritos de cada sub-rede rastreada e esgota/esvazia via pipeline em formatos tabulares ou iteráveis Array baseando suas lógicas primárias numa tabela de Polarity injetável e iterável, para finalmente registrar todas alocações no formato XLSX ou CSV demandado pelo executor CLI.

## Exemplo de Uso

Execução direta via módulo Python na raiz do repositório:

```bash
python -m script.reddit -s conversas brasil desabafos -k linux python programacao -l pt -t 10000 -o extracao_dataset.xlsx -f xlsx
```

## Parâmetros e Flags Suportados

| Flag Curta | Flag Estendida |  Tipo Suportado   | Obrigatório |  Valor Padrão   | Propósito / Descrição                                                                                |
| :--------: | :------------- | :---------------: | :---------: | :-------------: | :--------------------------------------------------------------------------------------------------- |
|    `-s`    | `--subreddits` |    $n$ Strings    |     Não     | `["conversas"]` | Nome da comunidade-alvo sendo batida na mineração (pode ser mais de uma).                            |
|    `-k`    | `--keywords`   |    $n$ Strings    |   **Sim**   |        -        | Palavra(s)-chave alvo a serem pesquisadas diretamente na coleta de dados.                            |
|    `-l`    | `--language`   |  Enum `Language`  |     Não     |      `pt`       | Identificador que barra dados sujos em idiomas aleatórios. Suporta ISO `(pt, en, es)`.               |
|    `-t`    | `--total`      |      Inteiro      |     Não     |     `50000`     | Contador teto que mata processo impedindo o raspador exceder as margens do provedor.                 |
|    `-o`    | `--output`     |      OS Path      |   **Sim**   |        -        | Destino consolidado amparando os hashes, textos brutos limpos e categorias prontas.                  |
|    `-f`    | `--format`     | Enum `FileFormat` |     Não     |     `xlsx`      | Designador da engine que irá abstrair listagens de dados (ex. pandas para gerar um excel analítico). |
