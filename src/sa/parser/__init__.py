"""
Módulo de parsing de argumentos de linha de comando (CLI).

Fornece as classes base e módulos independentes para gerenciamento
de argumentos via terminal para diferentes scripts operacionais do sistema
(coleta, conversão de arquivos e geração visual).
"""

from .convert import ConverterParserNamespace, create_conveter_parser, parse_converter_args
from .reddit import RedditParserNamespace, create_reddit_parser, parse_reddit_args
from .view import WordCloudParserNamespace, create_wordcloud_parser, parse_wordcloud_args

__all__ = [
    "ConverterParserNamespace",
    "create_conveter_parser",
    "create_reddit_parser",
    "create_wordcloud_parser",
    "parse_converter_args",
    "parse_reddit_args",
    "parse_wordcloud_args",
    "RedditParserNamespace",
    "WordCloudParserNamespace",
]
