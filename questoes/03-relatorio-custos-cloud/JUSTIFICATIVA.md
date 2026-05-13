# Justificativa — T-A-G (Questão 03)

**Task:** define audiência (Goldie/CEO), objetivo numérico (**15%** sem degradar SLA) e insumo (CSV) — isso ancora o “o quê”.

**Action:** enumera passos analíticos (total, oportunidades, campos obrigatórios, ordenação, seção de gap) — isso vira o “como”.

**Goal:** fecha o formato de entrega (Markdown, tabela com colunas exigidas, tom executivo) — isso define o “para quê” e evita resposta genérica.

**Nota sobre output ruim:** `OUTPUT_tentativa_ruim.md` mostra o tipo de falha que aparece quando o modelo **não** amarra percentuais ao denominador correto e ignora restrições de SLA; na prática eu refinaría o prompt com **cálculo explícito do total** e uma linha “não sugira mudanças que violem Multi-AZ sem mitigação”.
