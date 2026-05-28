"""Script CLI orquestrador e coordenador da base Crawler para o ecossistema do API Reddit."""

from __future__ import annotations

import os
from sys import argv, exit
from typing import TYPE_CHECKING, NoReturn

from dotenv import load_dotenv

from sa.client import create_reddit_client
from sa.collector import RedditCollector
from sa.file import CSVPostSaver, FileFormat, XLSXPostSaver
from sa.logger import create_logger, create_reddit_logger
from sa.model import Language
from sa.parser import parse_reddit_args

if TYPE_CHECKING:
    from sa.model import PostRecord


logger = create_logger(__name__)


def main() -> None:
    """
    Inicializador transacional do script encarregado da captura em série das chamadas Crawler.

    Passos essenciais orquestrados sequencialmente:
    - Importa metadados rígidos dotEnv para proteger tokens e AppSecrets da API PRAW.
    - Restringe caminhos sobrescrevíveis pra evitar sobregravações.
    - Cria Conectores Wrapper que efetuam handshakes do protocolo OAuth2 perante aos servidores Reddit.
    - Itera sobre N comunindades (subreddits) fornecidas chamando instancias isoladas de Loggers e Scraping Engines independentes.
    - Funde, estende dados agregando massivamente os registros a uma estrutura Array (`all_posts_`).
    - Exclusivamente no fim de todos fechamentos, subem arquivos gerados ao disco usando classes abstratas (CSV/XLSX) formatados via Pandas O(n).

    Raises:
        - KeyError: Irá fatalizar se token dotEnv ausente.
    """

    load_dotenv(".env")

    try:
        reddit_client_id = os.environ["REDDIT_CLIENT_ID"]
        reddit_client_secret = os.environ["REDDIT_CLIENT_SECRET"]
        reddit_client_username = os.environ["REDDIT_CLIENT_USERNAME"]
    except KeyError as e:
        fatal(f"erro ao carregar a variável de ambiente {e}")

    args = parse_reddit_args(argv[1:])

    if args.output.exists():
        fatal(f"O arquivo de saída {str(args.output)!r} já existe. Por favor, escolha um caminho diferente ou remova o arquivo existente.")

    reddit_client = create_reddit_client(
        reddit_client_id,
        reddit_client_secret,
        reddit_client_username,
    )

    all_posts: list[PostRecord] = []

    for subreddit in args.subreddits:
        subreddit_logger = create_reddit_logger(subreddit)

        scrapper = RedditCollector(
            reddit_client=reddit_client,
            subreddit_name=subreddit,
            logger=subreddit_logger,
        )

        subreddit_logger.info("Iniciando a coleta de posts  do subredit %s...", subreddit)

        subreddit_posts = list(
            scrapper.collect(
                keywords=args.keywords,
                lang=Language(args.language),
                total_per_word=args.total,
            )
        )

        subreddit_logger.info("Coleta do subredit %s finalizada. Total de posts: %d", subreddit, len(subreddit_posts))

        all_posts.extend(subreddit_posts)

    output_filepath = args.output.resolve()

    match args.format:
        case FileFormat.CSV:
            logger.info("Exportando dados para CSV...")

            CSVPostSaver(output_filepath).save(all_posts)
        case FileFormat.XLSX:
            logger.info("Exportando dados para XLSX...")

            XLSXPostSaver(output_filepath).save(all_posts)
        case _:
            logger.error("Formato de armazenamento desconhecido: %s", args.format)

    logger.info("Dados exportados com sucesso em %s", output_filepath)


def fatal(message: str) -> NoReturn:
    """
    Aborto imediato padronizado de terminal.

    Args:
        message (str): Erro emitido para depuração em console e syslog antes de matar processamento daemon.
    """

    logger.fatal(message)
    exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nColeta interrompida pelo usuário.")
