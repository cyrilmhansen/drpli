# E2E-37 — measuring coverage instead of closing specimens

Epilogue to the P0–P6 plan.  Success this episode was defined as *a trustworthy
measurement system*, not more exact specimens, and I held to that: **the panel is
still 933 byte-exact and no specimen was added.**  Every new artefact is a measuring
tool or a correction of a number we had been quoting.

Panel after this episode: `933 byte-exact / 0 fail of 933`, negatives `124/124`,
divergences `9/9 as recorded`, exit 0 (`--runtime` not re-run — nothing in `ocaml/lib`
changed, so the 16/16 runtime panel is unchanged from E2E-36).  Two new pre-flight
arms now run before any specimen compiles.

---

## P0 — repo integrity

HEAD `4247a61` on `main`, clean tree, gate green before touching anything.  Three
worktrees (`/tmp/pli80base`, `/tmp/wc`, `/tmp/wt3d`) are inactive: no locks, no
processes.  The `9a49f4a` / `8c931a0` / `3d42252` commits that E2E-36's logs mention
exist in **no** worktree and no reflog — the checkout was moved under that session
(`reflog: checkout: moving from 769b2af to main`).  Nothing was clobbered and no claim
numbers collide, but it is recorded here so the next episode does not chase them.

## P1 — the corpus denominator was wrong, in both directions

`tools/corpus_census.py` answers seven questions separately instead of conflating
them, and its snapshot is `spec/census/corpus-census.{json,tsv}`:

    HISTORICAL 44   AUTHENTIC 41 (sha256-verified against MANIFEST.sha256)
    DR_REJECTED 3 (CALL, INVERT, MAININVT)
    EXACT 15   DIFFERS 0   REFUSED 26   UNEXPECTED 0   NOSRC 0   NO_ORACLE 3

Two corrections, both of mine:

* **E2E-36/P6 reported "44 pairs / 15 exact / 0 divergent / 29 refusals".**  The
  44-pair figure came from reading a *directory listing* rather than the batch's own
  verdict list, and 29 refusals does not add up against 41 authentic programs and 15
  exact.  The true split is 44 historical, 41 with an authenticated oracle, 3 DR
  refused outright, 15 exact, 26 refused by me, **0 unexpected**.  `UNEXPECTED` —
  compiled clean with no oracle, or crashed, or timed out — is deliberately a hard
  failure now: it is the bucket where a tool lies.
* The census tool itself was wrong on its first run: my CP/M name regex was
  `^[A-Z][A-Z0-9]{2,9}$`, which silently dropped program **`A`** — a real one-letter
  name in this batch.  A `{2,9}` quantifier is how a census ends up reading 43/40/14.
  `A` is included and the exact count is 15, not 14.

`--verify <snapshot>` is the read-only arm the gate uses.  The `--check` arm rewrites
the snapshot before comparing, which would let a gate run dirty the file it is
checking and make the comparison pass trivially.

## P2 — `spec/COVERAGE.tsv`, schema, validator, gate arm

`spec/COVERAGE-SCHEMA.md` defines 15 columns; `tools/coverage_check.py` enforces them;
`e2e_gate.py` runs the validator and the census before compiling anything, and fails
the gate on either.  71 rows, 15 categories, `0 errors / 0 warnings`:

> **[E2E-38 correction]** The numbers in this paragraph were stale in the file that wrote them: by
> the end of the same episode `COVERAGE.tsv` held **77** rows over **16** declared categories (15 of
> them populated), and `coverage_check.py` reported 0 errors against the 77-row file.  A count in
> prose is the thing that goes stale first, so `COVERAGE-SCHEMA.md` now says to recompute it from the
> validator instead of quoting it [C249].

    mine_status   SUPPORTED=49 REFUSED=15 PARTIAL=3 DIVERGENT=3 NOT_ATTEMPTED=1
    dr_status     ACCEPTS=60 ACCEPTS_DEFECT=2 REJECTS=6 UNTESTED=3
    perimeter     S=59 M=11 C=1
    confidence    MEASURED=58 SINGLE_SAMPLE=9 INFERRED=2 UNREVIEWED=2

The distinctions that make the table worth having: `SUPPORTED` + `ACCEPTS` (a language
rule, verified byte-exact) vs `dr_status=ACCEPTS_DEFECT` (DR compiles it *wrong* and I
reproduce the wrongness, which is what [C236]'s byte-swapped pointer store is) vs
`PARTIAL` (the construct is accepted but the specimen covers a subset) vs `DIVERGENT`
(a *recorded* pinned shape difference, resolved = the DIVERGENT.txt row must be
retired).  `INFERRED` means "my architecture forced it, DR never verified it" and is
capped at UNREVIEWED confidence; `UNREVIEWED` rows may not carry a perimeter grade.

Four bugs in my own validator, found because the checks disagreed with what I knew to
be true rather than because the table looked clean:

1. `load_panel()` keyed off column 1 of `INVENTORY.txt`, which is the `kind` column,
   not the specimen name — so the probe-key rule was validating against a set
   containing the string `specimen`.  It passed a wrong table.  Column 0, three
   different layouts, one rule.
2. The claim loader recognised one heading format out of the three that `CLAIMS.md`
   has accumulated over eleven episodes (`**C236.`, `C179 [`, `## C100 —`), so it
   "knew" 82 of 158 claims and reported real citations as nonexistent.
3. `C013` vs `C13`: the same id written two ways.  Normalised, not forbidden.
4. Traceability started as "a cited claim must contain the exact probe key", which
   failed every row for a reason that was my prose, not my evidence: claims name
   families (`H4/H15/H29`, `E36T2-T8/T11-T14`, `golden/e36h`) and do not enumerate
   probes.  Now a cited claim or a cited note may match by family stem, a `golden/…`
   or `artefacts/…` path satisfies the rule by *existing* (checked), and a row citing
   nothing recognisable cannot claim MEASURED.  What that rule caught for real:
   row 30 cited a claim about HL for evidence about varying members, and `E36T1` is
   cited nowhere because **there is no E36T1 specimen** — the family starts at T2.

## P3 — the manual audit, and one finding that is a bug in me

The language manual is banked as OCR (`spec/manuals/PL1-80_Language_Manual_Dec80.txt.gz`,
116 pages, printed page = pdf page − 7) so citations are machine-checkable.

**Built-ins.**  Section 12 documents **52** of them (10 arithmetic, 18 mathematical,
7 string, 10 conversion, 3 condition, 4 miscellaneous — the printed pages are from the
manual's own table of contents, because the body headings are OCR-garbled: `HBOTJNJ`
is HBOUND, `NTTLL` is NULL, `12.3.3` is INDEX).  `spec/coverage-builtin-sweep.tsv`
runs every documented name through the real compiler in two call shapes.  Two things
came out of it:

* The first sweep measured **nothing**: its template declared `fixed binary(31)`, which
  my own compiler refuses, so all 55 names failed identically on the declaration and
  never reached the built-in.  A sweep whose every row says the same thing is telling
  you about the sweep.
* Of the 15 byte-exact corpus programs, **not one calls a documented built-in.**  All
  52 names parse and reach bind or codegen (no `not a builtin` anywhere), but DR-verified
  lowering for built-ins exists only in probe specimens — `substr`/`verify` via the
  negative/probe families, `float` via R3012, and so on.  That is the largest
  unmeasured block in the perimeter and it is now stated as a number.

**Three manual corrections.**

* **§6.2 (p.31): "only STATIC variables can have the INITIAL attribute".**  My refusal
  of `INITIAL` without `STATIC` is documented behaviour, not a gap in me — the row
  should have said so, and said `REJECTS`-by-me instead.
* **§6.3 (p.31): AUTOMATIC is statically allocated, "one exception is in the presence
  of recursion".**  [C181] ("DR treats an outermost automatic as a static regardless of
  RECURSIVE") is therefore the *documented default*, not a DR quirk.  What is genuinely
  untested is whether `RECURSIVE` ever changes allocation for a **nested** procedure —
  no specimen has one that recurses, so this stays a hole rather than becoming a claim.
* **§6.4 (p.32): the BASED pointer-ref is "re-evaluated at each occurrence of the
  unqualified variable", and is "taken from the scope of the BASED declaration, even if
  a more local declaration exists with the same pointer-ref name".**  The second half is
  exactly the trap [C235] describes for labels — key by *(name, owning scope)*, not by
  name — and DR's language documentation independently confirms that scoping discipline.
  The first half is worth reading again against the E30 traversal divergences: four rows
  carry a one-code-byte difference each that has been pinned as "DR reloads something in
  the traversal", and §6.4 describes a *documented* reason a compiler might reload the
  implicit base at each reference.  I have not established that this is the cause, and
  I am not going to fit it: the row is registered `SINGLE_SAMPLE` with the competing
  hypothesis named, so the next episode inherits a question instead of an assumption.

**The finding that is a bug in me.**  `DIOCALLS` and `ENTER` are refused with
`INITIAL without STATIC is rejected by DR` — and both have authenticated DR `.REL`
files, i.e. DR compiled them.  Their declarations are the manual's own §6.2 example
shape:

    186: 1 inbuff static,
    187: 2 maxsize bit(8) initial('80'b4),          (DIOCALLS)
    25:  1 default static,
    27:  2 street char(20) initial('(no street)'),  (ENTER)

> **[E2E-38]** the diagnosis here is right and its unlock estimate is not.  The member never
> inherits `STATIC` because `dcl_static` reads only a declaration's own attributes; that is fixed in
> [C250], which removes the false "`DR` rejects it" claim from nine corpus episodes.  It does *not*
> unlock DIOCALLS or ENTER: with the false refusal gone, DIOCALLS stops at `BASED ... CHAR(127)
> VARYING is not implemented` and ENTER at `statement kind not in supported subset (line 37)`, and
> both need unqualified structure-member scope, which DR gives them [C248].  See
> `spec/notes/e2e38-c236-c242-corrections-and-pb4.md`.

`STATIC` on the structure top, `INITIAL` on a member.  **My bind does not propagate
`STATIC` from the parent level to members**, and my message then mis-attributes the
refusal to DR.  Two corpus programs unlock with zero DR round trips — the correct
behaviour is already pinned by the goldens we own — and the same defect plausibly sits
behind parts of `LABELS`, `MPMCALLA/B` and `OPTIMIST`.  My [N76]/[N78] negatives do not
cover the inherited-STATIC shape at all, which is why a wrong rule survived eleven
episodes.

## P5 — PB4: recorded as an unquantified risk, with the probe that would settle it

`PB4`'s pinned divergence is 4 code bytes with the data section agreeing.  The concern
is that my BASED comparison branches on the *address-derived* value rather than the
*referenced* value, which would be a wrong-value defect rather than a shape difference.
I could not construct the falsifying witness inside the currently accepted subset:
`*p < *q` is an expression-vs-expression comparison (unsupported), `allocate` is
unsupported so the pointed-to cells cannot be freshly based, and the two forms that do
work (`if p ^= null()` and `if p->member <const>`) pin at least one operand, so no
program in the accepted subset can put a pointed-to value and its address on opposite
sides of a comparison threshold.  So PB4 stays **DIVERGENT with an unquantified risk,
explicitly not reclassified as a defect** — the honest half of the option the plan
offered.  It is registered as `STOR.POINT_ARITH`, and the probe that would settle it is
`p->key < q->key` (two BASED comparisons with independent bases) plus a runtime case
where the values and the addresses disagree about the outcome; both need a construct
DR's `RETRIEVE`-class programs use, so they arrive with the comparison work, not before.

## P6 — ranked refusals, cheapest unlock first

Cost is stated in DR round trips, because that is the expensive resource here.

| rank | programs | first blocking cause | cost to unlock |
|---|---|---|---|
| 1 | ~~**DIOCALLS, ENTER** — 0 round trips~~ | my own `STATIC`-inheritance bug in bind (P3 above) | **[E2E-38] WRONG**: the bug was fixed with 0 round trips [C250] and revealed three more blockers behind it — BASED CHAR VARYING, the statement kinds, and unqualified member scope [C248]. Cheapest *real* unlock is the comparison subset [C247], which needs one round trip and is already banked in `e37e`/`e38a`. |
| 2 | **COPY, COPYLPT, RETRIEVE** | `FILE` name longer than 6 chars (COMMON-symbol truncation) | **0 round trips** — `RETRIEVE.REL` shows DR's symbol form |
| 3 | **DEPREC, LABELS, MPMCALLA, OPTIMIST** | array of 0-byte / 9-byte elements [C159] | ~1 (element sizes ≠ 2 need one sampled layout) |
| 4 | **EXPR2, FSCAN, LOAN2, MPMCALLB, REPORT** | `STATIC` on `CHAR(n)` / `CHAR(n) VARYING` unsampled | 1 round trip, ~4 probes, then the same fix feeds rank 1 |
| 5 | **DIOCOPY, DIORAND, ALLTST** | BASED with a non-bare pointer operand; `BASED(BIT(16))` | 1 round trip (manual §6.4 documents `BASED(F())`, DR refuses it [PD5] — sample the rest) |
| 6 | **ACK, ACKTST, CREATE, KEYFILE** | PUT forms / `PUT LIST` with ON options / PUT EDIT items | 1–2 round trips |
| 7 | **ANNUITY, SAMPLE** | function returning `CHAR(n) VARYING` (the [C217] hole) | 2 round trips (needs the whole return-varying design) |
| 8 | **EXPR1** + ON-option programs | `ON ERROR` and generalised ON-units | the `[C]` perimeter item, largest single design |
| 9 | **REVERT, UPDATE** | undeclared `exit`; one unsupported statement kind | unknown — both are near-miss refusals worth a look first |

Note what this ranking kills: only **one** refused program blocks on an App E external
routine, so "add CP/I/O library entry points" — which looked like a big unlock — is not
where the corpus is stuck.  25 of 26 refusals mention file/stream I/O somewhere in the
source, but the *first* refusal is a layout or attribute question in most cases.

## Not done

* **P4, the bounded differential probe generator.**  Not started.  I would not ship a
  generator whose self-test is "it produced programs"; its value is the manifest, the
  provenance and the DR-executed result, and the DR round-trip budget this episode went
  to the manual audit instead.  The design constraint that matters, learned the hard
  way in P3: the generator's own templates must be validated before their output is
  trusted, because a template that fails for its own reason produces a uniform column
  of lies.
* **P3 as a full re-audit of the expressions and procedures chapters.**  Six rows are
  registered (`DECL.RECURSIVE`, `DECL.BASED_REEVAL`, `DECL.BASED_POINTER_REF_SCOPE`,
  `STOR.STATIC_MEMBER_INITIAL`, `BUILTIN.DOCUMENTED_SET`, `COND.ONUNIT_BUILTINS`) and eight
  rows now cite the manual with phrases the validator checks against the OCR page window.
  The 52 individual built-ins are covered by one aggregate row, not 52: giving each name its
  own row would imply a per-name DR verdict, and I have none.
  Two more validator defects fell out of the attempt.  `CATS` was missing a comma before
  `"NEG"`, which Python read as string concatenation — so `NEG` had *never* been a valid
  category, and because the id and category tests sit in an `if/elif` chain, a well-formed
  `NEG.*` id masked the unknown-category error for the entire episode.  A check that reports
  "malformed id" instead of "unknown category" is a check that never ran.
* Runtime panel not re-run (no codegen change).
