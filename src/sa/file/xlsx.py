from pathlib import Path
from typing import TYPE_CHECKING, Iterable

import pandas as pd

from sa.common import FileReaderABC, FileSaverABC

if TYPE_CHECKING:
    from sa.model import PostRecord


class XLSXPostSaver(FileSaverABC["PostRecord"]):
    """
    Salvador concreto responsável pela escrita de coleções de posts em formato Excel (XLSX).

    Implementando o `FileSaverABC`, esta versão assume a geração de datasets densos a partir de
    tabelas Excel usando a biblioteca `pandas` como driver de escrita subjacente. Permite a gravação
    de dados tipificados em planilhas específicas do workbook limitando ruídos nas conversões.

    Attributes:
        _path (Path): Caminho absoluto/relativo destinado a salvar o layout gerado.
        _sheet_name (str): Planilha destino configurada pela classe onde ficam estruturados
             os registros serializados pelos pipelines NLP.

    Observações:
        - Dependências exclusas: É obrigatória a instalação do módulo externo de extração (openpyxl).
        - Os metadados criados podem consumir processamento temporário acentuado (to_excel) se a base de dados
         ultrapassar tamanhos gigantescos por usar serialização do office XML.
    """

    def __init__(self, path: str | Path, sheet_name: str = "posts"):
        """
        Instancia parâmetros locais para a geração do XLSX exportado definindo comportamentos.

        Args:
            path (str | Path): O caminho para arquivo final `.xlsx` a ser redigido.
            sheet_name (str, optional): Indica a guia de trabalho que será reescrita para aceitar o dataset.
                Por default assume "posts" para não poluir ou sobreescrever guias antigas "Sheet1".
        """

        self._path = Path(path)
        self._sheet_name = sheet_name

    def save(self, values: Iterable["PostRecord"]) -> None:
        """
        Consolida iterador de Posts dentro do workbook do arquivo selecionado de escrita em disco.

        Esgota o array passado construindo primeiramente a dimensão analítica sobre as colunas. Processa a
        coluna com tags temporárias e garante o dump efetivando transação segura com o índice zerado para não
        produzir formatações estranhas e índices perdidos que prejudiquem visões dos usuários finais em programas
        como o Office ou Libre Office.

        Args:
            values (Iterable[PostRecord]): Pacote empacotado que contem registros estruturados em Dictionary.

        Raises:
            ValueError: Interrompe a transação a disco em casos onde são passadas coleções de tamanho zero (listas vazias).
        """

        posts_list = list(values)

        if not posts_list:
            raise ValueError("Nenhum post para exportar.")

        df = pd.DataFrame(posts_list)

        if "created_at" in df.columns:
            if pd.api.types.is_numeric_dtype(df["created_at"]):
                df["created_at"] = pd.to_datetime(df["created_at"], unit="s", errors="coerce")
            else:
                df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

        df.to_excel(self._path, index=False, sheet_name=self._sheet_name)


class XLSXColumnReader(FileReaderABC[list[str]]):
    """
    Leitor concreto voltado à exrtação segmentada de strings a partir de uma tabela Excel.

    Implementa a assinatura `FileReaderABC` visando lidar apenas com leitura em massa
    de strings limitadas pela configuração semantica da classe, extraindo unicamente a
    coluna requerida especificada em uma pasta Excel através de varredura automatizada
    que despreza anomalias e ruídos indesejados (Nulls / NAans).

    Attributes:
        _path (Path): Objeto representativo de apontamento do arquivo .xlsx leitura do OS.
        _sheet_name (str): Guia tabular selecionada no leitor de arquivos Pandas.
        _column (str): Título da coluna da qual serão transpostas e iteradas as palavras localizadas.

    Observações:
        - Muito pertinente no workflow atual como responsável por extrair Dicionários / Lexicons
         prontos customizados e mantidos pela equipe de usuários operando em planilhas tabulares em nuvem.
        - Descarta colunas com tipagem nula via subset mapping do Pandas de maneira rigorosa.
    """

    def __init__(self, path: str | Path, sheet_name: str, column: str) -> None:
        """
        Constrói o leitor da classe atribuindo alocações fixas das planilhas extraídas baseando-se
        no cenário apontado pela inicialização de variáveis do construtor de extração nominal do excel.

        Args:
            path (str | Path): Caminho referenciado obrigatório com planilhas tabulares prontas (XLSX).
            sheet_name (str): Nome de guia explicitamente requerida. Impede erros na alteração de referências.
            column (str): Título nominal indexador do header baseando a área pesquisada.
        """

        self._path = Path(path)
        self._sheet_name = sheet_name
        self._column = column

    def read(self) -> list[str]:
        """
        Opera o mecanismo Pandas extraindo os dados do disco, efetuando parsing via tipagem para lista
        básica em formato Python (string).

        O método faz carregamento em massa ignorando dados ausentes e cast de variáveis exóticas para text formato nativo,
        garantindo sanitização de pipeline limpa perante as etapas previsoras de pre-processamento em NPL.

        Returns:
            list[str]: Ampla lista vetorial constituida por itens do eixo column purificado extraído do pacote Excel.

        Raises:
            KeyError: Levanta interrupção rigorosa no processo de execução caso a tabela excel passada por parâmetros
            não represente de nenhuma forma e conformidade o cabeçalho column passado no instanciador da base.
        """

        df: pd.DataFrame = pd.read_excel(self._path, sheet_name=self._sheet_name)

        if self._column not in df.columns:
            raise KeyError(f"Coluna '{self._column}' não encontrada na aba '{self._sheet_name}'.")

        df = df.dropna(subset=[self._column])

        return [str(v) for v in df[self._column]]
