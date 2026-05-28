"""
Módulo de definição dos modelos de dados do domínio.

Centraliza todas as estruturas de dados, enums e tipos personalizados
utilizados ao longo do projeto. Atua como a "linguagem ubíqua" do sistema,
garantindo que todos os componentes (coleta, armazenamento, NLP) se
comuniquem utilizando os mesmos formatos e contratos.
"""

from .language import Language
from .post import UNKNOWN_AUTHOR_PLACEHOLDER, PostRecord, pack_post

__all__ = [
    "Language",
    "pack_post",
    "PostRecord",
    "UNKNOWN_AUTHOR_PLACEHOLDER",
]
