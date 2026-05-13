# Decisão de organização do repositório

O enunciado deixa a **organização interna livre**, com a orientação de **guardar a decisão** para comparar depois com o Capítulo 4 (criação e versionamento de prompts).

## O que foi escolhido

1. **Uma pasta numerada por questão** (`questoes/01-...` até `questoes/08-...`), com slug curto no nome para navegação humana e URLs estáveis.
2. **Quatro arquivos fixos por questão** — `PROMPT.txt`, `MODELO.md`, `OUTPUT.md`, `JUSTIFICATIVA.md` — para o avaliador nunca precisar adivinhar onde está cada campo obrigatório.
3. **`PROMPT.txt` em texto puro** para permitir `diff` limpo, cópia direta para APIs e automação (`scripts/run_*.py`) sem interpretar Markdown.
4. **`OUTPUT.md` em Markdown** porque várias respostas são relatórios, runbooks ou múltiplos blocos de código com anotações.
5. **`docs/`** só para meta (esta decisão), mantendo **toda a nota da entrega** sob `questoes/`.

## Trade-offs conscientes

- **Prós:** previsível para correção; fácil de versionar por questão; prompts “copiáveis” sem ruído de formatação.
- **Contras:** mais arquivos do que um único `ENTREGA.md` monolítico; quem prefere tudo em um notebook precisa juntar manualmente.

Se no Capítulo 4 surgir convenção de `prompts/` versionados por data ou por `semver`, esta árvore pode ganhar um `prompts/v1/` sem mudar o significado dos quatro arquivos por questão.
