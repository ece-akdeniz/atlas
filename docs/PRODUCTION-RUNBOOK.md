> **Current decision — 13 October 2026:** $0/month overrides the earlier paid-hosting acceptance. Follow [FREE-HOME-HOSTING.md](FREE-HOME-HOSTING.md) for private Tailscale home hosting. Do not buy a domain/server. Paid cloud instructions below are historical/optional, not the active plan. Home-host uptime requires the host awake; paid writing/email APIs are disabled in the new home configuration.

# Atlas + Application Studio: production runbook

Status: executable preparation, **not production-tested**. Owner must supply the server, domain and SSH access. The user accepted the existing hosting proposal on 13 October 2026, while requesting a cheaper `.tr` comparison. No purchase has been made; the domain name, checkout total and account/SSH access remain outstanding. This is the only supported deployment procedure; the Docker example is legacy.

## One concrete hosting proposal (prices checked 13 October 2026)

- Hetzner CX23, Germany, Debian 13, 2 vCPU / 4 GB, 40 GB disk: **€5.49/month net**. [Official current price](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/).
- One Primary IPv4: **€0.50/month net**. [Official pricing](https://docs.hetzner.com/cloud/servers/primary-ips/overview/).
- Seven server backup slots: **20% of VM price = €1.098/month net**. [Official billing rule](https://docs.hetzner.com/cloud/billing/faq/).
- Combined VM + IP + server backups: **€8.44/month including 19% German VAT**, rounding components conservatively.
- One ordinary `.de` domain at Domain.de: use the published regular **€12.80/year VAT-inclusive** price, **€1.07/month amortized**. The advertised €1.99 promotion is deliberately excluded from the recurring budget; confirm renewal terms and the chosen name in checkout. DNS A/AAAA/MX/TXT management is included. [Registrar price list](https://www.domain.de/domainsuche/preisliste/preisliste.php).
- Resend Free: **€0**, 3,000 transactional emails/month, 100/day; Atlas defaults to two/day. No inbox access, paid IP, marketing plan or Resend automation needed. [Pricing](https://resend.com/pricing).
- Caddy, Python, SQLite, Chromium, Bubblewrap and TeX Live: **€0** software subscriptions.
- Encrypted off-server backup: Backblaze B2 first 10 GB free, with restic encryption and a logged 5 GB warning threshold. [Pricing](https://www.backblaze.com/cloud-storage/pricing). Separate B2 account and bucket key required; stay below free storage/transaction allowances.

**Recurring hosting total: €9.51/month**, excluding optional writing API usage. This is a calculated quote from public prices, not a measured bill; the user has accepted this hosting proposal, but no purchase has been made. Domain billed annually. Confirm CX23 availability; do not substitute a costlier VM without approval. No second server, managed database or external scheduler.

Writing is separate: GPT-6 Luna standard $0.10 input/$0.50 output per million tokens, $2/month Atlas reservation cap. At 50 drafts of 8k input + 2k output each, estimated usage is $0.09/month before retries/tax; worst allowed application spend is $2 before tax/FX. Leave at least €3/month of the €15 budget for exchange-rate/tax variation. Set a matching account project budget/alert and turn off automatic credit replenishment if unwanted. [Current OpenAI model](https://developers.openai.com/api/docs/models/gpt-6-luna), [pricing](https://developers.openai.com/api/docs/pricing). Account/model access passed; real generation returned depleted-credit errors. No successful generation or provider invoice has been measured. Add credit through account Billing before retrying; the $2 Atlas cap remains enforced.

Networking: incoming/internal traffic is free; outbound transfer above the selected plan allowance is billable. Hetzner sends 75%/100% alerts, not a hard spending cap. Confirm the actual German CX23 allowance/overage in checkout and do not approve paid add-ons. This small private portal should stay within allowance, but €9.51 is not an absolute traffic/storage bill ceiling. [Official billing rules](https://docs.hetzner.com/cloud/billing/faq/).

## Domain alternative and private ownership — 13 October 2026

The official [METUnic Turkish price list](https://metunic.com.tr/fiyat-listesi/) shows `.tr` registration **₺229/year**, renewal **₺309/year**, VAT excluded (effective 28 April 2026; rendered table checked). At the [ECB 12 October reference rate](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.ff.html) of ₺55.1635 per euro, these are approximately **€4.15 / €5.60 before VAT**. Checkout tax, exchange rate and payment fees can differ. Domain.de's €1.99 first-year promotion is cheaper initially; `.tr` renewal is cheaper before tax than `.de`'s regular €12.80 including VAT. Do not use the stale English METUnic list. A `.tr` domain does not require Turkish hosting. Availability remains unchecked until the owner chooses a name.

The existing Gmail destination is registered privately as the sole Atlas owner, with a backup taken first. Production now requires owner email + password, a valid server session and matching owner identity; there is no registration route. The sign-in page and static styling are publicly reachable, but private pages, APIs, uploaded CVs and document downloads require authentication. `noindex` is an additional indexing preference, not access protection. Local loopback development remains separate and does not require sign-in. Password creation uses the hidden terminal prompt after a domain is selected; it has not been completed.

Future Europe-wide multi-user access is deferred. Before inviting anyone, implement per-user ownership for profiles, workflow, uploads, Studio projects/documents and notification settings; scoped queries, migration and isolation tests; account provisioning/recovery and roles. The present shared private dataset must never be exposed by merely adding another login.

## Exact owner steps before access exists

1. Create/sign in to Hetzner Cloud, enable account MFA. Within the accepted proposal, create a CX23 in Germany with Debian 13, IPv4 and backups. Add **your public SSH key** during creation. Keep private keys/passwords out of chat. The server can initially have inbound SSH restricted to your IP; ports 80/443 are opened for Caddy after app authentication is configured.
2. Choose an available domain name and confirm its checkout total: `.de` at Domain.de or the cheaper-renewal `.tr` option below. No name has been selected or registered. Set an `A` record for `atlas.<your-domain>` to the VM IPv4; only add `AAAA` if the actual IPv6 is configured. TTL 300 during setup. Do not buy a separate TLS certificate.
3. Provide only the domain and SSH host/user or a working local SSH alias. Confirm the host fingerprint from the provider console before first login; do not disable SSH host verification.
4. Create a Resend Free account and add your sending domain, e.g. `mail.<your-domain>`. Add exactly the DKIM/SPF/MX verification records shown by Resend to DNS; do not invent DNS values. Verify the domain, create a sending key, and enter it through the hidden terminal setup below. No Gmail password or inbox permission is needed.
5. For off-site backups, create a private B2 bucket, configure a bucket-scoped application key, and provide it through the server's protected backup environment file. Save the restic recovery password separately in your password manager. Do not paste either secret into chat.

## Local writing activation now (does not need the server)

Observed 13 October, 14:01 UTC: the existing private key and selected model passed preflight. Real generation later returned `credit_balance_exhausted`; add API credit in the account Billing page, then retry. The commands below remain the setup/rotation procedure, not a request to replace the working key.

```sh
cd /Users/Student/Downloads/Atlas
.venv/bin/python -m scripts.configure_providers writing
.venv/bin/python -m scripts.provider_preflight
```

The first command uses a hidden `getpass` prompt and atomically saves mode-0600 `private/providers.json`, ignored by Git. It preserves other provider settings. The check sends **no profile/CV data** and makes no generation call. The running web/document worker reads settings on each request/job; after updating code once, changing a key does not require another restart. Reload Studio, review its explicit data-processing consent, and trigger writing only for the intended project. Model quality, résumé grounding, section preservation, token usage and PDFs must then be tested with the real provider. A valid-looking key is not an account preflight.

Email uses `python -m scripts.configure_providers email`. A hidden key prompt and verified sender address are saved. Transport remains disabled without the production HTTPS origin. A successful send response does not establish Gmail receipt.

## Server installation (after access and approval)

Use `sudo` on the selected server. Never run the following against an unrelated host. Review `deploy/install-native.sh` first, then execute it from the checked-out release. It installs packages, a dedicated service account and protected directories; it does **not** start public services or overwrite data/secrets. The source checkout goes in `/opt/atlas`; the service account cannot edit code. Use `python3 -m venv /opt/atlas/.venv`, then install `requirements.lock` and `requirements-rendering.lock` if the renderer is enabled. Install the matching Playwright Chromium binary and OS dependencies with:

```sh
/opt/atlas/.venv/bin/python -m playwright install-deps chromium
runuser -u atlas -- env PLAYWRIGHT_BROWSERS_PATH=/var/lib/atlas/browser-cache /opt/atlas/.venv/bin/python -m playwright install chromium
```

No personal browser profile is used. The collector uses the Chromium sandbox; test rendering under the actual service unit and do not disable it if namespace support fails.

Prepare production authentication locally only after choosing the hostname:

```sh
.venv/bin/python -m scripts.configure_production --domain atlas.your-domain.de
```

The setup reuses the privately registered owner email (or asks for it on a fresh installation). The hidden prompt hashes a minimum-12-character sign-in password, generates a random session secret and creates mode-600 files inside ignored `private/production-settings/`. It refuses to overwrite an existing directory and starts no service. Transfer both files over authenticated SSH to a private staging directory on the approved host (replace `atlas-host` with the verified alias):

```sh
ssh atlas-host 'umask 077; mkdir -p ~/atlas-settings'
scp private/production-settings/atlas.env private/production-settings/caddy.env atlas-host:atlas-settings/
```

On the server, install them without displaying their contents:

```sh
sudo install -o root -g atlas -m 640 ~/atlas-settings/atlas.env /etc/atlas.env
sudo install -o root -g caddy -m 640 ~/atlas-settings/caddy.env /etc/caddy/atlas.env
```

The app file contains production domain/origin, sole owner email, hashed password, random session secret, private provider path and browser-cache path. Keep transfer copies private; never paste or commit them. Caddy receives only the domain file, not provider or application secrets.

Run the provider setup as atlas with `ATLAS_PROVIDER_CONFIG` set to that path, or keep keys in `/etc/atlas.env`. Environment settings override private JSON. The app never returns secrets in API state. Keep Caddy's separate `/etc/caddy/atlas.env` limited to `PORTAL_DOMAIN`; it must not receive application/model/email secrets.

Create a full consistent local archive with `python -m scripts.backup backup data/backups/pre-deploy.tar.gz`. Transfer that archive over SSH/SCP; do not copy a live SQLite database without its WAL or push private data to Git. On the server restore into a **fresh empty** staging directory:

```sh
/opt/atlas/.venv/bin/python -m scripts.backup restore /secure-transfer/pre-deploy.tar.gz --destination /var/lib/atlas-restored
```

Inspect SQLite integrity and counts; preserve originals. Stop all three services before switching `/var/lib/atlas` to the restored dataset. Keep browser-cache and provider configuration separately during swaps. Set private ownership to atlas:atlas and directories 700/files 600. The database path is `/var/lib/atlas/portal.sqlite3`; uploaded files must remain under the archive's existing `private/` structure.

Run schema/bootstrap upgrades only after a complete backup, with the workers stopped. Start one web service (Gunicorn loopback 8000), one collector and one document worker using `deploy/systemd`. Test loopback authenticated startup before installing the Caddy site. Set Caddy's systemd drop-in EnvironmentFile to `/etc/caddy/atlas.env`, install `deploy/Caddyfile.native` as `/etc/caddy/Caddyfile` (loopback `127.0.0.1:8000`; never the legacy Docker `web:8000` target), validate it with the same domain environment, then start HTTPS. No loopback development port is exposed.

## Compiler, restart and recovery gates

Before enabling document jobs, run `scripts/verify_tex_sandbox.py` **as the actual atlas Linux service user**. Normal templates must compile; attempts to read outside the sandbox or execute TeX shell commands must fail. Bubblewrap uses new network/PID/user namespaces and read-only TeX resources. Do not disable the sandbox if namespace creation fails. Also verify no network access and bounded CPU/output/memory under the real unit. Local macOS checks are not proof of Linux behavior.

Restart web, collector and documents individually; confirm profile/workflow/template/document counts and job recovery. The web app must reject missing production auth settings. Verify two concurrent refresh requests do not overlap. With the laptop disconnected, observe a genuinely scheduled run (not `--once` or a refresh button) and a queued document job completing on the server.

Rollback: stop all three units; retain the failed release and private data separately. Switch to the prior code release **and the matching pre-migration archive restored into an empty directory**, set ownership, start services, verify data and access. Do not run older code against an incompatible migrated database. Keep the previous archive until acceptance; migrations do not justify deleting the user's files.

## Backup and restore

Daily collector backups include a consistent SQLite snapshot plus templates, CVs and versioned documents, retaining seven local archives. Hetzner backups protect VM loss but are not a substitute for application-consistent encrypted off-site backups. The optional `atlas-offsite.timer` runs the included restic upload script using `/etc/atlas-backup.env` (root:atlas 640), a private B2 repository and an external recovery password. Keep credentials outside the archive. Configure `RESTIC_REPOSITORY`, `RESTIC_PASSWORD_FILE`, `B2_ACCOUNT_ID` and `B2_ACCOUNT_KEY` in that protected environment file; restrict the B2 key to the private Atlas bucket. Store the recovery password in a separate mode-600 file readable by atlas and keep a second secure recovery copy. Initialize once, without putting secrets in shell arguments:

```sh
systemd-run --wait --pipe --collect --uid=atlas --property=EnvironmentFile=/etc/atlas-backup.env /usr/bin/restic init
systemctl start atlas-offsite.service
systemctl enable --now atlas-offsite.timer
```

Inspect the backup log and run a restore before relying on it. The script warns above 5 GB of repository data; cloud-provider billing controls must also be configured. A local threshold cannot guarantee zero cloud charges. Restore a selected complete archive into a fresh directory, run integrity checks, compare personal-data counts, then start an isolated instance. Do this on the host before calling recovery verified. Set retention/deletion rules for encrypted remote backups and document recovery-key custody.

## Release evidence required

Record each result and timestamp in VALIDATION.md:

- Anonymous `/api/state`, Studio API, upload/document/PDF/source-bundle downloads denied. Login, CSRF, secure cookies and HTTPS succeed; no data directory route.
- Same saved item and document version on actual laptop, phone and iPad. Responsive emulation alone does not pass this gate.
- Scheduled collection and document work while laptop disconnected; truthful failures and old data retained.
- Service restarts preserve state and recover jobs; backup restored into an empty dataset and inspected.
- Production LaTeX private-file/shell/network/resource tests; actual templates compile and PDFs inspected.
- Real writing generation, single-section revision and selected résumé edits, unchanged masters, usage measured, language/tone/length reviewed, provider outage safe.
- Resend verified domain, clearly labeled test sent, **provider acceptance** recorded, then **Gmail receipt confirmed by the user**. No false “delivered” assertion from HTTP 200. After the recipient actually sees the message, Settings → Delivery history → Confirm receipt records explicit recipient confirmation; never click it based solely on provider acceptance.
- One qualifying synthetic alert in an isolated notification database sent as a clearly labeled test; replay produces no duplicate and daily limits hold. Do not enable a flood of existing listings or fabricate a real opportunity.
