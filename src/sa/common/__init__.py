"""
Módulo de abstrações genéricas para operações com arquivos.

Define as interfaces base (ABCs genéricas) que padronizam os contratos de
leitura, escrita, persistência e conversão de arquivos em todo o projeto.
Garante que todas as implementações concretas sigam uma interface
consistente e intercambiável.
"""

from .file import FileConverterABC, FileReaderABC, FileSaverABC, FileWriterABC
from .parser import Parser, ParserError, ParserNamespace

__all__ = [
    "FileConverterABC",
    "FileReaderABC",
    "FileSaverABC",
    "FileWriterABC",
    "Parser",
    "ParserError",
    "ParserNamespace",
]
