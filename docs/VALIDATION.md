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
