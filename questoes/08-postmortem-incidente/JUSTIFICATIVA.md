# Justificativa — Questão 08 (T-A-G + comparação com outros frameworks)

## Framework escolhido: **T-A-G (Task, Action, Goal)**

**Task:** o prompt descreve o entregável (“postmortem de 20 minutos”), o público (Doc/CTO) e a **decisão binária** rollback vs scaling emergencial — isso fixa o problema como “decisão sob incerteza com fatos limitados”.

**Action:** a seção “Action” obriga uma estrutura mínima (sumário, timeline, hipóteses, blast radius, recomendação primária/fallback, lacunas) — isso força o modelo a **encadear evidências** em vez de soltar um veredito solto.

**Goal:** o “Goal” exige reconciliar alerta de memória vs médias vs logs de DB — isso define o critério de qualidade do texto (não ignorar contradições) e melhora a utilidade executiva do output.

## Comparação 1 — **R-T-F** (alternativa)

**O que se ganharia:** maior controle de “persona” (ex.: “você é SRE principal”) e formato muito rígido (útil se a avaliação exigisse saída ultra padronizada).

**O que se perderia:** R-T-F não empurra naturalmente uma **árvore de decisão** com **primário/fallback**; “Format” tende a virar template fixo e pode **achatar** a narrativa de timeline/hipóteses que o Doc precisa em incidente ativo.

## Comparação 2 — **R-I-S-E** (alternativa)

**O que se ganharia:** excelente para **runbook** (passos + verificações + critérios de escalação), muito alinhado a “plantão executando”.

**O que se perderia:** R-I-S-E privilegia **procedimento**; aqui o Doc pediu **postmortem técnico** para **decidir estratégia** (rollback vs scaling). Dá para adaptar, mas vira “lista de passos” sem forçar tão bem **hipóteses ranqueadas + blast radius + lacunas** como o esqueleto do T-A-G neste prompt.

## O que eu faria diferente se o output viesse “ruim”

- Apertar o prompt com **uma linha final**: “Mostre o cálculo explícito \(12 \times 20 \approx 240\)\) e o que acontece se HPA subir réplicas” para evitar modelo que fala genericamente de pool sem amarrar ao limite do RDS.
