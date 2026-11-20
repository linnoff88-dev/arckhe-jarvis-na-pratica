"""Cérebro 2 — Codex pela ASSINATURA do ChatGPT (`codex exec`). Sem API, sem chave.

`--output-schema` obriga o formato; `-s read-only` numa pasta vazia e `--ephemeral` (não guarda sessão).
O esquema estrito da OpenAI não aceita objeto de chaves livres, então os argumentos de cada
ferramenta vêm como texto JSON em `args_json` (o comum.normalizar converte).
O prompt entra pelo stdin ("-") e o stdin é fechado; sem isso o codex exec espera para sempre.
"""
import asyncio
import json
import os
import subprocess
import tempfile

from intelecto.provedores.base import ErroProvedor, Provedor, Resposta

from .comum import conversa_em_texto, normalizar, sistema

ESQUEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "texto": {"type": "string"},
        "chamadas": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "properties": {"nome": {"type": "string"}, "args_json": {"type": "string"}},
            "required": ["nome", "args_json"]}},
    },
    "required": ["texto", "chamadas"],
}
AVISO = ("Você está sendo usado só como cérebro: NÃO rode comandos nem leia arquivos desta pasta. "
         "Devolva apenas o JSON. Em 'chamadas', 'args_json' é um objeto JSON em texto, ex.: "
         '{"comando": "df -h /"}.')


class CodexAssinatura(Provedor):
    nome = "codex"

    def __init__(self, modelo=None, esforco=None, tempo=240, binario=None):
        self.modelo = modelo or os.environ.get("CODEX_MODELO", "gpt-6.2-sol")
        self.esforco = esforco or os.environ.get("CODEX_ESFORCO", "low")
        self.tempo = tempo
        self.binario = binario or os.environ.get("CODEX_BIN", "codex")
        self.pasta = tempfile.mkdtemp(prefix="cerebro-codex-")
        self.esquema = os.path.join(self.pasta, ".esquema.json")
        with open(self.esquema, "w") as f:
            json.dump(ESQUEMA, f)

    def comando(self, saida):
        return [self.binario, "exec", "-m", self.modelo, "-c", f'model_reasoning_effort="{self.esforco}"',
                "-s", "read-only", "-C", self.pasta, "--skip-git-repo-check", "--ephemeral", "--json",
                "--output-schema", self.esquema, "-o", saida, "-"]

    async def conversar(self, mensagens, ferramentas=None) -> Resposta:
        prompt = f"{sistema(mensagens, ferramentas)}\n\n{AVISO}\n\n--- conversa ---\n{conversa_em_texto(mensagens)}"
        saida = tempfile.mktemp(prefix="resposta-", suffix=".json", dir=self.pasta)
        env = {k: v for k, v in os.environ.items() if not k.startswith(("OPENAI_", "OPENROUTER_"))}  # assinatura, nunca API
        try:
            p = await asyncio.to_thread(subprocess.run, self.comando(saida), input=prompt, capture_output=True,
                                        text=True, timeout=self.tempo, env=env)
        except subprocess.TimeoutExpired as e:
            raise ErroProvedor(f"codex exec passou de {self.tempo} s") from e
        try:
            with open(saida, encoding="utf-8") as f:
                s = json.load(f)
        except (OSError, ValueError) as e:
            raise ErroProvedor(f"codex exec sem JSON ({p.returncode}): {(p.stderr or p.stdout)[-300:]}") from e
        finally:
            if os.path.exists(saida):
                os.remove(saida)
        entrada = saida_tk = 0
        for linha in p.stdout.splitlines():   # eventos JSONL: o turn.completed traz o uso de tokens
            try:
                ev = json.loads(linha)
            except ValueError:
                continue
            u = ev.get("usage") if isinstance(ev, dict) else None
            if u:
                entrada += int(u.get("input_tokens") or 0)
                saida_tk += int(u.get("output_tokens") or 0)
        texto, chamadas = normalizar(s, ferramentas)
        return Resposta(texto, chamadas, {"entrada": entrada, "saida": saida_tk, "custo_usd": 0.0})
