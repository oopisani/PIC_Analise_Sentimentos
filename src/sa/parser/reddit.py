"""Parser de argumentos CLI para coleta de posts do Reddit."""

from __future__ import annotations

from pathlib import Path

from sa.common import Parser, ParserNamespace
from sa.file import FileFormat
from sa.model import Language

DEFAULT_LANGUAGE = Language.PT
"""Variável de Linguagem Padrão base da busca do PRAW e NL."""

DEFAULT_OUTPUT_FORMAT = FileFormat.XLSX
"""Formato padrão estipulado em caso da flag omissa de exportação."""

DEFAULT_TOTAL_PER_WORD = 50000
"""Teto operacional máximo garantido (cap) por tópico analisado."""


class RedditParser(Parser):
    """
    Parser configurado unicamente para lidar com o script de coleta contínua da API (RedditCollector).

    Herda base argparse estendendo para alocar metadados descritivos durante debug.
    """


class RedditParserNamespace(ParserNamespace):
    """
    Estrutura que vincula forte tipagem nas propriedades do wrapper Namespace.

    Força restrições nas saídas originárias dos scripts de parse. Atende primáriamente as tipagens nativas do NLP
    sendo absorvidas a longo dos controladores de script (`sa-reddit`).

    Attributes:
        subreddits (list[str]): Coleção ordenada das strings (nomes de abas Reddit alvo) processadas em massa.
        keywords (list[str]): Lista de palavras-chave a serem pesquisadas no reddit.
        language (Language): Estrutura enumerador de filtragem (es, pt).
        total (int): Volume numérico int teto usado na função `limit`.
        output (Path): Path consolidado garantindo compatibilidade da saída.
        format (FileFormat): Sinalética rigorosa para driver interpretador (pandas: csv/xlsx).
        verbose (bool): Define a verbosidade do logger (DEBUG vs INFO).
    """

    subreddits: list[str]
    keywords: list[str]
    language: Language
    total: int
    output: Path
    format: FileFormat
    verbose: bool


def create_reddit_parser() -> RedditParser:
    """
    Cria e configura o subparser contendo as regras de CLI voltados para o Reddit API.

    Retorna o container ArgumentParser enriquecido das checagens necessárias como total de limites, linguage e
    destino do Path operando o `sys.argv`.

    Returns:
        RedditParser: Instancia não iniciada pronta processável com as flags (--total, --language).
    """

    parser = RedditParser(
        prog="sa-reddit",
        description="Collects Reddit posts filtered by keywords and exports them to a file.",
    )

    parser.add_argument(
        "-s",
        "--subreddits",
        type=str,
        nargs="+",
        required=True,
        help="Target subreddit(s) for collection, space-separated.",
    )

    parser.add_argument(
        "-k",
        "--keywords",
        type=str,
        nargs="+",
        required=True,
        help="Target keyword(s) for collection, space-separated.",
    )

    parser.add_argument(
        "-l",
        "--language",
        type=Language,
        choices=[lang.value for lang in Language],
        default=DEFAULT_LANGUAGE.value,
        help=f"Language of the posts to be collected (default: {DEFAULT_LANGUAGE.value}).",
    )

    parser.add_argument(
        "-t",
        "--total",
        type=int,
        default=DEFAULT_TOTAL_PER_WORD,
        help=f"Maximum limit of posts collected per keyword (default: {DEFAULT_TOTAL_PER_WORD}).",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Output file path for the collected posts.",
    )

    parser.add_argument(
        "-f",
        "--format",
        type=FileFormat,
        choices=[fmt for fmt in FileFormat],
        default=DEFAULT_OUTPUT_FORMAT,
        metavar=f"{{{','.join(fmt.value for fmt in FileFormat)}}}",
        help=f"Desired format for the output file (default: {DEFAULT_OUTPUT_FORMAT.value}).",
    )

    return parser


def parse_reddit_args(argv: list[str] | None = None) -> RedditParserNamespace:
    """
    Inicializa processamento CLI transformando input livre de String em Variáveis Fortes (Namespace Customizado).

    Lida com injeções isoladas de lista Python para facilitar injeção de Mock por TDD sem interações com o Terminal, ou assume terminal normal via PRAW/script local `sys.argv`.

    Args:
        argv (list[str] | None, optional): Parâmetro para simular chaves pelo shell ou pytest de forma programática.

    Returns:
        RedditParserNamespace: Atributos convertidos para sua classe raiz (Paths, Enums, Lists) protegidos por tipo.
    """

    parser = create_reddit_parser()

    return parser.parse_args(argv, namespace=RedditParserNamespace())
