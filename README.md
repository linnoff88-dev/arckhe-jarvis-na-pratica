ï»¿# ê°Å¸Â§Â  Jarvis na prêÂ¡tica ê¢â¬â cêÂ©rebro trocêÂ¡vel

<div align="center">
  <img src="capa/logo.svg" alt="Arckhé AI" height="48" />
  <p><strong>Arckhé AI</strong></p>
</div>


[![Jarvis na prêÂ¡tica: cêÂ©rebro trocêÂ¡vel](guia/assets/banner.jpg)](https://linnoff88-dev.github.io/arckhe-/guia/)

**ê°Å¸â¡Â§ê°Å¸â¡Â· [PortuguêÂªs](README.md) êÂ· ê°Å¸â¡Âºê°Å¸â¡Â¸ [English](README.en.md) êÂ· ê°Å¸â¡Âªê°Å¸â¡Â¸ [EspaêÂ±ol](README.es.md)**

## O que êÂ©

êâ° o Jarvis do INTELECTO v2, um assistente pessoal grêÂ¡tis, rodando de verdade com trêÂªs "cêÂ©rebros" trocêÂ¡veis: o Claude Code e o Codex, que vocêÂª usa pela assinatura que jêÂ¡ paga, e o OpenRouter, que cobra centavos por uso. Serve para quem quer um assistente no prêÂ³prio computador ou servidor sem ficar preso a uma empresa de IA. A gente pêÂ´s os trêÂªs para ter a mesma conversa, no mesmo servidor, e mediu acerto, tempo e custo. Para usar, vocêÂª precisa de um computador ou servidor Linux e de pelo menos um dos trêÂªs cêÂ©rebros.

## ê°Å¸ââ Guia de uso

Guia completo (o ganho, como funciona, qual cêÂ©rebro usar e a prova medida): **https://linnoff88-dev.github.io/arckhe-/guia/**

<!-- VIDEO: entra o explicavideo do projeto quando publicado -->

## Comece pedindo para a sua IA

Abra o Claude Code ou o Codex na mêÂ¡quina onde o Jarvis vai morar e cole:

```text
Leia o projeto "Jarvis na prêÂ¡tica" em https://github.com/linnoff88-dev/jarvis-na-pratica (o README explica tudo, inclusive a instalaêÂ§êÂ£o).
Depois confira esta mêÂ¡quina e me responda em portuguêÂªs simples:
1. Quais dos trêÂªs cêÂ©rebros eu jêÂ¡ consigo usar aqui (Claude Code, Codex ou OpenRouter)?
2. O que falta instalar ou ligar, e se a caixa fechada (Docker) funciona nesta mêÂ¡quina.
3. Qual cêÂ©rebro vocêÂª recomenda para mim, e por quêÂª.
NêÂ£o instale nada ainda. Mostre o plano e espere eu dizer sim.
Se eu aprovar, rode primeiro o ensaio sem IA e depois a conversa de teste sêÂ³ no cêÂ©rebro que eu escolher.
```

## O resultado medido (20/11/2026, servidor Linux de 15 GB, caixa Docker ligada, uma rodada por cêÂ©rebro)

A mesma conversa de 6 passos (disco ê¢â â lembrar ê¢â â recordar ê¢â â apagar com NêÆO ê¢â â apagar com SIM ê¢â â `sudo reboot`):

| cêÂ©rebro | modelo | acertos | tempo total | custo cobrado |
|---|---|---|---|---|
| Claude Code (assinatura) | haiku | 6/6 | 38,6 s | US$ 0 (equivalente na API: US$ 0,0033) |
| Codex (assinatura) | gpt-6.2-sol, esforêÂ§o baixo | 6/6 | 41,3 s | US$ 0 |
| OpenRouter (API) | deepseek/deepseek-v4.1-flash | 6/6 | 8,4 s | US$ 0,000891 |

Troca de cêÂ©rebro no meio da conversa (`jarvis.py trocar`): um cêÂ©rebro guarda "o prazo do contrato da cliente Marta vence dia 12", outro responde depois da troca. Claude ê¢â â OpenRouter: "Vence dia 12." OpenRouter ê¢â â Codex: "O prazo do contrato da cliente Marta vence no dia 12." (a memêÂ³ria êÂ© do Jarvis).

As 8 tarefas do `intelecto avaliar`: 8/8 nos trêÂªs (5,9 s, 6,5 s e 1,6 s por tarefa; o OpenRouter cobrou US$ 0,002185).
Os registros brutos estêÂ£o em [`resultados/`](resultados/) (a mêÂ¡quina medida: [`maquina-vps6.txt`](resultados/maquina-vps6.txt); uma instalaêÂ§êÂ£o do zero: [`instalacao-limpa-2026-11-20.txt`](resultados/instalacao-limpa-2026-11-20.txt)).

---

## InstalaêÂ§êÂ£o têÂ©cnica

### PrêÂ©-requisitos

- Linux com Python 3.10+ e `git`.
- Docker, para a caixa fechada (contêÂªiner `python:3.12-slim` sem rede). Sem Docker, use `--executor local`.
- Pelo menos um cêÂ©rebro:
  - **Claude Code** logado na assinatura (`claude` no PATH). Nenhuma `ANTHROPIC_API_KEY` êÂ© usada: o kit tira essas variêÂ¡veis do processo.
  - **Codex** logado no ChatGPT (`codex login`; `codex` no PATH, versêÂ£o recente). Nenhuma `OPENAI_API_KEY` êÂ© usada.
  - **OpenRouter**: `OPENROUTER_API_KEY` no ambiente, ou num arquivo `.env` apontado por `OPENROUTER_ENV` (padrêÂ£o `~/.config/ARCKHÉ/.env`). Paga por uso.

### Instalar

```bash
git clone https://github.com/linnoff88-dev/jarvis-na-pratica && cd jarvis-na-pratica
./instalar.sh        # cria .venv, instala o INTELECTO v2 (commit d428f31 = v2.3.2) e roda os testes
```

### Usar

```bash
.venv/bin/python jarvis.py medir --cerebros mock --executor local   # ensaio sem IA e sem Docker (ver abaixo)
.venv/bin/python jarvis.py medir                                    # a mesma conversa nos 3 cêÂ©rebros ê¢â â resultados/
.venv/bin/python jarvis.py medir --cerebros claude                  # sêÂ³ um
.venv/bin/python jarvis.py avaliar --cerebro codex                  # as 8 tarefas do intelecto avaliar
.venv/bin/python jarvis.py conversar --cerebro openrouter           # conversa no terminal (OK pedido no terminal)
.venv/bin/python jarvis.py trocar --de claude --para openrouter     # troca o cêÂ©rebro no meio: o novo lembra?
```

**Ensaio sem IA:** o cêÂ©rebro `mock` êÂ© um cêÂ©rebro de mentira que vem com o INTELECTO. Ele nêÂ£o pensa (sêÂ³ entende pedidos que comeêÂ§am com `rode:`), entêÂ£o metade dos passos sai como falha, e isso êÂ© esperado. Serve sêÂ³ para conferir que a instalaêÂ§êÂ£o, a memêÂ³ria, a trava e a mediêÂ§êÂ£o funcionam antes de gastar com uma IA de verdade.

**No dia a dia:** pelo Telegram (seêÂ§êÂ£o abaixo) ou pelo terminal: `conversar` abre a conversa; quando o cêÂ©rebro pede uma ordem que muda algo, aparece `rodar 'ê¢â¬Â¦'? [s/N]` e sêÂ³ roda com `s`.

**Entrar no servidor e logar sem navegador:** `ssh usuêÂ¡rio@endereêÂ§o` (Terminal do Windows/PowerShell ou Terminal do Mac). O Claude Code mostra um link para abrir no navegador do seu computador e pede o cêÂ³digo de volta; o Codex usa `codex login --device-auth`.

**Onde foi testado:** sêÂ³ num servidor Linux alugado (Ubuntu 24.04, 4 processadores, 15 GB; [`resultados/maquina-vps6.txt`](resultados/maquina-vps6.txt)). Claude Code e Codex rodam em Windows, Mac e Linux pelas pêÂ¡ginas oficiais ([Claude Code](https://code.claude.com/docs/en/setup), [Codex](https://developers.openai.com/codex/cli)), mas o kit e a caixa Docker sêÂ³ foram provados no Linux.

VariêÂ¡veis êÂºteis: `CODEX_MODELO` (padrêÂ£o `gpt-6.2-sol`), `CODEX_ESFORCO` (`low`), `OPENROUTER_MODELO` (`deepseek/deepseek-v4.1-flash`), `CLAUDE_BIN`, `CODEX_BIN`.

### Usar pelo Telegram

1. **Crie o bot:** no Telegram, `@BotFather` ê¢â â `/newbot` ê¢â â copie o token.
2. **Guarde o token e os donos no `.env` do kit.** O arquivo fica fora do git. Cole o token direto no terminal da mêÂ¡quina (por exemplo, `nano .env`), nunca na conversa com a IA nem em chat:
   ```bash
   # na pasta do kit
   touch .env && chmod 600 .env
   nano .env      # escreva TELEGRAM_BOT_TOKEN=<cole o token> e, na linha de baixo, DONOS=
                  # salvar: Ctrl+O e Enter êÂ· sair: Ctrl+X  (o token nêÂ£o fica no histêÂ³rico do terminal)
   ```
3. **Descubra o seu id:** ligue uma vez (`.venv/bin/python jarvis.py telegram`), mande `/id` ao bot, pare com Ctrl+C e ponha o nêÂºmero em `DONOS=` (vêÂ¡rios: `DONOS=111,222`). Com `DONOS` vazio o bot sêÂ³ responde `/id`.
4. **Ligue como serviêÂ§o** (volta sozinho depois de reiniciar a mêÂ¡quina; precisa de `loginctl enable-linger $USER` para rodar sem vocêÂª logado):
   ```bash
   mkdir -p dados/area ~/.config/systemd/user
   cp systemd/jarvis-na-pratica-telegram.gerado.service ~/.config/systemd/user/jarvis-na-pratica-telegram.service   # o instalar.sh gerou com o caminho desta pasta
   systemctl --user daemon-reload && systemctl --user enable --now jarvis-na-pratica-telegram
   journalctl --user -u jarvis-na-pratica-telegram -f      # deve mostrar "Jarvis no Telegram: @seu_bot"
   ```
   Parar: `systemctl --user stop jarvis-na-pratica-telegram` êÂ· religar: `systemctl --user restart jarvis-na-pratica-telegram` êÂ· desligar de vez: `systemctl --user disable --now jarvis-na-pratica-telegram`.
5. **Comandos no chat:** `/cerebro` (mostra quem pensa) êÂ· `/cerebro claude|codex|openrouter` (troca; memêÂ³ria e trava ficam) êÂ· `/sim` e `/nao` (aprovaêÂ§êÂ£o, 120 s; `/yes`, `/no` e `/si` tambêÂ©m valem) êÂ· `/id` êÂ· `/ajuda`.

Por dentro: `telegram_jarvis.py` usa o canal do prêÂ³prio INTELECTO (`intelecto/canais/telegram.py`: lista de donos, `/id`, aprovaêÂ§êÂ£o por `/sim` `/nao`), com long polling (sem porta aberta) e trava de arquivo (uma instêÂ¢ncia sêÂ³). O token êÂ© lido do `.env` sem ir para o ambiente do processo, entêÂ£o o `claude -p` e o `codex exec` nunca o recebem. A memêÂ³ria e a pasta de trabalho ficam em `dados/` (variêÂ¡vel `JARVIS_HOME`) e duram entre reinêÂ­cios. O serviêÂ§o comeêÂ§a com o cêÂ©rebro `claude`; o OpenRouter sêÂ³ entra se vocêÂª mandar `/cerebro openrouter`.

### Como funciona por dentro

| arquivo | o que faz |
|---|---|
| `cerebros/comum.py` | as regras do cêÂ©rebro, a conversa em texto e a conversêÂ£o da resposta para o formato do INTELECTO |
| `cerebros/claude.py` | `claude -p --tools "" --json-schema ê¢â¬Â¦` numa pasta vazia: o Claude sêÂ³ decide, nêÂ£o roda nada |
| `cerebros/codex.py` | `codex exec -s read-only --ephemeral --output-schema ê¢â¬Â¦` com o prompt pelo stdin (fechado); argumentos chegam em `args_json` porque o esquema da OpenAI êÂ© estrito |
| `cerebros/openrouter.py` | chamada `chat/completions` com ferramentas nativas e `usage.include` (o custo vem da conta) |
| `telegram_jarvis.py` | modo Telegram: canal do INTELECTO + `/cerebro` para trocar a IA na conversa, token sêÂ³ do `.env`, uma instêÂ¢ncia |
| `systemd/jarvis-na-pratica-telegram.service` | o serviêÂ§o de usuêÂ¡rio que mantêÂ©m o bot no ar |
| `jarvis.py` | monta as 8 peêÂ§as do INTELECTO com o cêÂ©rebro escolhido (`montar(config, provedor=ê¢â¬Â¦)`), sem mudar o INTELECTO; `medir`, `avaliar`, `conversar`, `trocar` |
| `instalar.sh` | venv + INTELECTO v2 fixo + conferêÂªncia + testes |
| `testes/test_cerebros.py` | 8 testes sem modelo: Claude e Codex falsos (scripts), OpenRouter falso (servidor local), conversa inteira com o mock |
| `testes/test_telegram.py` | 7 testes sem Telegram nem modelo: Telegram falso (servidor local) e cêÂ©rebros de roteiro ê¢â¬â sem dono sêÂ³ /id responde; com dono cadastrado, quem êÂ© de fora êÂ© ignorado e anotado na auditoria; dono passa; /nao mantêÂ©m, /sim apaga (e /no, /yes); /cerebro troca e lembra; token fora do ambiente; uma instêÂ¢ncia |
| `resultados/` | os JSON e MD das mediêÂ§êÂµes |

O cêÂ©rebro nunca toca na mêÂ¡quina. Ele devolve `{"texto", "chamadas"}`; quem roda êÂ© o INTELECTO, depois da trava: comando que sêÂ³ lêÂª passa, qualquer outro pede o OK do dono, e os destrutivos conhecidos (`sudo`, `reboot`, `mkfs`, `rm -rf /`ê¢â¬Â¦) sêÂ£o barrados mesmo com OK. O que roda vai para a caixa Docker sem rede, presa na pasta de trabalho, e tudo entra no registro de auditoria.

### Testes

```bash
.venv/bin/python -m pytest -q testes     # 15 passed, sem chamar nenhum modelo nem o Telegram
```

## O processo, do inêÂ­cio ao fim

| # | passo | comando | quem faz |
|---|---|---|---|
| 1 | Conferir a mêÂ¡quina (Python, Docker, quais cêÂ©rebros existem) | `./instalar.sh` | ê¢Å¡â¢ê¯Â¸Â script |
| 2 | Ensaio sem IA | `jarvis.py medir --cerebros mock --executor local` | ê¢Å¡â¢ê¯Â¸Â script |
| 3 | Medir a mesma conversa nos cêÂ©rebros | `jarvis.py medir` | ê¢Å¡â¢ê¯Â¸Â script (chama ê°Å¸Â¤â `claude -p`, ê°Å¸Â¤â `codex exec` e a API do OpenRouter) |
| 4 | Rodar as 8 tarefas do teste padrêÂ£o | `jarvis.py avaliar --cerebro <nome>` | ê¢Å¡â¢ê¯Â¸Â script |
| 4b | Trocar o cêÂ©rebro no meio da conversa | `jarvis.py trocar --de <nome> --para <nome>` | ê¢Å¡â¢ê¯Â¸Â script |
| 5 | Conferir os resultados e escolher o cêÂ©rebro | `resultados/*.md` | ê°Å¸Â§Â  vocêÂª |
| 6 | Usar no dia a dia pelo terminal | `jarvis.py conversar --cerebro <nome>` | ê°Å¸Â§Â  vocêÂª |
| 7 | Ligar o bot do Telegram | `.env` + `systemctl --user enable --now jarvis-na-pratica-telegram` | ê°Å¸Â§Â  vocêÂª + ê¢Å¡â¢ê¯Â¸Â serviêÂ§o |
| 8 | Conversar e trocar a IA pelo celular | `/cerebro codex` | ê°Å¸Â§Â  vocêÂª |

## CrêÂ©ditos e licenêÂ§a

ConstruêÂ­do sobre o [INTELECTO v2](https://github.com/linnoff88-dev/intelecto-v2) ([guia](https://linnoff88-dev.github.io/arckhe-/guia/)). MIT.
GrêÂ¡tis no [ARCKHÉ AI](https://ARCKHÉ AI), direto na internet.

---

<div align="center">
  <img src="capa/logo.svg" alt="Arckhé AI" height="32" />
  <p><strong>Arckhé AI</strong></p>
</div>