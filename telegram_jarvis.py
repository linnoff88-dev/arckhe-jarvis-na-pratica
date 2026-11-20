"""Modo Telegram do Jarvis na prática: o canal do INTELECTO v2 (donos + /sim /nao) com o cérebro trocável.

    python3 jarvis.py telegram --cerebro claude

- Token e donos vêm do arquivo .env do kit (TELEGRAM_BOT_TOKEN=, DONOS=id1,id2), lidos em tempo de execução.
  O token não vai para o ambiente do processo: os cérebros (claude -p, codex exec) nunca o recebem.
- Long polling (sem porta aberta) e uma instância só (trava de arquivo).
- /cerebro <claude|codex|openrouter> troca a IA na conversa; memória, trava e caixa continuam as do Jarvis.
- A memória fica numa pasta fixa (JARVIS_HOME, padrão ./dados), então dura entre reinícios.
"""
import fcntl
import os
import pathlib

AQUI = pathlib.Path(__file__).resolve().parent

DESCRICAO = {
    "claude": "Claude Code pela assinatura (sem custo a mais)",
    "codex": "Codex pela assinatura do ChatGPT (sem custo a mais)",
    "openrouter": "OpenRouter, pago por uso (na nossa medição, a conversa de 6 pedidos custou US$ 0,0009)",
}
AJUDA = ("Sou o Jarvis. Peça em português: \"quanto espaço livre tem no disco?\", \"lembre que…\", "
         "\"apaga a pasta X\" (eu pergunto antes de mudar algo; responda /sim ou /nao — /yes e /no também valem).\n\n"
         "/cerebro mostra qual IA está pensando · /cerebro claude|codex|openrouter troca · /id mostra o seu id")


SINONIMOS = {"/yes": "/sim", "/si": "/sim", "/sí": "/sim", "/no": "/nao"}   # só os comandos com barra


def canal_telegram():
    """O canal do INTELECTO, aceitando também /yes /no (inglês) e /si /no (espanhol) na aprovação."""
    from intelecto.canais.telegram import Telegram

    class TelegramMultilingue(Telegram):
        async def api(self, metodo, **params):
            d = await super().api(metodo, **params)
            if metodo == "getUpdates":
                for u in d.get("result", []):
                    msg = u.get("message") or {}
                    t = (msg.get("text") or "").strip()
                    if t.lower() in SINONIMOS:
                        msg["text"] = SINONIMOS[t.lower()]
            return d
    return TelegramMultilingue


def ler_env(caminho) -> dict:
    """Lê KEY=valor sem exportar para os.environ (o token não vaza para os subprocessos)."""
    d = {}
    try:
        with open(caminho, encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if linha and not linha.startswith("#") and "=" in linha:
                    k, v = linha.split("=", 1)
                    d[k.strip()] = v.strip().strip('"').strip("'")
    except OSError:
        pass
    return d


def uma_instancia(caminho):
    """Trava de arquivo: um segundo processo sai na hora (dois long pollings brigam pelo mesmo bot)."""
    f = open(caminho, "w")
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit("o bot já está rodando (trava em uso): pare o outro antes")
    return f


def fazer_ao_receber(p, criar, nome_inicial):
    """Devolve a função que o canal Telegram do INTELECTO chama a cada mensagem do dono."""
    estado = {"nome": nome_inicial}

    async def ao_receber(chat, texto, perguntar):
        partes = texto.split()
        cmd = partes[0].lower().split("@")[0] if partes else ""
        if cmd in ("/start", "/ajuda", "/help"):
            return AJUDA
        if cmd == "/cerebro":
            if len(partes) == 1:
                return (f"Quem pensa agora: {estado['nome']} — {DESCRICAO.get(estado['nome'], '')}.\n"
                        "Para trocar: /cerebro claude, /cerebro codex ou /cerebro openrouter. A memória e a trava ficam.")
            nome = partes[1].lower()
            if nome not in DESCRICAO:
                return "Não conheço esse cérebro. Use claude, codex ou openrouter."
            try:
                novo = criar(nome)
            except Exception as e:   # sem chave, sem programa instalado…
                return f"Não consegui ligar o {nome}: {e}. Continuo com o {estado['nome']}."
            p.agente.provedor = novo
            estado["nome"] = nome
            if p.auditoria:
                p.auditoria.registrar("cerebro_trocado", para=nome)
            return f"Pronto: agora quem pensa é o {DESCRICAO[nome]}. Lembro de tudo o que já sabia, e a trava é a mesma."
        p.portao.perguntar = perguntar          # a aprovação vai para o Telegram de quem pediu
        return await p.agente.responder(chat, texto)

    ao_receber.estado = estado
    return ao_receber


async def rodar(nome, executor="caixa"):
    import cerebros
    from jarvis import montar_jarvis
    Telegram = canal_telegram()

    env = ler_env(os.environ.get("JARVIS_ENV", AQUI / ".env"))
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or env.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        raise SystemExit("falta TELEGRAM_BOT_TOKEN no .env do kit")
    donos = [d.strip() for d in (os.environ.get("DONOS") or env.get("DONOS", "")).split(",") if d.strip()]
    url = os.environ.get("TELEGRAM_API") or env.get("TELEGRAM_API", "https://api.telegram.org")
    home = os.path.abspath(os.path.expanduser(os.environ.get("JARVIS_HOME") or env.get("JARVIS_HOME") or str(AQUI / "dados")))
    os.makedirs(home, exist_ok=True)
    trava = uma_instancia(os.path.join(home, ".telegram.lock"))  # noqa: F841 (fica aberta enquanto roda)

    p = montar_jarvis(cerebros.criar(nome), executor, None, home=home)
    bot = Telegram(token, donos, url, p.auditoria)
    eu = (await bot.api("getMe")).get("result", {})
    print(f"Jarvis no Telegram: @{eu.get('username')} · cérebro {nome} · donos {len(donos)} · "
          f"executor {executor} · memória em {home}", flush=True)
    if not donos:
        print("ATENÇÃO: DONOS vazio → o bot só responde /id (mande /id para ele e ponha o número em DONOS)", flush=True)
    await bot.rodar(fazer_ao_receber(p, cerebros.criar, nome))
