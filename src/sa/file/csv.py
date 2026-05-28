from pathlib import Path
from typing import TYPE_CHECKING, Iterable

import pandas as pd

from sa.common import FileSaverABC

if TYPE_CHECKING:
    from sa.model import PostRecord


class CSVPostSaver(FileSaverABC["PostRecord"]):
    """
    Salvador concreto responsável pela escrita de coleções de posts em formato CSV.

    Implementa a interface genérica `FileSaverABC` definindo o tipo `PostRecord`.
    Recebe as coleções emitidas pelo pipeline (como as listas filtradas do Reddit Collector
    e processadas pela NLP) e converte em massa para um arquivo CSV estruturado. O uso
    do pacote pandas garante rapidez e manipulação eficiente das formatações de colunas.

    Attributes:
        _path (Path): Caminho resolvido de gravação do arquivo .csv no disco.

    Observações:
        - Delega ao Pandas a conversão dos Dicionários brutos listados através do DataFrame.
        - Converte automaticamente datas em texto para tipos temporais `pd.to_datetime`.
    """

    def __init__(self, path: str | Path):
        """
        Prepara a intância do salvador fornecendo o local de armazenamento persistente do CSV.

        Args:
            path (str | Path): Diretório somado ao nome do arquivo (eg "posts_coletados.csv").
                Será avaliado com `Path` interno garantindo suporte multiplataforma.
        """

        self._path = Path(path)

    def save(self, values: Iterable["PostRecord"]) -> None:
        """
        Efetua a execução em massa da iteração de posts transformando-as em arquivo.

        Converte a sequência ou gerador que foi fornecida em listas explícitas para garantir
        tamanho e a inferência automatizada do layout do Dataframe. Caso hajam dados na coluna
        `created_at`, é aplicado parsing de correção temporal ignorando campos de coerção duvidosa.
        Finalmente, escreve os dados persistindo codificação global em UTF-8.

        Args:
            values (Iterable[PostRecord]): Um aglomerado em iterador de registros capturados via API.

        Raises:
            ValueError: Se o conjunto avaliado for iterável porém retorne lista vazia ou for null.
        """

        posts_list = list(values)

        if not posts_list:
            raise ValueError("Nenhum post para exportar.")

        df: pd.DataFrame = pd.DataFrame(posts_list)

        if "created_at" in df.columns:
            if pd.api.types.is_numeric_dtype(df["created_at"]):
                df["created_at"] = pd.to_datetime(df["created_at"], unit="s", errors="coerce")
            else:
                df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

        df.to_csv(self._path, index=False, encoding="utf-8")
