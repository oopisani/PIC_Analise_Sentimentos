from abc import ABC
from argparse import ArgumentParser, HelpFormatter, Namespace, RawTextHelpFormatter
from typing import Callable, NoReturn

class ParserError(Exception):
    """
    Exceção base para erros relacionados ao parser.
    """

class ParserHelpFormatter(RawTextHelpFormatter):
    """
    Formatador de ajuda customizado que cria documentação CLI altamente legível.

    Limpa metavars repetitivos, formata listas de forma elegante (ex: KEYWORDS... em vez de KEYWORDS [KEYWORDS ...]),
    e alinha as descrições dos argumentos perfeitamente.
    """

    def __init__(self, prog: str) -> None:
        """
        Inicializa o formatador com margens ampliadas para melhor legibilidade.

        Args:
            prog (str): Nome do programa em execução (fornecido pelo ArgumentParser).
        """

        super().__init__(prog, max_help_position=38, width=100)

    def _format_action_invocation(self, action):
        """
        Formata a string de invocação da ação (ex: '-k, --keywords KEYWORDS...').

        Remove redundâncias exibindo o metavar apenas uma vez ao invés de
        repeti-lo para cada alias de flag (ex: elimina `-k KEYWORDS, --keywords KEYWORDS`).
        """

        if not action.option_strings:
            default = self._get_default_metavar_for_positional(action)
            metavar, = self._metavar_formatter(action, default)(1)

            return metavar
        else:
            if action.nargs != 0:
                default = self._get_default_metavar_for_optional(action)
                args_string = self._format_args(action, default)

                return f"{', '.join(action.option_strings)} {args_string}"
            else:
                return ", ".join(action.option_strings)

    def _format_args(self, action, default_metavar):
        """
        Formata a representação visual dos argumentos baseada no 'nargs' da flag.

        Substitui as notações complexas do argparse padrão por reticências simples e
        intuitivas (ex: '+' vira 'METAVAR...').
        """

        get_metavar = self._metavar_formatter(action, default_metavar)

        if action.nargs is None:
            return f"{get_metavar(1)[0]}"
        elif action.nargs == '?':
            return f"[{get_metavar(1)[0]}]"
        elif action.nargs == '*':
            return f"[{get_metavar(1)[0]}...]"
        elif action.nargs == '+':
            return f"{get_metavar(1)[0]}..."

        return super()._format_args(action, default_metavar)


class Parser(ABC, ArgumentParser):
    def __init__(
        self,
        /,
        prog: str | None = None,
        usage: str | None = None,
        description: str | None = None,
        add_help: bool = True,
    ) -> None:
        formatter_class = self.get_formatter_class()

        super().__init__(
            prog=prog,
            usage=usage,
            description=description,
            formatter_class=formatter_class,
            add_help=add_help,
        )

        self.add_argument(
            "-v",
            "--verbose",
            type=bool,
            default=False,
            help="Verbose mode, displaying detailed information during program execution.",
        )

    def error(self, message: str) -> NoReturn:
        raise ParserError(message)

    def get_formatter_class(self) -> Callable[..., HelpFormatter]:
        return ParserHelpFormatter


class ParserNamespace(Namespace): ...
