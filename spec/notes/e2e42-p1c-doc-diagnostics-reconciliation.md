# E2E-42/P1c — reconciling the FILE prose and the FILE diagnostics after P0/P1a/P1b

**Documentation and diagnostic text only.**  No parser, binder, lowering or runtime change is
made in this episode, and that is proved below rather than asserted.

P1a and P1b each moved the compiler forward without moving every sentence that describes it.
Several active documents still said a VARIABLE TITLE refuses, that a long FILE name is a
my-gap, and that there are nine `OUTPUT` rows in the OPEN census.  Two of those statements were
correct when written and are now false; the third was never correct and is the counting error
[C287] records.  This episode repairs the descriptions, and in doing so it found one thing that
was not a description problem at all (§4).

Authority for everything below: [C283]–[C289], especially [C287] (the recount) and [C288] (the
dispatch), and the objects under `golden/e42p1/`, `golden/e42p1b/`, `golden/e42p1c/`.

## 1. WHAT WAS STALE, AND WHERE

| place | said | now says | why the old text was wrong |
|---|---|---|---|
| `codegen.ml`, `prescan_stmt` (~2788) | "Only literal titles are counted: a variable title routes to ?SLVTS and refuses." | only a literal allocates a pool cell, **because a variable operand points at a cell the declaration already made** — measured: E46F1/E46F2 have a 1-byte DATA area (their own PUT literal) where E46D6's literal `'T.DAT'` makes it 5 bytes | the *rule* was right and its *reason* was false; a wrong reason on a pool-order invariant is how the next person "fixes" it by counting variable titles |
| `codegen.ml`, OPEN/CLOSE header | "Everything else -- a VARIABLE title (?SLVTS) ... still refuses below" | P0/P1a/P1b added, and the refusal list is now OPTION WORDS + specific operand shapes | E46F1–F4 are byte-exact since P1b |
| `codegen.ml`, `refuse_file_opt` | "...and a VARIABLE title routes to ?SLVTS -- none of those is lowered byte-exactly by this compiler yet"; "outside the E2E-41/P3 witnessed subset" | the lowered set is enumerated with its claim numbers, and the message names which statement kind it is refusing | a KEYED/RECORD/SEQUENTIAL/UPDATE refusal recited a TITLE gap that has nothing to do with why the program was refused |
| `codegen.ml`, `open_title` operand message | "all five measured variable titles ... and my own E46F1/F2/F3/F5 name a simple CHARACTER variable" | five historical + my four byte-exact probes (E46F1/F3/F4 varying, E46F2 fixed); E46F5 is a DR-side-only witness | E46F5 refuses at its declaration and never reaches this arm, so it measures nothing about a route |
| `codegen.ml`, `lower_open` kind message | "plus my E46F1/F3/F5 (varying) and E46F2 (fixed)" | nine CHARACTER operands, E46F5's status spelled out | same |
| `codegen.ml`, file-PUT SKIP guard | "CREATE ... but its own open carries a VARIABLE title, so no specimen of mine pins the bytes" | CREATE's open IS lowered (E46F1's shape); what is missing is a specimen carrying a file attach **and** a SKIP | the title stopped being the blocker at P1b; CREATE now refuses at its six-item PUT, line 39 |
| `e2e_gate.py`, `NEG_META["E41X6"]` | "CREATE itself is unreachable here anyway: its title is a VARIABLE (?SLVTS), which is not lowered." | the same sentence corrected, plus the console-SKIP witnesses that ARE byte-exact (LOAN1, N302, REVERSE 00FE) | a panel narrative that blames the wrong gap makes a future fix look like something it is not |
| `PERIMETER.md`, FILE cluster row | "Still refusing by name: a VARIABLE title (the ?SLVTS route), ..."; "the long-name refusal here is a my-gap" | the P0/P1a/P1b additions with their claims; the long-name gap marked CLOSED; the refusal list is option words + operand shapes | both were superseded in the preceding two commits |
| `PERIMETER.md`, E2E-11 frontier row | `open file(f) stream title(t)` → "refuses" | annotated as refused-at-E2E-11, literal lowered at E2E-41/P2b, variable at E2E-42/P1b -- and E17A's operand is the **literal** `'$1.$1'`, so that row never measured a variable title at all | the row's evidence does not support reading it as the variable case |
| `COVERAGE.tsv`, `FILE.OPEN_STREAM_OUTPUT` | "of the nine OUTPUT rows in OPEN-MATRIX.tsv the other seven ..." | **seven** spell `output`; three lower here; the refusals are three option words; the titleless case is explained by 0x0650 being an attach word only | the nine is [C287]'s counting error: LOAN2:54/56 say `open file(output)` and `output` there is the file's NAME |
| `COVERAGE.tsv`, `FILE.PUT_LIST` | "...(PRINT, keyed, ENVIRONMENT, LINESIZE, **variable TITLE**: E41X5's family)" | variable TITLE removed from the list; E41X5's blocker is the option word | [C288] |
| `COVERAGE.tsv`, `DECL.FILE_NAME_LEN` | `[C277] [C283] [C284] [C283]` | `[C277] [C283] [C284]` | a citation pasted twice |
| `spec/CLAIMS.md`, [C280] | "Of the nine OUTPUT rows ... All nine carry a TITLE -- seven literal, two variable" | the paragraphs are kept **verbatim** under a [C287] correction banner | [C280] is the record of what E2E-41/P3b measured; only its counts are superseded, and silently editing a claim would destroy the fact that it was once believed |
| `e2e42-p0` note | quotes E46H1's full old message | marked as the P0-era text, with the pinned prefix kept | the note is the P0 record; the panel matches a prefix, not the tail |

Historical evidence files are deliberately NOT rewritten:
`spec/lab-evidence/e2e41-p1/{REFUSALS,CODE-DIFF}.txt`,
`spec/lab-evidence/e2e41-p2/REFUSALS.txt` and `spec/notes/e2e41-*.md` still quote the message
as it read in E2E-41, because they are what was observed at the time.  They cite an episode,
so an obsolete sentence inside them is a correct record rather than an obsolete claim.

## 2. THE DIAGNOSTIC REWRITE AND THE SNAPSHOTS IT MOVED

`refuse_file_opt` is shared by OPEN and CLOSE.  Before this change a CLOSE refusal recited the
whole OPEN history.  The function now picks its narrative by the `what` argument:

```
CLOSE arm: 5 measured sites (E16D, E17D, RETRIEVE, P072H, P081Q), all `close file(<one name>)',
           6 bytes, nothing pushed [C275]; %s is an operand no measured CLOSE carries.
OPEN  arm: the lowered set with claims [C273] [C278] [C280] [C283][C284] [C286] [C288], then
           "nothing in this message is a TITLE gap or a name-length gap: %s refuses as an
           OPTION WORD", then what each refused word would need.
```

`Printf.sprintf` requires a **literal** format, so this is two calls rather than one call with a
selected tail string; that is also what keeps the two narratives from leaking into each other.

The four pinned markers are prefixes (`OPEN option KEYED|RECORD|SEQUENTIAL|UPDATE is outside`),
so the rewrite keeps all four matching — verified by running the negative panel, **149/149**.
Nothing pins a CLOSE marker, and `close file(fa) keyed` was confirmed to reach the new CLOSE arm.

Two snapshots did depend on the wording, and both were regenerated **explicitly**:

* `spec/census/corpus-census.{json,tsv}` — [C265] makes `--verify` compare `msg` byte-for-byte,
  precisely because a snapshot once claimed reason A while the compiler gave reason B.  It
  reported the expected drift on exactly four rows — **COPY, ENTER, RETRIEVE, UPDATE** — and
  only in the `msg` column; every bucket count is unchanged
  (`HISTORICAL 44, AUTHENTIC 41, DR_REJECTED 3, EXACT 15, DIFFERS 0, REFUSED 26, UNEXPECTED 0`).
  Regenerated, and `--verify` then reports "recomputed counts match ... (nothing written)".
* `spec/INVENTORY.txt` — stores each panel row's narrative text, so `E41X6`'s corrected
  `NEG_META` moved exactly one line.  `--update-inventory` rewrote it and the count stayed
  **1004 entries**.  The gate aborted *before* that with "panel and committed inventory
  disagree", which is the check doing its job rather than a failure of the change.

No golden, no `.PRN`, no runtime expectation and no probe source changed.

## 3. PROOF THAT NOTHING EXECUTABLE CHANGED

Comments and string literals were stripped from `HEAD:ocaml/lib/codegen.ml` and from the working
file with `tools/strip_comments.py` (nested-comment and string-literal aware), then
whitespace-normalised and diffed at token level.  The entire residue delta is three fragments, all inside
`refuse_file_opt`:

```
+ if what = "CLOSE" then
  ...s.Ast.spos.Source.line            ->  s.Ast.spos.Source.line o.Ast.io_key
+ else failwith (Printf.sprintf <CLOSE narrative> what o.io_key line o.io_key)
```

No other function's code differs.  `refuse_file_opt` still raises on exactly the inputs it
raised on before — one `failwith` per branch, same guard, same call sites — so the set of
accepted programs and every emitted byte are untouched, which is what the panels confirm:

```
e2e gate: 1004 byte-exact / 0 fail of 1004
e2e gate: negative panel clean (149/149 refused)
e2e gate: divergence panel 9/9 as recorded (compiles, differs, shape pinned)
coverage_check: 92 rows, 0 errors, 0 warnings
corpus census: recomputed counts match spec/census/corpus-census.json (nothing written)
```

## 4. WHAT THE AUDIT FOUND THAT IS NOT A WORDING PROBLEM

Auditing the COPYLPT sentences led me to compile the member-title shape in isolation, and it
**compiles with the wrong route**:

```
  declare (pf) file, (line character(14), buff character(254)) varying;
  open file(pf) stream input title(line);

  mine: LXI H,<cell> ; MVI A,0E ; CALL ?SLCTS      (the ?SLCTS arm, 29-byte block)
  DR:   LXI H,<descriptor> ;       CALL ?SLVTS     (COPYLPT 014C..016D, ?SLVTS at 014F)
```

The operand is an UNQUALIFIED identifier, so `open_title` returns `T_var` and `lower_open`
consults `st.vars`, where a member of a varying structure binds as a **fixed** cell.  The same
binding routes the PUT item the same way wrong, which I checked rather than assumed:

| shape | mine | DR |
|---|---|---|
| `put list(nm)`, `nm char(14) varying` (scalar) | `?SLVTS` | `?SLVTS` ✓ |
| `put list(line)`, member of `(... ) varying` | `?SLCTS` + `MVI A,<len>` | `?SLVTS`, no `MVI A` — COPYLPT `0191 LXI H` / `0194 CD` chained to `?SLVTS` at `0195`, inside the `put skip list('"',line,'...')` at line 43 |
| `title(line)` in an OPEN | `?SLCTS` + `MVI A,<len>` | `?SLVTS` — COPYLPT `014F`, `01EC` |

So the bug is not in `lower_open`: it is in the storage class an unqualified varying-member
reference gets, and [C174]'s PUT dispatch inherits it.  The `?SLVTS`-for-a-member route that
`codegen.ml` documents from V8/V6/V7 is the **BASED** structure case (`LHLD <pointer> / CALL
?SLVTS`), a different route from an internal member, and that one is byte-exact.

This is a real divergence, not a stale sentence, and it is out of scope here: fixing it means
changing a storage class at the binding or adding a third dispatch arm, and P1c is allowed to
touch neither.  What P1c does is make sure nothing calls it lowered correctly — [C288] now says
it claims scalar `Vvar`/`Vfix` and nothing more, `FILE.OPEN_TITLE_VAR`'s boundary states it as a
divergence rather than a refusal, the OPEN/CLOSE header in `codegen.ml` records it, and the P1b
note's "the member case is refused" is corrected in place with the test that shows otherwise.
COPYLPT itself remains unreachable here, but for its `PRINT`/`PAGESIZE`/`LINESIZE` opens and its
`PUT PAGE`, never for its title — which is why no specimen has ever exposed this.  Neither the
PUT half nor the TITLE half is fixed in P1c: both need a binder change, and no probe of mine
pins either, so writing one would be inventing a byte pattern.

**A second, unrelated thing noticed while testing the message text:** on a **LF-only** source
file the refusal's `(line N)` is reported against the wrong line (E46H1 converted to LF says
`line 2` for its line-4 OPEN; the CRLF original says `line 4`).  Every panel and census source is
CRLF CP/M — the gate normalises `\r\n` — so no committed artifact depends on it, and no pinned
marker carries a line number except `LP10`'s `] (line 3)`, which is CRLF.  Recorded here as an
open finding; a line-code bug in the lexer is not a documentation fix.

## 5. THE CHECK THAT WOULD HAVE CAUGHT THIS, NOW WIRED IN

A stale sentence emits no bytes, so no panel can see it, and `coverage_check` validates that a
cited claim EXISTS but never whether the prose around it still matches the code.  P1c therefore
adds two tools and wires one of them into the gate:

* **`tools/file_prose_check.py`** — asserts that seven specific obsolete assertions are ABSENT
  from the five active descriptions (`codegen.ml`, `parser.ml`, `PERIMETER.md`, `COVERAGE.tsv`,
  `e2e_gate.py`), that the seven pinned negative-panel marker prefixes still exist in the source,
  that [C280] still carries its correction banner, and that no provenance cell repeats a claim in
  its leading cite cluster.  It is pointedly SILENT on `spec/notes/e2e41-*` and
  `spec/lab-evidence/**`: those are the historical record and the old sentences there are
  evidence, not bugs.  Run by the gate on every invocation, next to the coverage panel and the
  corpus census; it exits 1 and the gate aborts.
* **`tools/strip_comments.py`** — the mechanical no-logic-change proof of §3.

Verified both ways, because a check that cannot fail is not a check: reintroducing the sentence
"the long-name refusal here is a my-gap" into `PERIMETER.md` makes it report

```
file prose check: FAIL -- 1 stale assertion(s) in active descriptions
   spec/PERIMETER.md:38  | FILE attribute cluster ...
        [the long-name refusal is CLOSED since [E2E-42/P1a] -- [C283]]
```

and against `git show HEAD:ocaml/lib/codegen.ml` + `HEAD:spec/PERIMETER.md` it finds exactly the
four stale assertions this episode repaired — three in `codegen.ml` (2788, 8441, 8452) and one in
`PERIMETER.md` — which is the self-test that says the patterns match what they are meant to match.
The duplicate-provenance rule is deliberately restricted to the leading cluster for the reason in
its comment: `DECL.MEMBER_SCOPE` legitimately writes "Corrects [C261]'s E39S5 sentence" after
citing `[C261]`, and a blanket test flags that as a duplicate.

Two `bind_gate.py` FAILs (`P008`, `P063A`) are **pre-existing at the baseline** — re-measured by
building `HEAD`'s `codegen.ml` in a scratch stash, which reproduces `43 exact / 2 known-gap / 2
FAIL` identically.  This episode changes no binder behaviour.

## 6. HOW TO RE-CHECK EVERY CLAIM IN THIS NOTE

```sh
cd ocaml && dune build bin/pli80c.exe && cd ..

# the two markers the rewrite had to preserve
for k in E46H1 E46H3 E46H4 E46H7; do
  ocaml/_build/default/bin/pli80c.exe probes/$k.PLI /tmp/k.rel 2>&1 \
    | grep -oE 'OPEN option [A-Z]+ is outside'
done

# the CLOSE arm is reachable, and no longer recites OPEN history
printf 'TC3: procedure options(main);\n  declare fa file;\n  open file(fa) stream input title(%s);\n  close file(fa) keyed;\n  stop;\nend TC3;\n' "'A'" > /tmp/tc3.pli
ocaml/_build/default/bin/pli80c.exe /tmp/tc3.pli /tmp/tc3.rel 2>&1 | head -2

# the member divergence
printf 'T7: procedure options(main);\n  declare (pf) file,\n          (line character(14), buff character(254)) varying;\n  open file(pf) stream input title(line);\n  stop;\nend T7;\n' > /tmp/t7.pli
ocaml/_build/default/bin/pli80c.exe /tmp/t7.pli /tmp/t7.rel
python3 tools/reldump.py /tmp/t7.rel | grep 'CHAIN-EXT.*(SLVTS|SLCTS)'   # -> ?SLCTS, no ?SLVTS

# the census the corrected rows quote
python3 spec/lab-evidence/e2e42-p0/census.py | head -4
grep -n "CREATE:22\|LOAN2" spec/lab-evidence/e2e42-p0/OPEN-CENSUS.txt

# CREATE's live blocker, which the old SKIP comment blamed on the title
ocaml/_build/default/bin/pli80c.exe artefacts/CREATE.PLI /tmp/cr.rel 2>&1 | grep -oE 'line [0-9]+'

# the no-logic-change proof
python3 tools/file_prose_check.py                       # the check itself, and now a gate step
git show HEAD:ocaml/lib/codegen.ml > /tmp/old_cg.ml
python3 tools/strip_comments.py /tmp/old_cg.ml > /tmp/o.txt
python3 tools/strip_comments.py ocaml/lib/codegen.ml > /tmp/n.txt
python3 -c "import difflib,io; a=io.open('/tmp/o.txt').read().split(); b=io.open('/tmp/n.txt').read().split(); \
[print(t, ' '.join(a[i1:i2])[:80], '->', ' '.join(b[j1:j2])[:80]) for t,i1,i2,j1,j2 in \
difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes() if t!='equal']"

timeout 900 python3 tools/e2e_gate.py
timeout 900 python3 tools/corpus_census.py --verify spec/census/corpus-census.json
python3 tools/coverage_check.py
```
