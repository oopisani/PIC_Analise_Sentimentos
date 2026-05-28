"""Script interativo do terminal (CLI) focado na conversão de extensões tabulares."""

from __future__ import annotations

from sys import argv, exit
from typing import NoReturn

from sa.file import ConverterFactory
from sa.logger import create_logger
from sa.parser import parse_converter_args

logger = create_logger(__name__)


def _main() -> None:
    """
    Ponto de inicialização do programa de console de conversão.

    Avalia de forma sequencial todos as flags CLI inseridas no trigger, convertendo o formato
    bruto capturado para nomes limpos e restrições. Paralelamente provê travas
    e impedimentos de perda de dados acidental (como abortar ao tentar sobreescrever um
    arquivo acidentalmente). Posteriormente transaciona os buffers no Pandas Factory logando o avanço.

    Exceptions/Raises:
        - Os raises críticos do argParse acendem a flag fatal da aplicação injetando exitCode=1.
    """

    args = parse_converter_args(argv[1:])

    input_path = args.input_path.resolve()
    output_path = args.output_path.resolve()

    if not input_path.exists():
        fatal(f"O arquivo de entrada {str(input_path)!r} não existe.")

    if output_path.exists():
        fatal(f"O arquivo de saída {str(output_path)!r} já existe. Por favor, escolha um caminho diferente ou remova o arquivo existente.")

    logger.info("Convertendo %s (%s) para %s (%s)...", input_path, args.input_format.value, output_path, args.output_format.value)

    converter = ConverterFactory.get_converter(args.input_format, args.output_format)

    try:
        converter.convert(str(input_path), str(output_path))
    except Exception as e:
        fatal(f"Falha inesperada durante a conversão: {e}")

    logger.info("Conversão concluída com sucesso: %s", output_path)


def fatal(message: str) -> NoReturn:
    """
    Controlador estrito disparador de erros irrecuperáveis via Shell.

    Anota o registro de evento critico final e força um encerramento forçoso não nulo OS `exit(1)`
    repassando adequadamente falhas a orquestradores docker e makefiles de rotina.

    Args:
        message (str): String com formato descritivo terminal informando por quê a aplicação abortou.
    """

    logger.fatal(message)
    exit(1)


def main() -> None:
    try:
        _main()
    except KeyboardInterrupt:
        print("Conversão interrompida pelo usuário.")
    except RuntimeError as e:
        print(f"Erro de uso ou execução: {e}")
        exit(2)
    except Exception as e:
        print(f"Falha fatal não tratada: {e}")
        exit(1)

if __name__ == "__main__":
    main()
