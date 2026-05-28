# Renderizador Gráfico CLI (`view.py`)

Ponto de término visual da engine atuando sobre a extração lexical formatada. O script interage com os dataframes resultantes da máquina gerando gráficos cartesianos de incidência absoluta numérico (Barchart) e Nuvens Dinâmicas Plotáveis via Matplotlib.

## Papel no Sistema

Responsável por viabilizar estatísticas em interfaces compreensíveis para serem avaliados e apresentados por negócio ao redor de pesquisas orientadas a produto ou sociologia. O script consolida as etapas de "limpeza neural" englobando dicionários de stop-words customizados interligando-se à biblioteca de SpaCy (NLP nativo Python C) de forma encadeada de cima à baixo e, repassa esses vetores higienizados não repetitivos ao gerador gráfico instanciador, traduzindo sentimentos matemáticos densos em mídias imagéticas exportáveis `PNG`.

## Comportamento

Verifica inicialmente a robustez de recebimento do Arquivo lido (tabelas lidas via Path nativo cruzando os enums). Engatilha matriz de Stop-words com CSV via injeção customizada, sobe alocadores em RAM limitantes como "core_news_lg" no SpaCy e iterando cada aba tabular "lê, suprime stopwords inúteis (com Lematização restritiva ADJ/NOUN)" computando aglomerados vetoriais lexos e esgotando a base contada iterativa perante drivers estritos de plotagem sem gerar janelas em interface ativa num processo perfeitamente contínuo via backend CLI (headless map generation).

## Exemplo de Uso

Execução direta via módulo Python na raiz do repositório:

```bash
python -m script.view -i extracao_dataset.xlsx -o output_graficos/ -s posts -n 20 -e extra_stopwords.csv
```

## Parâmetros e Flags Suportados

| Flag Curta | Flag Estendida | Tipo Suportado | Obrigatório | Valor Padrão | Propósito / Descrição                                                                                                                       |
| :--------: | :------------- | :------------: | :---------: | :----------: | :------------------------------------------------------------------------------------------------------------------------------------------ |
|    `-i`    | `--input-path` |   File Path    |   **Sim**   |      -       | Direciona o banco de dados/planilha estéril consolidado pela máquina que será mapeado.                                                      |
|    `-o`    | `--output-dir` |  Folder Path   |   **Sim**   |      -       | Pasta vazia pronta pra encher com extensões gráficas (`.PNG` das Nuvens/Charts).                                                            |
|    `-s`    | `--sheets`     |  $n$ Strings   |     Não     | `["posts"]`  | Amarra o algoritmo plotador unicamente às seções de interesse delimitadas em abas do Dataset Excel.                                         |
|    `-n`    | `--top-n`      |    Inteiro     |     Não     |     `20`     | Delimitante matemático (teto inferior) das maiores concentrações de léxicos, definindo a abrangência plotada Matplotlib.                    |
|    `-e`    | `--extras`     |   File Path    |     Não     |    `None`    | Fornecimento aditivo dinâmico: Manda planilhas com dicionários adicionais injetáveis de "Palavras a se suprimir" que afetam o parser `NLP`. |
