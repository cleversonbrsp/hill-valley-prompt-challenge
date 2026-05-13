# Output — Questão 02

> Resposta do modelo: script bash completo.

```bash
#!/usr/bin/env bash
set -euo pipefail

# Dependencies (Ubuntu 22.04): postgresql-client, awscli, jq, coreutils
# Cron example:
#   0 3 * * * /usr/local/bin/ledger-backup.sh >>/var/log/ledger-backup.log 2>&1

readonly LOG_FILE="/var/log/ledger-backup.log"
readonly WORKDIR="/var/backups/ledger"
readonly BUCKET="hvt-ledger-backups"
readonly PREFIX="ledger/"
readonly REGION="us-east-1"

readonly PGHOST="ledger-db.internal.hvt.io"
readonly PGPORT="5432"
readonly PGDATABASE="ledger_prod"
readonly PGUSER="backup_user"

ts() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

log() {
  # shellcheck disable=SC2068
  printf '%s %s\n' "$(ts)" "$*" | tee -a "${LOG_FILE}" >/dev/null
}

fail() {
  log "ERROR: $*"
  exit 1
}

on_exit_err() {
  local ec=$?
  log "ERROR: script failed (exit=${ec}) at line ${BASH_LINENO[0]:-?}"
  exit "${ec}"
}
trap on_exit_err ERR

command -v pg_dump >/dev/null 2>&1 || fail "pg_dump not found (install postgresql-client)"
command -v aws >/dev/null 2>&1 || fail "aws CLI not found"
command -v jq >/dev/null 2>&1 || fail "jq not found (required for retention pruning)"
command -v gzip >/dev/null 2>&1 || fail "gzip not found"

export AWS_DEFAULT_REGION="${REGION}"

if [[ -z "${PGPASSWORD:-}" ]]; then
  fail "PGPASSWORD is unset or empty"
fi

umask 077
mkdir -p "${WORKDIR}"
touch "${LOG_FILE}" 2>/dev/null || true

UTC_STAMP="$(date -u +"%Y%m%dT%H%M%SZ")"
LOCAL_PATH="${WORKDIR}/ledger_${UTC_STAMP}.sql.gz"
S3_KEY="${PREFIX}ledger_${UTC_STAMP}.sql.gz"

log "START backup host=${PGHOST} db=${PGDATABASE} user=${PGUSER} -> ${S3_KEY}"

export PGHOST PGPORT PGDATABASE PGUSER
# PGPASSWORD intentionally not exported beyond what pg tools read from env; it's already in environment.

# Stream pg_dump -> gzip -> file (avoids uncompressed on-disk dump)
if ! pg_dump --no-owner --no-acl --format=plain \
      | gzip -1 >"${LOCAL_PATH}.partial"; then
  rm -f "${LOCAL_PATH}.partial" 2>/dev/null || true
  fail "pg_dump|gzip failed"
fi
mv -f "${LOCAL_PATH}.partial" "${LOCAL_PATH}"

if ! aws s3 cp "${LOCAL_PATH}" "s3://${BUCKET}/${S3_KEY}" --only-show-errors; then
  rm -f "${LOCAL_PATH}" 2>/dev/null || true
  fail "aws s3 cp upload failed"
fi

rm -f "${LOCAL_PATH}" || true
log "OK uploaded s3://${BUCKET}/${S3_KEY}"

# Retention: delete objects older than 30 days under PREFIX
CUTOFF_ISO="$(date -u -d '30 days ago' +"%Y-%m-%dT%H:%M:%SZ")"
log "RETENTION cutoff_utc=${CUTOFF_ISO} bucket=${BUCKET} prefix=${PREFIX}"

mapfile -t OLD_KEYS < <(
  aws s3api list-objects-v2 \
    --bucket "${BUCKET}" \
    --prefix "${PREFIX}" \
    --output json \
    | jq -r --arg cutoff "${CUTOFF_ISO}" '
        (.Contents // [])[]
        | select(.Key != null and .LastModified != null)
        | select(.LastModified < $cutoff)
        | .Key
      '
)

deleted=0
for key in "${OLD_KEYS[@]:-}"; do
  [[ -z "${key}" ]] && continue
  if aws s3api delete-object --bucket "${BUCKET}" --key "${key}" --output text >/dev/null; then
    log "DELETE old_object key=${key}"
    deleted=$((deleted + 1))
  else
    fail "delete-object failed for key=${key}"
  fi
done

log "SUCCESS retention_deleted=${deleted}"
exit 0
```
