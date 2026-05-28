"""Carregamento e composição de stopwords."""

from __future__ import annotations

from pathlib import Path

import nltk  # type: ignore[import-untyped]
import spacy
from unidecode import unidecode

_NLTK_TO_SPACY: dict[str, str] = {
    "portuguese": "pt",
    "english": "en",
    "spanish": "es",
}
"""Mapeamento referencial para conversão sintáxica dos IDs base do inglês NLTK frente à SpaCy."""


def load_base_stopwords(lang: str = "portuguese") -> set[str]:
    """
    Mescla as coleções fixas da engine de NLP reunindo bases abertas contidas na SpaCy e NLTK.

    Acessa ambas APIS unificando a base das engines famosas. Adiciona operação SET
    aumentando assim o "Dicionário Bloqueador" das conjunções e sufixos ignorados na modelagem da plataforma final.

    Args:
        lang (str, optional): Texto definidor não estático de ISO que obriga tradução e procura no mapa O(1).
             Por padrão preenchido buscando lexo brasileiro no NLTK.

    Returns:
        set[str]: HashSet de altíssimo desempenho não repetido indexado do conjunto.

    Observações:
        - Suprime ativamente avisos silenciosamente provindos de downloads background ativados da classe Download.
    """

    nltk.download("stopwords", quiet=True)

    from nltk.corpus import stopwords as nltk_stopwords  # type: ignore[import-untyped]

    spacy_lang = _NLTK_TO_SPACY.get(lang, lang)
    nlp = spacy.blank(spacy_lang)
    nltk_sw: set[str] = set(nltk_stopwords.words(lang))
    spacy_sw: set[str] = nlp.Defaults.stop_words

    return nltk_sw | spacy_sw


def load_extra_stopwords(path: Path) -> set[str]:
    """
    Lê uma malha customizada via sistema arquivo para stopwords criadas por equipe de negócio.

    Itera coluna explícita (DataFrame Pandas) em tabelas importadas, permitindo
    ao cliente do SA injetar o seu set paramétrico particular via disco rígido não compativel em memórias fixas.

    Args:
        path (Path): Objeto representativo de apontamento referenciando arquivo .CSV do SO isolado.

    Returns:
        set[str]: HashSet massificado, livre de unicode que fará o pareamento dedup no model.
    """

    import pandas as pd

    df = pd.read_csv(path)
    raw: list[str] = df["palavra"].astype(str).tolist()

    return {unidecode(w).lower().strip() for w in raw}


def build_stopwords(
    lang: str = "portuguese",
    extras_path: Path | None = None,
    keep: set[str] | None = None,
) -> set[str]:
    """
    Compõe, orquestra e monta os lexos parciais reunidos em stopwords numa matriz set única funcional para NLP.

    Aplica processadores isolados, primeiramente extraindo bases padrões e logo submetendo ao injectório OS para adicionar regras dinâmicas, se existitirem. Exceções inversas podem
    ser descontadas a fim de forçar o algoritmo a escutar determinadas `keep` words, não matando seu sentímento dentro das classificadoras finais em POS.

    Args:
        lang (str, optional): Ponto ISO que invoca o `load_base_stopwords` configurando O motor inicial nativo.
        extras_path (Path | None, optional): Se passado, instiga as coletas subjacentes CSV chamando funções aditivas extras externas.
        keep (set[str] | None, optional): Subtrai/Permite strings predeterminados por analistas que não deveriam compor a lista dos excluídos.

    Returns:
        set[str]: Contêiner hash perfeitamente otimizado final com words nulas no NPL que limpa tokens processados pela máquina de processamento.
    """

    sw = load_base_stopwords(lang)

    if extras_path is not None:
        sw = sw | load_extra_stopwords(extras_path)

    if keep is not None:
        sw = sw - keep

    return sw
