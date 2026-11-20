# 🧠 Jarvis en la práctica — cerebro intercambiable

[![Jarvis en la práctica: cerebro intercambiable](guia/assets/banner-es.jpg)](https://inematds.github.io/jarvis-na-pratica/guia/es/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## Qué es

Es el Jarvis de INTELECTO v2, un asistente personal gratis que funciona de verdad con tres “cerebros” intercambiables: Claude Code y Codex, que usas con la suscripción que ya pagas, y OpenRouter, que cobra centavos por uso. Sirve para quienes quieren un asistente en su propia computadora o servidor sin quedar atados a una empresa de IA. Pusimos los tres a mantener la misma conversación en el mismo servidor y medimos aciertos, tiempo y costo. Para usarlo, necesitas una computadora o servidor Linux y al menos uno de los tres cerebros.

## 📖 Guía de uso

Guía completa (los beneficios, cómo funciona, qué cerebro usar y la prueba medida): **https://inematds.github.io/jarvis-na-pratica/guia/es/**

<!-- VIDEO: entra o explicavideo do projeto quando publicado -->

## Empieza pidiéndoselo a tu IA

Abre Claude Code o Codex en la máquina donde vivirá Jarvis y pega esto:

```text
Lee el proyecto “Jarvis na prática” en https://github.com/inematds/jarvis-na-pratica (el README explica todo, incluida la instalación).
Después revisa esta máquina y respóndeme en portugués sencillo:
1. ¿Cuáles de los tres cerebros puedo usar aquí (Claude Code, Codex u OpenRouter)?
2. ¿Qué falta instalar o activar, y si la caja cerrada (Docker) funciona en esta máquina?
3. ¿Qué cerebro me recomiendas y por qué?
Todavía no instales nada. Muéstrame el plan y espera a que te diga sí.
Si lo apruebo, ejecuta primero el ensayo sin IA y después la conversación de prueba solo con el cerebro que elija.
```

## El resultado medido (20/11/2026, servidor Linux de 15 GB, caja Docker activada, una ronda por cerebro)

La misma conversación de 6 pasos (disco → recordar → recordar → borrar con NO → borrar con SÍ → `sudo reboot`):

| cerebro | modelo | aciertos | tiempo total | costo cobrado |
|---|---|---|---|---|
| Claude Code (suscripción) | haiku | 6/6 | 38,6 s | US$ 0 (equivalente en la API: US$ 0,0033) |
| Codex (suscripción) | gpt-6.2-sol, esfuerzo bajo | 6/6 | 41,3 s | US$ 0 |
| OpenRouter (API) | deepseek/deepseek-v4.1-flash | 6/6 | 8,4 s | US$ 0,000891 |

Cambio de cerebro a mitad de la conversación (`jarvis.py trocar`): un cerebro guarda “el plazo del contrato de la clienta Marta vence el día 12”; otro responde después del cambio. Claude → OpenRouter: “Vence el día 12”. OpenRouter → Codex: “El plazo del contrato de la clienta Marta vence el día 12” (la memoria es de Jarvis).

Las 8 tareas de `intelecto avaliar`: 8/8 con los tres (5,9 s, 6,5 s y 1,6 s por tarea; OpenRouter cobró US$ 0,002185).
Los registros sin procesar están en [`resultados/`](resultados/) (la máquina evaluada: [`maquina-vps6.txt`](resultados/maquina-vps6.txt); una instalación desde cero: [`instalacao-limpa-2026-11-20.txt`](resultados/instalacao-limpa-2026-11-20.txt)).

---

## Instalación técnica

### Requisitos previos

- Linux con Python 3.10+ y `git`.
- Docker, para la caja cerrada (contenedor `python:3.12-slim` sin red). Sin Docker, usa `--executor local`.
- Al menos un cerebro:
  - **Claude Code** con la sesión iniciada en la suscripción (`claude` en el PATH). No se usa ninguna `ANTHROPIC_API_KEY`: el kit quita esas variables del proceso.
  - **Codex** con la sesión iniciada en ChatGPT (`codex login`; `codex` en el PATH, versión reciente). No se usa ninguna `OPENAI_API_KEY`.
  - **OpenRouter**: `OPENROUTER_API_KEY` en el entorno o en un archivo `.env` indicado por `OPENROUTER_ENV` (predeterminado `~/.config/inema/.env`). Se paga por uso.

### Instalar

```bash
git clone https://github.com/inematds/jarvis-na-pratica && cd jarvis-na-pratica
./instalar.sh        # crea .venv, instala INTELECTO v2 (commit d428f31 = v2.3.2) y ejecuta las pruebas
```

### Usar

```bash
.venv/bin/python jarvis.py medir --cerebros mock --executor local   # ensayo sin IA y sin Docker (ver abajo)
.venv/bin/python jarvis.py medir                                    # la misma conversación con los 3 cerebros → resultados/
.venv/bin/python jarvis.py medir --cerebros claude                  # solo uno
.venv/bin/python jarvis.py avaliar --cerebro codex                  # las 8 tareas de intelecto avaliar
.venv/bin/python jarvis.py conversar --cerebro openrouter           # conversación en la terminal (OK solicitado en la terminal)
.venv/bin/python jarvis.py trocar --de claude --para openrouter     # cambia el cerebro a mitad: ¿el nuevo recuerda?
```

**Ensayo sin IA:** el cerebro `mock` es un cerebro ficticio que viene con INTELECTO. No piensa (solo entiende solicitudes que empiezan con `rode:`), así que la mitad de los pasos termina en error, y eso es lo esperado. Sirve para comprobar que la instalación, la memoria, el bloqueo y la medición funcionan antes de gastar en una IA de verdad.

**En el día a día:** por Telegram (sección de abajo) o por la terminal: `conversar` abre la conversación; cuando el cerebro solicita una orden que cambia algo, aparece `rodar '…'? [s/N]` y solo se ejecuta con `s`.

**Entrar al servidor e iniciar sesión sin navegador:** `ssh usuario@dirección` (Terminal de Windows/PowerShell o Terminal de Mac). Claude Code muestra un enlace para abrir en el navegador de tu computadora y pide que ingreses el código; Codex usa `codex login --device-auth`.

**Dónde se probó:** solo en un servidor Linux alquilado (Ubuntu 24.04, 4 procesadores, 15 GB; [`resultados/maquina-vps6.txt`](resultados/maquina-vps6.txt)). Claude Code y Codex funcionan en Windows, Mac y Linux según sus páginas oficiales ([Claude Code](https://code.claude.com/docs/en/setup), [Codex](https://developers.openai.com/codex/cli)), pero el kit y la caja Docker solo se probaron en Linux.

Variables útiles: `CODEX_MODELO` (predeterminado `gpt-6.2-sol`), `CODEX_ESFORCO` (`low`), `OPENROUTER_MODELO` (`deepseek/deepseek-v4.1-flash`), `CLAUDE_BIN`, `CODEX_BIN`.

### Usar por Telegram

1. **Crea el bot:** en Telegram, `@BotFather` → `/newbot` → copia el token.
2. **Guarda el token y los propietarios en el `.env` del kit.** El archivo queda fuera de git. Pega el token directamente en la terminal de la máquina (por ejemplo, `nano .env`), nunca en la conversación con la IA ni en un chat:
   ```bash
   # en la carpeta del kit
   touch .env && chmod 600 .env
   nano .env      # escribe TELEGRAM_BOT_TOKEN=<pega el token> y, en la línea de abajo, DONOS=
                  # guardar: Ctrl+O y Enter · salir: Ctrl+X  (el token no queda en el historial de la terminal)
   ```
3. **Averigua tu id:** enciéndelo una vez (`.venv/bin/python jarvis.py telegram`), envíale `/id` al bot, detenlo con Ctrl+C y pon el número en `DONOS=` (varios: `DONOS=111,222`). Si `DONOS` está vacío, el bot solo responde a `/id`.
4. **Actívalo como servicio** (se inicia solo después de reiniciar la máquina; necesita `loginctl enable-linger $USER` para funcionar sin que hayas iniciado sesión):
   ```bash
   mkdir -p dados/area ~/.config/systemd/user
   cp systemd/jarvis-na-pratica-telegram.gerado.service ~/.config/systemd/user/jarvis-na-pratica-telegram.service   # instalar.sh lo generó con la ruta de esta carpeta
   systemctl --user daemon-reload && systemctl --user enable --now jarvis-na-pratica-telegram
   journalctl --user -u jarvis-na-pratica-telegram -f      # debe mostrar "Jarvis no Telegram: @seu_bot"
   ```
   Detener: `systemctl --user stop jarvis-na-pratica-telegram` · reiniciar: `systemctl --user restart jarvis-na-pratica-telegram` · desactivar definitivamente: `systemctl --user disable --now jarvis-na-pratica-telegram`.
5. **Comandos en el chat:** `/cerebro` (muestra quién piensa) · `/cerebro claude|codex|openrouter` (cambia; la memoria y el bloqueo se mantienen) · `/sim` (sí) y `/nao` (no) (aprobación, 120 s; `/yes`, `/no` y `/si` también funcionan) · `/id` · `/ajuda`.

Por dentro: `telegram_jarvis.py` usa el canal propio de INTELECTO (`intelecto/canais/telegram.py`: lista de propietarios, `/id`, aprobación por `/sim` `/nao`), con long polling (sin puerto abierto) y bloqueo de archivo (una sola instancia). El token se lee del `.env` sin pasar al entorno del proceso, así que `claude -p` y `codex exec` nunca lo reciben. La memoria y la carpeta de trabajo quedan en `dados/` (variable `JARVIS_HOME`) y persisten entre reinicios. El servicio empieza con el cerebro `claude`; OpenRouter solo se activa si envías `/cerebro openrouter`.

### Cómo funciona por dentro

| archivo | qué hace |
|---|---|
| `cerebros/comum.py` | las reglas del cerebro, la conversación en texto y la conversión de la respuesta al formato de INTELECTO |
| `cerebros/claude.py` | `claude -p --tools "" --json-schema …` en una carpeta vacía: Claude solo decide, no ejecuta nada |
| `cerebros/codex.py` | `codex exec -s read-only --ephemeral --output-schema …` con el prompt por stdin (cerrado); los argumentos llegan en `args_json` porque el esquema de OpenAI es estricto |
| `cerebros/openrouter.py` | llamada `chat/completions` con herramientas nativas y `usage.include` (el costo aparece en la cuenta) |
| `telegram_jarvis.py` | modo Telegram: canal de INTELECTO + `/cerebro` para cambiar la IA en la conversación, token solo desde `.env`, una instancia |
| `systemd/jarvis-na-pratica-telegram.service` | el servicio de usuario que mantiene el bot activo |
| `jarvis.py` | arma las 8 piezas de INTELECTO con el cerebro elegido (`montar(config, provedor=…)`), sin cambiar INTELECTO; `medir`, `avaliar`, `conversar`, `trocar` |
| `instalar.sh` | venv + INTELECTO v2 fijo + comprobación + pruebas |
| `testes/test_cerebros.py` | 8 pruebas sin modelo: Claude y Codex ficticios (scripts), OpenRouter ficticio (servidor local), conversación completa con el mock |
| `testes/test_telegram.py` | 7 pruebas sin Telegram ni modelo: Telegram ficticio (servidor local) y cerebros con guion — sin propietario solo responde `/id`; con propietario registrado, ignora a quienes son de fuera y los anota en la auditoría; el propietario pasa; `/nao` conserva, `/sim` borra (y `/no`, `/yes`); `/cerebro` cambia y recuerda; token fuera del entorno; una instancia |
| `resultados/` | los archivos JSON y MD de las mediciones |

El cerebro nunca toca la máquina. Devuelve `{"texto", "chamadas"}`; quien ejecuta es INTELECTO, después del bloqueo: los comandos que solo leen pasan, cualquier otro necesita la aprobación del propietario, y los destructivos conocidos (`sudo`, `reboot`, `mkfs`, `rm -rf /`…) se bloquean incluso con aprobación. Lo que se ejecuta va a la caja Docker sin red, limitada a la carpeta de trabajo, y todo queda en el registro de auditoría.

### Pruebas

```bash
.venv/bin/python -m pytest -q testes     # 15 passed, sin llamar a ningún modelo ni a Telegram
```

## El proceso, de principio a fin

| # | paso | comando | quién lo hace |
|---|---|---|---|
| 1 | Revisar la máquina (Python, Docker, qué cerebros existen) | `./instalar.sh` | ⚙️ script |
| 2 | Ensayo sin IA | `jarvis.py medir --cerebros mock --executor local` | ⚙️ script |
| 3 | Medir la misma conversación con los cerebros | `jarvis.py medir` | ⚙️ script (llama a 🤖 `claude -p`, 🤖 `codex exec` y a la API de OpenRouter) |
| 4 | Ejecutar las 8 tareas de la prueba estándar | `jarvis.py avaliar --cerebro <nome>` | ⚙️ script |
| 4b | Cambiar el cerebro a mitad de la conversación | `jarvis.py trocar --de <nome> --para <nome>` | ⚙️ script |
| 5 | Revisar los resultados y elegir el cerebro | `resultados/*.md` | 🧠 tú |
| 6 | Usar en el día a día por la terminal | `jarvis.py conversar --cerebro <nome>` | 🧠 tú |
| 7 | Activar el bot de Telegram | `.env` + `systemctl --user enable --now jarvis-na-pratica-telegram` | 🧠 tú + ⚙️ servicio |
| 8 | Conversar y cambiar la IA desde el celular | `/cerebro codex` | 🧠 tú |

## Créditos y licencia

Construido sobre [INTELECTO v2](https://github.com/inematds/intelecto-v2) ([guía](https://inematds.github.io/intelecto-v2/guia/) (en portugués)). MIT.  
Gratis en [inema.club](https://inema.club), directamente en Internet.