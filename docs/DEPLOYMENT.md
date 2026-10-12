# Deployment and operating costs

## Recommended default

One small Linux VPS in Germany, Docker Compose, Caddy HTTPS, Flask/Gunicorn, SQLite on a persistent volume, and a separate Python worker. This is suitable for one private user and modest daily collection. It avoids paying separately for a database, scheduler, model, and web host. SQLite's backup API gives consistent snapshots; web and worker use WAL mode and short transactions.

A hosted Sites schedule is not used because the available schedule mechanism creates recurring cloud tasks, conflicting with the requested independent application.

## Costs checked 12 October 2026

The [official Hetzner June 2026 price adjustment](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) lists CX23 at €5.49/month excluding VAT and IPv4 in Germany/Finland. At 19% VAT that base is approximately €6.53. IPv4 and backup options are additional; verify the checkout total before purchase. This is not a measured bill.

Plan approximately €9–15/month including a small server, an allowance for IPv4/backups, and a domain amortized over the year. Domain and backup allowances are estimates, not verified quotes. Keeping an existing domain or using an existing server can lower the incremental cost.

No paid model is required or configured: €0 model cost. Parsing, deduplication, ranking, filtering, factual change detection, scheduling and tracking run without one. No model/provider choice is recommended until a measured extraction benchmark shows a benefit; current model availability/prices have therefore not been asserted. A future optional model adapter must pin model and prompt versions, validate a schema, cache by content hash, enforce a monthly hard budget, and avoid sending the CV. Its cost must be verified when selected.

Collection estimate: 12 substantive adapters plus a few legacy monitors, roughly 60–100 requests per daily cycle when detail pages/PDFs are fetched, or approximately 1,800–3,000 requests/month before retries. This is a planning estimate, not measured billing. Actual request counts depend on index contents, robots caching, failures and conditional requests. Responses are bounded to 2 MB; adapters disclose limits (for example DLR 30 details, Fraunhofer 8 index pages / 50 details, IFF 2 PDFs/topic / 12 pages/PDF). RPG has no silent 20-project cap. Cache records and database snapshots are local; monitor disk usage as coverage expands.

## Accounts / prerequisites

- A VPS provider account and a Linux server with Docker Engine and Compose.
- A domain/DNS account; point its A/AAAA records at the server.
- SSH access and permission to open TCP 80/443. Keep SSH access restricted.
- No OpenAI or other model API key. No email credentials. No application submissions.

No server account, domain, billing authorization, or deployment credentials were supplied in this conversation. The package is prepared locally; production deployment cannot be claimed until performed and verified.

## Launch

1. Copy the source to the server, excluding `.git`, `.venv`, `.env`, and `data`. Use the repository or a private file transfer.
2. Create the virtual environment and install requirements, then run `python scripts/configure.py` interactively. It asks for a domain and hidden password and writes a mode-0600 `.env`. The password is stored only as a salted scrypt hash. Do not paste passwords or API keys into chat.
3. Run `docker compose build` and `docker compose up -d`. Named volumes hold the database and TLS state. Only Caddy exposes public ports; neither SQLite nor the application container is directly published.
4. Open the HTTPS domain and verify sign-in. An anonymous GET to `/api/state` must return 401. Check `docker compose logs --tail=100 web worker caddy`.
5. Import a private profile inside the web container, or enter the profile in the app. For an existing database, stop both services before copying it into the named volume; retain the file owner (UID 10001). Prefer SQLite backup/export over copying a live WAL database.
6. Verify that Source coverage changes after `docker compose exec worker python -m portal.worker --once`, respecting per-source due times. Close the browser; worker heartbeats must continue. Server restarts must restore both services.

Production startup fails if the session secret, password hash, or public origin is missing. Use `PORTAL_ENV=production`. The origin must match the browser URL exactly. Do not trust arbitrary forwarded identity headers. Authentication is app-owned and independent of ChatGPT.

## Backups and restore

The worker makes one consistent SQLite backup per UTC day and keeps seven in `/data/backups`. These are local recovery copies, not disaster protection: configure an encrypted off-server backup of that folder before relying on the server. Keep encryption keys separately. Backups contain private profile and application data.

Restore drill: stop web and worker; retain the damaged database separately; replace `portal.sqlite3` using a known-good backup; remove old WAL/SHM companions while all connections are stopped; restore UID 10001 ownership; start services; verify profile, notes, record count, and worker heartbeat. Never overwrite an actively used database.

The UI's personal-data deletion removes local backups and the local profile-import JSON. It cannot delete downloads or remote backup copies. A production off-site backup policy must propagate deletions or expire those encrypted copies on a documented retention schedule.

## Updates and limits

Stop the worker before schema maintenance. Back up first. Current schema is version 2; future changes require explicit sequential migrations rather than changing already-applied schema in place. Rebuild and restart after code changes. Keep one worker; database locks prevent overlapping runs. Review failing adapters and source policies before enabling new sources.

The domain/password setup, Docker build on a target server, TLS issuance, restore drill on that server, and actual monthly cost remain deployment-stage checks. Do not describe the local preview as production hosting.
