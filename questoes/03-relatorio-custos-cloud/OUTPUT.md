# Output — Questão 03

## Executive summary

- **Meta:** reduzir **≥ 15%** do gasto mensal AWS do mês de referência **sem degradar SLA**.
- **Gasto total (CSV):** **USD 41.800 / mês** (soma das linhas do enunciado).
- **Alvo de economia (15%):** **USD 6.270 / mês**.
- **Leitura rápida:** dá para montar um **portfólio** que fecha a meta com **risco controlado**, desde que itens de banco e compute sejam tratados com mudanças **graduais** e **validação de SLO**.

## Portfólio de oportunidades (ordenado por impacto)

> **Assunções explícitas:** faixas de economia são **estimativas** baseadas no mix atual; cada item precisa de baseline (Cost Explorer / CUR) e janela de validação antes de “travar” o número para a diretoria.

| Priority | Opportunity | Est. monthly savings (USD) | % of total spend | Effort | Key risks / prereqs |
|---:|---|---:|---:|---|---|
| 1 | **Compromissos + rightsizing do grosso “variável” (EC2 on-demand + EKS)** | **2.400 – 3.600** | **5,7% – 8,6%** | Medium | Pré-req: tagging/cost allocation + recomendações Compute Optimizer; risco: mudança de shape/capacidade se feita sem canário; mitigação: janelas, autoscaling e rollback. |
| 2 | **RDS PostgreSQL (Reserved/ Savings + tuning operacional sem sacrificar Multi-AZ)** | **1.200 – 2.000** | **2,9% – 4,8%** | Medium | Pré-req: baseline de CPU/IO/latência e janela de manutenção; risco: apertar storage/IOPS demais; mitigação: mudanças incrementais + alarmes de replica lag/latência. |
| 3 | **CloudWatch Logs (retenção por subtipo + sampling/OTel + índices)** | **900 – 1.600** | **2,2% – 3,8%** | Low–Medium | Risco: perda de diagnóstico se retenção cair demais no “wrong tier”; mitigação: política por log group (app vs segurança) e export/archive para S3 Glacier quando necessário. |
| 4 | **S3 Standard → lifecycle + Intelligent-Tiering + revisão de padrões de upload** | **700 – 1.200** | **1,7% – 2,9%** | Low | Pré-req: inventário por bucket/prefix; risco: latência de restore em classes frias (se aplicável); mitigação: não mover dados críticos de leitura quente sem teste. |
| 5 | **Data Transfer Out + NAT (VPC endpoints, consolidação de egress, desenho regional)** | **600 – 1.100** | **1,4% – 2,6%** | Medium | Risco: endpoints mal dimensionados / custo fixo inesperado; mitigação: medir primeiro, priorizar serviços que mais “pagam NAT/egress”. |
| 6 | **ElastiCache (dimensionamento + política de TTL/eviction + separação dev/prod)** | **300 – 700** | **0,7% – 1,7%** | Low–Medium | Risco: pressão de memória aumentar miss rate; mitigação: monitorar hit rate/latência e canário. |
| 7 | **EBS gp3 (volumes subutilizados + snapshots + anexos órfãos)** | **200 – 500** | **0,5% – 1,2%** | Low | Risco: cortar throughput/IOPS além do suportado; mitigação: métricas `VolumeIdleTime` / latência de IO. |
| 8 | **Lambda + métricas CW “ruído” (consolidação de métricas custom + revisão de polling)** | **100 – 350** | **0,2% – 0,8%** | Low | Risco baixo; ganho típico menor, bom como “vitória rápida”. |

## Gap-to-goal (15%)

- **Meta:** USD **6.270** (15% de USD 41.800).
- **Cenário conservador (soma dos pisos acima):** ~USD **6.400+/mês** — **atinge a meta** com folga pequena, assumindo execução disciplinada e medição pré/pós.
- **Se a meta não fechar no pessimista:** subir prioridade de **(1)** e **(5)** (egress/NAT costuma ser “dinheiro no chão” quando há endpoints faltando) e abrir um trabalho paralelo de **arquitetura de observabilidade** para reduzir volume ingestado em logs sem perder sinal de incidente.

## Sequência sugerida (90 dias)

1. **Semana 1–2:** baseline (CUR), tagging, top-10 drivers por serviço/time; definir “guardrails” de SLO.
2. **Semana 3–6:** Quick wins (S3 lifecycle, logs retention tiering, EBS hygiene) + preparação de compromissos (RI/SP) com recomendações.
3. **Semana 7–12:** mudanças estruturais (EKS/EC2 commitment mix, endpoints/NAT, RDS tuning + purchase strategy) com canários e rollback.
