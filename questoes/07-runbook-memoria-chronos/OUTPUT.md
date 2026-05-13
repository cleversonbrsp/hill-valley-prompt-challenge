# Output — Questão 07

## Objetivo do runbook

Responder ao alerta **`[CRITICAL] High memory usage on Chronos API pods (>85% for 10min)`** de forma **procedural**, reduzindo variância entre plantonistas e evitando “achismo” quando o sintoma for **memória** mas a causa raiz puder ser **pressão downstream** (Ledger/Reactor) ou **mudança recente** no deploy.

## Préâmbulo (o que você está tentando provar em 10–15 minutos)

1. **Isso é saturação real de heap RSS** ou um **sinal enganoso** (ex.: baseline alto porém estável + HPA no teto por CPU)?
2. Existe **correlação temporal** com deploy (Argo CD) ou com **degradação do Ledger** (timeouts, pool, conexões)?
3. Há **mitigação segura imediata** (scale / rollback) com **risco** explícito documentado?

Canal: `#oncall-chronos`  
Escalação: `@chronos-core` — **15m** (comercial) / **30m** (fora)

---

## Passo 0 — Checar incidente ativo e ancorar contexto

**Comandos**

```bash
date -u
kubectl config current-context
kubectl get ns production
```

**Verificação esperada**

- Você está no **cluster/EKS correto** e o namespace `production` existe.

**Escalar se**

- Você não consegue autenticar no cluster (bloqueio de acesso) **e** o alerta segue CRITICAL.

**Slack (template)**

`[Chronos] Oncall: iniciando triagem de high memory — cluster=$(kubectl config current-context) ns=production`

---

## Passo 1 — Snapshot de réplicas, HPA e métrica “de pressão”

**Comandos**

```bash
kubectl -n production get deploy chronos-api -o wide
kubectl -n production get pods -l app=chronos-api -o wide
kubectl -n production get hpa
kubectl -n production top pods -l app=chronos-api
```

**Verificação esperada**

- `READY` bate com `replicas` desejadas.
- `kubectl top` mostra **memória** e **CPU** por pod (se metrics-server estiver ok).

**Escalar se**

- Pods em **CrashLoopBackOff** em massa, ou **Pending** por scheduler/quotas, ou **top** indisponível **e** o alerta persiste >10 min.

---

## Passo 2 — Separar “memória alta” de “explosão de tráfego / fila”

**Comandos**

```bash
kubectl -n production describe hpa | sed -n '1,200p'
kubectl -n production get pods -l app=chronos-api \
  -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[0].resources.requests.memory}{"\t"}{.spec.containers[0].resources.limits.memory}{"\n"}{end}'
```

**Verificação esperada**

- HPA no **máximo** com motivo coerente (CPU alta, ou custom metric, conforme configurado).
- Requests/limits de memória **existem** (não “ilimitado”).

**Escalar se**

- HPA está no **máximo** por **CPU** enquanto o Beacon acusa **memória** (possível descompasso de métrica/SLO) **ou** há sinais de **throttling**/`OOMKilled`.

---

## Passo 3 — Logs recentes focados em erros (Beacon via kubectl)

> Ajuste o seletor `app=chronos-api` se o label real for outro; aqui usamos o label do enunciado.

**Comandos**

```bash
kubectl -n production logs deploy/chronos-api --since=30m --tail=200 | egrep -i 'error|warn|timeout|oom|ledger|sqs|reactor|batch' || true
```

**Verificação esperada**

- Você identifica **padrão** (ex.: timeouts do Ledger, falhas SQS, endpoint novo `/batch`, etc.).

**Escalar se**

- Erros indicam **data plane** (RDS/SQS) com indisponibilidade clara **e** o erro rate impacta clientes.

---

## Passo 4 — Investigação “dependências” mínima (Ledger/Reactor)

### 4A — Ledger (sinal via app + métricas)

**Comandos**

```bash
kubectl -n production port-forward svc/chronos-api 8080:8080 >/tmp/pf-chronos.log 2>&1 &
sleep 2
curl -fsS http://127.0.0.1:8080/metrics | egrep -i 'ledger|postgres|db|pool|jdbc|timeout' | head -n 50 || true
kill %1 || true
```

**Verificação esperada**

- Você confirma se há **contadores** relacionados a DB/pool (nomes variam por instrumentação).

**Escalar se**

- Há evidência forte de **esgotamento de pool** / **timeouts em massa** correlacionados ao início do incidente.

### 4B — Reactor (SQS) — visão macro via AWS CLI

> Substitua `REGION` e o nome exato da fila conforme o runbook interno; aqui usamos a fila do cenário: `chronos-transactions`.

**Comandos**

```bash
export AWS_REGION=us-east-1
aws sqs get-queue-url --queue-name chronos-transactions --output text
QUEUE_URL="$(aws sqs get-queue-url --queue-name chronos-transactions --output text)"
aws sqs get-queue-attributes --queue-url "$QUEUE_URL" \
  --attribute-names ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible ApproximateNumberOfMessagesDelayed
```

**Verificação esperada**

- Você captura **backlog** e mensagens in-flight (sinal de pressão acumulada).

**Escalar se**

- Backlog cresce monotonicamente **e** Chronos está degradando latência/erro.

---

## Passo 5 — Checar mudança recente (Argo CD)

**Comandos**

```bash
argocd app list | egrep -i 'chronos|hvt/chronos-api' || true
argocd app history chronos-api | head -n 30 || true
argocd app get chronos-api --refresh | sed -n '1,200p' || true
```

**Verificação esperada**

- Você identifica **sync** recente, **versão de imagem** e possíveis **diffs** relevantes.

**Escalar se**

- Mudança correlaciona com início do incidente **e** você não tem permissão para rollback/hotfix.

---

## Passo 6 — Mitigações (escolha com registro de risco)

### Opção A — Scale manual (mitigação rápida, pode mascarar causa)

**Comandos**

```bash
kubectl -n production scale deploy/chronos-api --replicas=8
kubectl -n production rollout status deploy/chronos-api --timeout=5m
```

**Verificação esperada**

- Mais pods **READY** e pressão por pod tende a cair **se** o problema for capacidade.

**Escalar se**

- Scale **não** melhora memória por pod / erro rate continua alto.

### Opção B — Rollback controlado via GitOps (quando deploy suspeito)

> Somente com **aprovação** e seguindo política interna (change management).

**Comandos (ilustrativo)**

```bash
argocd app rollback chronos-api <REVISION> --prune
```

**Verificação esperada**

- Argo mostra app **Healthy** e rollout completo.

**Escalar se**

- Rollback falha ou retorna erro de configuração.

---

## Critérios objetivos para escalar `@chronos-core`

- **(E1)** Erro rate / p99 **piorando** por **3 janelas consecutivas** (ex.: 10 min) após mitigação inicial.
- **(E2)** Evidência de **indisponibilidade** do Ledger (timeouts em massa) **e** conexões RDS no limite (via métricas internas / DBA).
- **(E3)** `OOMKilled` em **≥2 pods** ou reinícios em cascata.
- **(E4)** Você precisa de **decisão de negócio** (rollback de release com dependências externas) em **< SLA** restante.

---

## Critério para “resolver” o incidente (mitigação estável)

- Beacon: memória **abaixo do threshold** por **≥30 min** (dois ciclos de avaliação) **ou** política interna equivalente.
- HPA: **não** preso no máximo por motivo errado (CPU/memória coerentes com demanda).
- Erro rate / p99 **voltaram ao baseline** documentado no dashboard.

## Critério para “fechar” o incidente (encerramento)

- Existe **nota final** com: causa provável, timeline, ações tomadas, itens de follow-up (ticket/issue).
- Se houve rollback/scale: **owner** definido para correção definitiva (pool sizes, timeouts, autoscaling, query, etc.).

**Slack (fechamento)**

`[Chronos] RESOLVED: high memory alert — mitigação=<scale|rollback|config>, causa provável=<...>, follow-up=<ticket>`
