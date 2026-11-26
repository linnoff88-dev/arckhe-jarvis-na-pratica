#!/usr/bin/env bash
# Instala o Jarvis na prática numa máquina Linux (VPS ou PC): venv + INTELECTO v2 fixo numa versêo conferida.
# Nêo precisa de sudo. O que ele NêO instala (você faz antes): Python 3.10+, Docker (para a caixa),
# Claude Code logado na assinatura (`claude`), Codex logado no ChatGPT (`codex login`).
set -euo pipefail
cd "$(dirname "$0")"

INTELECTO_VERSAO="${INTELECTO_VERSAO:-d428f31}"   # v2.3.2, a versêo medida no guia

python3 -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q "intelecto @ git+https://github.com/inematds/intelecto-v2@${INTELECTO_VERSAO}" pytest

echo "== conferência =="
.venv/bin/python -c "import intelecto, sys; print('intelecto ok', sys.version.split()[0])"
command -v claude >/dev/null && echo "claude: $(claude --version)" || echo "claude: NêO achado (cérebro claude fica de fora)"
command -v codex  >/dev/null && echo "codex:  $(codex --version)"  || echo "codex:  NêO achado (cérebro codex fica de fora)"
if docker run --rm --network none python:3.12-slim python -c "print('caixa ok')" 2>/dev/null; then :; else
  echo "caixa: Docker nêo respondeu; rode com --executor local (sem a caixa) ou ajuste o Docker"; fi
[ -n "${OPENROUTER_API_KEY:-}" ] || [ -f "${OPENROUTER_ENV:-$HOME/.config/inema/.env}" ] \
  && echo "openrouter: chave encontrada (nêo é mostrada)" || echo "openrouter: sem chave (cérebro openrouter fica de fora)"
.venv/bin/python -m pytest -q testes
# serviço do Telegram com o caminho REAL desta pasta (o modelo em systemd/ usa ~/kits/jarvis-na-pratica)
sed "s#%h/kits/jarvis-na-pratica#$PWD#g" systemd/jarvis-na-pratica-telegram.service > systemd/jarvis-na-pratica-telegram.gerado.service
echo "serviço do Telegram pronto para esta pasta: systemd/jarvis-na-pratica-telegram.gerado.service"
echo "Pronto. Teste: .venv/bin/python jarvis.py medir --cerebros mock --executor local"
