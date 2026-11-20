"""Os três cérebros trocáveis do Jarvis (INTELECTO v2). Todos seguem o contrato intelecto.provedores.base.Provedor."""


def criar(nome: str, modelo: str | None = None):
    if nome == "claude":
        from .claude import ClaudeAssinatura
        return ClaudeAssinatura(modelo or "haiku")
    if nome == "codex":
        from .codex import CodexAssinatura
        return CodexAssinatura(modelo)
    if nome == "openrouter":
        from .openrouter import OpenRouterAPI
        return OpenRouterAPI(modelo)
    if nome == "mock":
        from intelecto.provedores.mock import Mock
        return Mock()
    raise ValueError(f"cérebro desconhecido: {nome} (use claude, codex, openrouter ou mock)")


NOMES = ("claude", "codex", "openrouter")
