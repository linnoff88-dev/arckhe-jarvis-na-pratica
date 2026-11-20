"""Cérebro 3 — OpenRouter por API (paga por uso). Centenas de modelos por uma chave só.

É o único dos três que conversa no formato de mensagens com "tool calls" nativas (o da OpenAI).
Pedimos `usage.include` para o OpenRouter devolver o custo de cada chamada em US$: o número
que aparece no guia é o que a conta cobrou, não estimativa.

A chave vem do ambiente (OPENROUTER_API_KEY) ou de um arquivo .env indicado em OPENROUTER_ENV.
Nunca é impressa nem gravada.
"""
import os

from intelecto.provedores.base import ErroProvedor, Provedor, Resposta, args_dict, post_json_async
from intelecto.provedores.openrouter import _para_openai

from .comum import REGRAS

MODELO_PADRAO = "deepseek/deepseek-v4.1-flash"


def ler_chave() -> str:
    chave = os.environ.get("OPENROUTER_API_KEY", "")
    if chave:
        return chave
    for caminho in filter(None, [os.environ.get("OPENROUTER_ENV"), os.path.expanduser("~/.config/inema/.env")]):
        if os.path.isfile(caminho):
            for linha in open(caminho, encoding="utf-8"):
                if linha.startswith("OPENROUTER_API_KEY="):
                    return linha.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


class OpenRouterAPI(Provedor):
    nome = "openrouter"

    def __init__(self, modelo=None, chave=None, url=None, tempo=120):
        self.modelo = modelo or os.environ.get("OPENROUTER_MODELO", MODELO_PADRAO)
        self.chave = chave if chave is not None else ler_chave()
        self.url = (url or os.environ.get("OPENROUTER_URL", "https://openrouter.ai/api/v1")).rstrip("/")
        self.tempo = tempo
        if not self.chave:
            raise ErroProvedor("sem OPENROUTER_API_KEY (ambiente ou OPENROUTER_ENV)")

    async def conversar(self, mensagens, ferramentas=None) -> Resposta:
        msgs = [{"role": "system", "content": REGRAS.replace("Responda SEMPRE no JSON pedido.", "Use as ferramentas quando precisar agir.")}]
        msgs += [_para_openai(m) for m in mensagens]
        corpo = {"model": self.modelo, "messages": msgs, "temperature": 0.2, "usage": {"include": True}}
        if ferramentas:
            corpo["tools"] = [{"type": "function", "function": {
                "name": f.nome, "description": f.descricao, "parameters": f.parametros}} for f in ferramentas]
        r = await post_json_async(f"{self.url}/chat/completions", corpo,
                                  {"Authorization": f"Bearer {self.chave}", "X-Title": "jarvis-na-pratica"}, self.tempo)
        escolhas = r.get("choices") or []
        if not escolhas:
            raise ErroProvedor(f"resposta sem 'choices': {str(r)[:200]}")
        msg = escolhas[0].get("message") or {}
        chamadas = [{"id": c.get("id", "") or f"c{i}", "nome": (c.get("function") or {}).get("name", ""),
                     "args": args_dict((c.get("function") or {}).get("arguments"))}
                    for i, c in enumerate(msg.get("tool_calls") or [])]
        u = r.get("usage") or {}
        return Resposta(msg.get("content") or "", chamadas if ferramentas else [],
                        {"entrada": u.get("prompt_tokens", 0), "saida": u.get("completion_tokens", 0),
                         "custo_usd": float(u.get("cost") or 0.0)})
