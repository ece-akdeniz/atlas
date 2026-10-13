# Current validation — 13 October 2026, 12:28 UTC (14:28 Berlin)

This section supersedes the dated snapshots below. Starting commit: `cbb0e30`. No production, provider-generation or Gmail-delivery claim is made. A complete private backup (`before-activation-update-20261013.tar.gz`) preceded changes. Comparing its database to the current one confirmed workflow/bookmarks/notes/tracking (3 rows), uploads (5), Studio projects (1) and document versions (1) were byte-identical. Profile values were unchanged except normal `last_visit` updates. No fixture project or document was inserted into the personal database.

## Checks executed in this implementation

**77 isolated tests passed** with `.venv/bin/python -m unittest discover -s tests -q`. JS syntax and deployment shell syntax checks passed. New tests in `tests/test_activation.py` verify private provider-file permissions/allowlist/environment precedence; account preflight uses the exact model and sends no profile; secrets never appear in state; cached generations incur no repeat call; missing usage keeps a budget reservation; non-finite/nonpositive budgets cannot disable caps; every mapped logo has a local asset and provenance; financial-controller titles do not count as flight controls; rendered mobile/desktop event duplicates collapse; malformed dates and unloaded event shells fail; ETH event years/registration/affiliation conditions remain explicit; four Agentic tracks remain unverified academic routes. Mocked preflight/generation responses are fixtures, not provider-quality evidence.

The existing completion suite also passed again: initial alert backlog suppression, delayed first qualification, cancellation of closed queued alerts, exceptional free technical events without job-style skill lists, cosmetic-versus-material changes, frequency limits/idempotency; complete-empty versus incomplete/truncated feeds and retained verification; CV conflict resolution/Undo and preference preservation; immutable résumé edits, selected paragraph revision and project-specific jobs/readiness; clause-specific document requirements and normalized multi-type/workload filtering. Previous real isolated browser CV/Studio/compilation/download evidence remains below with its original date; it was retained rather than relabeled as a new model-assisted run.

## Current browser observations

- Interests is the first full-width Profile row, before academic background and projects. At 1440 px it spans 1150 px; subsequent sections remain readable columns. At 820 and 390 px, no horizontal page overflow; CV remains last and private eligibility collapsed. Import history is absent. A temporary unsaved preference triggered the keep/discard dialog and was discarded without saving.
- Fresh/reloaded Browse starts Jobs & Industry. Research → search-all on → off restored Research; Jobs did the same. Cards/List preference survived reload independently. Three city toggles share the full City dropdown. Selecting Munich replaced Zurich/Stuttgart, retained `robot` search and Part-time workload, and selecting Munich again cleared only location. Munich includes actual-location Oberpfaffenhofen. Events retained the selected city. No unrelated chips returned.
- Phone 390×844: all three tab labels and city labels fit; first List result began at 467 px with the added city row, and the complete first item/actions was visible. Light and dark layouts had no horizontal overflow. Desktop and tablet Profile checks passed. Calendar used 990 px at a 1280 px viewport; Compare with two selected records used the same 990 px table without an empty third opportunity slot. These are viewport checks, not physical-device/remote tests.
- Skydio “Autonomy Engineer - Deep Learning”: Cards show **Professional role · Full-time** and the source-specific computer-vision/multimodal-model responsibility. List shows **Full-time; weekly hours not stated**. Details retain concrete activities, requirements, official application URL, evidence/history and truthful unspecified application documents. Official Skydio identity renders on both views.
- Six new ETH AI Club events appear under Zurich / Programs & Events. Cards and rows show real event dates. Impulse Hack cards explicitly say **ETH affiliation needs confirmation**, and other hosted events show **Host approval required**. No false external-student eligibility or free-entry inference. All nine roboTUM editions are closed/past and absent from upcoming results.
- Official-logo audit covered **36 distinct current listing organizations** plus every registered source. Shared identity mapping serves cards/list/details/recommendations/Sources. 42 candidate assets were rendered in both themes (84 images loaded). White/black logo contrast errors were corrected; the unrecognizable Hackathon Hub touch icon was rejected from mapping. Final remaining initials are source-only SIROP, Daedalean and Hackathon Hub, with reasons in `identities.json`. TUM is now the university mark, not CVG's eye mark; Verity and Verity Studios are distinct.
- Studio landing displays **Writing · Not configured**, actual/reserved usage and the enforced cap, with a hidden-prompt terminal setup path. The account check is unavailable until a key exists. No CV is sent by preflight. Current measured model ledger: **zero calls, $0**. Real wording quality, language/tone/length, provider-backed revisions/suggestions and PDFs remain unverified.

Local screenshots are saved under ignored `docs/screenshots/activation/` (private UI screenshots are not pushed to Git): Profile desktop/mobile, Browse mobile light/dark, Skydio Cards/List, Studio provider setup and two-theme logo audit.

## Fresh source evidence

At **12:28 UTC**, database totals are **201 stored records / 53 registered sources / 29 sources producing validated records / 175 non-closed/non-expired stored records**. Stored categories: 98 jobs, 69 research, 34 events. Counts include uncertain records, future full-time roles, academic routes and historical events; they are not a count of suitable applications.

Current city/metro coverage (checked is not eligibility):
- Stuttgart: jobs: 5 checked / 3 uncertain; research: 7 checked / 7 uncertain; events: 1 checked / 0 uncertain.
- Munich: jobs: 12 checked / 2 uncertain; research: 8 checked / 1 uncertain; events: 1 checked / 0 uncertain.
- Zurich: jobs: 25 checked / 6 uncertain; research: 39 checked / 7 uncertain; events: 6 checked / 0 uncertain.

- Real refresh: ETH Agentic now produces **4 published tracks**, adding 3 routes; linked Notion instructions remain incomplete. Distinct source summaries and route labels are preserved. No individual recruitment claim.
- Real refresh: roboTUM rendered its permitted public event index, deduplicated 46 mobile/desktop cards to **23 unique editions**, and stored **9 technical past events**. No upcoming technical event was found. Event-detail extraction and recognition of a true empty organizer state remain unfinished. A failed robots connection attempt and a failed first repeat were observed; they did not produce fresh record verification. A later successful repair/repeat at **12:21 UTC** produced 9 records, **0 additions / 0 updates**.
- Real refresh: official ETH AI Club calendar → six linked Luma registration pages → validated event records. JSON-LD supplies year, timezone, dates and location; visible registration text supplies host approval; organizer description preserves ETH participation conditions. The repeat at **12:21 UTC** produced **0 additions**, with 5 expected summary updates after removing generic welcome text. Six current events remain visible under Zurich; this does not imply external-student acceptance.
- Corrected startup technical relevance excludes financial/revenue/quality-control false matches. Destinus and Quantum Systems were recollected; records absent after relevance refinement retain history/verification and are uncertain rather than falsely declared closed. Explicit “Working Student / Intern” type wording now retains both supported filters.
- Aionic: bounded public rendering attempted but Notion content failed to load; existing manually checked internship remains manual, not operational. General SIROP access remains restricted; public lab feeds remain separately operational. Bosch's official student-page robots check returned 406 during this investigation; no bypass. Existing BMW/Bosch registry failures remain visible, with last attempt 09:39 UTC and no false successful collection. Legacy employer/program/university adapters and restricted PDFs remain product work in the [complete source audit](SOURCE-AUDIT-2026-10-13.md).

The web app, collector and document worker were restarted locally. A browser refresh/manual collection is **not** proof of production scheduling. Current local service execution still depends on this laptop. Previous local scheduled-run evidence is dated below; remote scheduled operation remains a release gate.

## Provider, deployment and recovery boundaries

The secure configuration CLI, private file loader, model preflight endpoint, usage display and conservative budget controls are implemented and locally tested. They do not substitute for an actual API key and quality evaluation. No paid request was made. The user confirmed there is no server/domain. No host was purchased or service exposed publicly. Resend transport has no verified sender/key and no test email was sent; provider acceptance and Gmail receipt both remain unverified.

`docs/DEPLOYMENT.md` explicitly supersedes the obsolete Docker path. The only supported procedure is [PRODUCTION-RUNBOOK.md](PRODUCTION-RUNBOOK.md): native Debian 13, Caddy, three systemd services, private persistent SQLite/files, Chromium sandbox, Bubblewrap compilation, migration/rollback, restic/B2 backup and physical-device/offline-laptop/restart/auth/download/restore gates. Installer and backup scripts passed shell syntax checks only; no Linux/remote execution is claimed. Public-price estimate is €9.51/month hosting/domain/backups plus a separate $2 writing cap, awaiting approval and actual checkout. Remote backup initialization/transfer/restore and production compiler isolation are still untested.

See [STUDIO-DEPLOYMENT.md](STUDIO-DEPLOYMENT.md) for each remaining action, exact dependency and acceptance check. Source coverage and document-extraction gaps are explicitly separate from credentials.

---

# Historical validation snapshots (not current counts or production evidence)

# Current validation — 2026-10-13T09:06:40+00:00

This section supersedes the dated snapshots below. Nothing is production-tested. Destructive/workflow tests used `/tmp/atlas-completion-qa/portal.sqlite3` or temporary test databases, not personal data. A complete private backup was taken before changes. Personal workflow (3 rows), uploads (5), Studio projects (1), and document versions (1) were preserved at the 08:58 UTC check; fixture projects and edits exist only in isolation. A subsequent backup comparison confirmed workflow, uploads, projects and documents were byte-identical at the row level; the only changed profile key was `last_visit`, updated by normal browsing.

## Automated behavior

68 isolated tests passed (`.venv/bin/python -m unittest discover -s tests -q`). JavaScript syntax checks passed. New checks cover delayed first-alert qualification; closed queued-alert cancellation before network delivery; free technical events without job-style skills; complete empty versus incomplete/truncated feeds; preservation of old verification; CV conflict replacement/Undo and manual preferences; accepted résumé edits as immutable versions; single-section letter edits and project-specific job IDs; document/checklist readiness; and controlled type migration without touching workflow/verification.

Taxonomy `types-1.1` stores `original_type`, a controlled `types` array, and separate `employment_arrangements`. Equivalent apostrophe/case variants normalize consistently. Explicit multi-type listings match each supported filter once. Ambiguous student project/thesis remains degree-unspecified; absent types remain Unspecified. RPG now reads its actual Thesis Type section, recovering the explicitly published bachelor's option for Time-continuous Facial Motion Capture. DLR/startup parsers no longer default every thesis to a master's degree. Database startup migrates representations without changing discovery, verification, notes, bookmarks, or application history. Future upserts use the same normalization. Workload uses published employment metadata, not a title guess.

## Browser and document evidence

- Research filter: Embodied, Agentic AI returned the same single ID under Master's thesis, Semester project, and Internship. Details preserved “Semester Project / Internship / Master Thesis”. Category-specific dropdowns contain controlled labels, never full-time/part-time.
- Skydio Autonomy Engineer - Deep Learning: Cards show Professional role plus source-confirmed Full-time; List shows Full-time with weekly hours not stated. The summary describes designing/deploying computer-vision and multimodal models, with the official Skydio logo. Full-time availability remains a visible concern.
- Isolated CV upload: transient result dialog resolved education, experience, projects and German language conflicts; the update persisted in Profile; Undo restored the prior facts and retained workload/location preferences. Upload remains at the bottom, and the removed permanent history section is absent.
- Atlas opportunity → Prepare application → separate Studio → actual compilation-copy template → editable letter → one-paragraph revision → worker compilation → PDF preview passed. Unrelated paragraphs remained intact. PDF, .tex and complete source-bundle downloads succeeded through their actual controls.
- Résumé accept/reject/apply was exercised with a clearly labeled isolated suggestion fixture (no model call). Applying the accepted equivalent-wording change created a new version and retained the master/previous source. The resulting résumé compiled to one page; its rendered PDF was inspected with intact headings, entries, readable text and no visible overflow. Automated tests also verify immutable edits and readiness.
- Production authentication/download protection, job persistence/dedupe, profile persistence, ranking stability and previous responsive checks remain covered by the existing isolated suite/history. Browser viewport emulation is not proof of access from physical phone/iPad or remote synchronization.

Current responsive recheck: 390×844 light/dark Atlas and Studio had no horizontal page overflow. Browse's first List result began at 434 px with all three category labels visible. At 820×1180, Profile/Calendar used the available workspace and two selections created exactly two opportunity columns in Compare (plus the field-label column). At 1440×1000, Profile occupied 1150 px in two readable 566 px sections, exceeding the old 950 px cap. Its final section was CV Upload; permanent import history was absent. Local screenshot evidence is retained under ignored `docs/screenshots/completion/`.

Real macOS sandbox checks rerun successfully: ordinary compilation, denied private-file read, and denied TeX shell execution. No claim of Linux production isolation follows from that result.

## Current collection snapshot

183 stored records from 52 registered sources; 166 non-expired/non-closed stored records; 27 operational collectors. Stored categories: {'jobs': 98, 'research': 66, 'events': 19}. These include future full-time options, undated routes, uncertain records and historical events; they are not all suitable current openings. Shared Verity boards deduplicate by publisher identity.

Checked / uncertain visible records using the actual city/metro coverage rule:
- Stuttgart: jobs 4 checked / 4 uncertain; research 7 checked / 7 uncertain; events 1 checked / 0 uncertain.
- Munich: jobs 13 checked / 1 uncertain; research 8 checked / 1 uncertain; events 1 checked / 0 uncertain.
- Zurich: jobs 25 checked / 6 uncertain; research 39 checked / 4 uncertain; events 0 checked / 0 uncertain.

Every registered source, current timestamps, limitations and next actions are in [SOURCE-AUDIT-2026-10-13.md](SOURCE-AUDIT-2026-10-13.md). BMW's robots connection timed out and Bosch returned HTTP 410; neither has a successful collection timestamp. DLR RM and hackaTUM recovered during this pass. The full manual cycle checked 29 sources, followed by targeted reprocessing; this is not scheduler evidence.

Newly operational: Embotech (5 relevant index-confirmed roles, linked PDF details blocked by 403) and main Verity (2 records shared/deduplicated with Verity Studios, including one speculative route). Aionic Labs has one manually source-checked research/engineering internship, explicitly incomplete; automatic collection remains unfinished. ETH confirms Aionic Labs' origin, but its identity as the user's intended “Aionics Lab” remains an explicit assumption. roboTUM's official upcoming-events view returned no events; its 2025/June-2026 hackathons are historical. General SIROP is access-limited; lab-supported public feeds remain operational.

Real repeat collection in a separate database at 08:30 UTC: Skydio 9, Embotech 5, Verity 2; each added 0 and changed 0 payloads. This establishes idempotence for those unchanged official inputs, not reliability for every website. Complete-feed absence marks a record unverified without falsely renewing its verification or declaring closure. Parser errors/truncation preserve prior records; access restrictions remain enforced.

## Unverified and blocked

No paid model call or email was sent. Provider acceptance and Gmail receipt are both unverified. Linux TeX isolation, live HTTPS/authentication, physical-device synchronization, scheduler operation with the laptop disconnected, remote service restart and encrypted off-server restore remain production gates. Dynamic Aionic/roboTUM collection, additional Agentic tracks, several legacy employers/programs, complete PDF extraction and current Zurich event coverage remain product/integration work, not credential-only blockers. See the complete [product/deployment ledger](STUDIO-DEPLOYMENT.md).

---

# Historical snapshot — earlier implementation, 13 October 2026 (before this pass)

# Update validation — 13 October 2026

Ranking version 2.2.0 records the added full-time/future-option and explicit nationality-conflict rules. 51 isolated regression tests pass. Tests include the prior extraction/ranking/workflow checks plus four distinct RPG checklist items, transcript disambiguation, ZIP traversal rejection, CV import dedupe/preferences/Undo protection, immutable Studio snapshots and master files, authenticated document access, CSRF recovery, persistent local sessions, durable job dedupe/error retention, manual refresh/backoff, initial alert suppression, failed-source alert suppression and destination-change cancellation.

Real macOS TeX sandbox checks passed: ordinary compilation succeeds, an absolute private-file read fails, and shell escape cannot create a file. The actual résumé and cover-letter templates compile from separate repaired working copies; master uploads are preserved. Atlas → Prepare application → Studio → template selection → local draft → worker compilation → private PDF page preview was exercised in an isolated database. Generated résumé and letter PDFs were visually inspected, each one page. The résumé retains all wording and only reorders intact project blocks. Local letters are explicitly English evidence-only starters; model quality has not been evaluated without a key.

Backup and restore of a private validation copy passed SQLite integrity validation. Tests do not modify the personal workflow. Production-mode local tests protect Studio/state/documents behind sign-in; live HTTPS authentication and multi-device sharing remain unverified.

## Collection snapshot

177 stored records, 52 registered sources, 160 non-expired/non-closed stored records, and 23 integrations currently producing records. These are not 160 confirmed suitable vacancies. Full-time future options, speculative routes and uncertain projects are retained with labels.

New successful collectors: FIUS 4 PDF postings; Auterion 1; Destinus 14; Dufour 1; ETH Agentic Systems 1 academic route; Flyability 1; NEURA 24; NODE 1; Quantum Systems 26; Sereact 3; Skydio 9; Verity Studios 2 (one published speculative route); Wingtra 2. Existing UZH RPG has 24 projects and the exact CV / bachelor's transcript / master's transcript / relevant-project-description checklist for the world-models project. CVG's manually added homepage is linked to its existing project collector. Both publisher and employer evidence are preserved for FIUS PDFs. Verity's role-specific location is not inferred from its headquarters.

Checked versus uncertain visible records by priority area:
- Stuttgart: jobs 4 / 4; research 7 / 7; events 1 / 0.
- Munich: jobs 12 / 2; research 5 / 4; events 0 / 1. Nearby records keep actual cities, including Gilching, Garching and Oberpfaffenhofen; the filter/coverage label is Munich.
- Zurich: jobs 16 / 9; research 39 / 4; events 0 / 0.

An independently running collector completed scheduled cycles at 23:02, 23:10 and 23:17 UTC on 12 October (13 October locally). The repeat cycle across twelve established new adapters added zero records and changed zero payloads. The subsequent targeted reprocess updated one repaired FIUS description; Verity produced two validated records. This demonstrates the local scheduler loop, not operation while the laptop sleeps.

## Remaining source limits

BMW, Bosch, DLR RM and hackaTUM failures remain visible; previous records retain their prior successful verification. General SIROP and roboTUM remain link-only/access or integration limited. Aionic Labs is an explicit identity assumption with a linked student route, not a fabricated opening. Embotech and main Verity have access/rendering limitations; the separate Verity Studios collector is operational. Several legacy company/university registry entries still need adapters; registered URLs do not count as operational. NEURA covers its AI category, not every department. Current event coverage remains weak in Munich and Zurich. Official logos are used where identity/provenance was verified, with deliberate initials where suitable assets were unavailable.

## Browser and deployment

Verified real List rows, persisted view choice across navigation/reload, four-item checklist, separate Studio navigation, private PDF previews, and Profile's bottom CV Upload without the removed history panel. Mobile checks use 390 px; the native file-input overflow was found and repaired. Desktop and mobile themes were inspected. Source coverage includes horse/pretzel/Alps icons and visual worker state, without a duplicate topbar page name.

Server/systemd/Caddy setup is prepared; no server has been purchased or deployed. No paid model call or Gmail email has been sent. Outstanding dependencies and price assumptions are in STUDIO-DEPLOYMENT.md. PDF sandbox behavior on Linux, remote restart recovery, remote scheduler operation, device sign-in/sync and real Gmail receipt remain release gates.

---

## Previous audit-time validation (preserved)

# Validation — 12 October 2026

## Automated checks

34 tests passed with temporary isolated SQLite databases. Coverage includes token boundaries (`across` cannot match ROS), ROS/ROS2 aliases, all 25 synthetic RPG projects, source-present requirements/contacts, preferred qualifications, PDF line wraps and contact-section boundaries, incomplete versus source-absent fields, cross-publisher SiROP identity, conflicting evidence, idempotent upserts, changed deadlines, failed-source retention, stable ranking and recommendation gates, enrollment/workload distinctions, event years, profile persistence and invalid dates, bookmark independence, removal from application tracking without losing notes, CSRF, private-address rejection, robots specificity, production authentication/fail-closed configuration and personal-data deletion. Fixtures never enter the personal database.

Python compileall and JavaScript syntax checks passed. Authentication was tested locally with the production configuration test; public HTTPS hosting is not deployed.

## Actual collection and coverage

The personal database contains 88 source-backed records across 34 registered sources. Ten integrations were healthy at the latest full cycle; two additional integrations (DLR and hackaTUM) had previously succeeded but timed out on the latest check. The registry is not a listing count or a claim of comprehensive coverage.

Successful outputs: UZH RPG 24, ETH RSL public feed 16, ETH Movement public feed 1, DLR Robotics/Mechatronics 4, Stuttgart IFF 8, Fraunhofer IPA 5, TUM CVG 4, TUM SRL 1 lead, ANYbotics 3, TUM.ai 16 historical events, hackaTUM 1 and Cyber Valley nICLAS 1. RPG, DLR, IFF, CVG, RSL, IPA and ANYbotics representative fields were inspected against official HTML, JSON or PDFs. IFF documents retain source page, document URL, hash, page references and date evidence. Hosting a PDF does not establish recruitment or supervision.

Current checked research records: Stuttgart 7, Munich/nearby 4, Zurich 39. Stuttgart also has one checked event; Zurich has three checked industry roles, all full-time/future options. The latest Munich jobs/event checks are uncertain after fetch failures. Six undated IFF academic routes and the SRL lab lead remain distinct from confirmed openings. Old TUM.ai events are not upcoming. No current Zurich AI/robotics hackathon or fresh Stuttgart industry role was verified. Exact counts and statuses: coverage-snapshot.json.

## Repeat collection and stability

A real repeat collection used `/tmp/atlas-idempotence.sqlite3`, copied with SQLite's backup API. Eight integrations reproduced identical IDs and payload hashes with zero new history entries. IFF retained all IDs but recorded two document-failure transitions and preserved last-known facts/verification. TUM CVG failed its robots connection check. These failures are reported rather than called idempotent successes. The detailed measurements are in repeat-collection.json. Deterministic fixture tests separately establish identical-input idempotence and stable ranking for the same profile, evaluation date and ranking version 2.1.0.

## Independent scheduler

The worker was started as a separate process against `/tmp/atlas-validation.sqlite3`. RPG was set due at 21:14:40 UTC; a scheduled run started at 21:15:21 and completed at 21:15:26. The requests table contained zero manual requests. This verifies the worker's due-time loop independently of browser/manual refresh; it does not prove a full elapsed 24-hour interval or production uptime. Personal collection runs in its own worker process and stops when the computer sleeps or that process exits.

## Browser workflows

Rendered checks at 1360×900 and 390×844 in both themes: home, category navigation, search, profile summary, details, source coverage and Saved. At 390 px the first complete recommendation ends around 563 px and the body has no horizontal overflow. All three category labels fit. Sensitive profile information starts collapsed. Focus moves to Close when a detail dialog opens; the visible outline and theme tokens were inspected. Theme preference persists across reloads. Eight normal-text semantic color pairs passed WCAG AA (4.5:1), ranging from 5.9:1 to 14.97:1; values are in contrast-check.json.

In the isolated test copy, profile maximum hours saved and survived reload; unsaved-edit navigation showed Keep editing / Discard. Bookmarking, moving to Applied and notes persisted. After the UI Remove action the tracker was empty, while Saved still contained the same record and details retained its private note with Stage = Not tracked. Personal profile/workflow tests never used the personal database. Its existing workflow row remains stage-null, unbookmarked and without notes.

Before/after screenshots are in docs/screenshots/before and docs/screenshots/after. The application-pipeline screenshot is explicitly named `applications-dark-isolated.jpg` because it contains a test workflow, not a user-created application.

## Remaining unverified behavior

No target-server Docker build, TLS certificate, deployed sign-in, restart recovery or off-site restore drill was performed. Logos identify publishers; they do not imply endorsement. General SIROP search requires a permitted integration, and roboTUM's dynamic data integration remains pending. Further employers, programs, grants and complete extraction of all undated PDFs remain coverage work. Current source errors and bounds stay visible.
