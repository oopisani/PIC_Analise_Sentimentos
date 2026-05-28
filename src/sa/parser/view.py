"""Parser de argumentos CLI para geração de nuvens de palavras."""

from __future__ import annotations

from pathlib import Path

from sa.common import Parser, ParserNamespace

DEFAULT_SHEETS = ["posts"]
"""Abas tabulares base utilizadas quando nenhum `-s` é indicado ao acionar o processador do gráfico."""

DEFAULT_TOP_N = 20
"""Teto delimitante máximo gerado nas representações das Barras Analíticas de Plotagem."""


class WordCloudParser(Parser):
    """
    Parser adaptado para orquestração da camada de processamento visual Plt/WordCloud.

    Subclasse estendida provendo identificador base `sa-wordcloud` acoplada aos módulos
    de leitura local da arquitetura.
    """


class WordCloudParserNamespace(ParserNamespace):
    """
    Estruturação final de namespace garantindo a validação explícita no Mypy.

    Permite a interface interagir via auto-complete no IDE identificando Paths validados
    pela base ao invés das strings dinâmicas comuns ao módulo builtin.

    Attributes:
        input_path (Path): Path OS verificável com endereço real a aba lida.
        output_dir (Path): Pasta alocada para emissão dos PNGs/JPGs pós rendering.
        sheets (list[str]): Referência matriz indicando as planilhas extraídas individualmente.
        top_n (int): Delimitador algorítimo limitando top items renderizados da word cloud / charts.
        extras (Path | None): Referencia secundária ao stopwords.csv fornecido ao modelo via inject opcional.
    """

    input_path: Path
    output_dir: Path
    sheets: list[str]
    top_n: int
    extras: Path | None


def create_wordcloud_parser() -> WordCloudParser:
    """
    Assina a estipulação tipada do Parser gráfico.

    Agrega ao construtor da instância os nós `--sheets` `--target` e formata as
    dependências vitais limitantes pro pacote Matplotlib em tempo de bootstrap CLI.

    Returns:
        WordCloudParser: Configurado pronto com descrições das `--help` de modo técnico e opções setadas.
    """

    parser = WordCloudParser(
        prog="sa-wordcloud",
        description="Generates word clouds and frequency charts from post files.",
    )

    parser.add_argument(
        "-i",
        "--input-path",
        type=Path,
        required=True,
        help="Path of the input file containing the data (Excel or CSV).",
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        required=True,
        help="Path of the output directory for the generated images.",
    )

    parser.add_argument(
        "-s",
        "--sheets",
        type=str,
        nargs="+",
        default=DEFAULT_SHEETS,
        help=f"Name(s) of the sheet(s) to process, space-separated (default: {' '.join(DEFAULT_SHEETS)}).",
    )

    parser.add_argument(
        "-n",
        "--top-n",
        type=int,
        default=DEFAULT_TOP_N,
        help=f"Amount of most frequent words to display on the chart (default: {DEFAULT_TOP_N}).",
    )

    parser.add_argument(
        "-e",
        "--extras",
        type=Path,
        default=None,
        help="Path of the CSV file containing extra stopwords.",
    )

    return parser


def parse_wordcloud_args(argv: list[str] | None = None) -> WordCloudParserNamespace:
    """
    Lê o comando disparado e devolve instanciado na Namespace as resoluções da tela para o pipeline gráfico final.

    Ouve os eventos do prompt através de `create_wordcloud_parser` resolvendo tipificadamente em base de
    dados as orientações que nortearão todo processador visual sobre o corpus submetido.

    Args:
        argv (list[str] | None, optional): Parâmetro para simular chaves pelo shell ou pytest de forma programática.

    Returns:
        WordCloudParserNamespace: Coleção engessada dos subitens extraídos (List e Paths seguros).
    """

    parser = create_wordcloud_parser()

    return parser.parse_args(argv, namespace=WordCloudParserNamespace())
