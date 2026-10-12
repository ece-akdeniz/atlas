# Atlas + Application Studio deployment

Prepared, **not deployed**. No server account, SSH access, domain/DNS, outbound-email credential or model credential has been supplied. Do not expose the loopback development server. The production configuration requires a strong session secret, password hash and exact HTTPS origin before starting.

## Recommendation and expected cost

Use a single German Hetzner CX23-class VM (2 vCPU, 4 GB), Debian 13, persistent disk, Caddy HTTPS, native systemd services for web/collection/document jobs, and SQLite. This avoids a second database subscription and permits Bubblewrap to isolate each TeX compilation. Compilation is serial and resource-limited.

Prices checked 13 October 2026: [Hetzner's official adjustment](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) lists CX23 at €5.49/month before VAT. With German 19% VAT this is approximately €6.53. Budget €9–15/month including a modest domain, IPv4 and backups; these additions are estimates, and the final checkout must remain under €15. Availability and the final tax-inclusive quote must be checked before ordering. Nothing has been purchased.

[Resend Free](https://resend.com/pricing) supports 3,000 emails/month, 100/day; Atlas defaults to at most two exceptional alerts/day. A verified sending domain is required, but no Gmail inbox access is needed. Provider acceptance is logged separately from confirmed inbox receipt. Destination is private database configuration, not committed code.

[OpenAI's current standard API rates](https://developers.openai.com/api/docs/pricing): gpt-6-luna $0.10 input/$0.50 output per million tokens; gpt-6.1-sol $2/$10. Luna is the economical opt-in writing default. At 50 drafts/month, each 8k input + 2k output, estimates are $0.09 or $1.80 respectively, before retries and tax. This is an estimate, not measured consumption or a demonstrated quality comparison. No paid model calls were made. Collection/ranking/CV import use no paid model. Budget reservations, output validation, evidence identifiers and versioned cache are implemented; provider failures retain existing drafts. Default environment example caps writing at $2/month.

## Native server preparation

1. Create a dedicated `atlas` system user. Put the checkout in `/opt/atlas`, owned by the deployment user, readable but not writable by the service user. Create `/var/lib/atlas` owned by atlas, mode 700. Install Python 3.13+ with venv, Caddy, Bubblewrap, TeX Live LaTeX recommended/extra, XeTeX, recommended fonts and Poppler from official Debian repositories.
2. Create `/opt/atlas/.venv`, install `requirements.lock`. Copy `.env.example` to `/etc/atlas.env`, owner root:atlas, mode 640. Set the exact `PORTAL_ORIGIN=https://your-domain`, `PORTAL_DOMAIN`, a random secret of at least 32 characters and a Werkzeug scrypt password hash. Generate credentials on the server and never commit or print them into chat. Caddy also needs PORTAL_DOMAIN via its systemd environment file, or replace the domain placeholder in its Caddyfile.
3. Restore the private data backup into a fresh `/var/lib/atlas` before starting services. Transfer it over authenticated SSH, never through Git. Database and templates/drafts/PDFs travel together. Protect or encrypt any off-server backup; local copies alone are not disaster recovery.
4. Install the three units from `deploy/systemd`, and `deploy/Caddyfile.native` as Caddy's config. Set DNS, allow inbound HTTPS/HTTP and restricted SSH only. Port 8000 binds loopback.
5. Before enabling document jobs, run `PYTHONPATH=. .venv/bin/python scripts/verify_tex_sandbox.py` as the atlas service account. It must compile normal text while rejecting private-file reads and shell execution. Bubblewrap requires working unprivileged namespaces. If the host blocks these, keep compilation disabled and resolve the sandbox configuration; do not run TeX unsandboxed or make a container privileged. Linux sandbox execution is not yet live-tested.
6. Enable/start `atlas-web`, `atlas-collector`, `atlas-documents` and Caddy. Inspect service logs for errors. Jobs run independently of all browsers and laptops once these server services are verified. The current local workers still depend on this laptop being awake.

## Release gates on the actual host

- Unauthenticated requests to `/studio`, `/api/state`, `/api/studio`, PDF/TeX/source-bundle downloads and upload history must fail or redirect to sign-in. Sign in, then verify the same bookmark and checklist on laptop, phone and iPad.
- Verify HTTPS certificate, secure cookie, CSRF/origin checks and no public access to the data directory. Keep credentials server-side.
- Close browsers and disconnect the laptop; observe a scheduled collection run and its successful/failed sources. Manual collection is not proof of this test.
- Restart each service. Confirm stored data persists and interrupted document jobs become retryable. Check the hourly/daily worker heartbeat and actual run results.
- Generate and visually inspect a PDF with the actual template/assets. Confirm malformed TeX fails safely, no outbound compiler network access and no private-file reads.
- Set Resend credentials and verified sender, enable desired alert settings, then send the clearly labeled test. Confirm receipt in Gmail. This has **not** happened yet. First enable excludes all existing listings. Email retries preserve one provider idempotency key and stop for manual review within its safety window.
- Optionally set the writing API key. Review first generated letters/edits and actual usage before increasing limits. Direct editing/local starters remain available when the provider fails.

## Backups and restore

The collector makes daily database and complete private-data backups with seven-day retention. Complete archives include a consistent SQLite snapshot plus uploaded assets and documents. Use `PORTAL_DB=/var/lib/atlas/portal.sqlite3 .venv/bin/python -m scripts.backup backup /private/location/atlas.tar.gz`. Copy encrypted backups off-server separately.

Stop all three services before switching a restored dataset. Restore to an empty directory with `.venv/bin/python -m scripts.backup restore /private/location/atlas.tar.gz --destination /var/lib/atlas-restored`; integrity verification runs automatically. Check ownership/modes and point services to the restored database. Retain the old directory until the restore is verified. An isolated local backup/restore passed; recovery on the proposed server remains a deployment gate.
