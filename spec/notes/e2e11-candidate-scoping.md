# E2E-11 candidate scoping — SUPERSEDED by `e2e11-step0-step1-endfile.md`

> **Read the newer note instead.**  This draft ranked candidates by the FIRST
> refusal my compiler reports, which the user correctly rejected: most remaining
> programs need several kinds at once, so a first-blocker ranking systematically
> over-states the payoff of whatever happens to be checked first.  Two concrete
> errors it made, both corrected by the full dependency audit
> (`ocaml/bin/pli80deps.exe` + `tools/blocker_audit.py`):
>
> * it reported **FILE as gating 14 programs**, which was a first-blocker artefact;
>   the complete sets show FILE travels with `ON ENDFILE` (8/8 in this corpus) and
>   with `open` (10/17), and **no program is closable by FILE alone**;
> * it **missed `CALL` as a statement entirely**, which is the single largest
>   blocker in the corpus (23 programs) and is unimplemented
>   (`codegen.ml: Ast.Sprocedure_stmt -> failwith`).
>
> `FLTPOLY2` survives as the near-term target, now with a *measured* requirement
> set — exactly `{BIT(1) + STATIC INITIAL}` and `{FILE + ON ENDFILE}` — instead of
> a guess, and `REVERT` is confirmed unsuitable (it also needs LABEL-as-data and
> `GOTO`).  Keeping this file for the record rather than deleting it, because the
> mistake it documents is the mistake the audit exists to prevent.

---


Date: 2026-10-20, immediately after E2E-10 closed (FFACT, FLTPOLY, TEST
accepted; corpus 9/41 EXACT, 0 DIFFERS, 32 REFUSED; gate 285 byte-exact /
57 negatives refused).

This is a SCOPING note, not an assessment: it records why the remaining
refusals were re-ranked the way they were, and what the first probe batch of
E2E-11 should be.  No compiler code and no oracle run were produced for it.

## 1. First-blocker census (authoritative, from `tools/sweep_corpus.py`)

| first refusal | programs |
|---|---|
| `declared variable kind ... FILE` | 14 |
| `declared variable kind ... POINTER` | 4 |
| `declared variable kind ... BIT(1...)` | 4 |
| character VARYING return type | 2 |
| ENTRY / unknown external (`fdiv2`, DTEST) | 2 |
| label-as-data (`dcl (x,y,z(3)) label`, LABELS) | 1 |
| `OPTIONS(STACK)` + generated PUT list (ACK, ACKTST) | 2 |
| other single-program blockers (A: float->fixed; FSCAN: no-formal procedure) | 2 |
| remaining VARYING/FILE combinations | ~1 |

Caveat that matters: this is the FIRST blocker only.  A program blocked by BIT
is usually blocked by more than BIT.  Reading the four BIT-blocked programs:

* `FLTPOLY2` — `bit(1) static initial(false)` + `dcl sysin file` + `on
  endfile(sysin)` (and `%replace false/true`, which is already supported).
* `LOAN2` — `bit(1)`, `file`, `open file(...) print pagesize(0)`,
  `put file(output) page/skip/edit`, `on undefinedfile`, character VARYING.
* `UPDATE` — keyed `file`, struct overlays, a dozen VARYING fields.
* `DIORAND` — `bit(1)`, `bit(16)`, `bit(8) based(dbuff())`, VARYING based buffer.

So BIT(1) alone unlocks none of them; each needs FILE too.

## 2. Keyword co-occurrence (crude grep over `artefacts/*.PLI`, for scale only)

`varying` appears in 22 of the not-yet-accepted programs, `open/put/get/close
file(...)` in 11, `based(...)` in 4, `on endfile(sysin)` in 6.  The smallest
true FILE specimens — the ones whose ONLY file verb is an `ON ENDFILE(SYSIN)`
guard — are `FLTPOLY2`, `REVERT`, `EXPR1`, `EXPR2`, `NETWORK`.

## 3. Reading of the census

FILE is the gate on most of what is left, and it arrives bundled: the six
small `ON ENDFILE(SYSIN)` programs want (a) a FILE declaration kind, (b) the
SYSIN device handle, (c) condition-to-file association, and (d) the
`ON`-unit mechanism attached to a file condition.  `FLTPOLY2` additionally
wants BIT(1) + `STATIC INITIAL`, which is exactly the shape the other three
BIT programs need as well — so BIT(1)/STATIC INITIAL is cheap to take in the
same pass rather than separately.

VARYING is the second gate and is independent of FILE for many programs; it is
the direction with the widest single-program payoff (22 programs mention it)
but the value model is non-trivial (length prefix, `^i`-style edit output,
`substr`/`length` runtime surface).

POINTER/BASED (4 programs: ALLTST, DIOCALLS, DIOCOPY, DIORAND) is the third
gate and all four also use FILE or VARYING, so it is strictly a follower.

## 4. Proposed E2E-11 plan (to confirm before any code is written)

Step 0 — per-program BLOCKER SET audit (the missing piece: iterate the
compiler past the first refusal by probing each construct individually, so the
ranking is by *number of distinct kinds*, not by first blocker).  Cheap, no
oracle.
Step 1 — minimal SYSIN `ON ENDFILE` model: pick `REVERT`/`FLTPOLY2` and ask DR
what `on endfile(sysin)` actually compiles to (control-block layout, condition
registration, the terminal-exception interaction already pinned by C102).
Step 2 — BIT(1) storage + `STATIC INITIAL` (independently useful, small, and
FLTPOLY2 needs it before step 3 pays off).
Step 3 — `put file(...)` / `get file(...)` sequential text I/O, then
`open/close` and `pagesize`, if REVERT or FLTPOLY2 is still short.

Deliberately NOT in E2E-11: ENTRY/multi-module (DTEST, FDTEST, ENTER),
label-as-data (LABELS), struct overlays (UPDATE).  Those are separate kinds and
each would dilute a FILE slice the way multi-argument ABI once did.

## 5. Loose ends worth carrying forward

* Float perimeter members still open (all fail-loud, none corpus-blocking):
  whole-literal float arithmetic via DR's DEC runtime [R3044], `<>` (DR rejects
  it [R3075]), non-`=` relations inside conjunctions, float->fixed store (which
  is program `A`'s only blocker, so it is a 1-program payoff if ever wanted).
* `R3094` (first draft) is explained and closed: DR answers `NOT IMP` to every
  `fixed bin(31)` declaration, including procedure locals — five separate lines
  in that one probe — which re-confirms C079 outside the main block.  The probe
  was rebuilt with plain `fixed` and is now byte-exact, and the rebuilt version
  plus R3101/R3102 settled C106: a dedup'd callee's declared formal cell (FIXED
  or FLOAT) occupies nothing; only a written-RECURSIVE callee's does.
* `R3055` (using a variable before its `dcl`) is byte-identical and now a gate
  positive — DR accepts forward references inside a block, which is worth
  remembering when scoping any procedure-related slice.
