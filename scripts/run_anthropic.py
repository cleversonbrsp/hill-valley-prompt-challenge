#!/usr/bin/env python3
"""
Opcional: reexecuta um PROMPT.txt contra a API Anthropic e imprime a resposta.
Uso:
  export ANTHROPIC_API_KEY=...
  python3 scripts/run_anthropic.py ../questoes/01-dockerfile-lift/PROMPT.txt

Requer: pip install anthropic
"""
from __future__ import annotations

import os
import sys


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: python3 scripts/run_anthropic.py <caminho/PROMPT.txt>", file=sys.stderr)
        return 2
    path = sys.argv[1]
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        print("Defina ANTHROPIC_API_KEY.", file=sys.stderr)
        return 1
    try:
        import anthropic
    except ImportError:
        print("Instale: pip install anthropic", file=sys.stderr)
        return 1

    prompt = open(path, encoding="utf-8").read()
    client = anthropic.Anthropic(api_key=key)
    model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
    msg = client.messages.create(
        model=model,
        max_tokens=8192,
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}],
    )
    for block in msg.content:
        if block.type == "text":
            print(block.text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
