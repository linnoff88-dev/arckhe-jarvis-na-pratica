"""Cérebro 1 — Claude Code pela ASSINATURA (`claude -p`). Sem API, sem chave.

`--tools ""` tira as ferramentas do próprio Claude Code (ele não roda nada na máquina);
`--json-schema` obriga o formato; o processo roda numa pasta vazia, sem CLAUDE.md alheio.
"""
import asyncio
import json
import os
import subprocess
import tempfile

from intelecto.provedores.base import ErroProvedor, Provedor, Resposta

from .comum import conversa_em_texto, normalizar, sistema

ESQUEMA = json.dumps({
    "type": "object",
    "properties": {
        "texto": {"type": "string"},
        "chamadas": {"type": "array", "items": {"type": "object", "properties": {
            "nome": {"type": "string"}, "args": {"type": "object"}}, "required": ["nome", "args"]}},
    },
    "required": ["texto", "chamadas"],
})


class ClaudeAssinatura(Provedor):
    nome = "claude-code"

    def __init__(self, modelo="haiku", tempo=180, binario=None):
        self.modelo, self.tempo = modelo, tempo
        self.binario = binario or os.environ.get("CLAUDE_BIN", "claude")
        self.pasta = tempfile.mkdtemp(prefix="cerebro-claude-")

    def comando(self, mensagens, ferramentas):
        return [self.binario, "-p", conversa_em_texto(mensagens), "--model", self.modelo, "--output-format", "json",
                "--tools", "", "--no-session-persistence", "--strict-mcp-config", "--setting-sources", "",
                "--system-prompt", sistema(mensagens, ferramentas), "--json-schema", ESQUEMA]

    async def conversar(self, mensagens, ferramentas=None) -> Resposta:
        env = {k: v for k, v in os.environ.items() if not k.startswith(("ANTHROPIC_", "OPENROUTER_"))}  # assinatura, nunca API
        try:
            p = await asyncio.to_thread(subprocess.run, self.comando(mensagens, ferramentas), cwd=self.pasta,
                                        capture_output=True, text=True, timeout=self.tempo,
                                        stdin=subprocess.DEVNULL, env=env)
        except subprocess.TimeoutExpired as e:
            raise ErroProvedor(f"claude -p passou de {self.tempo} s") from e
        try:
            d = json.loads(p.stdout)
            s = d.get("structured_output") or json.loads(d.get("result") or "{}")
        except (ValueError, TypeError) as e:
            raise ErroProvedor(f"claude -p sem JSON ({p.returncode}): {(p.stderr or p.stdout)[-300:]}") from e
        texto, chamadas = normalizar(s, ferramentas)
        u = d.get("usage") or {}
        entrada = sum(int(u.get(k) or 0) for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
        # total_cost_usd do Claude Code = quanto custaria na API; pela assinatura não é cobrado à parte.
        return Resposta(texto, chamadas, {"entrada": entrada, "saida": int(u.get("output_tokens") or 0),
                                          "custo_api_equivalente_usd": d.get("total_cost_usd") or 0.0,
                                          "custo_usd": 0.0})
