"""Script unificado CLI executável produtor dos relatórios analíticos de sentimentos das planilhas."""

from __future__ import annotations

from collections import Counter
from sys import argv, exit
from typing import NoReturn

import spacy

from sa.common import ParserError
from sa.file import XLSXColumnReader
from sa.logger import create_logger
from sa.nlp import build_stopwords, preprocess_text
from sa.parser import parse_wordcloud_args
from sa.visualization import generate_frequency_chart, generate_wordcloud

COLORMAPS: dict[str, str] = {
    "posts": "viridis",
}
"""Matriz mapeando e restringindo tabelas estéticas aos humores do matplotlib correlatos as Sheets das planilhas."""


BAR_COLORS: dict[str, str] = {
    "posts": "steelblue",
}
"""Hash map isolando palhetas cores sólidas matplotlib as sheets do Excel correlacionadas dinâmicamente."""

logger = create_logger(__name__)


def _main() -> None:
    """
    Rotina construtora central iterável produtora do motor final visual da pipeline (View Script CLI).

    Atribui primeiramente restrições estruturais CLI. Aciona motor pesada de redes neurais carregando o SpaCy LG core em memoria principal. Fabrica Set de stopwords, então itera ciclicamente as abas lidas, pre-processando via Lematização tokenizada com filtragem `visual_pos (NOUN e ADJ)` o Corpus textual massivo agrupando os outputs estáticos via counter para extração iteradora dos utilitários `generate_frequency_chart` e `generate_wordcloud`.

    Observações:
        - Carrega dependência "pt_core_news_lg" estática consumindo memória no build.
        - Filtra apenas por Substantivos e Adjetivos, para aprimorar o contexto visual dos sentimentos gerados em plot.
    """

    args = parse_wordcloud_args(argv[1:])

    input_path = args.input_path.resolve()
    output_dir = args.output_dir.resolve()

    if not input_path.exists():
        fatal(f"The input file {str(input_path)!r} does not exist.")

    if args.extras and not args.extras.exists():
        fatal(f"The additional stopwords file {str(args.extras)!r} was not found.")

    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Loading spaCy model...")

    nlp = spacy.load("pt_core_news_lg")

    logger.info("Building stopwords...")

    stopwords = build_stopwords(lang="portuguese", extras_path=args.extras)

    visual_pos = {"NOUN", "ADJ"}

    for sheet in args.sheets:
        logger.info("Processing sheet '%s'...", sheet)

        reader = XLSXColumnReader(input_path, sheet_name=sheet, column="texto")

        try:
            texts = reader.read()
        except KeyError:
            logger.warning("Sheet '%s' does not have 'texto' column. Skipping.", sheet)
            continue

        cleaned_texts = [preprocess_text(t, stopwords, nlp, allowed_pos=visual_pos) for t in texts]
        combined = " ".join(" ".join(t) for t in cleaned_texts)

        if not combined.strip():
            logger.warning("No text remaining after cleaning in sheet '%s'. Skipping.", sheet)

            continue

        word_counts = Counter(combined.split()).most_common(args.top_n)

        colormap = COLORMAPS.get(sheet, "viridis")
        bar_color = BAR_COLORS.get(sheet, "steelblue")

        wc_path = output_dir / f"nuvem_{sheet}.png"

        generate_wordcloud(combined, wc_path, colormap=colormap)

        logger.info("Wordcloud saved to %s", wc_path)

        chart_path = output_dir / f"frequencia_{sheet}.png"

        generate_frequency_chart(word_counts, chart_path, color=bar_color)

        logger.info("Frequency chart saved to %s", chart_path)
        logger.info("Top %d words for '%s':", args.top_n, sheet)

        for word, freq in word_counts:
            logger.info("  %-15s | %d", word, freq)

    logger.info("Process finished successfully.")


def fatal(message: str) -> NoReturn:
    """Interrompe e relata aborto sistêmico do construtor gráfico visual."""

    logger.fatal(message)
    exit(1)


def main() -> None:
    try:
        _main()
    except KeyboardInterrupt:
        print("Process interrupted by user.")
    except ParserError as e:
        print(f"Usage error: {e}")
        exit(2)
    except Exception as e:
        print(f"Unhandled fatal failure: {e}")
        exit(1)

if __name__ == "__main__":
    main()
