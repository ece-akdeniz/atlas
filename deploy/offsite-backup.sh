#!/bin/sh
# Credentials supplied by a protected EnvironmentFile; never print them.
set -eu
umask 077
: "${RESTIC_REPOSITORY:?Configure private encrypted backup repository}"
: "${RESTIC_PASSWORD_FILE:?Configure protected recovery password file}"
archive_dir=$(mktemp -d /var/lib/atlas/offsite-XXXXXX)
trap 'rm -f "$archive_dir/atlas-complete.tar.gz"; rmdir "$archive_dir"' EXIT INT TERM
cd /opt/atlas
.venv/bin/python -m scripts.backup backup "$archive_dir/atlas-complete.tar.gz"
restic backup --tag atlas-complete "$archive_dir/atlas-complete.tar.gz"
# Retention deletes encrypted recovery points only under this application tag.
restic forget --tag atlas-complete --group-by tags --keep-daily 7 --keep-weekly 4 --keep-monthly 3 --prune
restic check

restic stats --mode raw-data --json | /opt/atlas/.venv/bin/python -c 'import json,sys; size=json.load(sys.stdin).get("total_size",0); print("Backup repository bytes:",size); print("WARNING: backup repository exceeds 5 GB; review B2 storage allowance",file=sys.stderr) if size>5000000000 else None'
