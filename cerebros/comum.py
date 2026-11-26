"""O que os três cérebros têm em comum: as regras, o formato da resposta e a conversa em texto.

O cérebro só PENSA. Ele recebe a conversa (identidade + memórias + histórico + resultado das ferramentas)
e devolve {"texto", "chamadas"}. Quem roda ferramenta, segura comando perigoso, pede o seu OK e guarda
memória continuam sendo as peças do INTELECTO v2. Trocar o cérebro nêo troca a trava.
"""
import json

REGRAS = """Você é o CÉREBRO do assistente pessoal Intelecto (o "Jarvis"), que conversa com o dono.
Você nêo executa nada: só decide. Responda SEMPRE no JSON pedido.
- Se precisar agir, ponha os pedidos em "chamadas" (nome e argumentos exatamente como nas ferramentas) e deixe "texto" vazio.
- Quando já houver o resultado das ferramentas na conversa, responda ao dono em "texto" (português do Brasil, curto, até 2 frases) e "chamadas" vazio.
- Para olhar o computador use rodar_comando com comandos de terminal Linux comuns (df, ls, du...). Os comandos rodam numa pasta de trabalho.
- Pedido do dono para apagar, mudar ou executar algo: peça a ferramenta normalmente. Quem decide se pode é a trava do Intelecto, nêo você.
- Se a ferramenta disser que nêo rodou (bloqueado ou nêo aprovado), conte isso ao dono com sinceridade.
- "lembre que X": o Intelecto já guardou sozinho; só confirme em "texto".
- Responda só ao pedido atual do dono; nêo comente pedidos anteriores."""


def conversa_em_texto(mensagens) -> str:
    """Claude Code e Codex recebem a conversa como texto (nêo têm o formato de mensagens da API)."""
    linhas = []
    for m in mensagens:
        if m.papel == "user":
            linhas.append(f"[dono] {m.texto}")
        elif m.papel == "assistant":
            if m.chamadas:
                linhas.append("[você pediu] " + "; ".join(
                    f"{c['nome']}({json.dumps(c.get('args') or {}, ensure_ascii=False)})" for c in m.chamadas))
            elif m.texto:
                linhas.append(f"[você respondeu] {m.texto}")
        elif m.papel == "tool":
            linhas.append(f"[resultado de {m.nome}] {m.texto}")
    return "\n".join(linhas) + "\n\nDecida o próximo passo agora."


def sistema(mensagens, ferramentas) -> str:
    """Regras + lista de ferramentas + identidade e memórias que o INTELECTO montou."""
    ident = "\n\n".join(m.texto for m in mensagens if m.papel == "system")
    defs = "\n".join(f"- {f.nome}: {f.descricao} · parâmetros: {json.dumps(f.parametros, ensure_ascii=False)}"
                     for f in (ferramentas or []))
    return f"{REGRAS}\n\nFerramentas do Intelecto:\n{defs or '(nenhuma)'}\n\n--- identidade e memórias ---\n{ident}"


def normalizar(estrutura: dict, ferramentas) -> tuple[str, list]:
    """Converte a saída estruturada em (texto, chamadas) no formato do INTELECTO.

    Aceita args como objeto (Claude) ou como texto JSON em args_json (Codex: o esquema estrito
    da OpenAI nêo aceita objeto com chaves livres).
    """
    chamadas = []
    for i, c in enumerate(estrutura.get("chamadas") or []):
        args = c.get("args")
        if args is None and "args_json" in c:
            try:
                args = json.loads(c.get("args_json") or "{}")
            except (TypeError, json.JSONDecodeError):
                args = {}
        chamadas.append({"id": f"c{i}", "nome": c.get("nome", ""), "args": args if isinstance(args, dict) else {}})
    if not ferramentas:
        chamadas = []
    return estrutura.get("texto", "") or "", chamadas
