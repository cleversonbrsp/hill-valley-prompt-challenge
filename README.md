# Hill Valley Tech — Desafio de Prompt Engineering

Entrega do desafio **Um dia na Hill Valley Tech**: oito cenários com **prompt** (texto exato), **modelo** escolhido, **output** registrado e **justificativa** do framework (R-T-F, T-A-G, B-A-B, C-A-R-E, R-I-S-E).

## Estrutura do repositório

| Caminho | Conteúdo |
|---------|----------|
| `docs/decisao-de-organizacao.md` | Por que esta árvore de pastas (para o Capítulo 4). |
| `questoes/NN-*/` | Uma pasta por questão: `PROMPT.txt`, `MODELO.md`, `OUTPUT.md`, `JUSTIFICATIVA.md`. |
| `scripts/` | Scripts opcionais para reexecutar prompts com **OpenAI** ou **Anthropic** quando houver chaves. |

Cada `questoes/NN-*` segue o contrato do enunciado: quatro arquivos obrigatórios por questão.

## Providers (requisito: ≥ 2)

| Questões | Provider sugerido | Motivo |
|----------|-------------------|--------|
| 01, 02, 05, 07 | **Anthropic** (ex.: Claude Sonnet) | Código, shell, Kubernetes e runbook procedural tendem a sair mais consistentes com forte ênfase em instruções e segurança. |
| 03, 04, 06, 08 | **OpenAI** (ex.: GPT-4o) | Relatórios tabulares, SQL, HCL e texto executivo/comparativo costumam responder bem a formato estrito. |

**Como estes arquivos foram gerados:** no ambiente onde o repositório foi montado **não havia** `OPENAI_API_KEY` nem `ANTHROPIC_API_KEY` no shell. Os `OUTPUT.md` foram produzidos executando os **PROMPT.txt** literais nesta mesma sessão de agente (modelo de código da Cursor). Para alinhar à avaliação com **duas APIs distintas**, use `scripts/run_openai.py` e `scripts/run_anthropic.py` (ou cole cada `PROMPT.txt` no ChatGPT e no Claude conforme a tabela) e substitua os outputs na pasta correspondente.

## Questão 03 — tentativa ruim (bônus do enunciado)

Em `questoes/03-relatorio-custos-cloud/OUTPUT_tentativa_ruim.md` há um exemplo de saída **fraca** (percentuais somando errado e sem esforço/risco), comentada na `JUSTIFICATIVA.md`.

## Publicar no GitHub

```bash
cd "/home/cleverson/repos/desafios/Um dia na Hill Valley Tech/hill-valley-prompt-challenge"
git init
git add .
git commit -m "Entrega: prompts, outputs e justificativas (8 questões)"
gh repo create hill-valley-prompt-challenge --public --source=. --remote=origin --push
```

Se `gh` não estiver autenticado, crie o repositório vazio no GitHub e:

```bash
git remote add origin https://github.com/cleversonbrsp/hill-valley-prompt-challenge.git
git branch -M main
git push -u origin main
```

## Link da entrega (repositório público)

https://github.com/cleversonbrsp/hill-valley-prompt-challenge
