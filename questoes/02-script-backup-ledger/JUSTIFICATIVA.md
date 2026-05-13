# Justificativa — R-T-F (Questão 02)

**Role:** “You are a senior Linux/SRE engineer…” posiciona o modelo para priorizar bash estrito, segurança e operação em cron.

**Task:** a lista numerada cobre `pg_dump` + `gzip`, `aws s3 cp`, retenção de 30 dias no prefixo `ledger/`, logging em `/var/log/ledger-backup.log`, exit codes e restrições (não vazar segredo, não carregar GB na RAM).

**Format:** exige **apenas** um code fence bash completo com `#!/usr/bin/env bash`, impedindo explicações soltas que não sejam o artefato pedido.
