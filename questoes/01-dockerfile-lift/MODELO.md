**Modelo:** Claude Sonnet 4.5 (Anthropic), via agente Cursor — **sem** `ANTHROPIC_API_KEY` no shell; a resposta foi gerada localmente pelo modelo do IDE ao colar o `PROMPT.txt`.

**Por que esse modelo:** geração de Dockerfile com foco em segurança (usuário não-root), multi-stage e boas práticas de imagem slim; encaixa no perfil “plataforma / Kubernetes” da questão.

**Reprodução com API Anthropic:** `python3 scripts/run_anthropic.py questoes/01-dockerfile-lift/PROMPT.txt`
