# Parser phase notes — features discovered rebuilding the grammar from the corpus

The OCaml recursive-descent parser (`ocaml/`) was validated against all 44
artefact `.PLI` files + 43 probes. 84 parse clean; the only 3 failures are
sources the ORIGINAL compiler also rejects (`tools/parse_gate.py` enforces
this parity). Below: every construct the corpus proved that our prior
grammar/manual read had MISSED or misstated.

## Lexical
- `_` is a valid identifier character (COPY: `input_file`).
- Bit literals carry a repeat suffix: `'20'b4` (DIORAND), hex-bit `'ffff'b4`
  (MPMCALLB). Expansion semantics untested [PROBE 53].
- `~` AND `^` both mean logical NOT (MPMCALLA vs DIOCOPY). `~=` is a third
  not-equal spelling alongside `<>` and `><` (MPMCALLB).
- `^=` XOR (DIOCOPY `if sear(...) ^= -1`). [PROBE 52: operand types/prec]

## Declarations
- `DCL` is a live synonym of `DECLARE` (RECORD.DCL; DR delta?).
- Type words standalone: bare `DECIMAL(p[,s])`, `BINARY(p)` (ACKTST, DEPREC),
  `PTR` for POINTER (ALLTST: `memptr ptr`).
- `FILE` as a TYPE: `declare (in_file, out_file) file;` (COPY) — vs the FILE
  attribute used in EMPDB-style stream decls.
- Types and attributes INTERLEAVE freely: `q based(p) fixed` (P041).
- Declaration groups: `(lvl, a, b) attrs` (ANNUITY `(1,p) picture(...)`),
  AND members may carry their OWN dims/type inside the group parens:
  `(line character(14), buff character(254)) varying;` (COPYLPT),
  `(x, y, z(3)) label;` (LABELS).
- Attr words seen beyond manual App C reading: `LABEL` (LABELS),
  `INITIAL(...)` (REPORT), `VARIABLE` (CALL, DEPREC), `VAR` (MPMCALLA),
  `RECURSIVE` (DFACT: nested proc suffix).
- ENTRY params may themselves be name groups:
  `invert entry ((maxrow,maxcol) float(24), fixed(6), fixed(6));` (MAININVT).

## Statements
- `PUT SKIP;` / `PUT PAGE;` and `GET SKIP;` with NO data/kind tail
  (CREATE:41, EXPR1, REPORT) — bare control PUT/GET.
- PUT/GET options and controls interleave: `put skip file(output) edit (...)`
  (LOAN2:177).
- Labels may be subscripted: `c(1): ;` (LABELS) — label-array refs; parse
  keeps coarse [PROBE 54 for runtime dispatch].
- A label may sit immediately before `end`: `exit:` / `end;` (REVERT:14).
- `END` is SOFT even as a statement head when followed by `=`/`(`/`.`:
  LOAN2 declares a variable literally named `end`.
- DO forms: `do ind = e [BY s] [TO l] [WHILE c] [REPEAT n]` in ANY order
  (IFACT `to 1 by -1`; DIOCOPY `repeat(i+1) while(i^=..)`); unbounded
  forever loop `do i = 0 by 1;` (DTEST). REPEAT count semantics [PROBE 55].

## PUT/GET edit parentheses
- Counted single items: `4a` (DIOCALLS:74).
- Counted groups: `2(skip, column(indent), a)` (DEPREC:231), nested counts
  `2(2(p'99',a),...)` (LOAN2:149).
- Replication spec on a data item: `(decimal(n,4) do n=0 to maxn)`
  (ACK:13, MAININVT get list) — a `do`-clause INSIDE IO parens.
- Format item keywords beyond App D: `COLUMN`/`COL`?, `WIDTH`? — seen
  `column(indent)` (DEPREC); added the attested ones.

## Compiler behaviour nuance
- P024 (`p->.q`) passes PASS 1 clean and reports **SYNTAX in PASS 2**
  (probes11 transcript) — C026's pass partition needs this exception
  [folded into PROBE 52 battery].

## Binder round (this session)
- `ocaml/lib/bind.ml`: resolution + $S-format dump; `tools/bind_gate.py`
  byte-diffs vs golden/bind*/S (7 EXACT, 3 known-gap).
- `pli80bind --inc DIR FILE` expands `%include 'x.y';` textually
  (directive-only span; original ';' retained — matches FCB.DCL fragment
  splicing) and strips ^Z.
- Binary storage ladder datapoints: BIN(6)=1B, BIN(15)=2B, BIN(31)=4B;
  boundaries <=8/<=16 are HYPOTHESES [PROBE 63: bin(1,7,8,9,16,17,24,31,32)].
- CREATE: bare `addr` in `get list(addr)` still registers ADDR BUILTIN —
  builtins bind by token, not call shape; interplay with same-named
  structure fields needs a runtime probe [PROBE 61].
