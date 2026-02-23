from abc import ABC
from argparse import ArgumentParser, HelpFormatter, Namespace
from typing import Callable, NoReturn


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
            help="Modo verboso, exibindo informações detalhadas durante a execução do programa.",
        )

    def error(self, message: str) -> NoReturn:
        raise RuntimeError(message)

    def get_formatter_class(self) -> Callable[..., HelpFormatter]:
        return self._default_formatter_factory

    @staticmethod
    def _default_formatter_factory(*, prog: str) -> HelpFormatter:
        return HelpFormatter(prog, max_help_position=30)


class ParserNamespace(Namespace): ...
