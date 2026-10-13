# Current source audit — 2026-10-13T12:28:03+00:00

This current section supersedes the clearly dated history below. Registry entries, operational collectors and usable current opportunities are different counts.

- 53 registered sources; 29 with successful validated collection.
- 201 stored records: 98 jobs, 69 research, 34 events. Includes historical, uncertain, route and future employment records.
- Two registered failures remain: BMW and Bosch. Current failure messages and timestamps appear per source; earlier HTTP/timeout results remain historical.
- Official shared identity registry: `portal/static/logos/identities.json`; per-asset provenance: `manifest.json`. All current listing organizations mapped. Remaining source-only initials: SIROP (official asset fetch restricted), Daedalean (redirect to Destinus does not establish a reusable historical brand asset), Hackathon Hub (official touch icon is not recognizable at UI size).

## Current per-source ledger

### FIUS · employer postings & PDFs (`807d62512a4a`)
- Official source: https://www.fius.de/en/aushang/
- Status: **Operational within stated scope**; adapter `fius-pdf`. Stored 4; not closed/past 4 (not a suitability count).
- Last attempt: 2026-10-13T08:03:56+00:00; last successful collection: 2026-10-13T08:03:56+00:00.
- Scope/evidence: Official feed or bounded index-to-detail collector; excludes senior and unrelated roles.
- Last result: 4 relevant validated records from 10 published entries; official publisher IDs; no title-only quota. All index entries inspected; eligible detail pages followed.
- Remaining action/dependency: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### cvg.cit.tum.de (`a4c63ea3bfa3`)
- Official source: https://cvg.cit.tum.de/
- Status: **Shared collector → tum-cvg**; adapter `alias`. Stored 0; not closed/past 0 (not a suitability count).
- Last attempt: Never; last successful collection: Never.
- Scope/evidence: Covered by TUM CVG project collector; homepage retained as source history.
- Remaining action/dependency: Use the shared collector status and avoid duplicate collection.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Aionic Labs (`aionic-labs`)
- Official source: https://aioniclabs.notion.site/team-careers
- Status: **Manual review only**; adapter `pending`. Stored 1; not closed/past 1 (not a suitability count).
- Last attempt: Never; last successful collection: Never.
- Scope/evidence: Public rendered careers page lists Zurich roles including Research / Engineering Internship (13 Oct 2026). Automatic index extraction still requires a permitted rendered-page collector; linked Google form robots check returned HTTP 400. Browser-reviewed record is not an operational feed.
- Remaining action/dependency: Bounded public Notion renderer was attempted with no access-control bypass; document failed to load. Keep manual internship lead, not automated freshness. Resolve public rendering or obtain a supported feed; Google form instructions remain uncollected.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Airbus · careers (`airbus`)
- Official source: https://www.airbus.com/en/careers
- Status: **Pending setup**; adapter `pending`. Stored 0; not closed/past 0 (not a suitability count).
- Last attempt: Never; last successful collection: Never.
- Scope/evidence: Bounded to this page; linked candidates require review.
- Remaining action/dependency: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### ANYbotics · public Lever postings (`anybotics`)
- Official source: https://api.lever.co/v0/postings/anybotics?mode=json&limit=100
- Status: **Operational within stated scope**; adapter `lever`. Stored 3; not closed/past 3 (not a suitability count).
- Last attempt: 2026-10-13T08:04:00+00:00; last successful collection: 2026-10-13T08:04:00+00:00.
- Scope/evidence: Bounded official index and detail extraction; operational only after validated records.
- Last result: Unchanged; cached validated extraction
- Remaining action/dependency: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Auterion (`auterion`)
- Official source: https://boards-api.greenhouse.io/v1/boards/auterion/jobs?content=true
- Status: **Operational within stated scope**; adapter `greenhouse`. Stored 1; not closed/past 1 (not a suitability count).
- Last attempt: 2026-10-13T08:04:02+00:00; last successful collection: 2026-10-13T08:04:02+00:00.
- Scope/evidence: Official feed or bounded index-to-detail collector; excludes senior and unrelated roles.
- Last result: 1 relevant validated records from 19 published entries; official publisher IDs; no title-only quota. All index entries inspected; eligible detail pages followed.
- Remaining action/dependency: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### BMW Group · student roles (`bmw`)
- Official source: https://www.bmwgroup.jobs/de/de/jobfinder/job-description.196070.html
- Status: **Failed collection**; adapter `jsonld`. Stored 1; not closed/past 1 (not a suitability count).
- Last attempt: 2026-10-13T09:39:07+00:00; last successful collection: Never.
- Scope/evidence: Bounded to this page; linked candidates require review.
- Last result: Cannot verify robots policy: [Errno 8] nodename nor servname provided, or not known
- Failure: Cannot verify robots policy: [Errno 8] nodename nor servname provided, or not known
- Remaining action/dependency: Find a permitted official feed or supported board integration; robots-policy connection timeout must not be bypassed.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Bosch · computer vision (`bosch`)
- Official source: https://jobs.bosch.de/de/job/Praktikum-im-Computer-Vision-Stuttgart-Mitte?id=dadc07dc-69c4-4750-ba7b-59e087068551
- Status: **Failed collection**; adapter `reviewed`. Stored 1; not closed/past 1 (not a suitability count).
- Last attempt: 2026-10-13T09:39:07+00:00; last successful collection: Never.
- Scope/evidence: Bounded to this page; linked candidates require review.
- Last result: Cannot verify robots policy: [Errno 8] nodename nor servname provided, or not known
- Failure: Cannot verify robots policy: [Errno 8] nodename nor servname provided, or not known
- Remaining action/dependency: Replace retired HTTP-410 career URL using the current official careers navigation, then validate a permitted collector.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Cyber Valley · nICLAS Forum 2026 (`cyber-niclas`)
- Official source: https://www.cyber-valley.de/de/events/niclas-forum-2026
- Status: **Operational within stated scope**; adapter `cyber`. Stored 1; not closed/past 1 (not a suitability count).
- Last attempt: 2026-10-13T08:04:03+00:00; last successful collection: 2026-10-13T08:04:03+00:00.
- Scope/evidence: Bounded official index and detail extraction; operational only after validated records.
- Last result: 1 official event; registration status and financial support require confirmation
- Remaining action/dependency: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Cyber Valley · ecosystem announcements (`cyber-valley`)
- Official source: https://cyber-valley.de/en/events
- Status: **Pending setup**; adapter `pending`. Stored 0; not closed/past 0 (not a suitability count).
- Last attempt: Never; last successful collection: Never.
- Scope/evidence: Bounded to this page; linked candidates require review.
- Remaining action/dependency: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### DAAD · scholarships & mobility (`daad`)
- Official source: https://www.daad.de/en/studying-in-germany/scholarships/
- Status: **Pending setup**; adapter `pending`. Stored 0; not closed/past 0 (not a suitability count).
- Last attempt: Never; last successful collection: Never.
- Scope/evidence: Bounded to this page; linked candidates require review.
- Remaining action/dependency: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Daedalean (`daedalean`)
- Official source: https://daedalean.ai/careers
- Status: **Shared collector → destinus**; adapter `alias`. Stored 0; not closed/past 0 (not a suitability count).
- Last attempt: Never; last successful collection: Never.
- Scope/evidence: Shared official Destinus board; Daedalean affiliation retained when named in the posting.
- Remaining action/dependency: Use the shared collector status and avoid duplicate collection.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Destinus (`destinus`)
- Official source: https://www.workable.com/api/accounts/destinusgroup?details=true
- Status: **Operational within stated scope**; adapter `workable`. Stored 14; not closed/past 14 (not a suitability count).
- Last attempt: 2026-10-13T10:35:11+00:00; last successful collection: 2026-10-13T10:35:11+00:00.
- Scope/evidence: Official feed or bounded index-to-detail collector; excludes senior and unrelated roles.
- Last result: 12 relevant validated records from 171 published entries; official publisher IDs; no title-only quota. All index entries inspected; eligible detail pages followed.
- Remaining action/dependency: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### DLR · student research (`dlr`)
- Official source: https://www.dlr.de/en/careers
- Status: **Pending setup**; adapter `pending`. Stored 0; not closed/past 0 (not a suitability count).
- Last attempt: Never; last successful collection: Never.
- Scope/evidence: Bounded to this page; linked candidates require review.
- Remaining action/dependency: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### DLR · Robotics & Mechatronics students (`dlr-rm`)
- Official source: https://www.dlr.de/en/rm/jobs/students
- Status: **Operational within stated scope**; adapter `dlr`. Stored 4; not closed/past 4 (not a suitability count).
- Last attempt: 2026-10-13T08:04:27+00:00; last successful collection: 2026-10-13T08:04:27+00:00.
- Scope/evidence: Bounded official index and detail extraction; operational only after validated records.
- Last result: 4 of 4 linked student postings; single index; maximum 30 details
- Remaining action/dependency: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Dufour Aerospace (`dufour`)
- Official source: https://join.com/companies/dufour
- Status: **Operational within stated scope**; adapter `join-html`. Stored 1; not closed/past 1 (not a suitability count).
- Last attempt: 2026-10-13T08:04:35+00:00; last successful collection: 2026-10-13T08:04:35+00:00.
- Scope/evidence: Official feed or bounded index-to-detail collector; excludes senior and unrelated roles.
- Last result: 1 relevant validated records from 1 published entries; official publisher IDs; no title-only quota. All index entries inspected; eligible detail pages followed.
- Remaining action/dependency: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Embotech (`embotech`)
- Official source: https://embotech.ai/career
- Status: **Operational within stated scope**; adapter `embotech-pdf`. Stored 5; not closed/past 5 (not a suitability count).
- Last attempt: 2026-10-13T08:04:43+00:00; last successful collection: 2026-10-13T08:04:43+00:00.
- Scope/evidence: Official role index; source-hosted PDF details where permitted. Blocked PDFs remain explicitly incomplete.
- Last result: 5 relevant validated records from 9 published entries; official publisher IDs; no title-only quota. All index entries inspected; eligible detail pages followed.
- Remaining action/dependency: Five index-confirmed roles stored; PDF documents returned 403. Obtain permitted document access/feed to complete responsibilities, requirements and application documents.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### ETH · Energy Now! (`energy-now`)
- Official source: https://esc.ethz.ch/industry/entrepreneurship/energy-now.html
- Status: **Needs review**; adapter `reviewed`. Stored 1; not closed/past 0 (not a suitability count).
- Last attempt: 2026-10-13T08:04:47+00:00; last successful collection: 2026-10-13T08:04:47+00:00.
- Scope/evidence: Bounded to this page; linked candidates require review.
- Last result: Reachable; structured details need review
- Remaining action/dependency: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### ETH Agentic Systems Lab (`eth-agentic-systems`)
- Official source: https://agenticsystems.ethz.ch/
- Status: **Operational within stated scope**; adapter `agentic-route`. Stored 4; not closed/past 4 (not a suitability count).
- Last attempt: 2026-10-13T10:35:13+00:00; last successful collection: 2026-10-13T10:35:13+00:00.
- Scope/evidence: Four officially published application tracks; academic routes, not confirmed individual openings. Linked Notion instructions incomplete.
- Last result: 4 published academic application tracks; linked Notion instructions incomplete; no individual vacancy claim.
- Remaining action/dependency: All four published tracks collected as unverified academic routes. Linked Notion instructions still incomplete; do not imply individual vacancies or external-student acceptance.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### ETH AI Club · upcoming events (`eth-ai-club`)
- Official source: https://www.ethaiclub.org/
- Status: **Operational within stated scope**; adapter `eth-ai-events`. Stored 6; not closed/past 6 (not a suitability count).
- Last attempt: 2026-10-13T12:21:33+00:00; last successful collection: 2026-10-13T12:21:33+00:00.
- Scope/evidence: Official feed or bounded index-to-detail collector; excludes senior and unrelated roles.
- Last result: 6 organizer-linked registration pages validated; maximum 20 upcoming cards; host/enrollment conditions retained.
- Remaining action/dependency: Six official organizer-linked Luma event pages produce current records with full dates and ETH/host-approval conditions. Continue daily checks; sample cancellation and fee fields as source formats change.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### ETH · project mobility (`eth-mobility`)
- Official source: https://ethz.ch/en/studies/non-degree-courses/project.html
- Status: **Needs review**; adapter `reviewed`. Stored 1; not closed/past 1 (not a suitability count).
- Last attempt: 2026-10-13T08:05:01+00:00; last successful collection: 2026-10-13T08:05:01+00:00.
- Scope/evidence: Bounded to this page; linked candidates require review.
- Last result: Reachable; structured details need review
- Remaining action/dependency: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### ETH · Movement Biomechanics public feed (`eth-movement`)
- Official source: https://movement.ethz.ch/student-projects.html
- Status: **Operational within stated scope**; adapter `eth-projects`. Stored 1; not closed/past 1 (not a suitability count).
- Last attempt: 2026-10-13T08:05:03+00:00; last successful collection: 2026-10-13T08:05:03+00:00.
- Scope/evidence: Bounded official index and detail extraction; operational only after validated records.
- Last result: 1 relevant projects from 1 official public lab feeds; 0 restricted descriptions; full SIROP search not collected
- Remaining action/dependency: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Flyability (`flyability`)
- Official source: https://www.workable.com/api/accounts/flyability?details=true
- Status: **Operational within stated scope**; adapter `workable`. Stored 1; not closed/past 1 (not a suitability count).
- Last attempt: 2026-10-13T08:05:08+00:00; last successful collection: 2026-10-13T08:05:08+00:00.
- Scope/evidence: Official feed or bounded index-to-detail collector; excludes senior and unrelated roles.
- Last result: 1 relevant validated records from 7 published entries; official publisher IDs; no title-only quota. All index entries inspected; eligible detail pages followed.
- Remaining action/dependency: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Fraunhofer · jobs & theses (`fraunhofer`)
- Official source: https://jobs.fraunhofer.de/
- Status: **Pending setup**; adapter `pending`. Stored 0; not closed/past 0 (not a suitability count).
- Last attempt: Never; last successful collection: Never.
- Scope/evidence: Bounded to this page; linked candidates require review.
- Remaining action/dependency: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Hackathon Hub · secondary discovery (`hackathonhub`)
- Official source: https://hackathonhub.eu/events
- Status: **Pending setup**; adapter `pending`. Stored 0; not closed/past 0 (not a suitability count).
- Last attempt: Never; last successful collection: Never.
- Scope/evidence: Bounded to this page; linked candidates require review.
- Remaining action/dependency: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### hackaTUM · official FAQ (`hackatum`)
- Official source: https://hack.tum.de/faq/
- Status: **Operational within stated scope**; adapter `hackatum`. Stored 1; not closed/past 1 (not a suitability count).
- Last attempt: 2026-10-13T08:05:12+00:00; last successful collection: 2026-10-13T08:05:12+00:00.
- Scope/evidence: Bounded to this page; linked candidates require review.
- Last result: Extracted 1 records
- Remaining action/dependency: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### HackZurich · organizer (`hackzurich`)
- Official source: https://hackzurich.com/
- Status: **Needs review**; adapter `reviewed`. Stored 0; not closed/past 0 (not a suitability count).
- Last attempt: 2026-10-13T08:05:16+00:00; last successful collection: 2026-10-13T08:05:16+00:00.
- Scope/evidence: Bounded to this page; linked candidates require review.
- Last result: Reachable; no listing parser configured
- Remaining action/dependency: Verify the next official edition and registration rather than reusing historical dates; collector remains incomplete.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Fraunhofer IPA · Stuttgart student research (`ipa-students`)
- Official source: https://jobs.fraunhofer.de/search/?q=&locationsearch=Stuttgart&optionsFacetsDD_customfield1=Studentische+Hilfskr%C3%A4fte&optionsFacetsDD_customfield4=IPA+-+Produktionstechnik+und+Automatisierung
- Status: **Operational within stated scope**; adapter `fraunhofer`. Stored 5; not closed/past 5 (not a suitability count).
- Last attempt: 2026-10-13T08:05:40+00:00; last successful collection: 2026-10-13T08:05:40+00:00.
- Scope/evidence: Bounded official index and detail extraction; operational only after validated records.
- Last result: 5 relevant IPA student research roles from 6 details / 1 index pages; up to 8 pages and 50 details
- Remaining action/dependency: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Mercedes-Benz · careers (`mercedes`)
- Official source: https://jobs.mercedes-benz.com/
- Status: **Pending setup**; adapter `pending`. Stored 0; not closed/past 0 (not a suitability count).
- Last attempt: Never; last successful collection: Never.
- Scope/evidence: Bounded to this page; linked candidates require review.
- Remaining action/dependency: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Max Planck · Intelligent Systems (`mpi-is`)
- Official source: https://is.mpg.de/jobs
- Status: **Pending setup**; adapter `pending`. Stored 0; not closed/past 0 (not a suitability count).
- Last attempt: Never; last successful collection: Never.
- Scope/evidence: Bounded to this page; linked candidates require review.
- Remaining action/dependency: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### NEURA Robotics (`neura`)
- Official source: https://jobs.neura-robotics.com/category/ai/58bd0246-cfdb-4930-b2f3-bc758471b5a6
- Status: **Operational within stated scope**; adapter `neura-html`. Stored 24; not closed/past 24 (not a suitability count).
- Last attempt: 2026-10-13T08:06:48+00:00; last successful collection: 2026-10-13T08:06:48+00:00.
- Scope/evidence: Official feed or bounded index-to-detail collector; excludes senior and unrelated roles.
- Last result: 24 relevant validated records from 37 published entries; official publisher IDs; no title-only quota. All index entries inspected; eligible detail pages followed.
- Remaining action/dependency: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### NODE Robotics (`node`)
- Official source: https://node-robotics-gmbh.jobs.personio.de/?language=en
- Status: **Operational within stated scope**; adapter `personio-html`. Stored 1; not closed/past 1 (not a suitability count).
- Last attempt: 2026-10-13T08:06:52+00:00; last successful collection: 2026-10-13T08:06:52+00:00.
- Scope/evidence: Official feed or bounded index-to-detail collector; excludes senior and unrelated roles.
- Last result: 1 relevant validated records from 2 published entries; official publisher IDs; no title-only quota. All index entries inspected; eligible detail pages followed.
- Remaining action/dependency: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Porsche · careers (`porsche`)
- Official source: https://jobs.porsche.com/
- Status: **Pending setup**; adapter `pending`. Stored 0; not closed/past 0 (not a suitability count).
- Last attempt: Never; last successful collection: Never.
- Scope/evidence: Bounded to this page; linked candidates require review.
- Remaining action/dependency: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Quantum Systems (`quantum-systems`)
- Official source: https://career.quantum-systems.com/api/offers
- Status: **Operational within stated scope**; adapter `recruitee`. Stored 26; not closed/past 26 (not a suitability count).
- Last attempt: 2026-10-13T10:35:56+00:00; last successful collection: 2026-10-13T10:35:56+00:00.
- Scope/evidence: Official feed or bounded index-to-detail collector; excludes senior and unrelated roles.
- Last result: 22 relevant validated records from 198 published entries; official publisher IDs; no title-only quota. All index entries inspected; eligible detail pages followed.
- Remaining action/dependency: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### roboTUM · organizer events (`robotum`)
- Official source: https://www.robotum.info/events
- Status: **Operational within stated scope**; adapter `robotum-rendered`. Stored 9; not closed/past 0 (not a suitability count).
- Last attempt: 2026-10-13T12:21:48+00:00; last successful collection: 2026-10-13T12:21:48+00:00.
- Scope/evidence: Public rendered organizer index, at most 100 unique events. Past editions retained as closed; event-detail extraction incomplete. No access controls bypassed.
- Last result: 23 unique published events checked; 9 technically relevant editions stored. Historical editions excluded from upcoming results. Event-detail extraction remains incomplete.
- Remaining action/dependency: Rendered public index now stores nine technical historical editions; no upcoming edition. Finish event-detail extraction and robust explicit-empty-state handling; transient robots connection failures must preserve data.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### UZH · Robotics and Perception Group (`rpg`)
- Official source: https://rpg.ifi.uzh.ch/student_projects.php
- Status: **Operational within stated scope**; adapter `rpg`. Stored 24; not closed/past 24 (not a suitability count).
- Last attempt: 2026-10-13T08:07:32+00:00; last successful collection: 2026-10-13T08:07:32+00:00.
- Scope/evidence: Bounded to this page; linked candidates require review.
- Last result: Unchanged; cached validated extraction
- Remaining action/dependency: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### ETH · Robotic Systems Lab public SIROP feed (`rsl`)
- Official source: https://rsl.ethz.ch/education-students/student-projects0.html
- Status: **Operational within stated scope**; adapter `eth-projects`. Stored 16; not closed/past 16 (not a suitability count).
- Last attempt: 2026-10-13T08:07:41+00:00; last successful collection: 2026-10-13T08:07:41+00:00.
- Scope/evidence: Bounded official index and detail extraction; operational only after validated records.
- Last result: 16 relevant projects from 1 official public lab feeds; 2 restricted descriptions; full SIROP search not collected
- Remaining action/dependency: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Sereact (`sereact`)
- Official source: https://jobs.ashbyhq.com/sereact
- Status: **Operational within stated scope**; adapter `ashby-html`. Stored 3; not closed/past 3 (not a suitability count).
- Last attempt: 2026-10-13T08:08:01+00:00; last successful collection: 2026-10-13T08:08:01+00:00.
- Scope/evidence: Official feed or bounded index-to-detail collector; excludes senior and unrelated roles.
- Last result: 3 relevant validated records from 37 published entries; official publisher IDs; no title-only quota. All index entries inspected; eligible detail pages followed.
- Remaining action/dependency: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### SIROP · protected general search (`sirop`)
- Official source: https://sirop.org/app
- Status: **Link only**; adapter `pending`. Stored 0; not closed/past 0 (not a suitability count).
- Last attempt: Never; last successful collection: Never.
- Scope/evidence: General search robots check returned HTTP 403 on 13 Oct 2026. Use official public lab-embedded feeds (RSL/Movement) or open this source manually. No login or access-control bypass.
- Remaining action/dependency: General collection receives access restrictions. Obtain a supported feed or permission; retain direct link. RSL and Movement public project feeds work independently.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Skydio (`skydio`)
- Official source: https://www.skydio.com/careers
- Status: **Operational within stated scope**; adapter `skydio-html`. Stored 9; not closed/past 9 (not a suitability count).
- Last attempt: 2026-10-13T08:09:22+00:00; last successful collection: 2026-10-13T08:09:22+00:00.
- Scope/evidence: Official feed or bounded index-to-detail collector; excludes senior and unrelated roles.
- Last result: 9 relevant validated records from 157 published entries; official publisher IDs; no title-only quota. All index entries inspected; eligible detail pages followed.
- Remaining action/dependency: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### START Hack · organizer (`start-hack`)
- Official source: https://www.startglobal.org/start-hack
- Status: **Pending setup**; adapter `pending`. Stored 0; not closed/past 0 (not a suitability count).
- Last attempt: Never; last successful collection: Never.
- Scope/evidence: Bounded to this page; linked candidates require review.
- Remaining action/dependency: Add official current-edition detail extraction and date/eligibility checks; reachable page is not operational coverage.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Stuttgart · university events (`stuttgart-events`)
- Official source: https://www.uni-stuttgart.de/en/university/news/event/
- Status: **Pending setup**; adapter `pending`. Stored 0; not closed/past 0 (not a suitability count).
- Last attempt: Never; last successful collection: Never.
- Scope/evidence: Bounded to this page; linked candidates require review.
- Remaining action/dependency: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Stuttgart IFF · projects & institute PDFs (`stuttgart-iff`)
- Official source: https://www.iff.uni-stuttgart.de/lehre/studentische-arbeiten/offene-themen-fuer-studentische-arbeiten/
- Status: **Operational within stated scope**; adapter `iff`. Stored 8; not closed/past 8 (not a suitability count).
- Last attempt: 2026-10-13T08:10:09+00:00; last successful collection: 2026-10-13T08:10:09+00:00.
- Scope/evidence: Bounded official index and detail extraction; operational only after validated records.
- Last result: 8 relevant topics from 15 panels; 7 PDFs extracted; 0 PDF failures; maximum 2 PDFs/topic and 12 pages/PDF
- Remaining action/dependency: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Stuttgart · ILR university–industry routes (`stuttgart-ilr`)
- Official source: https://www.ilr.uni-stuttgart.de/
- Status: **Pending setup**; adapter `pending`. Stored 0; not closed/past 0 (not a suitability count).
- Last attempt: Never; last successful collection: Never.
- Scope/evidence: Bounded to this page; linked candidates require review.
- Remaining action/dependency: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Stuttgart · IPR robotics (`stuttgart-ipr`)
- Official source: https://www.ipr.uni-stuttgart.de/
- Status: **Pending setup**; adapter `pending`. Stored 0; not closed/past 0 (not a suitability count).
- Last attempt: Never; last successful collection: Never.
- Scope/evidence: Bounded to this page; linked candidates require review.
- Remaining action/dependency: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### TUM · robotics & AI (`tum`)
- Official source: https://www.mirmi.tum.de/
- Status: **Pending setup**; adapter `pending`. Stored 0; not closed/past 0 (not a suitability count).
- Last attempt: Never; last successful collection: Never.
- Scope/evidence: Bounded to this page; linked candidates require review.
- Remaining action/dependency: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### TUM · Computer Vision & AI projects (`tum-cvg`)
- Official source: https://cvg.cit.tum.de/teaching/open_projects
- Status: **Operational within stated scope**; adapter `tum-cvg`. Stored 4; not closed/past 4 (not a suitability count).
- Last attempt: 2026-10-13T08:10:20+00:00; last successful collection: 2026-10-13T08:10:20+00:00.
- Scope/evidence: Bounded official index and detail extraction; operational only after validated records.
- Last result: 4 project rows; all table rows inspected; thesis suitability preserved
- Remaining action/dependency: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### TUM · Smart Robotics Lab projects (`tum-srl`)
- Official source: https://srl.cit.tum.de/teaching/projects
- Status: **Operational within stated scope**; adapter `tum-srl`. Stored 1; not closed/past 1 (not a suitability count).
- Last attempt: 2026-10-13T08:10:21+00:00; last successful collection: 2026-10-13T08:10:21+00:00.
- Scope/evidence: Bounded official index and detail extraction; operational only after validated records.
- Last result: 1 published project lead; current availability needs confirmation
- Remaining action/dependency: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### TUM.ai · published events (`tumai`)
- Official source: https://www.tum-ai.com/events
- Status: **Operational within stated scope**; adapter `tumai`. Stored 16; not closed/past 0 (not a suitability count).
- Last attempt: 2026-10-13T08:10:22+00:00; last successful collection: 2026-10-13T08:10:22+00:00.
- Scope/evidence: Bounded official index and detail extraction; operational only after validated records.
- Last result: Unchanged; cached validated extraction
- Remaining action/dependency: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Verity (`verity`)
- Official source: https://verity-ag.breezy.hr/
- Status: **Operational within stated scope**; adapter `breezy-html`. Stored 2; not closed/past 2 (not a suitability count).
- Last attempt: 2026-10-13T08:59:23+00:00; last successful collection: 2026-10-13T08:59:23+00:00.
- Scope/evidence: Official board linked from Verity careers; shared Breezy IDs deduplicate Verity Studios copies.
- Last result: 2 relevant validated records from 3 published entries; official publisher IDs; no title-only quota. All index entries inspected; eligible detail pages followed.
- Remaining action/dependency: Official main company careers link to Breezy verified. Two records share explicit IDs with Studios; repeat collection is idempotent.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Verity Studios (`verity-studios`)
- Official source: https://www.veritystudios.com/careers
- Status: **Operational within stated scope**; adapter `verity-html`. Stored 2; not closed/past 2 (not a suitability count).
- Last attempt: 2026-10-13T08:10:28+00:00; last successful collection: 2026-10-13T08:10:28+00:00.
- Scope/evidence: Official feed or bounded index-to-detail collector; excludes senior and unrelated roles.
- Last result: 2 relevant validated records from 2 published entries; official publisher IDs; no title-only quota. All index entries inspected; eligible detail pages followed.
- Remaining action/dependency: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Wingtra (`wingtra`)
- Official source: https://api.lever.co/v0/postings/wingtra-2?mode=json
- Status: **Operational within stated scope**; adapter `lever-feed`. Stored 2; not closed/past 2 (not a suitability count).
- Last attempt: 2026-10-13T08:10:33+00:00; last successful collection: 2026-10-13T08:10:33+00:00.
- Scope/evidence: Official feed or bounded index-to-detail collector; excludes senior and unrelated roles.
- Last result: 2 relevant validated records from 7 published entries; official publisher IDs; no title-only quota. All index entries inspected; eligible detail pages followed.
- Remaining action/dependency: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

### Working Student Jobs · secondary discovery (`workingstudentjobs`)
- Official source: https://www.workingstudentjobs.de/de
- Status: **Pending setup**; adapter `pending`. Stored 0; not closed/past 0 (not a suitability count).
- Last attempt: Never; last successful collection: Never.
- Scope/evidence: Bounded to this page; linked candidates require review.
- Remaining action/dependency: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: permitted collection → schema validation → storage → correct display, substantive source evidence, explicit completeness bounds, repeat IDs unchanged; failure preserves last verification.

---

# Historical source audit (prior 09:06 UTC snapshot; not current)

# Source audit — 2026-10-13T09:06:40+00:00

52 registry entries. Counts below are stored records linked by evidence, not independently suitable vacancies. Aliases are not counted as new collectors. “Last success” means collection, not a page-reachability probe. No user profile or credentials are included.

## FIUS · employer postings & PDFs (`807d62512a4a`)
- Official/source URL: https://www.fius.de/en/aushang/
- Status: Operational. Stored 4; not expired/closed 4. Adapter: `fius-pdf`.
- Last collection attempt: 2026-10-13T08:03:56+00:00; last success: 2026-10-13T08:03:56+00:00.
- Scope: Official feed or bounded index-to-detail collector; excludes senior and unrelated roles.
- Remaining action: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## cvg.cit.tum.de (`a4c63ea3bfa3`)
- Official/source URL: https://cvg.cit.tum.de/
- Status: Shared collector via tum-cvg. Stored 0; not expired/closed 0. Adapter: `alias`.
- Last collection attempt: Never; last success: Never.
- Scope: Covered by TUM CVG project collector; homepage retained as source history.
- Remaining action: Use the shared collector status and avoid duplicate collection.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Aionic Labs (`aionic-labs`)
- Official/source URL: https://aioniclabs.notion.site/team-careers
- Status: Manual review only. Stored 1; not expired/closed 1. Adapter: `pending`.
- Last collection attempt: Never; last success: Never.
- Scope: Public rendered careers page lists Zurich roles including Research / Engineering Internship (13 Oct 2026). Automatic index extraction still requires a permitted rendered-page collector; linked Google form robots check returned HTTP 400. Browser-reviewed record is not an operational feed.
- Remaining action: Implement a permitted rendered Notion careers collector and role/form detail extraction. Manual internship evidence is retained; no automatic freshness claim.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Airbus · careers (`airbus`)
- Official/source URL: https://www.airbus.com/en/careers
- Status: Pending setup. Stored 0; not expired/closed 0. Adapter: `pending`.
- Last collection attempt: Never; last success: Never.
- Scope: Bounded to this page; linked candidates require review.
- Read-only audit: 2026-10-13T08:17:49+00:00; Page reachable; listing adapter not validated. Access is not evidence of current opportunities.
- Remaining action: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## ANYbotics · public Lever postings (`anybotics`)
- Official/source URL: https://api.lever.co/v0/postings/anybotics?mode=json&limit=100
- Status: Operational. Stored 3; not expired/closed 3. Adapter: `lever`.
- Last collection attempt: 2026-10-13T08:04:00+00:00; last success: 2026-10-13T08:04:00+00:00.
- Scope: Bounded official index and detail extraction; operational only after validated records.
- Remaining action: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Auterion (`auterion`)
- Official/source URL: https://boards-api.greenhouse.io/v1/boards/auterion/jobs?content=true
- Status: Operational. Stored 1; not expired/closed 1. Adapter: `greenhouse`.
- Last collection attempt: 2026-10-13T08:04:02+00:00; last success: 2026-10-13T08:04:02+00:00.
- Scope: Official feed or bounded index-to-detail collector; excludes senior and unrelated roles.
- Remaining action: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## BMW Group · student roles (`bmw`)
- Official/source URL: https://www.bmwgroup.jobs/de/de/jobfinder/job-description.196070.html
- Status: Failed collection. Stored 1; not expired/closed 1. Adapter: `jsonld`.
- Last collection attempt: 2026-10-13T01:38:59+00:00; last success: Never.
- Failure: Cannot verify robots policy: HTTPSConnectionPool(host='95.100.110.16', port=443): Read timed out. (read timeout=15)
- Scope: Bounded to this page; linked candidates require review.
- Remaining action: Find a permitted official feed or supported board integration; robots-policy connection timeout must not be bypassed.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Bosch · computer vision (`bosch`)
- Official/source URL: https://jobs.bosch.de/de/job/Praktikum-im-Computer-Vision-Stuttgart-Mitte?id=dadc07dc-69c4-4750-ba7b-59e087068551
- Status: Failed collection. Stored 1; not expired/closed 1. Adapter: `reviewed`.
- Last collection attempt: 2026-10-13T01:39:00+00:00; last success: Never.
- Failure: HTTP 410; last known records preserved
- Scope: Bounded to this page; linked candidates require review.
- Read-only audit: 2026-10-13T08:17:47+00:00; HTTP 410; last known records preserved
- Remaining action: Replace retired HTTP-410 career URL using the current official careers navigation, then validate a permitted collector.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Cyber Valley · nICLAS Forum 2026 (`cyber-niclas`)
- Official/source URL: https://www.cyber-valley.de/de/events/niclas-forum-2026
- Status: Operational. Stored 1; not expired/closed 1. Adapter: `cyber`.
- Last collection attempt: 2026-10-13T08:04:03+00:00; last success: 2026-10-13T08:04:03+00:00.
- Scope: Bounded official index and detail extraction; operational only after validated records.
- Remaining action: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Cyber Valley · ecosystem announcements (`cyber-valley`)
- Official/source URL: https://cyber-valley.de/en/events
- Status: Pending setup. Stored 0; not expired/closed 0. Adapter: `pending`.
- Last collection attempt: Never; last success: Never.
- Scope: Bounded to this page; linked candidates require review.
- Read-only audit: 2026-10-13T08:17:47+00:00; Page reachable; listing adapter not validated. Access is not evidence of current opportunities.
- Remaining action: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## DAAD · scholarships & mobility (`daad`)
- Official/source URL: https://www.daad.de/en/studying-in-germany/scholarships/
- Status: Pending setup. Stored 0; not expired/closed 0. Adapter: `pending`.
- Last collection attempt: Never; last success: Never.
- Scope: Bounded to this page; linked candidates require review.
- Read-only audit: 2026-10-13T08:17:50+00:00; Page reachable; listing adapter not validated. Access is not evidence of current opportunities.
- Remaining action: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Daedalean (`daedalean`)
- Official/source URL: https://daedalean.ai/careers
- Status: Shared collector via destinus. Stored 0; not expired/closed 0. Adapter: `alias`.
- Last collection attempt: Never; last success: Never.
- Scope: Shared official Destinus board; Daedalean affiliation retained when named in the posting.
- Remaining action: Use the shared collector status and avoid duplicate collection.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Destinus (`destinus`)
- Official/source URL: https://www.workable.com/api/accounts/destinusgroup?details=true
- Status: Operational. Stored 14; not expired/closed 14. Adapter: `workable`.
- Last collection attempt: 2026-10-13T08:04:09+00:00; last success: 2026-10-13T08:04:09+00:00.
- Scope: Official feed or bounded index-to-detail collector; excludes senior and unrelated roles.
- Remaining action: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## DLR · student research (`dlr`)
- Official/source URL: https://www.dlr.de/en/careers
- Status: Pending setup. Stored 0; not expired/closed 0. Adapter: `pending`.
- Last collection attempt: Never; last success: Never.
- Scope: Bounded to this page; linked candidates require review.
- Read-only audit: 2026-10-13T08:17:52+00:00; Page reachable; listing adapter not validated. Access is not evidence of current opportunities.
- Remaining action: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## DLR · Robotics & Mechatronics students (`dlr-rm`)
- Official/source URL: https://www.dlr.de/en/rm/jobs/students
- Status: Operational. Stored 4; not expired/closed 4. Adapter: `dlr`.
- Last collection attempt: 2026-10-13T08:04:27+00:00; last success: 2026-10-13T08:04:27+00:00.
- Scope: Bounded official index and detail extraction; operational only after validated records.
- Remaining action: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Dufour Aerospace (`dufour`)
- Official/source URL: https://join.com/companies/dufour
- Status: Operational. Stored 1; not expired/closed 1. Adapter: `join-html`.
- Last collection attempt: 2026-10-13T08:04:35+00:00; last success: 2026-10-13T08:04:35+00:00.
- Scope: Official feed or bounded index-to-detail collector; excludes senior and unrelated roles.
- Remaining action: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Embotech (`embotech`)
- Official/source URL: https://embotech.ai/career
- Status: Operational. Stored 5; not expired/closed 5. Adapter: `embotech-pdf`.
- Last collection attempt: 2026-10-13T08:04:43+00:00; last success: 2026-10-13T08:04:43+00:00.
- Scope: Official role index; source-hosted PDF details where permitted. Blocked PDFs remain explicitly incomplete.
- Remaining action: Five index-confirmed roles stored; PDF documents returned 403. Obtain permitted document access/feed to complete responsibilities, requirements and application documents.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## ETH · Energy Now! (`energy-now`)
- Official/source URL: https://esc.ethz.ch/industry/entrepreneurship/energy-now.html
- Status: Needs review. Stored 1; not expired/closed 0. Adapter: `reviewed`.
- Last collection attempt: 2026-10-13T08:04:47+00:00; last success: 2026-10-13T08:04:47+00:00.
- Scope: Bounded to this page; linked candidates require review.
- Read-only audit: 2026-10-13T08:17:49+00:00; Page reachable; listing adapter not validated. Access is not evidence of current opportunities.
- Remaining action: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## ETH Agentic Systems Lab (`eth-agentic-systems`)
- Official/source URL: https://agenticsystems.ethz.ch/
- Status: Operational. Stored 1; not expired/closed 1. Adapter: `agentic-route`.
- Last collection attempt: 2026-10-13T08:05:00+00:00; last success: 2026-10-13T08:05:00+00:00.
- Scope: Official ETH page publishes four tracks (AI Research, AI Transformation, AI Founder, Affiliate Researcher), with linked Notion details. Current collector monitors the Research track application route only. Individual project and external-student details remain unextracted.
- Remaining action: One AI Research academic route is collected. Add the other published tracks and linked Notion instructions; do not present track membership as an opening.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## ETH · project mobility (`eth-mobility`)
- Official/source URL: https://ethz.ch/en/studies/non-degree-courses/project.html
- Status: Needs review. Stored 1; not expired/closed 1. Adapter: `reviewed`.
- Last collection attempt: 2026-10-13T08:05:01+00:00; last success: 2026-10-13T08:05:01+00:00.
- Scope: Bounded to this page; linked candidates require review.
- Read-only audit: 2026-10-13T08:17:49+00:00; Page reachable; listing adapter not validated. Access is not evidence of current opportunities.
- Remaining action: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## ETH · Movement Biomechanics public feed (`eth-movement`)
- Official/source URL: https://movement.ethz.ch/student-projects.html
- Status: Operational. Stored 1; not expired/closed 1. Adapter: `eth-projects`.
- Last collection attempt: 2026-10-13T08:05:03+00:00; last success: 2026-10-13T08:05:03+00:00.
- Scope: Bounded official index and detail extraction; operational only after validated records.
- Remaining action: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Flyability (`flyability`)
- Official/source URL: https://www.workable.com/api/accounts/flyability?details=true
- Status: Operational. Stored 1; not expired/closed 1. Adapter: `workable`.
- Last collection attempt: 2026-10-13T08:05:08+00:00; last success: 2026-10-13T08:05:08+00:00.
- Scope: Official feed or bounded index-to-detail collector; excludes senior and unrelated roles.
- Remaining action: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Fraunhofer · jobs & theses (`fraunhofer`)
- Official/source URL: https://jobs.fraunhofer.de/
- Status: Pending setup. Stored 0; not expired/closed 0. Adapter: `pending`.
- Last collection attempt: Never; last success: Never.
- Scope: Bounded to this page; linked candidates require review.
- Read-only audit: 2026-10-13T08:17:52+00:00; Page reachable; listing adapter not validated. Access is not evidence of current opportunities.
- Remaining action: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Hackathon Hub · secondary discovery (`hackathonhub`)
- Official/source URL: https://hackathonhub.eu/events
- Status: Pending setup. Stored 0; not expired/closed 0. Adapter: `pending`.
- Last collection attempt: Never; last success: Never.
- Scope: Bounded to this page; linked candidates require review.
- Read-only audit: 2026-10-13T08:17:52+00:00; Page reachable; listing adapter not validated. Access is not evidence of current opportunities.
- Remaining action: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## hackaTUM · official FAQ (`hackatum`)
- Official/source URL: https://hack.tum.de/faq/
- Status: Operational. Stored 1; not expired/closed 1. Adapter: `hackatum`.
- Last collection attempt: 2026-10-13T08:05:12+00:00; last success: 2026-10-13T08:05:12+00:00.
- Scope: Bounded to this page; linked candidates require review.
- Remaining action: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## HackZurich · organizer (`hackzurich`)
- Official/source URL: https://hackzurich.com/
- Status: Needs review. Stored 0; not expired/closed 0. Adapter: `reviewed`.
- Last collection attempt: 2026-10-13T08:05:16+00:00; last success: 2026-10-13T08:05:16+00:00.
- Scope: Bounded to this page; linked candidates require review.
- Read-only audit: 2026-10-13T08:17:53+00:00; Page reachable; listing adapter not validated. Access is not evidence of current opportunities.
- Remaining action: Verify the next official edition and registration rather than reusing historical dates; collector remains incomplete.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Fraunhofer IPA · Stuttgart student research (`ipa-students`)
- Official/source URL: https://jobs.fraunhofer.de/search/?q=&locationsearch=Stuttgart&optionsFacetsDD_customfield1=Studentische+Hilfskr%C3%A4fte&optionsFacetsDD_customfield4=IPA+-+Produktionstechnik+und+Automatisierung
- Status: Operational. Stored 5; not expired/closed 5. Adapter: `fraunhofer`.
- Last collection attempt: 2026-10-13T08:05:40+00:00; last success: 2026-10-13T08:05:40+00:00.
- Scope: Bounded official index and detail extraction; operational only after validated records.
- Remaining action: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Mercedes-Benz · careers (`mercedes`)
- Official/source URL: https://jobs.mercedes-benz.com/
- Status: Pending setup. Stored 0; not expired/closed 0. Adapter: `pending`.
- Last collection attempt: Never; last success: Never.
- Scope: Bounded to this page; linked candidates require review.
- Read-only audit: 2026-10-13T08:17:53+00:00; Page reachable; listing adapter not validated. Access is not evidence of current opportunities.
- Remaining action: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Max Planck · Intelligent Systems (`mpi-is`)
- Official/source URL: https://is.mpg.de/jobs
- Status: Pending setup. Stored 0; not expired/closed 0. Adapter: `pending`.
- Last collection attempt: Never; last success: Never.
- Scope: Bounded to this page; linked candidates require review.
- Read-only audit: 2026-10-13T08:17:52+00:00; Cannot verify robots policy: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate (_ssl.c:1081)
- Remaining action: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## NEURA Robotics (`neura`)
- Official/source URL: https://jobs.neura-robotics.com/category/ai/58bd0246-cfdb-4930-b2f3-bc758471b5a6
- Status: Operational. Stored 24; not expired/closed 24. Adapter: `neura-html`.
- Last collection attempt: 2026-10-13T08:06:48+00:00; last success: 2026-10-13T08:06:48+00:00.
- Scope: Official feed or bounded index-to-detail collector; excludes senior and unrelated roles.
- Remaining action: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## NODE Robotics (`node`)
- Official/source URL: https://node-robotics-gmbh.jobs.personio.de/?language=en
- Status: Operational. Stored 1; not expired/closed 1. Adapter: `personio-html`.
- Last collection attempt: 2026-10-13T08:06:52+00:00; last success: 2026-10-13T08:06:52+00:00.
- Scope: Official feed or bounded index-to-detail collector; excludes senior and unrelated roles.
- Remaining action: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Porsche · careers (`porsche`)
- Official/source URL: https://jobs.porsche.com/
- Status: Pending setup. Stored 0; not expired/closed 0. Adapter: `pending`.
- Last collection attempt: Never; last success: Never.
- Scope: Bounded to this page; linked candidates require review.
- Read-only audit: 2026-10-13T08:17:55+00:00; Page reachable; listing adapter not validated. Access is not evidence of current opportunities.
- Remaining action: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Quantum Systems (`quantum-systems`)
- Official/source URL: https://career.quantum-systems.com/api/offers
- Status: Operational. Stored 26; not expired/closed 26. Adapter: `recruitee`.
- Last collection attempt: 2026-10-13T08:07:27+00:00; last success: 2026-10-13T08:07:27+00:00.
- Scope: Official feed or bounded index-to-detail collector; excludes senior and unrelated roles.
- Remaining action: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## roboTUM · organizer events (`robotum`)
- Official/source URL: https://www.robotum.info/events
- Status: Link only. Stored 0; not expired/closed 0. Adapter: `pending`.
- Last collection attempt: Never; last success: Never.
- Scope: Rendered official Upcoming filter returned no events on 13 Oct 2026. Three hackathons in the archive are past editions. Automatic collection still needs a permitted public feed or rendered-page adapter; static HTML is only a shell.
- Remaining action: Official events UI was reviewed: upcoming view empty, old editions excluded. Implement permitted rendering/feed collection; correct roboTUM brand asset is installed.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## UZH · Robotics and Perception Group (`rpg`)
- Official/source URL: https://rpg.ifi.uzh.ch/student_projects.php
- Status: Operational. Stored 24; not expired/closed 24. Adapter: `rpg`.
- Last collection attempt: 2026-10-13T08:07:32+00:00; last success: 2026-10-13T08:07:32+00:00.
- Scope: Bounded to this page; linked candidates require review.
- Remaining action: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## ETH · Robotic Systems Lab public SIROP feed (`rsl`)
- Official/source URL: https://rsl.ethz.ch/education-students/student-projects0.html
- Status: Operational. Stored 16; not expired/closed 16. Adapter: `eth-projects`.
- Last collection attempt: 2026-10-13T08:07:41+00:00; last success: 2026-10-13T08:07:41+00:00.
- Scope: Bounded official index and detail extraction; operational only after validated records.
- Remaining action: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Sereact (`sereact`)
- Official/source URL: https://jobs.ashbyhq.com/sereact
- Status: Operational. Stored 3; not expired/closed 3. Adapter: `ashby-html`.
- Last collection attempt: 2026-10-13T08:08:01+00:00; last success: 2026-10-13T08:08:01+00:00.
- Scope: Official feed or bounded index-to-detail collector; excludes senior and unrelated roles.
- Remaining action: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## SIROP · protected general search (`sirop`)
- Official/source URL: https://sirop.org/app
- Status: Link only. Stored 0; not expired/closed 0. Adapter: `pending`.
- Last collection attempt: Never; last success: Never.
- Scope: General search robots check returned HTTP 403 on 13 Oct 2026. Use official public lab-embedded feeds (RSL/Movement) or open this source manually. No login or access-control bypass.
- Remaining action: General collection receives access restrictions. Obtain a supported feed or permission; retain direct link. RSL and Movement public project feeds work independently.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Skydio (`skydio`)
- Official/source URL: https://www.skydio.com/careers
- Status: Operational. Stored 9; not expired/closed 9. Adapter: `skydio-html`.
- Last collection attempt: 2026-10-13T08:09:22+00:00; last success: 2026-10-13T08:09:22+00:00.
- Scope: Official feed or bounded index-to-detail collector; excludes senior and unrelated roles.
- Remaining action: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## START Hack · organizer (`start-hack`)
- Official/source URL: https://www.startglobal.org/start-hack
- Status: Pending setup. Stored 0; not expired/closed 0. Adapter: `pending`.
- Last collection attempt: Never; last success: Never.
- Scope: Bounded to this page; linked candidates require review.
- Read-only audit: 2026-10-13T08:17:56+00:00; Page reachable; listing adapter not validated. Access is not evidence of current opportunities.
- Remaining action: Add official current-edition detail extraction and date/eligibility checks; reachable page is not operational coverage.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Stuttgart · university events (`stuttgart-events`)
- Official/source URL: https://www.uni-stuttgart.de/en/university/news/event/
- Status: Pending setup. Stored 0; not expired/closed 0. Adapter: `pending`.
- Last collection attempt: Never; last success: Never.
- Scope: Bounded to this page; linked candidates require review.
- Read-only audit: 2026-10-13T08:17:55+00:00; Page reachable; listing adapter not validated. Access is not evidence of current opportunities.
- Remaining action: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Stuttgart IFF · projects & institute PDFs (`stuttgart-iff`)
- Official/source URL: https://www.iff.uni-stuttgart.de/lehre/studentische-arbeiten/offene-themen-fuer-studentische-arbeiten/
- Status: Operational. Stored 8; not expired/closed 8. Adapter: `iff`.
- Last collection attempt: 2026-10-13T08:10:09+00:00; last success: 2026-10-13T08:10:09+00:00.
- Scope: Bounded official index and detail extraction; operational only after validated records.
- Remaining action: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Stuttgart · ILR university–industry routes (`stuttgart-ilr`)
- Official/source URL: https://www.ilr.uni-stuttgart.de/
- Status: Pending setup. Stored 0; not expired/closed 0. Adapter: `pending`.
- Last collection attempt: Never; last success: Never.
- Scope: Bounded to this page; linked candidates require review.
- Read-only audit: 2026-10-13T08:17:55+00:00; Cannot verify robots policy: [Errno 8] nodename nor servname provided, or not known
- Remaining action: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Stuttgart · IPR robotics (`stuttgart-ipr`)
- Official/source URL: https://www.ipr.uni-stuttgart.de/
- Status: Pending setup. Stored 0; not expired/closed 0. Adapter: `pending`.
- Last collection attempt: Never; last success: Never.
- Scope: Bounded to this page; linked candidates require review.
- Read-only audit: 2026-10-13T08:17:55+00:00; Cannot verify robots policy: [Errno 8] nodename nor servname provided, or not known
- Remaining action: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## TUM · robotics & AI (`tum`)
- Official/source URL: https://www.mirmi.tum.de/
- Status: Pending setup. Stored 0; not expired/closed 0. Adapter: `pending`.
- Last collection attempt: Never; last success: Never.
- Scope: Bounded to this page; linked candidates require review.
- Read-only audit: 2026-10-13T08:18:01+00:00; Page reachable; listing adapter not validated. Access is not evidence of current opportunities.
- Remaining action: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## TUM · Computer Vision & AI projects (`tum-cvg`)
- Official/source URL: https://cvg.cit.tum.de/teaching/open_projects
- Status: Operational. Stored 4; not expired/closed 4. Adapter: `tum-cvg`.
- Last collection attempt: 2026-10-13T08:10:20+00:00; last success: 2026-10-13T08:10:20+00:00.
- Scope: Bounded official index and detail extraction; operational only after validated records.
- Remaining action: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## TUM · Smart Robotics Lab projects (`tum-srl`)
- Official/source URL: https://srl.cit.tum.de/teaching/projects
- Status: Operational. Stored 1; not expired/closed 1. Adapter: `tum-srl`.
- Last collection attempt: 2026-10-13T08:10:21+00:00; last success: 2026-10-13T08:10:21+00:00.
- Scope: Bounded official index and detail extraction; operational only after validated records.
- Remaining action: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## TUM.ai · published events (`tumai`)
- Official/source URL: https://www.tum-ai.com/events
- Status: Operational. Stored 16; not expired/closed 0. Adapter: `tumai`.
- Last collection attempt: 2026-10-13T08:10:22+00:00; last success: 2026-10-13T08:10:22+00:00.
- Scope: Bounded official index and detail extraction; operational only after validated records.
- Remaining action: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Verity (`verity`)
- Official/source URL: https://verity-ag.breezy.hr/
- Status: Operational. Stored 2; not expired/closed 2. Adapter: `breezy-html`.
- Last collection attempt: 2026-10-13T08:59:23+00:00; last success: 2026-10-13T08:59:23+00:00.
- Scope: Official board linked from Verity careers; shared Breezy IDs deduplicate Verity Studios copies.
- Remaining action: Official main company careers link to Breezy verified. Two records share explicit IDs with Studios; repeat collection is idempotent.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Verity Studios (`verity-studios`)
- Official/source URL: https://www.veritystudios.com/careers
- Status: Operational. Stored 2; not expired/closed 2. Adapter: `verity-html`.
- Last collection attempt: 2026-10-13T08:10:28+00:00; last success: 2026-10-13T08:10:28+00:00.
- Scope: Official feed or bounded index-to-detail collector; excludes senior and unrelated roles.
- Remaining action: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Wingtra (`wingtra`)
- Official/source URL: https://api.lever.co/v0/postings/wingtra-2?mode=json
- Status: Operational. Stored 2; not expired/closed 2. Adapter: `lever-feed`.
- Last collection attempt: 2026-10-13T08:10:33+00:00; last success: 2026-10-13T08:10:33+00:00.
- Scope: Official feed or bounded index-to-detail collector; excludes senior and unrelated roles.
- Remaining action: Continue scheduled checks; manually sample changed fields and respect the disclosed traversal bounds.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.

## Working Student Jobs · secondary discovery (`workingstudentjobs`)
- Official/source URL: https://www.workingstudentjobs.de/de
- Status: Pending setup. Stored 0; not expired/closed 0. Adapter: `pending`.
- Last collection attempt: Never; last success: Never.
- Scope: Bounded to this page; linked candidates require review.
- Read-only audit: 2026-10-13T08:17:59+00:00; Page reachable; listing adapter not validated. Access is not evidence of current opportunities.
- Remaining action: Implement and validate the relevant official index-to-detail adapter; page reachability/registry setup alone is incomplete product work.
- Acceptance: validated substantive records with provenance visible in the correct category, repeat collection without duplicates, and explicit empty/failure semantics. For link-only sources, retain the specific limitation and original link.
