#!/bin/sh
# Run only on the approved Debian 13 host. Does not launch public services.
set -eu
[ "$(id -u)" -eq 0 ] || { echo 'Run as root on the approved host.'; exit 1; }
. /etc/os-release
[ "$ID" = debian ] && [ "$VERSION_ID" = 13 ] || { echo 'This installer supports Debian 13 only.'; exit 1; }
apt-get update
apt-get install -y python3 python3-venv caddy bubblewrap texlive-latex-extra texlive-xetex texlive-fonts-recommended poppler-utils restic
id atlas >/dev/null 2>&1 || useradd --system --home-dir /var/lib/atlas --shell /usr/sbin/nologin atlas
install -d -m 700 -o atlas -g atlas /var/lib/atlas
install -d -m 755 /opt/atlas
install -m 644 deploy/systemd/atlas-*.service /etc/systemd/system/
install -m 644 deploy/systemd/atlas-offsite.timer /etc/systemd/system/
systemctl daemon-reload
printf '%s\n' 'Packages and units installed. Services NOT started. Complete PRODUCTION-RUNBOOK.md authentication, data restore, sandbox and HTTPS gates first.'
