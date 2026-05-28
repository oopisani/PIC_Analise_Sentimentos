from typing import TYPE_CHECKING, Generator, Optional

from sa.model import UNKNOWN_AUTHOR_PLACEHOLDER, pack_post
from sa.nlp import matches_language, normalize_text

if TYPE_CHECKING:
    from logging import Logger

    from praw import Reddit  # type: ignore[import-untyped]
    from praw.models import Submission  # type: ignore[import-untyped]

    from sa.model import Language, PostRecord


class RedditCollector:
    """
    Responsável pela coleta, filtragem e pré-processamento de posts do Reddit.

    Orquestra o processo de busca de posts em um subreddit específico a partir de
    uma lista de palavras-chave.
    Cada post coletado passa por normalização de texto, verificação de idioma e
    deduplicação antes de ser entregue ao consumidor via generator.

    Integração no pipeline de NLP:
        - Recebe uma lista de palavras-chave para busca.
        - Utiliza `normalize_text` (subpacote `nlp`) para limpar título e corpo do post.
        - Utiliza `matches_language` (subpacote `nlp`) para filtrar posts no idioma desejado.
        - Empacota cada post no formato `PostRecord` via `pack_post` (subpacote `model`).
        - Entrega os registros prontos para ingestão pelo pipeline de análise de sentimentos.

    Observações:
        - Padrão utilizado: Iterator (implementado via generator com `yield`).
        - A deduplicação é feita por hash de conteúdo (`content_hash`) dentro de cada sessão
          de coleta, sem persistência entre execuções.
        - Posts cujo autor foi deletado recebem o placeholder `UNKNOWN_AUTHOR_PLACEHOLDER`.
    """

    def __init__(self, reddit_client: "Reddit", subreddit_name: str, logger: Optional["Logger"] = None):
        """
        Inicializa o coletor com o cliente Reddit, o subreddit alvo e o logger opcional.

        Args:
            reddit_client (Reddit): Instância autenticada do cliente PRAW, responsável
                pela comunicação com a API do Reddit.
            subreddit_name (str): Nome do subreddit de onde os posts serão coletados
                (sem o prefixo ``r/``).
            logger (Optional[Logger]): Instância de logger para registrar eventos e
                diagnósticos durante a coleta. Se `None`, os logs são silenciados.
        """

        self._client = reddit_client
        """Instância autenticada do cliente PRAW para comunicação com a API."""

        self._subreddit_name = subreddit_name
        """Nome do subreddit alvo da coleta."""

        self._logger = logger
        """Logger opcional para registro de eventos durante a coleta."""

    def collect(self, keywords: list[str], lang: "Language", total_per_word: int) -> Generator["PostRecord", None, None]:
        """
        Coleta posts de um subreddit baseando-se nas palavras-chave fornecidas.
        Retorna lista de dicionários com texto limpo e palavra-chave associada.

        Itera sobre as palavras-chave,
        realizando buscas no subreddit via API do Reddit. Para cada resultado, aplica
        um pipeline de filtragem sequencial: pré-processamento de texto, verificação
        de idioma e deduplicação por hash de conteúdo. Posts aprovados em todas as
        etapas são emitidos via ``yield``.

        Args:
            keywords (list[str]): Lista de palavras-chave
                de busca a serem submetidas à API do Reddit.
            lang (Language): Idioma esperado dos posts. Posts em outros idiomas
                são descartados com base na detecção feita por `matches_language`.
            total_per_word (int): Limite máximo de posts a recuperar por palavra-chave
                na chamada à API do Reddit. Também é usado como critério de parada
                antecipada do loop de palavras quando o total de hashes únicos
                atingir esse limite.

        Yields:
            PostRecord: Dicionário estruturado contendo os dados normalizados
                e metadados do post aceito (id, título, conteúdo, autor,
                palavra-chave, subreddit e timestamp de criação).

        Observações:
            - A busca na API usa ``sort="new"`` para priorizar posts recentes.
            - A deduplicação é baseada no campo ``content_hash`` do `PostRecord`,
              calculado durante o pré-processamento em `_preprocess_post`.
            - O loop de palavras-chave encerra antecipadamente quando o número de
              posts únicos acumulados atingir `total_per_word`.
        """

        content_hashes: set[str] = set()

        for keyword in keywords:
            self._log(f"Buscando palavra-chave: '{keyword}' | Limite por palavra: {total_per_word}")

            subreddit = self._client.subreddit(self._subreddit_name)

            # Pesquisa por palavra-chave no título ou texto
            for post in subreddit.search(keyword, sort="new", limit=total_per_word):
                clean_post = self._normalize_post(post, keyword)

                if not self._check_post_language(clean_post, lang):
                    self._log(f"Post {clean_post['post_id']} ignorado (não é {lang.value.upper()})")
                    continue

                if clean_post["content_hash"] in content_hashes:
                    self._log(f"Post {clean_post['post_id']} ignorado (duplicado)")
                    continue

                content_hashes.add(clean_post["content_hash"])

                self._log(f"Post {clean_post['post_id']} aceito!")

                yield clean_post

            if len(content_hashes) >= total_per_word:
                break

    def _normalize_post(self, post: "Submission", keyword: str) -> "PostRecord":
        """
        Normaliza e empacota os dados brutos de uma submissão do Reddit em um `PostRecord`.

        Aplica `normalize_text` ao título e ao corpo do post para limpeza e padronização
        do texto (ex.: remoção de caracteres especiais, normalização de espaços).
        Em seguida, delega o empacotamento estruturado à função `pack_post` do
        subpacote `model`.

        Args:
            post (Submission): Objeto de submissão bruto retornado pela API PRAW,
                contendo os atributos originais do post do Reddit.
            keyword (str): Palavra-chave de busca que resultou na recuperação deste post.

        Returns:
            PostRecord: Dicionário estruturado com os campos normalizados e metadados
                do post, pronto para as etapas subsequentes do pipeline de NLP.

        Observações:
            - Se `normalize_text` retornar `None` (ex.: texto vazio), o valor é
              substituído por uma string vazia ``""``.
            - Autores deletados (`post.author is None`) recebem o valor
              `UNKNOWN_AUTHOR_PLACEHOLDER` definido no subpacote `model`.
        """

        preprocess_title = normalize_text(post.title) or ""
        preprocess_content = normalize_text(post.selftext) or ""

        return pack_post(
            post_id=str(post.id),
            title=preprocess_title,
            content=preprocess_content,
            author=str(post.author) if post.author else UNKNOWN_AUTHOR_PLACEHOLDER,
            keyword=keyword,
            subreddit=self._subreddit_name,
            created_at=post.created_utc,
        )

    def _check_post_language(self, post: "PostRecord", lang: "Language") -> bool:
        """
        Verifica se o conteúdo ou título de um post corresponde ao idioma esperado.

        Delega a detecção de idioma à função `matches_language` do subpacote `nlp`,
        aplicando-a separadamente ao conteúdo e ao título do post. O critério é
        inclusivo: basta que um dos dois campos corresponda ao idioma alvo para
        que o post seja aceito.

        Args:
            post (PostRecord): Dicionário estruturado do post contendo os campos
                ``"content"`` e ``"title"`` já normalizados.
            lang (Language): Idioma esperado para o post, utilizado como critério
                de filtragem pela função `matches_language`.

        Returns:
            bool: `True` se o conteúdo **ou** o título do post corresponderem
                ao idioma `lang`; `False` caso contrário.
        """

        return matches_language(post["content"], lang) or matches_language(post["title"], lang)

    def _log(self, message: str) -> None:
        """
        Emite uma mensagem de log no nível INFO, se um logger estiver configurado.

        Método utilitário interno que encapsula a chamada ao logger, permitindo
        que a classe opere sem logger sem necessidade de verificações externas.

        Args:
            message (str): Mensagem a ser registrada no log.

        Observações:
            - Se `_logger` for `None`, a mensagem é silenciada sem efeito colateral.
        """

        if self._logger:
            self._logger.info(message)
