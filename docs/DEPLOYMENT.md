> **Current decision — 13 October 2026:** $0/month overrides the earlier paid-hosting acceptance. Follow [FREE-HOME-HOSTING.md](FREE-HOME-HOSTING.md) for private Tailscale home hosting. Do not buy a domain/server. Paid cloud instructions below are historical/optional, not the active plan. Home-host uptime requires the host awake; paid writing/email APIs are disabled in the new home configuration.

# Deployment — canonical procedure

**Superseded on 13 October 2026.** Use [STUDIO-DEPLOYMENT.md](STUDIO-DEPLOYMENT.md) for the product ledger and [PRODUCTION-RUNBOOK.md](PRODUCTION-RUNBOOK.md) for the supported launch, migration, rollback and verification procedure.

The supported deployment is **Debian 13 + native systemd + Caddy**, with separate web, collector and document workers, SQLite/private assets under `/var/lib/atlas`, and Bubblewrap for LaTeX. The older Docker Compose example is not the supported Application Studio production path and has not passed its compiler-isolation gates.

No production server exists yet. The user confirmed no server or domain on 13 October 2026. No purchase or live deployment is implied by preparation. The existing hosting proposal was accepted later on 13 October; domain name/checkout confirmation and account/SSH access remain required. The runbook includes the requested `.tr` comparison. Sole-owner email/password access is implemented and locally tested; production password setup and hosted verification remain outstanding. Local writing key/account/model access has passed; actual generation is currently blocked by exhausted API credit. Add credit in the account Billing page; no key replacement is necessary. `python -m scripts.configure_providers writing` remains the secure setup/rotation command; keys must never be pasted into chat or Git.

All dated local, provider and production evidence is recorded separately in [VALIDATION.md](VALIDATION.md). Do not use a manual refresh as proof of scheduling, an HTTP email response as proof of Gmail receipt, or a local browser viewport as proof of access from a physical device.
