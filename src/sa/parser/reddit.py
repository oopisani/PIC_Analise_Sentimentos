"""Parser de argumentos CLI para coleta de posts do Reddit."""

from __future__ import annotations

from sa.common import Parser, ParserNamespace

from pathlib import Path

from sa.file import FileFormat
from sa.model import Language

DEFAULT_SUBREDDIT = "conversas"
"""Nó padrão estipulado em caso de flag `--subreddits` ausente no console."""

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
        description="Coleta posts do Reddit filtrados por palavras-chave e exporta para arquivo.",
    )

    parser.add_argument(
        "-s",
        "--subreddits",
        type=str,
        nargs="+",
        default=[DEFAULT_SUBREDDIT],
        help=f"Subreddit(s) alvo da coleta, separados por espaço (default: {DEFAULT_SUBREDDIT}).",
    )

    parser.add_argument(
        "-k",
        "--keywords",
        type=str,
        nargs="+",
        required=True,
        help="Palavra(s)-chave alvo da coleta, separadas por espaço.",
    )

    parser.add_argument(
        "-l",
        "--language",
        type=Language,
        choices=[lang.value for lang in Language],
        default=DEFAULT_LANGUAGE.value,
        help=f"Idioma dos posts a serem coletados (default: {DEFAULT_LANGUAGE.value}).",
    )

    parser.add_argument(
        "-t",
        "--total",
        type=int,
        default=DEFAULT_TOTAL_PER_WORD,
        help=f"Limite máximo de posts coletados por palavra-chave (default: {DEFAULT_TOTAL_PER_WORD}).",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Caminho do arquivo de saída para os posts coletados.",
    )

    parser.add_argument(
        "-f",
        "--format",
        type=FileFormat,
        choices=[fmt.value for fmt in FileFormat],
        default=DEFAULT_OUTPUT_FORMAT.value,
        help=f"Formato desejado para o arquivo de saída (default: {DEFAULT_OUTPUT_FORMAT.value}).",
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
