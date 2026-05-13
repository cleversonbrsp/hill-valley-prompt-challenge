# Output — Questão 04

```sql
SELECT
  to_char(
    date_trunc(
      'month',
      (t.created_at AT TIME ZONE 'America/Sao_Paulo')
    ),
    'YYYY-MM'
  ) AS month,
  t.category,
  COUNT(*)::bigint AS transaction_count,
  ROUND(SUM(t.amount_cents) / 100.0, 2) AS total_brl
FROM transactions AS t
WHERE t.status = 'completed'
  AND t.category IN (
    'subscription',
    'one_time',
    'refund',
    'credit_adjustment'
  )
  AND t.created_at >= (
    (TIMESTAMP '2026-04-24 00:00:00' AT TIME ZONE 'America/Sao_Paulo')
    - INTERVAL '6 months'
  )
  AND t.created_at < (
    TIMESTAMP '2026-04-25 00:00:00' AT TIME ZONE 'America/Sao_Paulo'
  )
GROUP BY
  to_char(
    date_trunc(
      'month',
      (t.created_at AT TIME ZONE 'America/Sao_Paulo')
    ),
    'YYYY-MM'
  ),
  t.category
ORDER BY
  month ASC,
  category ASC;
```
