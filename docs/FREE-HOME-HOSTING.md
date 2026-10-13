> **Latest decision — 13 October 2026:** The user ruled out both this Mac and an always-on home computer. Home hosting is therefore an unused alternative, not the deployment target. The $0/month constraint remains; no domain/server purchase is authorized. Oracle Always Free is a candidate pending user account eligibility, regional capacity and acceptance of idle-resource reclamation risk. No cloud deployment has occurred.

# Private Atlas hosting with no subscription cost

Checked 13 October 2026 against commit 274ff02 and the actual source. This decision supersedes the paid-server/domain proposal: **do not purchase hosting or a domain under the current $0 constraint**.

## Architecture and choice

Atlas is full-stack, not a static website. `portal/app.py` serves Flask APIs plus the HTML/JS interface and Application Studio. `portal/db.py` uses SQLite with WAL, not PostgreSQL. `portal/worker.py` collects on its own schedule; `portal/jobs.py` processes document jobs. `portal/uploads.py` stores private CVs, templates and compiled files next to the database. `portal/compilation.py` requires TeX, PDF tools and OS isolation. Static deployment would lose the product's backend functionality.

**Use your existing home computer + Tailscale Personal + SQLite on its disk.** Hosting, DNS and HTTPS subscriptions: $0. Existing hardware, electricity, Internet and backup media are not magically free; no new hardware purchase is assumed. The host must remain awake and online. If the host is this laptop, scheduled work stops when it sleeps. An existing always-on Linux computer allows the laptop to disconnect.

Render Free is unsuitable for preserving this application: its web filesystem is ephemeral (including SQLite and uploads), free persistent disks are unavailable, free PostgreSQL expires after 30 days and free background-worker instances are unavailable. Accepting a cold start does not solve those limitations. No personal data was uploaded to Render. [Official free limits](https://render.com/docs/free). A disposable empty demo could use Render, but would not meet the personal-data or scheduling requirements.

[Tailscale Personal](https://tailscale.com/pricing) is $0 for personal use. [Serve](https://tailscale.com/kb/1312/serve) exposes a service only inside your tailnet with HTTPS. It supplies a `machine.tailnet.ts.net` hostname: no `.tr`/`.de` domain or DNS purchase. **Do not use Funnel**, router port forwarding or the old public Caddy compose file. Keep the tailnet single-owner and do not share this machine. Enable MFA for the identity used to sign into Tailscale. Atlas owner/password login remains an additional barrier.

`ATLAS_ZERO_COST=1` blocks writing and email provider credentials, even if keys already exist privately. It does not erase keys or drafts. Manual document editing, existing versions, deterministic collection and local compilation remain usable. Paid model generation is deliberately unavailable. No local-model writing integration is claimed. Gmail delivery is not activated by this plan; a ts.net hostname is not a sender domain you can publish DNS verification records for. Revisit a free email method separately rather than silently buying a domain or using a paid provider.

## A. Recommended on this Mac: preserve the existing installation

This uses native processes because the working macOS compiler already uses OS isolation. Containers are optional; see B for a separate Linux/Docker route. Do not run both routes against the same database.

1. Install the official [Tailscale macOS app](https://tailscale.com/download/mac), then sign in to a **Personal** tailnet. Install Tailscale on your phone and iPad and sign in with the same account. Complete system VPN permission yourself. Do not paste an authentication key here. Tailscale was not installed/available during this inspection.
2. In Tailscale's device list, copy this Mac's exact DNS hostname. Enable MagicDNS/HTTPS when prompted by Serve. Choose a neutral machine name: HTTPS certificate hostnames can appear in public certificate-transparency records, although Serve content remains private. The commands below use `atlas.YOUR-TAILNET.ts.net` as a placeholder, not an actual address.
3. Back up, then prepare settings. The password prompt is hidden. The existing private owner email is reused; settings are 0600, ignored by Git and never overwrite existing settings.

```sh
cd /Users/Student/Downloads/Atlas
.venv/bin/python -m scripts.backup backup "data/backups/before-home-$(date +%Y%m%d-%H%M%S).tar.gz"
.venv/bin/python -m scripts.home_host configure --hostname atlas.YOUR-TAILNET.ts.net
.venv/bin/python -m scripts.verify_tex_sandbox
.venv/bin/python -m scripts.home_host agents
```

4. Stop the existing local web, collector and document processes cleanly before switching; do not kill unrelated Python processes. Inspect `ps -axo pid,command` for this repository's `portal.app`, `portal.worker`, `portal.jobs` or Gunicorn processes; use `kill -TERM PID` for only those processes. Wait for active collection/document work to finish. Existing data remains in `data/`; nothing is imported or reset.
5. Install/start the generated per-user macOS LaunchAgents. They run at login and restart after failures, **not before macOS login and not while sleeping**. Logs live in ignored `private/home-host/logs/`; review/rotate them periodically. The generator checks for existing files; do not replace unrelated launch agents.

```sh
mkdir -p "$HOME/Library/LaunchAgents"
for role in web collector documents; do
  target="$HOME/Library/LaunchAgents/local.atlas.$role.plist"
  test ! -e "$target" || { echo "Already installed: $target"; break; }
  install -m 600 "private/home-host/agents/local.atlas.$role.plist" "$target"
  launchctl bootstrap "gui/$(id -u)" "$target"
done
```

6. Enable **private Serve** to the authenticated production server on loopback port 18765, not the old development port 8765. If `tailscale` is not in PATH, use the official app's CLI path below. Complete any HTTPS permission step Tailscale displays.

```sh
/Applications/Tailscale.app/Contents/MacOS/Tailscale serve --bg http://127.0.0.1:18765
/Applications/Tailscale.app/Contents/MacOS/Tailscale serve status
```

7. Open the exact HTTPS URL printed by Serve on your connected devices. Sign in with the owner email and the password you just chose. Studio is at `/studio`. Keep the Mac awake while serving (System Settings → Battery/Power options as appropriate). `caffeinate -i` in a separate terminal can temporarily prevent idle system sleep; it does not guarantee service through a closed laptop lid or power loss.
8. Verify all gates below before relying on it. Do not merely point Tailscale at the unauthenticated development server. Atlas validates the Host/Origin; if Serve shows an unrecognized-host error, compare its exact hostname with settings instead of disabling the check.

Stop: `tailscale serve --https=443 off` (use app CLI path if necessary), then `launchctl bootout gui/$(id -u) "$HOME/Library/LaunchAgents/local.atlas.web.plist"` and repeat for collector/documents. This stops services; it does not delete data. To return to development, stop these agents first, then start the former local processes. Do not overwrite the private home settings.

## B. Containerized home host (Linux Docker; not yet engine-tested)

The repository's original Dockerfile/compose lacks the document worker and TeX runtime. Use **only** the new `deploy/Dockerfile.home` + `compose.home.yaml` for this alternative. They build from explicit code/lockfiles, never copy personal data, bind web only to host loopback, run as UID 10001, persist `/data`, limit resources/logs and block paid APIs. Install Docker Engine/Compose from [official Linux instructions](https://docs.docker.com/engine/install/) on your existing Linux host; install Tailscale on the host, not in a privileged container. No cloud account or server rental.

On the Mac, create a consistent backup as in A3 and create private production settings for the actual **Linux host's** Tailscale hostname:

```sh
.venv/bin/python -m scripts.configure_production --domain atlas.YOUR-TAILNET.ts.net
```

This refuses to overwrite existing settings; use `--destination private/home-container-settings` if already configured, then securely transfer that folder's `atlas.env` to the Linux checkout's `private/production-settings/atlas.env`. Never commit it. Transfer the backup and environment file to the host through authenticated SSH/Tailscale SSH or an encrypted removable drive. Do not use Git for this transfer.

On the Linux host, clone the code into a writable directory and enter it. Install the locked Python dependencies in a temporary venv for the restore utility. Replace `/srv/atlas-home` with an empty dedicated location if necessary; never restore over existing data:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.lock
sudo mkdir -p /srv/atlas-home
sudo .venv/bin/python -m scripts.backup restore /PATH/TO/TRANSFERRED-BACKUP.tar.gz --destination /srv/atlas-home/data
sudo chown -R 10001:10001 /srv/atlas-home/data
chmod 600 private/production-settings/atlas.env
export ATLAS_DATA_DIR=/srv/atlas-home/data
docker compose -f compose.home.yaml config --quiet
docker compose -f compose.home.yaml build
docker compose -f compose.home.yaml up -d web collector
```

Do **not** print expanded compose config: it contains secrets. `--quiet` validates without printing them. Before enabling document jobs, probe isolation with the identical container policy:

```sh
docker compose -f compose.home.yaml --profile documents run --rm documents python -m scripts.verify_tex_sandbox
docker compose -f compose.home.yaml --profile documents up -d documents
tailscale serve --bg http://127.0.0.1:18765
tailscale serve status
```

Run the second command only if the first passes. Docker's default syscall/namespace restrictions can prevent nested Bubblewrap or Chromium from starting. **Do not add privileged mode, SYS_ADMIN or unconfined profiles to get past this.** If the probe fails, document compilation remains unavailable in that runtime; use the existing native Debian/systemd services (runbook's installation, restore and isolation steps) with Tailscale Serve replacing Caddy. Set `ATLAS_ZERO_COST=1` in `/etc/atlas.env`, keep Gunicorn loopback at 8000 and serve that port. This is a disclosed deployment gate, not verified container compilation. Missing custom fonts/template packages must be installed from legitimate sources, not solved by changing the master templates.

No Docker executable was available on the inspected Mac; image build, real container startup, Linux sandbox and network/device checks remain unverified. The compose file does not configure public Caddy or ports 80/443. Persist the ATLAS_DATA_DIR shell setting for future compose invocations. Restart policies resume containers when Docker starts; ensure the existing Linux host starts Docker/Tailscale at boot. Stop with `docker compose -f compose.home.yaml --profile documents down`; do not delete `/srv/atlas-home/data`.

## Verification, backup and recovery

- Anonymous HTTPS `/api/state`, Studio and document downloads deny access; correct owner login works and wrong email does not. Confirm Tailscale-disconnected device cannot reach the URL.
- Save an isolated test bookmark/note, reload and inspect from phone/tablet; confirm the same private dataset. Do not modify real application history for testing.
- Observe an actual due scheduled collection and queued document job with browsers closed. Disconnect the laptop only when using a separate home host; a laptop cannot keep serving while asleep.
- Restart the three services and verify database, templates, uploaded CVs and document versions persist. Check logs for failures and the Sources worker heartbeat.
- Compile a disposable document, inspect the PDF and all download formats. Pass the sandbox probe on the actual runtime; local Mac success does not prove container/Linux safety.
- Create consistent backups with `scripts.backup` (container: `docker compose -f compose.home.yaml exec web python -m scripts.backup backup /data/backups/manual.tar.gz`). Copy archives to an existing separate encrypted disk; same-disk backups do not protect hardware loss. No paid B2 bucket is required. Keep credentials/password recovery separately in your password manager.
- Restore into a fresh empty directory, check SQLite integrity and expected personal-data counts, then test an isolated instance before swapping paths. Stop all services before a swap. Keep the previous dataset for rollback. Never use `docker compose down -v` as a backup procedure.

Status: code/scripts and isolated configuration/provider-block tests are locally verified; no Tailscale connection, live private URL, container build, remote sign-in or device-offline scheduling has been demonstrated. Exact remaining input: install/sign into Tailscale and supply the chosen machine's `.ts.net` hostname, then enter the Atlas password privately. No domain purchase or hosting payment is needed.
