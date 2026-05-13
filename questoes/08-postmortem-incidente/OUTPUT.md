# Output — Questão 08

## Executive summary

- O deploy **v2.48.0** (sync **2026-04-23 18:42 UTC**) coincide com mudanças de **alta sensibilidade** no caminho crítico: **novo endpoint batch**, **refatoração do pool do Ledger**, **bump do psycopg** e **timeout mais agressivo (2s)**.
- A degradação observada entre **13:30–14:20 UTC** é um padrão clássico de **pressão no datastore + contenção no cliente**: latência e erro sobem com tráfego, e o log mostra **pool esgotado**, **timeouts em 2000ms** e **circuit breaker aberto** no cliente do Ledger.
- O gargalo numérico mais “duro” é **concorrência de conexões**: **12 pods** no máximo do HPA com pool **max=20** sugere **~240 conexões ativas** no app, encostando no **limite 250 do RDS** informado — isso explica resets/timeouts e degradação em cascata (Reactor falhando por erro upstream).
- O alerta de **memória** pode ser **sintoma correlato** (filas/objetos retidos sob pressão, buffers, retries, backlog de goroutines/threads) sem ser a **causa raiz primária**; **CPU 62% / mem 71%** médios não invalidam picos por pod ou pressão de alocação sob timeout/retry.
- Recomendação para decisão em **~20 min**: **caminho primário = rollback para v2.47.0** (mais rápido de validar e reverte o conjunto de mudanças correlacionadas), com **fallback = mitigação operacional** (aumentar limite/instância do RDS **e** reduzir concorrência de conexões no app via pool/replicas HPA **somente** se rollback não for viável).

## Timeline (UTC)

- **2026-04-23 18:42:11**: Argo CD sync conclui rollout **v2.47.0 → v2.48.0** (mudança de superfície: batch + cliente Ledger + timeouts/psycopg).
- **2026-04-24 13:30–14:00**: degradação leve inicial (**p99** sobe de **420ms → 780ms**; erro sobe para **0,8%**) enquanto **req/s** cresce (**1200 → 1780**).
- **2026-04-24 14:10–14:20**: “dobramento” rápido: **p99 2400 → 8100ms**, **erro 4,5% → 11,7%**, **req/s 2100 → 2650** (sistema entrando em modo de falha parcial + retries/competição).
- **2026-04-24 ~14:19:48–14:19:52** (log): evidência forte de **exaustão do pool** + **timeout 2000ms** + falha do **`POST /v2/transactions/batch`** + breaker **OPEN** + falha ao publicar no Reactor por erro upstream.

## Hipóteses ranqueadas (com evidências)

### H1 — Saturação de conexões / contenção no Ledger (RDS) acoplada ao novo padrão de carga (principal)

**A favor:** log com `connection pool exhausted (max=20, waiting=147)`; timeouts em **2000ms** alinhados ao changelog; **240/250** conexões ativas no RDS; padrão de latência/err rate explodindo com carga.

**Contra:** sozinho não explica “por que agora” sem o deploy — mas o deploy fornece o mecanismo (batch + pool refatorado + timeouts).

### H2 — Regressão/comportamento do pool após refatoração + bump psycopg (forte, complementar a H1)

**A favor:** mudança localizada no cliente; sintomas de pool e resets; rollout recente.

**Contra:** exige confirmação com diff/telemetria de pool (métricas internas) — não disponível aqui.

### H3 — “Só memória” como causa raiz (fraca)

**A favor:** alerta menciona memória >85% por 10m.

**Contra:** médias de pod **71%** e CPU **62%** sugerem que o alerta pode ser **pior caso/topN** ou **métrica desalinhada** com a causa sistêmica; o log aponta fortemente para **DB/cliente**.

## Blast radius

- **Clientes/API**: latência alta e erro >10% no pico recente (Beacon).
- **Ledger**: proximidade ao limite de conexões (risco de “hard stop” e instabilidade transacional).
- **Reactor/SQS**: backlog crescendo (**~800/min**), lag **~18m** e aumentando; publicações falhando por **erro upstream** (risco de atraso operacional e reprocessamentos).

## Recomendação (primária + fallback)

### Primária (recomendada): **Rollback para v2.47.0**

- **Por quê:** maximiza **reversibilidade** e remove, de uma vez, **batch + refactor de pool + timeout 2s + bump psycopg** como variáveis ativas.
- **Risco:** perde features do v2.48.0 (batch) temporariamente; pode não resolver se o tráfego “novo” for somente sazonalidade — mas o cenário traz **evidência forte de regressão** pós-deploy.
- **Verificação pós-rollback (15–30 min):** p99 e erro voltando ao baseline; queda de timeouts `ledger-client`; conexões RDS afastando do teto; taxa de crescimento do backlog SQS estabilizando/caindo.

### Fallback: **Scaling emergencial + contenção de concorrência**

- **RDS:** aumentar limite/throughput de conexões **via mudança de parâmetro/classe** (procedimento interno) para recuperar margem **imediatamente** (com custo e risco operacional).
- **App:** reduzir concorrência **por pod** (pool max, limites do worker, feature flag do batch, ou redução temporária de réplicas **com cuidado** para não concentrar carga) — **não** aumentar réplicas cegamente se isso **lineariza** conexões até estourar o RDS (aqui parece já estar no limite).
- **Risco:** “scaling” sem ajustar **pool × pods** pode **piorar** conexões; exige coordenação com DBA/SRE e validação minuto-a-minuto.

## O que ainda não sabemos + lacunas de instrumentação

- Distribuição **p99/pmax** de memória **por pod** vs alerta; correlacionar com **GC** ou vazamento exige profiles (não fornecidos).
- Detalhe do **novo pool** (limite global vs por worker, como o gunicorn workers multiplicam conexões) — necessário para dimensionar corretamente antes de reintroduzir v2.48.0.
- Query específica e plano no Ledger para o `SELECT ... transactions` (pode haver regressão de performance independente do pool).
