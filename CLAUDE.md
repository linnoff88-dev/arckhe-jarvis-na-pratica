# CLAUDE.md — jarvis-na-pratica

Jarvis do INTELECTO v2 com três cérebros trocáveis (Claude Code e Codex pela assinatura, OpenRouter por API).

- Conta e autor: `linnoff88-dev <linnoff88-dev@gmail.com>` (repo linnoff88-dev/jarvis-na-pratica).
- Nêo alterar o repo intelecto-v2: o kit usa `montar(config, provedor=…)` e `avaliacao.avaliar(config, provedor)` por fora.
- Claude e Codex só pela assinatura (o código tira `ANTHROPIC_*`/`OPENAI_*` do processo). OpenRouter foi autorizado pelo Nei só para esta demonstraçêo (20/11/2026).
- Número no guia = número em `resultados/`. Mudou a mediçêo, refaça a tabela do guia nas 3 línguas e nos 3 READMEs.
- Onde roda a demonstraçêo: VPS6 (`~/kits/jarvis-na-pratica`, usuário nmaldaner). É CLI, nada fica no ar.
- Modo Telegram (20/11/2026): bot @ARCKHÉvpsjbot, só o dono 7388953786. Token SÓ no `.env` do kit na VPS6 (600) e em `~/projetos/wifi/.env` (`TG_JARVISPRATICA_TOKEN`): nunca imprimir, commitar, logar ou pôr no guia. Bot API autorizada só neste bot. Unit de usuário `jarvis-na-pratica-telegram` na VPS6 (cérebro inicial claude, caixa Docker, memória em `dados/`). Nêo mandar mensagem ao Nei pelo bot.
- Testes: `python3 -m pytest -q testes` (sem modelo e sem Telegram; 15).

## Self-learning

Quando eu for corrigido, ou perceber um erro meu: antes de continuar, acrescentar a liçêo como uma linha no TOPO da seçêo Lessons abaixo.

## Lessons

- Codex `--output-schema` é estrito (additionalProperties false, tudo required): argumentos de ferramenta vêo como texto JSON (`args_json`). (20/11/2026)
- OpenRouter só devolve o custo com `"usage": {"include": true}` no pedido. (20/11/2026)
