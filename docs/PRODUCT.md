# Atlas: product, architecture, and staged roadmap

## Product decisions

The primary screen is stored discovery, not a chat. A quiet sage sidebar, warm white cards, restrained green accents, compact metadata, and a side panel keep browsing calm and comparisons practical. The three requested categories remain first-class. Research is the initial landing tab because a Zurich academic connection is a long-term priority. Company-hosted theses classify as research with partner affiliations, not duplicate job cards.

The first-version loop is source → normalized validated record → SQLite → deterministic matching → filters → source/application page → private application stage. The app never applies or sends messages.

## Initial scope and later work

Version 1 implements the complete local flow, a working daily worker, source health, records, profile matching, saved searches, notes/stages, calendar and comparison. Deployment assets provide private authentication and TLS for a single-server installation. Pending sources are presented honestly.

The next milestones are source-specific PDF and company-board adapters; stronger field-level extraction and evidence anchors; more working-student roles; funded hackathons in Stuttgart/Munich/Zurich; explicit supervision/agreement rules; tested deployment on the user's host; encrypted off-site backups; optional email notifications through the app. None requires ChatGPT automation.

Only add model extraction after measuring how many useful fields conventional parsers miss. Human review, LLM extraction and source facts need distinct provenance. Cache by normalized content hash, parser/model/prompt/schema versions, and never regenerate unchanged records. Low temperature is not a determinism guarantee.

## Architecture

The frontend is accessible HTML/CSS and plain JavaScript served by Flask. There is no frontend build pipeline or paid UI service. Fetch requests retrieve stored records; visiting or filtering the page does not crawl sources or generate text.

The backend uses Flask and Gunicorn, SQLite WAL, parameterized queries, strict JSON checks, controlled categories/stages, and small transactions. The single-user architecture intentionally avoids multi-tenant complexity. The local server restricts loopback/Host/Origin; production enforces session login, HTTPS cookies, origin checks, CSRF tokens, login throttling and a fixed public domain.

A separate Python process checks persisted per-source due times every minute. It is independent of web requests and the browser. Daily is the default; 12 hours is configurable. Exponential backoff and source due times still apply to manual refresh. A database lease prevents overlapping refreshes. The Docker restart policy resumes it after host/container restarts. It cannot continue when a local laptop is asleep or the process is stopped.

Collectors validate public HTTPS destinations, pin a public IP while verifying TLS for the source hostname, revalidate redirects, consult robots directives, cap response sizes and result counts, hash content, and use conditional requests. There is no credentialed scraping, CAPTCHA bypass, JavaScript execution from source content, or model instruction channel. Added URLs remain disabled until reviewed. Discovery from trusted lab pages stores at most 25 candidate links without automatically crawling them.

## Data model

The SQLite schema has distinct tables for opportunities, source evidence, sources, changes, application workflow, refresh runs, extraction cache, queued refresh requests, sessions, login attempts, and worker locks. `meta` stores the editable profile, saved searches, schema version, and worker heartbeat.

An opportunity's normalized JSON contains shared factual fields and category extensions. Stable identity uses a publisher ID plus organization when supplied, otherwise a canonical URL with tracking parameters removed. Research topics sharing one lab URL use topic-specific publisher IDs. Cross-source evidence links remain attached to the same identity. Different topics are never merged by an approximate title match. Changed deadlines and other facts create before/after history.

Shared fields cover title, organization, affiliations, type, topics, summary, requirements, preferred qualifications, technical mentions, languages, location, hours/workload, duration, start/deadline, funding, eligibility, application materials/method, original/application links, and source/verification timestamps. Research extensions cover project type, supervisor, question, deliverables, external-student policy and credit arrangements. Events extend dates, team rules, fees, prizes and support. Not every adapter fills every field; partial extraction is explicit.

`discovered` records first collection; `published` is publisher-supplied only; `verified` is last substantive record verification; `changed` is the last record edit. Source fetch timestamps and overall run timestamps are separate. A successful HTML download alone does not recertify manually reviewed facts. Failed fetches preserve records and add an uncertainty warning. No disappearance is treated as confirmed closure without affirmative source evidence. Expiry and near deadlines are derived against a fixed evaluation date; this date is part of the ranking/filter snapshot.

## Ranking and eligibility

Ranking version 1.0.0 computes interest overlap, CV/profile skill overlap, location preference, Zurich research relevance, known compatible hours and explicitly confirmed support. Weights are user editable. Tie-breakers are deadline, case-insensitive title and stable ID. Closed/expired records follow open records. The same records, profile, filter inputs, evaluation date and ranking version produce the same result.

This is prioritization, not a percentage likelihood. CV claims remain user-provided evidence; requirements absent from the profile are “not evidenced,” not “you lack this.” Eligibility conflicts remain prominent even with high topic relevance. A 40-hour internship is a planning option under a 20-hour preference; it becomes an explicit personal-constraint conflict only if hours are marked hard.

The four labels are implemented conservatively: an explicit requirement mismatch is a conflict; some known academic conditions yield “potentially compatible”; broadly open events can “appear compatible”; otherwise information is insufficient. Absence of a restriction does not prove eligibility. No admission/selection probability is estimated. Work authorization remains unresolved rather than inferred from nationality, German enrollment or a short workload.

German student employment, social insurance, immigration permission and internship/thesis classification are separate. For Switzerland, do not apply local student-work exceptions to a German-enrolled Turkish citizen by assumption. The official SEM guidance explains that authorization is required; ETH project mobility has its own academic and hosting requirements. The app links current reference pages with the date reviewed, and directs unresolved cases to the actual institution/employer/authority.

## Initial source inventory

The registry in `portal/seed.py` spans all three tabs and exposes its operational status in the interface. It includes BMW and Bosch; Airbus, Mercedes-Benz, Porsche and ANYbotics; UZH RPG, ETH RSL and ETH project mobility; Stuttgart ILR and IPR; TUM MIRMI; DLR, Fraunhofer, Max Planck Intelligent Systems; Energy Now!, hackaTUM, HackZurich, Cyber Valley announcements, START Hack, Stuttgart events and DAAD; plus Working Student Jobs and Hackathon Hub as secondary discovery only.

These entries are not a claim of active comprehensive monitoring. The app shows the exact checked URL and distinguishes extractor support, review-needed page monitoring, discovery-only links, source errors and pending setup. Most employer/institute entries initially require additional adapters. No indirect Airbus–ILR posting was fabricated from the user's interview example; the system preserves partner fields and registers the institute as a targeted coverage gap.

Named-program verification: Energy Now! is the ETH Energy Science Center impact accelerator; its current page stated registration closed on 12 October 2026. Cyber Valley is an ecosystem with separate initiatives. HackZurich's organizer page stated hiatus; no future date was invented. hackaTUM lists 27–29 November 2026 and an outdated 2025 notification date, so the inconsistency is surfaced.

## Staged validation

1. Parse real official records, store them, inspect evidence and original pages.
2. Exercise schema errors, duplicate identities, changed deadlines, failed sources, deterministic ordering and eligibility conflicts with synthetic test fixtures in temporary databases.
3. Verify search, filters, detail, saving, notes/stages, comparisons and responsive navigation in the browser.
4. Verify worker heartbeat, due times, restart/backoff, export/deletion and backup consistency.
5. Deploy on the user's selected server; verify HTTPS and unauthenticated rejection, closed-browser updates, restart recovery and restore from backup.
6. Expand only after each adapter has representative fixtures, bounded discovery and an explicit policy review. Audit source health weekly and evaluate coverage by source, not internet-wide claims.
