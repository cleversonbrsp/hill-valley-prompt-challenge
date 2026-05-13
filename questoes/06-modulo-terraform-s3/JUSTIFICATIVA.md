# Justificativa — C-A-R-E (Questão 06)

**Context:** descreve o padrão interno HVT (tags, prefixo `hvt-`, requisitos de S3 e estilo de variáveis) e a versão do provider.

**Action:** pede explicitamente um módulo Terraform reutilizável com arquivos (`variables.tf`, `main.tf`, `outputs.tf`) e exemplo de consumo.

**Result:** define o “done” verificável: buckets com encryption/versioning/BPA/logging + `outputs` úteis.

**Example:** incorpora o trecho do módulo VPC como **referência de estilo** (sem copiar o recurso), guiando `locals.common_tags` e `merge` de tags como no padrão da empresa.
