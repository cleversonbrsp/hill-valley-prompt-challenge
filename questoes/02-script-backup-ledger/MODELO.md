**Modelo:** Claude Sonnet 4.5 (Anthropic), via agente Cursor — geração local a partir do `PROMPT.txt` (sem chave de API no shell).

**Por que esse modelo:** o cenário mistura bash, cron, AWS CLI e operação segura de credenciais; modelos “Sonnet-class” costumam manter `set -euo pipefail`, logging e fluxos de erro mais coerentes.

**Reprodução com API Anthropic:** `python3 scripts/run_anthropic.py questoes/02-script-backup-ledger/PROMPT.txt`
