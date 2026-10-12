# Atlas — personal opportunity portal

Atlas is a standalone private web application with a SQLite database and an independent collection worker. No ChatGPT automation and no LLM are required.

## Open locally

```sh
./scripts/start-local.sh
```

Open http://127.0.0.1:8765. This local mode accepts only loopback requests and has no password. Do not expose it through a tunnel or bind it to a public interface. The worker runs while the process is running, including when the browser is closed. Your laptop must remain awake. The production Docker worker runs continuously on the server.

Your imported profile, saved listings, notes, run logs, and database are in `data/`, excluded from Git and Docker builds. Your original résumé has not been copied or uploaded. To import profile JSON on another installation: `python scripts/import_profile.py /private/path/profile.json`.

## What works

- Three discovery categories; company theses stay under research.
- Exact-fact search/filtering, saved searches, dense cards, deterministic ranking with separate eligibility explanations.
- Detail panel with source links, substantive verification dates, missing-field labels, uncertainty, change history.
- Bookmarks, dismissals, private notes, seven application stages, three-item comparison, deadline/event calendar.
- Editable CV-derived profile and weights, private export and deletion.
- Source registry, add-source queue, daily/12-hour settings, source failures and coverage limits.
- Independent worker, bounded fetches, robots checks, IP-pinned public HTTPS destinations, conditional requests, extraction caching, deduplication, exponential backoff, manual rate limits.
- Private production login, secure cookies, CSRF and origin checks, Caddy TLS, server-side data and secrets.

## Deliberate limits

This is a working first version, not comprehensive internet coverage. The registry distinguishes supported extraction, page monitoring needing review, discovery-only pages, failing sources, and pending integration. Source registration does not automatically enable arbitrary scraping.

Research HTML, public ETH/SiROP feeds, Lever jobs, Fraunhofer/DLR detail pages, TUM event data and institute PDF adapters are implemented. Many additional company boards and dynamically rendered pages still need source-specific adapters and access-policy review. Full posting text is not copied: facts and concise summaries link to original descriptions. Source omissions say “Not stated”; unfinished extraction says “Details incomplete”. The original is authoritative. No acceptance probabilities are calculated. Unknown authorization never becomes compatible solely because workload is under 20 hours.

`data/profile.json` includes the private imported profile. The user still needs to supply permit conditions, graduation timing, and the forthcoming academic commitment's exact dates. These are not invented. Free-text commitments are visible for review but not automatically parsed into scheduling restrictions in v1.

## Verify

```sh
.venv/bin/python -m unittest discover -s tests -v
node --check portal/static/app.js
.venv/bin/python -m portal.worker --once
```

Tests use temporary databases and synthetic fixtures. Synthetic test data is never seeded into the portal. Public bootstrapping records are human-reviewed official source facts with fixed review dates, not invented demo listings. Live collector status may be newer than the substantive human review.

See [deployment instructions](docs/DEPLOYMENT.md), [product and architecture](docs/PRODUCT.md), and [validation record](docs/VALIDATION.md).
