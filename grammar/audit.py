#!/usr/bin/env python3
"""Grammar-vs-corpus audit (Phase-1 item 3, re-runnable).

Scans all PL/I sources (artefacts/, probes/, .DCL context files) and
diffs the OBSERVED language vocabulary against the KNOWN coverage of
grammar/pli80.ebnf. Output is a markdown report: spec/notes/
grammar-vs-corpus.md. No parsing; this finds vocabulary gaps, the
hand-parse pass interprets them.

Usage: python3 grammar/audit.py [outfile]
"""
import os, re, sys, glob
from collections import Counter, defaultdict

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRCS = (glob.glob(os.path.join(PROJ, "artefacts", "*.PLI"))
        + glob.glob(os.path.join(PROJ, "probes", "*.PLI"))
        + [os.path.join(PROJ, "artefacts", "MATSIZE.LIB")]
        + [os.path.join(PROJ, "artefacts", f)
           for f in ("RECORD.DCL", "FCB.DCL", "DIO80.DCL", "DIOMOD.DCL",
                     "MPMDIO.DCL")])

# ---- KNOWN: vocabulary recognized by grammar/pli80.ebnf draft 0 ----
KEYWORDS = set("""
ALLOCATE AND ATEND AUTOMATIC BASED BEGIN BIT BUILTIN BY CALL CHAR
CHARACTER CLOSE DECLARE DECIMAL DEC DEFAULT DIM DO ELSE END ENTRY ENVIRONMENT
EXTERNAL EXT FILE FIXED FLOAT FORMAT FREE GET GOTO IF KEY KEYFROM
KEYTO LABEL LIST EDIT LIKE MAIN MOD NOT ON OPEN OR OPTIONS POINTER PTR
PROCEDURE PROC PUT READ REVERT RETURN RECURSIVE RETURNS SIGNAL SKIP
STATIC STOP STRUCTURE TITLE TO TRANSLATE UNTIL VARYING VAR WHILE WRITE
INPUT OUTPUT UPDATE INITIAL INTO INIT SET FROM PROMPT THEN REPEAT PAGE ENDFILE ENDPAGE UNDEFINEDFILE KEY FIXEDOVERFLOW UNDERFLOW ZERODIVIDE OVERFLOW ERROR TITLE KEYED STREAM PAGESIZE ENVIRONMENT SYSOUT SYSIN GO TO NULL BOOL HBOUND LBOUND LINENO PAGENO DIVIDE
""".split())
# preprocessor + control keywords handled separately
PREPROC = {"%INCLUDE", "%REPLACE", "%COPY", "%ENTRY"}
BI = set("""
ABS ACOS ADDR ALLWDS ASIN ATAN ATAND ASCII BIT BINARY CEIL CHAR COLLATE
COS COSD DECIMAL DIMENSION EXP FLOAT FLOOR INDEX LENGTH LOG LOG10 LOG2
MAX MAXWDS MIN MOD ONCODE ONFILE ONKEY RANK ROUND SIGN SIN SIND SINH
SQRT STKSIZ SUBSTR TAN TAND TANH TOTWDS TRANSLATE TRUNC UNSPEC VERIFY
""".split())
# PL/I reserved-ish common words we treat as known even if unused yet
COMMON = set("""
ABSTRACT ACCEPT ADD ADJUST AFTER ALIGNED ANY ARRAY ASSIGN AT ATTACH
BACKUP BEFORE BLOCK BODY CANCEL CHECK CHECKSUM CLOSE COBOL COLUMN
COMPLEX CONCURRENT CONDITION COPY DATA DEFAULT DELETE DESC DESCRIPTOR
DISABLE DISCONNECT ELSE EMPLIVATE ENTRY EXTERNAL FROM GROUP HANDLER
HYPOTHETICAL IDENTIFIER IGNORE INDEX INITIAL INTERNAL INVALID I/0
KEY LABEND LABEL LANGUAGE LEAVE LEVEL LIKE LINK LIST LOCAL LABEL
MAIN MAP MATCH MEMBER NO NONBASED NUMBER OFFSET ON OFF ORDER
OUT OVERFLOW PARAMETER PICTURE PROCESS PROGRAM PROPER PUT RECORD
RECOVER REGION REGISTER REPLICATED RESTORE RESTRICTED RESULT
RESUME RETAIN RETURN REVERSE SEARCH SECURED SEGMENT SEQUENCE
SERIAL SOURCE STRING STRUCTURE TABLE TASK TERM TIMEOUT TITLE
TYPE UNDEFINED UNIQUE UNIT UNTIL USE VALUE VARIABLE VARYING
WAIT WRITE ZONE
""".lower().split())
# App B: the 31 statement types (name -> leading keyword(s))
APPB = {
 "B1 ALLOCATE": "ALLOCATE", "B2 ASSIGNMENT": None, "B3 BEGIN": "BEGIN",
 "B4 CALL": "CALL", "B5 CLOSE": "CLOSE", "B6 DECLARE": "DECLARE|DCL",
 "B7 DO": "DO", "B8 END": "END", "B9 FORMAT": "FORMAT", "B10 FREE": "FREE",
 "B11 GET EDIT": "GET", "B12 GET LIST": "GET", "B13 GOTO": "GOTO|GO",
 "B14 IF": "IF", "B15 EMPTY": None, "B16 ON": "ON", "B17 OPEN": "OPEN",
 "B18 PROCEDURE": "PROCEDURE|PROC", "B19 PUT EDIT": "PUT",
 "B20 PUT LIST": "PUT", "B21 READ stream": "READ",
 "B22 READ sequential": "READ", "B23 READ KEYTO": "READ",
 "B24 READ KEY": "READ", "B25 RETURN": "RETURN", "B26 REVERT": "REVERT",
 "B27 SIGNAL": "SIGNAL", "B28 STOP": "STOP", "B29 WRITE stream": "WRITE",
 "B30 WRITE sequential": "WRITE", "B31 WRITE KEYFROM": "WRITE",
}

def norm(text):
    text = text.upper()
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)   # comments
    text = re.sub(r"'[^']*'", " ", text)                # literals (naive)
    return text

def main():
    toks = Counter()
    where = defaultdict(set)
    files = {}
    for p in SRCS:
        raw = open(p, errors="replace").read()
        files[os.path.basename(p)] = raw
        up = raw.upper()
        up = re.sub(r"/\*.*?\*/", " ", up, flags=re.S)  # strip comments
        for ln, line in enumerate(up.replace("\r", "").split("\n"), 1):
            line_c = re.sub(r"'[^']*'", " ", line)
            for m in re.finditer(r"%[A-Z]+|[A-Z][A-Z0-9]{1,11}", line_c):
                t = m.group(0)
                toks[t] += 1
                where[t].add(os.path.basename(p) + ":" + str(ln))
    out = open(sys.argv[1] if len(sys.argv) > 1
               else os.path.join(PROJ, "spec/notes/grammar-vs-corpus.md"), "w")
    W = out.write
    W("# Grammar-vs-corpus audit (auto: grammar/audit.py)\n\n")
    W(f"Scanned {len(files)} files, {sum(toks.values())} token hits.\n\n")

    known = KEYWORDS | BI | COMMON
    W("## 1. Tokens used in corpus but NOT in grammar's known vocabulary\n\n")
    unknown = [(t, c) for t, c in toks.most_common()
               if t not in known and not t.startswith("%")
               and t not in ("THE",) and c > 0]
    # filter out obvious user identifiers appearing in only 1-2 places? no:
    W("| token | count | first occurrences |\n|---|---|---|\n")
    for t, c in unknown:
        w = sorted(where[t])[:3]
        W(f"| {t} | {c} | {', '.join(w)} |\n")

    W("\n## 2. Preprocessor usage\n\n")
    for pp in sorted(PREPROC):
        hits = [(t, c) for t, c in toks.items() if t == pp]
        W(f"- {pp}: {hits[0][1] if hits else 0} occurrence(s)\n")
    for t, c in sorted(toks.items()):
        if t.startswith("%") and t not in PREPROC:
            W(f"- **UNEXPECTED** {t}: {c} ({sorted(where[t])[:2]})\n")

    W("\n## 3. Statement-type coverage across corpus (App B checklist)\n\n")
    stmt_use = defaultdict(set)
    for name, raw in files.items():
        up = re.sub(r"/\*.*?\*/", " ", raw.upper(), flags=re.S)
        up = re.sub(r"'[^']*'", " ", up)
        for key in ("ALLOCATE", "BEGIN", "CALL", "CLOSE", "FORMAT", "FREE",
                    "GOTO", "GO TO", "IF", "ON", "OPEN", "READ", "RETURN",
                    "REVERT", "SIGNAL", "STOP", "WRITE", "GET", "PUT",
                    "DO", "DCL", "DECLARE"):
            if re.search(r"(?<![A-Z0-9])" + key.replace(" ", r"\s+"), up):
                stmt_use[key].add(name)
    for key in sorted(stmt_use):
        W(f"- {key}: {len(stmt_use[key])} file(s)\n")
    for key in ("ALLOCATE", "FORMAT", "FREE", "GOTO", "ON", "REVERT",
                "SIGNAL", "STOP", "READ", "WRITE", "CLOSE", "OPEN",
                "CALL", "RETURN"):
        if key not in stmt_use:
            W(f"- **{key}: ABSENT from entire corpus -> needs synthetic probe**\n".replace("**", ""))

    W("\n## 4. Attributes observed inside DECLARE blocks\n\n")
    attrs = Counter()
    aw = defaultdict(set)
    for name, raw in files.items():
        up = re.sub(r"/\*.*?\*/", " ", raw.upper(), flags=re.S)
        for blk in re.finditer(r"(?:DCL|DECLARE)\s(.*?);", up, flags=re.S):
            for m in re.finditer(
                r"\b(FIXED(\s+(BINARY|B|DECIMAL|DEC)\(\s*\d+\s*(,\s*\d+)?(\s*\)|\s*\)\s*VARYING)?)?"
                r"|FLOAT(\s+(BINARY|BIN|DECIMAL|DEC))?( \(\d+\))?"
                r"|CHARACTER?\s*\(\d+\)(\s*VARYING)?|BIT\s*\(\d+\)(\s*ALIGNED)?"
                r"|POINTER|PTR|ENTRY|FILE|LABEL|BUILTIN|BASED\([A-Z0-9]+\)"
                r"|STATIC|AUTOMATIC|AUTO|EXTERNAL|EXT|INITIAL\(|INIT\("
                r"|VARIABLE|VARYING|DEFAULT|LIKE\()", blk.group(1)):
                a = re.sub(r"\s+", "", m.group(0))
                a = re.sub(r"\d+", "n", a)
                attrs[a] += 1
                aw[a].add(name)
    for a, c in attrs.most_common():
        W(f"- {a}: {c} ({len(aw[a])} files)\n")

    W("\n## 5. Built-in functions referenced\n\n")
    bis = Counter()
    for name, raw in files.items():
        up = re.sub(r"'[^']*'", " ", raw.upper())
        for m in re.finditer(r"\b(" + "|".join(sorted(BI)) + r")\s*\(", up):
            bis[m.group(1)] += 1
    for b, c in bis.most_common():
        W(f"- {b}: {c}\n")
    W("\n(unused built-ins => differential test material, not gaps)\n")

    W("\n## 6. Operator spellings observed\n\n")
    ops = Counter()
    opat = [("**", "**"), ("^=", "^="), ("/\\", "/\\"), ("\\/", "\\/"),
            ("||", "||"), ("&", "&"), ("|", "|"), ("^", "^"),
            ("<=", "<="), (">=", ">="), (":=", ":="), ("!=", "!="),
            ("=", "="), ("<", "<"), (">", ">"), ("+", "+"), ("-", "-"),
            ("*", "*"), ("/", "/")]
    for name, raw in files.items():
        up = re.sub(r"'[^']*'", " ", raw)
        for pat, key in opat:
            n = len(re.findall(re.escape(pat), up))
            if n:
                ops[key] += n
    for o, c in ops.most_common():
        W(f"- `{o}`: {c}\n")
    W("\nNOTE: ^,/\\,|| counts are heuristic vs comments/literals; "
      "verify by hand before making claims.\n")
    out.close()
    print("wrote", out.name)

if __name__ == "__main__":
    main()
