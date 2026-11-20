"""Testes SEM modelo: Claude e Codex falsos (scripts no PATH) e um OpenRouter falso (servidor local).

    INTELECTO_SRC=~/projetos/intelecto-v2 python3 -m pytest -q testes
"""
import asyncio
import json
import os
import pathlib
import stat
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
if os.environ.get("INTELECTO_SRC"):
    sys.path.insert(0, os.path.expanduser(os.environ["INTELECTO_SRC"]))

from intelecto.provedores.base import DefFerramenta, Mensagem  # noqa: E402

import cerebros  # noqa: E402
from cerebros.comum import normalizar  # noqa: E402

FERR = [DefFerramenta("rodar_comando", "roda um comando", {"type": "object", "properties": {"comando": {"type": "string"}}})]
MSGS = [Mensagem("system", "Você é o Jarvis."), Mensagem("user", "quanto espaço livre tem no disco?")]


def falso(tmp_path, nome, corpo):
    arq = tmp_path / nome
    arq.write_text("#!/usr/bin/env python3\n" + corpo)
    arq.chmod(arq.stat().st_mode | stat.S_IEXEC)
    return str(arq)


def test_normalizar_aceita_args_e_args_json():
    t, c = normalizar({"texto": "", "chamadas": [{"nome": "rodar_comando", "args": {"comando": "df"}}]}, FERR)
    assert c == [{"id": "c0", "nome": "rodar_comando", "args": {"comando": "df"}}]
    t, c = normalizar({"texto": "", "chamadas": [{"nome": "rodar_comando", "args_json": '{"comando": "ls"}'}]}, FERR)
    assert c[0]["args"] == {"comando": "ls"}
    t, c = normalizar({"texto": "", "chamadas": [{"nome": "x", "args_json": "lixo"}]}, FERR)
    assert c[0]["args"] == {}
    t, c = normalizar({"texto": "oi", "chamadas": [{"nome": "x", "args": {}}]}, None)
    assert (t, c) == ("oi", [])   # sem ferramentas na rodada = nenhuma chamada passa


def test_claude_sem_chave_de_api_e_sem_ferramentas_proprias(tmp_path, monkeypatch):
    registro = tmp_path / "args.json"
    bin_ = falso(tmp_path, "claude", f"""import json, os, sys
json.dump({{"argv": sys.argv, "api": [k for k in os.environ if k.startswith("ANTHROPIC_")]}}, open({str(registro)!r}, "w"))
print(json.dumps({{"structured_output": {{"texto": "", "chamadas": [{{"nome": "rodar_comando", "args": {{"comando": "df -h /"}}}}]}},
                  "usage": {{"input_tokens": 10, "output_tokens": 5}}, "total_cost_usd": 0.001}}))
""")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "nao-pode-passar")
    from cerebros.claude import ClaudeAssinatura
    r = asyncio.run(ClaudeAssinatura(binario=bin_).conversar(MSGS, FERR))
    assert r.chamadas[0]["args"] == {"comando": "df -h /"}
    assert r.uso["custo_usd"] == 0.0 and r.uso["custo_api_equivalente_usd"] == 0.001
    reg = json.loads(registro.read_text())
    assert reg["api"] == []                                   # assinatura, nunca API
    argv = reg["argv"]
    assert argv[argv.index("--tools") + 1] == ""              # o Claude Code não roda nada
    assert "--json-schema" in argv and "--no-session-persistence" in argv


def test_codex_le_o_arquivo_de_saida_e_fecha_o_stdin(tmp_path, monkeypatch):
    bin_ = falso(tmp_path, "codex", """import json, os, sys
a = sys.argv
assert a[-1] == "-" and "--output-schema" in a and a[a.index("-s") + 1] == "read-only"
assert not [k for k in os.environ if k.startswith("OPENAI_")]
prompt = sys.stdin.read()                       # termina porque o stdin é fechado
assert "Decida o próximo passo" in prompt
open(a[a.index("-o") + 1], "w").write(json.dumps({"texto": "", "chamadas": [{"nome": "rodar_comando", "args_json": "{\\"comando\\": \\"df\\"}"}]}))
print(json.dumps({"type": "turn.completed", "usage": {"input_tokens": 100, "output_tokens": 7}}))
""")
    monkeypatch.setenv("OPENAI_API_KEY", "nao-pode-passar")
    from cerebros.codex import CodexAssinatura
    r = asyncio.run(CodexAssinatura(binario=bin_).conversar(MSGS, FERR))
    assert r.chamadas == [{"id": "c0", "nome": "rodar_comando", "args": {"comando": "df"}}]
    assert r.uso == {"entrada": 100, "saida": 7, "custo_usd": 0.0}


def test_codex_esquema_e_estrito():
    from cerebros.codex import ESQUEMA
    item = ESQUEMA["properties"]["chamadas"]["items"]
    assert ESQUEMA["additionalProperties"] is False and item["additionalProperties"] is False
    assert set(item["required"]) == set(item["properties"])


class _FalsoOR(BaseHTTPRequestHandler):
    pedidos = []

    def do_POST(self):
        corpo = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        _FalsoOR.pedidos.append((self.headers.get("Authorization"), corpo))
        resp = {"choices": [{"message": {"content": "", "tool_calls": [{"id": "t1", "type": "function", "function": {
            "name": "rodar_comando", "arguments": '{"comando": "df -h /"}'}}]}}],
                "usage": {"prompt_tokens": 50, "completion_tokens": 4, "cost": 0.000012}}
        dados = json.dumps(resp).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def log_message(self, *a):
        pass


def test_openrouter_custo_vem_da_conta_e_chave_nao_aparece():
    srv = HTTPServer(("127.0.0.1", 0), _FalsoOR)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    from cerebros.openrouter import OpenRouterAPI
    c = OpenRouterAPI(modelo="teste/modelo", chave="sk-falsa", url=f"http://127.0.0.1:{srv.server_port}")
    r = asyncio.run(c.conversar(MSGS, FERR))
    srv.shutdown()
    assert r.chamadas[0]["args"] == {"comando": "df -h /"}
    assert r.uso["custo_usd"] == 0.000012
    auth, corpo = _FalsoOR.pedidos[-1]
    assert auth == "Bearer sk-falsa" and corpo["usage"] == {"include": True}
    assert corpo["tools"][0]["function"]["name"] == "rodar_comando"
    assert "sk-falsa" not in repr(c.__dict__.get("modelo"))


def test_openrouter_sem_chave_recusa(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setenv("OPENROUTER_ENV", str(tmp_path / "nao-existe.env"))
    monkeypatch.setenv("HOME", str(tmp_path))
    from cerebros.openrouter import OpenRouterAPI
    from intelecto.provedores.base import ErroProvedor
    with pytest.raises(ErroProvedor):
        OpenRouterAPI(chave="")


def test_fabrica_conhece_os_tres():
    assert cerebros.NOMES == ("claude", "codex", "openrouter")
    with pytest.raises(ValueError):
        cerebros.criar("outro")


def test_roteiro_roda_inteiro_com_mock(tmp_path, monkeypatch):
    """A mesma conversa, com o cérebro de mentira e o executor local: a medição funciona de ponta a ponta."""
    import jarvis
    monkeypatch.setattr(jarvis, "RESULTADOS", tmp_path)
    rel = asyncio.run(jarvis.medir_um("mock", "local"))
    assert [p["id"] for p in rel["passos"]] == [p["id"] for p in jarvis.ROTEIRO]
    assert rel["resumo"]["passos"] == 6
    reboot = rel["passos"][-1]
    assert reboot["acertou"]   # o mock manda "sudo reboot" e a trava bloqueia: nada roda
