from string import Template

from praw import Reddit  # type: ignore[import-untyped]


class RedditClient(Reddit):
    """
    Cliente Reddit especializado, estendendo a classe base do PRAW.

    Atua como adaptador (padrão Adapter) sobre a biblioteca PRAW (Python Reddit API Wrapper),
    centralizando a criação e o ponto de acesso à API do Reddit dentro da arquitetura do projeto.
    Permite que funcionalidades adicionais específicas do domínio sejam incorporadas futuramente
    sem alterar o contrato da biblioteca subjacente.
    """

    CLIENT_VERSION = "0.2"
    USER_AGENT_TEMPLATE = Template(f"python:analise-sentimentos-bot:v{CLIENT_VERSION} (by /u/$username)")


def create_reddit_client(client_id: str, secret: str, user_name: str) -> RedditClient:
    """
    Cria e retorna uma instância autenticada de `RedditClient`.

    Atua como função factory responsável por instanciar o cliente Reddit
    com as credenciais necessárias para autenticação na API do Reddit via OAuth2.
    Centraliza a criação do cliente, desacoplando o restante do sistema dos
    detalhes de configuração do PRAW.

    Args:
        client_id (str): Identificador único do aplicativo registrado no Reddit
            (obtido em https://www.reddit.com/prefs/apps).
        secret (str): Chave secreta do aplicativo Reddit, usada em conjunto
            com `client_id` para autenticação OAuth2.
        user_agent (str): String de identificação do cliente HTTP enviada nas
            requisições à API do Reddit. Deve seguir o formato recomendado pelo
            Reddit: ``<plataforma>:<app_id>:<versão> (by u/<usuário>)``.

    Returns:
        RedditClient: Instância configurada e pronta para uso do cliente Reddit,
            autenticada no modo somente leitura (script app sem login de usuário).

    Observações:
        - O `user_agent` inadequado pode resultar em bloqueio por rate limiting da API.
        - As credenciais devem ser carregadas de variáveis de ambiente, nunca
          embutidas diretamente no código.
    """

    user_agent = RedditClient.USER_AGENT_TEMPLATE.safe_substitute(username=user_name)

    return RedditClient(
        client_id=client_id,
        client_secret=secret,
        user_agent=user_agent,
    )
