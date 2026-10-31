# docs/history — DRPLi durable-document archive

Consolidated-out operational history from the durable files (AGENTS/HANDOFF/PROGRESS/LEARNINGS/
PROTOCOL). Archived 2026-10-31, Mission 1, operator-approved (policy:
`.agents/skills/pi-handoff/references/consolidation.md`, pinned commit `a877f283bdfd74a8ac311875a9a0195e706b057a`).
Baseline extraction commit: `f3a4c608189aabbee018a3b3c025cc0501de0288`.

**These are RECORDS, not current instructions.** Current authority: `HANDOFF.md` (one active
`## Next action`), `PROGRESS.md` (current phase + milestones), `spec/CLAIMS.md` (science),
`spec/lab-evidence/<round>/RESULTS.md` (round evidence), `PROTOCOL.md` Part 2 (handoff procedure).

| File | Source (baseline line ranges) | Content | Closed by / superseded at |
|---|---|---|---|
| `2026-10-29-e2e48-p1-states.md` | HANDOFF 27–66, 105–166 | E2E-48/P1 verification states + open items | P1 closed `992ccad`; science in claims C309–C316, `spec/lab-evidence/e2e48-p1/RESULTS.md` |
| `2026-10-29-handoff-deployment-window.md` | HANDOFF 67–104, 711–725, 736–786 | Infrastructure deployment-window record + retired discoveries | Procedures now in PROTOCOL.md Part 2; README staleness kept in PROGRESS.md Pending |
| `2026-10-30-next-actions.md` | HANDOFF 167–179, 189–206, 257–710, 726–735 | All superseded next-action sections + P2e arms 1–2 specs | Per-section closure commits named inside: run-1 `67bf83c`, wrap `60a2c06`, run-2 `d28ff5e`, arms a-f `6545b5d`/`6491981`/`a72ce43`/`18a06c0`/`1e8acb2`/`e21281a`, registration `adbfa2a`, coverage `218b474`, choice-(D) prereg `421656a`, goldens `e2b77ba`, arms 1–2 `d18c6ab`/`bab0d16` |
| `2026-10-30-progress-status-log.md` | PROGRESS 7–410, 450–452, 463–465, 487–508, 509–521 | Renewal-hop STATUS stack + stale evidence/blockers records | Current facts folded into PROGRESS '## Current phase' / '## Verified milestones' |
| `2026-10-30-learnings-superseded.md` | LEARNINGS 264–269, 283–287, 421–423, 464–467 | Operational LEARNINGS notes superseded by measurement | Pointers with classification kept in place in LEARNINGS.md |
| `2026-10-31-p2e-arm3-closed.md` | HANDOFF live Next-action step 3 (pre-`e49902a`) | E2E-48/P2e arm 3 verbatim spec + measured closure ACTUALS | Arm 3 landed `e49902a`; law = RESULTS §2.3, claim C329 recorded as C329 at `809af8d` |
| `2026-10-31-p2e-closed.md` | HANDOFF 35–94, PROGRESS 6–45, 124–135, 187–188 (at `0749fa6`) | P2e closing-era Last-verified-state, FULL-GATE next action, step-6 record, prior-arms prose, verified-evidence + stale debts bullet | Round CLOSED: FULL GATE rc=0 measured at `0749fa6` — ACTUAL 1127/0, neg 181/181, div 9/9, cov 118/0, census 15/0/26/0, prose clean |

Verification: every excerpt above is byte-identical to its source range at `f3a4c60`
(check: `git show f3a4c608:HANDOFF.md` etc.); no other historical text was altered.
