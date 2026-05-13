#!/usr/bin/env python3
"""
Opcional: reexecuta um PROMPT.txt contra a API OpenAI e imprime a resposta.
Uso:
  export OPENAI_API_KEY=...
  python3 scripts/run_openai.py ../questoes/01-dockerfile-lift/PROMPT.txt

Requer: pip install openai
"""
from __future__ import annotations

import os
import sys


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: python3 scripts/run_openai.py <caminho/PROMPT.txt>", file=sys.stderr)
        return 2
    path = sys.argv[1]
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        print("Defina OPENAI_API_KEY.", file=sys.stderr)
        return 1
    try:
        from openai import OpenAI
    except ImportError:
        print("Instale: pip install openai", file=sys.stderr)
        return 1

    prompt = open(path, encoding="utf-8").read()
    client = OpenAI(api_key=key)
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    print(resp.choices[0].message.content or "")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
