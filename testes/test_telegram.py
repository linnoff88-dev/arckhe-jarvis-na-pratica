"""Modo Telegram SEM Telegram e SEM modelo: um Telegram falso (servidor local) e cérebros de roteiro.

Prova: donos vazio recusa · dono passa · apagar pede OK · /nao mantém · /sim apaga · /cerebro troca e o novo lembra.
"""
import asyncio
import json
import os
import pathlib
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
if os.environ.get("INTELECTO_SRC"):
    sys.path.insert(0, os.path.expanduser(os.environ["INTELECTO_SRC"]))

from intelecto.canais.telegram import Telegram  # noqa: E402
from intelecto.provedores.base import Provedor, Resposta  # noqa: E402

import telegram_jarvis  # noqa: E402
from jarvis import montar_jarvis  # noqa: E402

DONO, ESTRANHO, CHAT = 7388953786, 42, 555


class FalsoTelegram(BaseHTTPRequestHandler):
    updates, enviados, n = [], [], [0]

    def do_POST(self):
        metodo = self.path.rsplit("/", 1)[-1]
        corpo = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
        if metodo == "getUpdates":
            res = [u for u in FalsoTelegram.updates if u["update_id"] >= corpo.get("offset", 0)]
        elif metodo == "sendMessage":
            FalsoTelegram.enviados.append(corpo["text"])
            res = {"message_id": len(FalsoTelegram.enviados)}
        elif metodo == "getMe":
            res = {"username": "falsobot"}
        else:
            res = True
        dados = json.dumps({"ok": True, "result": res}).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def log_message(self, *a):
        pass

    @classmethod
    def mensagem(cls, texto, de=DONO):
        cls.n[0] += 1
        cls.updates.append({"update_id": cls.n[0], "message": {"text": texto, "chat": {"id": CHAT}, "from": {"id": de}}})


class CerebroRoteiro(Provedor):
    """Cérebro de mentira: pede `rm -r logs` quando mandam apagar, e responde usando só o que o Jarvis pôs no contexto."""

    def __init__(self, nome):
        self.nome = nome

    async def conversar(self, mensagens, ferramentas=None):
        ultima_user = max(i for i, m in enumerate(mensagens) if m.papel == "user")
        pedido = mensagens[ultima_user].texto.lower()
        depois = mensagens[ultima_user + 1:]
        resultado = [m.texto for m in depois if m.papel == "tool"]
        if "apaga a pasta logs" in pedido and ferramentas and not resultado:
            return Resposta("", [{"id": "c0", "nome": "rodar_comando", "args": {"comando": "rm -r logs"}}])
        if resultado:
            return Resposta(f"[{self.nome}] {resultado[-1]}")
        if "quando vence" in pedido:
            contexto = " ".join(m.texto for m in mensagens if m.papel == "system")
            return Resposta(f"[{self.nome}] vence dia 12" if "dia 12" in contexto else f"[{self.nome}] nêo sei")
        return Resposta(f"[{self.nome}] anotado")


def rodar_cenario(tmp_path, donos):
    srv = HTTPServer(("127.0.0.1", 0), FalsoTelegram)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    FalsoTelegram.updates.clear(); FalsoTelegram.enviados.clear()
    p = montar_jarvis(CerebroRoteiro("claude"), "local", None, home=str(tmp_path / "dados"))
    area = pathlib.Path(p.config.area)
    (area / "logs").mkdir(parents=True, exist_ok=True)
    (area / "logs" / "a.log").write_text("x")
    bot = telegram_jarvis.canal_telegram()("TOKEN-FALSO", donos, f"http://127.0.0.1:{srv.server_port}", p.auditoria, espera=0)
    ao_receber = telegram_jarvis.fazer_ao_receber(p, lambda n: CerebroRoteiro(n), "claude")
    return srv, p, area, bot, ao_receber


async def enviar_e_esperar(bot, ao_receber, texto, espera_texto, de=DONO, tentativas=200):
    antes = len(FalsoTelegram.enviados)
    FalsoTelegram.mensagem(texto, de)
    for _ in range(tentativas):
        await bot.uma_rodada(ao_receber)
        novos = FalsoTelegram.enviados[antes:]
        if any(espera_texto in t for t in novos):
            return novos
        await asyncio.sleep(0.02)
    return FalsoTelegram.enviados[antes:]


def test_donos_vazio_recusa_e_so_id_responde(tmp_path):
    srv, p, area, bot, ao = rodar_cenario(tmp_path, [])

    async def cenario():
        FalsoTelegram.mensagem("apaga a pasta logs", de=ESTRANHO)
        await bot.uma_rodada(ao)
        await asyncio.sleep(0.1)
        assert FalsoTelegram.enviados == []                 # ninguém é dono: silêncio
        novos = await enviar_e_esperar(bot, ao, "/id", "Seu id é", de=ESTRANHO)
        assert any(str(ESTRANHO) in t for t in novos)
    asyncio.run(cenario())
    srv.shutdown()
    assert (area / "logs").exists()


def test_dono_apagar_pede_ok_nao_mantem_sim_apaga(tmp_path):
    srv, p, area, bot, ao = rodar_cenario(tmp_path, [DONO])

    async def cenario():
        novos = await enviar_e_esperar(bot, ao, "apaga a pasta logs", "Posso rodar")
        assert any("rm -r logs" in t for t in novos)
        novos = await enviar_e_esperar(bot, ao, "/nao", "nêo rodei")
        assert (area / "logs").exists()                    # NêO: a pasta fica
        novos = await enviar_e_esperar(bot, ao, "apaga a pasta logs", "Posso rodar")
        novos = await enviar_e_esperar(bot, ao, "/sim", "saída 0")
        assert not (area / "logs").exists()                # SIM: a pasta some
    asyncio.run(cenario())
    srv.shutdown()


def test_cerebro_troca_e_o_novo_lembra(tmp_path):
    srv, p, area, bot, ao = rodar_cenario(tmp_path, [DONO])

    async def cenario():
        await enviar_e_esperar(bot, ao, "lembre que o prazo do contrato da cliente Marta vence dia 12", "[claude]")
        novos = await enviar_e_esperar(bot, ao, "/cerebro", "Quem pensa agora: claude")
        novos = await enviar_e_esperar(bot, ao, "/cerebro openrouter", "pago por uso")
        assert ao.estado["nome"] == "openrouter" and p.agente.provedor.nome == "openrouter"
        novos = await enviar_e_esperar(bot, ao, "quando vence o prazo do contrato da cliente Marta?", "vence dia 12")
        assert any(t.startswith("[openrouter] vence dia 12") for t in novos)
        novos = await enviar_e_esperar(bot, ao, "/cerebro gemini", "Nêo conheço")
        assert ao.estado["nome"] == "openrouter"
    asyncio.run(cenario())
    srv.shutdown()


def test_token_fica_fora_do_ambiente(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("TELEGRAM_BOT_TOKEN=123:abc\nDONOS=1,2\n")
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    d = telegram_jarvis.ler_env(env)
    assert d["TELEGRAM_BOT_TOKEN"] == "123:abc" and d["DONOS"] == "1,2"
    assert "TELEGRAM_BOT_TOKEN" not in os.environ        # nunca exportado: os cérebros nêo recebem o token


def test_uma_instancia_so(tmp_path):
    import pytest
    trava = telegram_jarvis.uma_instancia(tmp_path / "x.lock")
    with pytest.raises(SystemExit):
        telegram_jarvis.uma_instancia(tmp_path / "x.lock")
    trava.close()


def test_com_dono_cadastrado_estranho_e_ignorado_e_auditado(tmp_path):
    srv, p, area, bot, ao = rodar_cenario(tmp_path, [DONO])

    async def cenario():
        for texto in ("oi", "apaga a pasta logs", "/cerebro openrouter", "/sim"):
            FalsoTelegram.mensagem(texto, de=ESTRANHO)
            await bot.uma_rodada(ao)
        await asyncio.sleep(0.2)
        assert FalsoTelegram.enviados == []                 # nenhuma resposta ao estranho
        assert ao.estado["nome"] == "claude"                # nem trocou o cérebro
        novos = await enviar_e_esperar(bot, ao, "/id", "Seu id é", de=ESTRANHO)
        assert len(novos) == 1                              # só o /id responde
    asyncio.run(cenario())
    srv.shutdown()
    assert (area / "logs").exists()
    ignorados = [l for l in p.auditoria.ultimas(50) if l.get("tipo") == "telegram_ignorado"]
    assert len(ignorados) == 4 and all(str(l.get("remetente")) == str(ESTRANHO) for l in ignorados)


def test_yes_e_no_tambem_aprovam(tmp_path):
    srv, p, area, bot, ao = rodar_cenario(tmp_path, [DONO])

    async def cenario():
        await enviar_e_esperar(bot, ao, "apaga a pasta logs", "Posso rodar")
        await enviar_e_esperar(bot, ao, "/no", "nêo rodei")
        assert (area / "logs").exists()
        await enviar_e_esperar(bot, ao, "apaga a pasta logs", "Posso rodar")
        await enviar_e_esperar(bot, ao, "/yes", "saída 0")
        assert not (area / "logs").exists()
    asyncio.run(cenario())
    srv.shutdown()
