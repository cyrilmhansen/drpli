/*
 * mir2o — P1-m0 native object emitter (PLAN §P1-m0.5, evidence D-3).
 *
 * Reads MIR text produced by the OCaml MIR backend, parses it with the
 * pinned MIR library (this parse IS the acceptance check, brief §8), and
 * emits an ELF relocatable .o through the pinned object-mode generation
 * sequence measured from the laboratory's src/microbench/aot_corpus.c:
 *
 *   MIR_init -> MIR_scan_string -> MIR_load_module (every module)
 *   -> MIR_gen_init -> MIR_gen_set_object_mode(ctx,1)
 *   -> MIR_link(ctx, MIR_set_gen_interface, NULL)
 *   -> MIR_gen (every MIR_func_item of the loaded modules)
 *   -> MIR_gen_object_emit -> write -> MIR_gen_finish -> MIR_finish
 *
 * MIR_object_load is deliberately NOT used (brief §2: the lab
 * docs/ISSUES.md records an import/data relocation defect in that path).
 * No MADC, no JIT, no execution here.  Nonzero rc on EVERY failure:
 * bad usage (2), input read (3), zero functions generated (4), emit (5),
 * output write (6).  MIR parser/syntax failures die inside the pinned
 * library's own error handler with a nonzero status (measured D-4:
 * "absent endfunc" aborts).  Generation and finalization run on every
 * exit path.  The backend emits exactly one function, but every
 * func_item of every loaded module is generated.
 *
 * E2E-54/P1-m1 (PLAN §P1-m1.6, additive): the pinned madc fork aborts
 * MIR_link on a STRONG import of a host symbol ("import of undefined
 * item") and its object emitter cannot express weak imports from MIR
 * text.  Before MIR_link, every MIR_import_item is therefore registered
 * with MIR_load_external(ctx, name, (void *) pli_ext_dummy).  The dummy
 * address is used only by JIT interfaces; the object capture records the
 * symbol NAME as an UNDEFINED STRONG ELF symbol (measured hop 2: nm shows
 * U pli_console_* / U exit and the dummy never enters the object).
 * Modules WITHOUT imports take zero extra steps, so their objects stay
 * byte-identical to the frozen §P1-m0 pins (CT2 re-check).  The pinned
 * laboratory itself is never touched.
 *
 * E2E-54/P1-mD (PLAN §P1-mD.2/.4, additive): `mir2o -f IN.mir OUT.o
 * [--debug-map MAP]`.  WITHOUT the flag NOTHING of the debug code runs —
 * the emitted bytes stay byte-identical to every frozen pin (§P1-mD.8
 * T9).  WITH the flag (all on the probe-2 PROVEN public route):
 *
 *   1. load IN.mir into the context (as today);
 *   2. parse and FULLY validate the sidecar MAP (§P1-mD.3) BEFORE
 *      annotating anything — all-or-nothing: magic + version, sha256 of
 *      the EXACT IN.mir bytes (embedded C implementation below; tools/ is
 *      not the ocaml/hir F8 vocabulary area, so hex literals are fine),
 *      absolute file path, one func (the P1-m0..m1 backend emits exactly
 *      one function), insn records in order i = 0..n-1 with each opcode
 *      matching MIR_insn_name at its index, count EQUAL to the parsed
 *      func->insns length, unique var names all present in func->vars;
 *   3. stamp insn->file_id/insn->line (line 0 => file_id 0, measured hop
 *      2: gen_record_line skips only the 0/0 pair) on every listed insn;
 *   4. debug codegen config (§P1-mD.1 fact 3): gen level 0, inline
 *      permission 0, spill_all, func homes-only + one MIR_set_reg_debug_home
 *      per sidecar var; then imports/link/gen exactly as the default path;
 *   5. MIR_gen_object_emit -> PLAIN capture in memory (no debug builder
 *      attached to the capture);
 *   6. IN-C STRUCTURAL ELF drop of .eh_frame and .rela.eh_frame with full
 *      bookkeeping (sh_link/sh_info/e_shstrndx remap, symtab entries with
 *      st_shndx remapped and dropped-section symbols removed, local count
 *      kept) — pure ELF arithmetic, ZERO DWARF semantics, no subprocess,
 *      no temp file (the objcopy stand-in of hop 3 measured the target
 *      shape; this is the same structural op);
 *   7. MIR_object_create + MIR_object_read of the stripped image (reader
 *      error => loud refusal with its err_msg);
 *   8. fresh MIR_debug builder: add_file (must return id 1), base_type
 *      carrier "fixed bin(15)" SIGNED 8 (every integer carrier of this
 *      backend is an 8-byte i64 holding a fixed bin(15) value — the window
 *      law §P1-m0.3; wording pinned measured-first from output),
 *      find_symbol on the FRESH object (.text section offset), add_func
 *      (func->line_map + func->cfi), then per var MIR_reg_frame_offset
 *      (failure => refusal, NEVER a silent un-homed var) + add_var;
 *      MIR_object_set_debug BEFORE MIR_object_emit; write OUT.o.
 *
 * Exit codes: usage 2, input read 3, zero functions 4, capture emit 5,
 * output write 6, sidecar read 7, sidecar validation 8, ELF eh_frame drop
 * 9, read-back/debug-build/final-emit 10 (§P1-mD.2; every refusal prints
 * its named reason to stderr).
 */
#include "mir.h"
#include "mir-gen.h"
#include "mir-debug.h"
#include <elf.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static MIR_context_t the_ctx = NULL;
static int gen_inited = 0;

/* Finish on every exit path (brief: gen_finish/finish on all paths). */
static void mir_finish_all(void) {
  if (the_ctx != NULL) {
    if (gen_inited) MIR_gen_finish(the_ctx);
    MIR_finish(the_ctx);
    the_ctx = NULL;
  }
}

/* Stable non-NULL dummy address for host-import registration (§P1-m1.6);
 * never called in object mode — the emitter records the symbol NAME as
 * undefined. */
static void pli_ext_dummy(void) {}

static char *read_whole(const char *path, size_t *size) {
  FILE *f = fopen(path, "rb");
  long n;
  char *p;
  if (f == NULL || fseek(f, 0, SEEK_END) != 0 || (n = ftell(f)) < 0
      || fseek(f, 0, SEEK_SET) != 0) {
    if (f != NULL) fclose(f);
    return NULL;
  }
  p = (char *)malloc((size_t)n + 1);
  if (p == NULL || fread(p, 1, (size_t)n, f) != (size_t)n) {
    free(p);
    fclose(f);
    return NULL;
  }
  fclose(f);
  p[n] = '\0';
  *size = (size_t)n;
  return p;
}

/* ---------------------------------------------------------------------
 * SHA-256 (FIPS 180-4), embedded (§P1-mD.3 validation: no external
 * dependency; tools/ is NOT under the ocaml/hir F8 vocabulary law, so
 * the standard hex constant tables are used verbatim).
 * ------------------------------------------------------------------ */
typedef struct {
  uint32_t h[8];
  uint64_t total_bits;
  unsigned char block[64];
  size_t block_len;
} sha256_ctx;

static const uint32_t sha_K[64] = {
  0x428a2f98u, 0x71374491u, 0xb5c0fbcfu, 0xe9b5dba5u, 0x3956c25bu, 0x59f111f1u,
  0x923f82a4u, 0xab1c5ed5u, 0xd807aa98u, 0x12835b01u, 0x243185beu, 0x550c7dc3u,
  0x72be5d74u, 0x80deb1feu, 0x9bdc06a7u, 0xc19bf174u, 0xe49b69c1u, 0xefbe4786u,
  0x0fc19dc6u, 0x240ca1ccu, 0x2de92c6fu, 0x4a7484aau, 0x5cb0a9dcu, 0x76f988dau,
  0x983e5152u, 0xa831c66du, 0xb00327c8u, 0xbf597fc7u, 0xc6e00bf3u, 0xd5a79147u,
  0x06ca6351u, 0x14292967u, 0x27b70a85u, 0x2e1b2138u, 0x4d2c6dfcu, 0x53380d13u,
  0x650a7354u, 0x766a0abbu, 0x81c2c92eu, 0x92722c85u, 0xa2bfe8a1u, 0xa81a664bu,
  0xc24b8b70u, 0xc76c51a3u, 0xd192e819u, 0xd6990624u, 0xf40e3585u, 0x106aa070u,
  0x19a4c116u, 0x1e376c08u, 0x2748774cu, 0x34b0bcb5u, 0x391c0cb3u, 0x4ed8aa4au,
  0x5b9cca4fu, 0x682e6ff3u, 0x748f82eeu, 0x78a5636fu,  0x84c87814u, 0x8cc70208u,
  0x90befffau, 0xa4506cebu, 0xbef9a3f7u, 0xc67178f2u,
};

static uint32_t rotr32(uint32_t x, unsigned n) { return (x >> n) | (x << (32 - n)); }

static void sha256_compress(sha256_ctx *c, const unsigned char *b) {
  uint32_t w[64];
  uint32_t a = c->h[0], bb = c->h[1], cc = c->h[2], d = c->h[3];
  uint32_t e = c->h[4], f = c->h[5], g = c->h[6], h = c->h[7];
  for (size_t i = 0; i < 64; i++) {
    if (i < 16) {
      w[i] = ((uint32_t)b[i * 4] << 24) | ((uint32_t)b[i * 4 + 1] << 16)
             | ((uint32_t)b[i * 4 + 2] << 8) | (uint32_t)b[i * 4 + 3];
    } else {
      uint32_t s0 = rotr32(w[i - 15], 7) ^ rotr32(w[i - 15], 18) ^ (w[i - 15] >> 3);
      uint32_t s1 = rotr32(w[i - 2], 17) ^ rotr32(w[i - 2], 19) ^ (w[i - 2] >> 10);
      w[i] = w[i - 16] + s0 + w[i - 7] + s1;
    }
    uint32_t S1 = rotr32(e, 6) ^ rotr32(e, 11) ^ rotr32(e, 25);
    uint32_t ch = (e & f) ^ ((~e) & g);
    uint32_t t1 = h + S1 + ch + sha_K[i] + w[i];
    uint32_t S0 = rotr32(a, 2) ^ rotr32(a, 13) ^ rotr32(a, 22);
    uint32_t maj = (a & bb) ^ (a & cc) ^ (bb & cc);
    uint32_t t2 = S0 + maj;
    h = g; g = f; f = e; e = d + t1; d = cc; cc = bb; bb = a; a = t1 + t2;
  }
  c->h[0] += a; c->h[1] += bb; c->h[2] += cc; c->h[3] += d;
  c->h[4] += e; c->h[5] += f; c->h[6] += g; c->h[7] += h;
}

static void sha256_init(sha256_ctx *c) {
  static const uint32_t h0[8] = {0x6a09e667u, 0xbb67ae85u, 0x3c6ef372u, 0xa54ff53au,
                                 0x510e527fu, 0x9b05688cu, 0x1f83d9abu, 0x5be0cd19u};
  memcpy(c->h, h0, sizeof h0);
  c->total_bits = 0;
  c->block_len = 0;
}

static void sha256_update(sha256_ctx *c, const unsigned char *data, size_t len) {
  c->total_bits += (uint64_t)len * 8u;
  while (len > 0) {
    size_t take = 64 - c->block_len;
    if (take > len) take = len;
    memcpy(c->block + c->block_len, data, take);
    c->block_len += take;
    data += take;
    len -= take;
    if (c->block_len == 64) {
      sha256_compress(c, c->block);
      c->block_len = 0;
    }
  }
}

static void sha256_final(sha256_ctx *c, unsigned char digest[32]) {
  uint64_t bits = c->total_bits;
  unsigned char pad = 0x80u;
  sha256_update(c, &pad, 1);
  unsigned char z = 0u;
  while (c->block_len != 56) sha256_update(c, &z, 1);
  unsigned char tail[8];
  for (int i = 0; i < 8; i++) tail[i] = (unsigned char)(bits >> (56 - 8 * i));
  sha256_update(c, tail, 8);
  for (int i = 0; i < 8; i++) {
    digest[i * 4] = (unsigned char)(c->h[i] >> 24);
    digest[i * 4 + 1] = (unsigned char)(c->h[i] >> 16);
    digest[i * 4 + 2] = (unsigned char)(c->h[i] >> 8);
    digest[i * 4 + 3] = (unsigned char)c->h[i];
  }
}

static void sha256_hex(const void *data, size_t len, char out_hex[65]) {
  sha256_ctx c;
  unsigned char digest[32];
  sha256_init(&c);
  sha256_update(&c, (const unsigned char *)data, len);
  sha256_final(&c, digest);
  for (int i = 0; i < 32; i++) sprintf(out_hex + 2 * i, "%02x", digest[i]);
  out_hex[64] = '\0';
}

/* ---------------------------------------------------------------------
 * Sidecar debug map (§P1-mD.3): parse + validation structures.
 * ------------------------------------------------------------------ */
typedef struct {
  char sha[65];          /* expected sha256 hex of the EXACT .mir bytes */
  char *file;            /* absolute .pli source path */
  char *func;            /* the single MIR function name */
  size_t n_insns;
  uint32_t *lines;       /* per insn (dlist order, labels included) */
  char **opcodes;        /* per insn expected MIR_insn_name */
  size_t n_vars;
  char **var_mir;        /* MIR local name (v<sid>) */
  char **var_src;        /* source name (sorig) */
} dbgmap_t;

static char *dup_tok(const char *start, size_t len) {
  char *s = (char *)malloc(len + 1);
  if (s != NULL) {
    memcpy(s, start, len);
    s[len] = '\0';
  }
  return s;
}

/* Split a record into single-space-separated fields.  Returns the field
 * count, or -1 for any malformed line (empty field, leading/trailing
 * space, tab).  Fields point INTO line (NUL-punched). */
static int split_fields(char *line, char **f, int max) {
  int n = 0;
  char *p = line;
  if (*p == '\0') return 0;
  if (*p == ' ' || *p == '\t' || p[strlen(p) - 1] == ' ' || strchr(p, '\t') != NULL) return -1;
  while (n < max) {
    char *sp = strchr(p, ' ');
    f[n++] = p;
    if (sp == NULL) return n;
    if (sp == p) return -1; /* empty field: double space */
    *sp = '\0';
    p = sp + 1;
  }
  return -1; /* too many fields */
}

static int parse_uint32(const char *tok, uint32_t *v) {
  unsigned long acc = 0;
  if (tok[0] < '0' || tok[0] > '9') return -1;
  for (const char *p = tok; *p != '\0'; p++) {
    if (*p < '0' || *p > '9') return -1;
    acc = acc * 10u + (unsigned long)(*p - '0');
    if (acc > 0xFFFFFFFFul) return -1;
  }
  *v = (uint32_t)acc;
  return 0;
}

static void dbgmap_free(dbgmap_t *m) {
  free(m->file);
  free(m->func);
  free(m->lines);
  for (size_t i = 0; i < m->n_insns; i++) free(m->opcodes[i]);
  free(m->opcodes);
  for (size_t i = 0; i < m->n_vars; i++) {
    free(m->var_mir[i]);
    free(m->var_src[i]);
  }
  free(m->var_mir);
  free(m->var_src);
  memset(m, 0, sizeof *m);
}

/* Parse the sidecar text (in place; syntax + law ONLY — content checks
 * against the parsed MIR happen in validate_map).  Returns 0, or nonzero
 * with a named reason in err. */
static int parse_map(char *text, dbgmap_t *m, char *err, size_t err_len) {
  int state = 0; /* 0 p1md, 1 mir, 2 file, 3 func, 4 insns, 5 vars */
  uint32_t next_i = 0;
  memset(m, 0, sizeof *m);
  size_t cap_insns = 16, cap_vars = 8;
  m->lines = (uint32_t *)malloc(cap_insns * sizeof *m->lines);
  m->opcodes = (char **)malloc(cap_insns * sizeof *m->opcodes);
  m->var_mir = (char **)malloc(cap_vars * sizeof *m->var_mir);
  m->var_src = (char **)malloc(cap_vars * sizeof *m->var_src);
  if (m->lines == NULL || m->opcodes == NULL || m->var_mir == NULL || m->var_src == NULL) {
    snprintf(err, err_len, "out of memory parsing the debug map");
    return -1;
  }
  char *cursor = text;
  while (cursor != NULL) {
    char *nl = strchr(cursor, '\n');
    if (nl != NULL) *nl++ = '\0';
    if (*cursor == '\0') {
      if (nl == NULL) { cursor = NULL; continue; } /* tolerate ONE trailing newline */
      snprintf(err, err_len, "debug map: empty line");
      return -1;
    }
    char *f[5];
    int nf = split_fields(cursor, f, 5);
    if (nf < 0) {
      snprintf(err, err_len, "debug map: malformed line: %s", cursor);
      return -1;
    }
    if (nf >= 1 && strcmp(f[0], "p1md") == 0) {
      if (state != 0 || nf != 2 || strcmp(f[1], "1") != 0) {
        snprintf(err, err_len, "debug map: bad magic/version line (want exactly 'p1md 1'): %s",
                 cursor);
        return -1;
      }
      state = 1;
    } else if (strcmp(f[0], "mir") == 0) {
      if (state != 1 || nf != 2 || strlen(f[1]) != 64) {
        snprintf(err, err_len, "debug map: bad 'mir <64-hex sha256>' record (position %d): %s",
                 state + 1, cursor);
        return -1;
      }
      for (int i = 0; i < 64; i++) {
        char c = f[1][i];
        if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) {
          snprintf(err, err_len, "debug map: sha hex char %d is not lowercase hex", i);
          return -1;
        }
      }
      memcpy(m->sha, f[1], 65);
      state = 2;
    } else if (strcmp(f[0], "file") == 0) {
      if (state != 2 || nf != 2 || f[1][0] != '/') {
        snprintf(err, err_len, "debug map: bad 'file <absolute path>' record: %s", cursor);
        return -1;
      }
      m->file = dup_tok(f[1], strlen(f[1]));
      if (m->file == NULL) {
        snprintf(err, err_len, "out of memory");
        return -1;
      }
      state = 3;
    } else if (strcmp(f[0], "func") == 0) {
      if (state != 3 && state != 4) {
        snprintf(err, err_len, "debug map: 'func' record out of position: %s", cursor);
        return -1;
      }
      if (nf != 3) {
        snprintf(err, err_len, "debug map: bad 'func <index> <name>' record: %s", cursor);
        return -1;
      }
      uint32_t fi;
      if (parse_uint32(f[1], &fi) != 0 || fi != 0u) {
        snprintf(err, err_len, "debug map: the P1-mD slice carries EXACTLY one func-item "
                               "(index must be 0): %s", cursor);
        return -1;
      }
      if (m->func != NULL) {
        snprintf(err, err_len, "debug map: duplicate func record (only one function is "
                               "emitted by this backend): %s", cursor);
        return -1;
      }
      m->func = dup_tok(f[2], strlen(f[2]));
      state = 4;
    } else if (strcmp(f[0], "insn") == 0) {
      if (state < 4) {
        snprintf(err, err_len, "debug map: 'insn' record before 'func': %s", cursor);
        return -1;
      }
      if (state == 5) {
        snprintf(err, err_len, "debug map: 'insn' record after a 'var' record: %s", cursor);
        return -1;
      }
      if (nf != 5) {
        snprintf(err, err_len, "debug map: bad 'insn <func> <i> <opcode> <line>' record: %s",
                 cursor);
        return -1;
      }
      uint32_t idx, line;
      if (parse_uint32(f[2], &idx) != 0 || idx != next_i) {
        snprintf(err, err_len, "debug map: insn index %s out of order (expected %u; duplicate or "
                               "gapped records are refused)",
                 f[2], next_i);
        return -1;
      }
      if (parse_uint32(f[4], &line) != 0) {
        snprintf(err, err_len, "debug map: bad line number in %s", cursor);
        return -1;
      }
      if (m->n_insns == cap_insns) {
        cap_insns *= 2;
        m->lines = (uint32_t *)realloc(m->lines, cap_insns * sizeof *m->lines);
        m->opcodes = (char **)realloc(m->opcodes, cap_insns * sizeof *m->opcodes);
        if (m->lines == NULL || m->opcodes == NULL) {
          snprintf(err, err_len, "out of memory");
          return -1;
        }
      }
      m->lines[m->n_insns] = line;
      m->opcodes[m->n_insns] = dup_tok(f[3], strlen(f[3]));
      if (m->opcodes[m->n_insns] == NULL) {
        snprintf(err, err_len, "out of memory");
        return -1;
      }
      m->n_insns++;
      next_i++;
      state = 4;
    } else if (strcmp(f[0], "var") == 0) {
      if (state < 4) {
        snprintf(err, err_len, "debug map: 'var' record before 'func'/'insn': %s", cursor);
        return -1;
      }
      if (nf != 3) {
        snprintf(err, err_len, "debug map: bad 'var <mir-name> <source-name>' record: %s",
                 cursor);
        return -1;
      }
      for (size_t k = 0; k < m->n_vars; k++)
        if (strcmp(m->var_mir[k], f[1]) == 0) {
          snprintf(err, err_len, "debug map: duplicate var record for %s", f[1]);
          return -1;
        }
      if (m->n_vars == cap_vars) {
        cap_vars *= 2;
        m->var_mir = (char **)realloc(m->var_mir, cap_vars * sizeof *m->var_mir);
        m->var_src = (char **)realloc(m->var_src, cap_vars * sizeof *m->var_src);
        if (m->var_mir == NULL || m->var_src == NULL) {
          snprintf(err, err_len, "out of memory");
          return -1;
        }
      }
      m->var_mir[m->n_vars] = dup_tok(f[1], strlen(f[1]));
      m->var_src[m->n_vars] = dup_tok(f[2], strlen(f[2]));
      if (m->var_mir[m->n_vars] == NULL || m->var_src[m->n_vars] == NULL) {
        snprintf(err, err_len, "out of memory");
        return -1;
      }
      m->n_vars++;
      state = 5;
    } else {
      snprintf(err, err_len, "debug map: unknown record: %s", cursor);
      return -1;
    }
    cursor = nl;
  }
  if (state < 4) {
    snprintf(err, err_len, "debug map: incomplete (missing func/insn records)");
    return -1;
  }
  return 0;
}

/* §P1-mD.3 content law against the PARSED function: every insn opcode name
 * matches MIR_insn_name at its dlist index; the count equals the parsed
 * func->insns length; every var name exists in func->vars. */
static MIR_item_t find_func_item(const char *name) {
  MIR_module_t mod;
  MIR_item_t it;
  for (mod = DLIST_HEAD(MIR_module_t, *MIR_get_module_list(the_ctx)); mod != NULL;
       mod = DLIST_NEXT(MIR_module_t, mod))
    for (it = DLIST_HEAD(MIR_item_t, mod->items); it != NULL;
         it = DLIST_NEXT(MIR_item_t, it))
      if (it->item_type == MIR_func_item && strcmp(it->u.func->name, name) == 0) return it;
  return NULL;
}

static MIR_reg_t find_reg_by_name(MIR_func_t func, const char *name) {
  for (size_t i = 0; i < VARR_LENGTH(MIR_var_t, func->vars); i++)
    if (strcmp(VARR_GET(MIR_var_t, func->vars, i).name, name) == 0) return (MIR_reg_t)(i + 1);
  return 0;
}

static int validate_map(dbgmap_t *m, MIR_func_t func, char *err, size_t err_len) {
  size_t n = 0;
  MIR_insn_t insn;
  for (insn = DLIST_HEAD(MIR_insn_t, func->insns); insn != NULL;
       insn = DLIST_NEXT(MIR_insn_t, insn))
    n++;
  if (n != m->n_insns) {
    snprintf(err, err_len,
             "debug map: insn count MISMATCH for %s: map carries %zu records, the parsed "
             "function carries %zu insns",
             func->name, m->n_insns, n);
    return -1;
  }
  size_t i = 0;
  for (insn = DLIST_HEAD(MIR_insn_t, func->insns); insn != NULL;
       insn = DLIST_NEXT(MIR_insn_t, insn), i++) {
    const char *op = MIR_insn_name(the_ctx, insn->code);
    if (strcmp(op, m->opcodes[i]) != 0) {
      snprintf(err, err_len, "debug map: opcode MISMATCH for %s insn %zu: expected '%s', "
                             "parsed '%s'",
               func->name, i, m->opcodes[i], op);
      return -1;
    }
  }
  for (i = 0; i < m->n_vars; i++)
    if (find_reg_by_name(func, m->var_mir[i]) == 0) {
      snprintf(err, err_len, "debug map: var MIR name %s is not a named register of %s",
               m->var_mir[i], func->name);
      return -1;
    }
  return 0;
}

/* ---------------------------------------------------------------------
 * In-C structural ELF drop of named sections (§P1-mD.4 step 6): pure
 * ELF64 bookkeeping — section headers removed, surviving indices remapped
 * in sh_link/sh_info/e_shstrndx and in symtab st_shndx, symbols defined in
 * a dropped section removed, local-symbol count (symtab sh_info) kept.
 * ZERO DWARF semantics.  Returns 0 and sets *out (malloc'd) + *out_len, or
 * nonzero with a named reason in err.
 * ------------------------------------------------------------------ */
static size_t align_up(size_t x, size_t a) {
  if (a <= 1) return x;
  return (x + a - 1) / a * a;
}

static int elf_drop_named(const unsigned char *in, size_t in_len, const char *const *drops,
                          size_t ndrops, unsigned char **outp, size_t *out_lenp, char *err,
                          size_t err_len) {
  if (in_len < sizeof (Elf64_Ehdr) || memcmp(in, ELFMAG, 4) != 0 || in[EI_CLASS] != ELFCLASS64
      || in[EI_DATA] != ELFDATA2LSB) {
    snprintf(err, err_len, "not a little-endian ELF64 image from the MIR capture");
    return -1;
  }
  const Elf64_Ehdr *eh = (const Elf64_Ehdr *)in;
  if (eh->e_type != ET_REL || eh->e_shentsize != sizeof (Elf64_Shdr) || eh->e_shnum == 0
      || eh->e_shstrndx >= eh->e_shnum) {
    snprintf(err, err_len, "unexpected ELF shape (e_type %u, shentsize %u, shnum %u, shstrndx %u)",
             (unsigned)eh->e_type, (unsigned)eh->e_shentsize, (unsigned)eh->e_shnum,
             (unsigned)eh->e_shstrndx);
    return -1;
  }
  size_t shnum = eh->e_shnum;
  if (eh->e_shoff > in_len || shnum > (in_len - eh->e_shoff) / sizeof (Elf64_Shdr)) {
    snprintf(err, err_len, "section header table runs past the image end");
    return -1;
  }
  const Elf64_Shdr *sh = (const Elf64_Shdr *)(in + eh->e_shoff);
  const Elf64_Shdr *str = &sh[eh->e_shstrndx];
  if (str->sh_offset > in_len || str->sh_size > in_len - str->sh_offset) {
    snprintf(err, err_len, ".shstrtab runs past the image end");
    return -1;
  }
  const char *strtab = (const char *)in + str->sh_offset;
  /* name lookup with a bounds-checked NUL terminator */
  char (*names)[64] = malloc(shnum * sizeof *names);
  char *dropped_sym = NULL;
  int *map = NULL;
  unsigned char *out = NULL;
  size_t *new_sec_off = NULL, *new_sec_size = NULL;
  if (names == NULL) {
    snprintf(err, err_len, "out of memory");
    return -1;
  }
  for (size_t i = 0; i < shnum; i++) {
    names[i][0] = '\0';
    if (str->sh_size > 0 && sh[i].sh_name < str->sh_size) {
      size_t left = str->sh_size - sh[i].sh_name;
      const char *nm = strtab + sh[i].sh_name;
      size_t nlen = strnlen(nm, left);
      if (nlen < sizeof names[i]) memcpy(names[i], nm, nlen + 1);
    }
  }
  int rc = -1;
  int *drop = (int *)calloc(shnum, sizeof *drop);
  map = (int *)malloc(shnum * sizeof *map);
  if (drop == NULL || map == NULL) {
    snprintf(err, err_len, "out of memory");
    goto done;
  }
  for (size_t k = 0; k < ndrops; k++) {
    int found = 0;
    for (size_t i = 0; i < shnum; i++)
      if (strcmp(names[i], drops[k]) == 0) {
        drop[i] = 1;
        found++;
      }
    if (found != 1) {
      snprintf(err, err_len, "section %s appears %d times in the capture (expected exactly 1)",
               drops[k], found);
      goto done;
    }
  }
  size_t keep = 0;
  for (size_t i = 0; i < shnum; i++) {
    map[i] = (int)(drop[i] ? 0 : keep);
    if (!drop[i]) keep++;
  }
  /* locate the single symtab */
  size_t symtab_idx = shnum;
  for (size_t i = 0; i < shnum; i++) {
    if (sh[i].sh_type == SHT_NOBITS && sh[i].sh_size > 0) {
      /* NOBITS with content is fine to carry through (bytes are not stored) */
    }
    if (sh[i].sh_type == SHT_SYMTAB) {
      if (symtab_idx != shnum || drop[i]) {
        snprintf(err, err_len, "expected exactly one surviving symtab");
        goto done;
      }
      symtab_idx = i;
    }
  }
  if (symtab_idx == shnum) {
    snprintf(err, err_len, "the capture carries no symtab at all");
    goto done;
  }
  {
    const Elf64_Shdr *st = &sh[symtab_idx];
    if (st->sh_entsize != sizeof (Elf64_Sym) || st->sh_size % sizeof (Elf64_Sym) != 0
        || st->sh_offset > in_len || st->sh_size > in_len - st->sh_offset) {
      snprintf(err, err_len, "symtab has an unexpected shape");
      goto done;
    }
  }
  const Elf64_Sym *syms = (const Elf64_Sym *)(in + sh[symtab_idx].sh_offset);
  size_t nsyms = sh[symtab_idx].sh_size / sizeof (Elf64_Sym);
  dropped_sym = (char *)malloc(nsyms);
  if (dropped_sym == NULL) {
    snprintf(err, err_len, "out of memory");
    goto done;
  }
  size_t kept_syms = 0, kept_locals = 0;
  for (size_t i = 0; i < nsyms; i++) {
    int gone = 0;
    if (syms[i].st_shndx < shnum && drop[syms[i].st_shndx]) gone = 1;
    dropped_sym[i] = (char)gone;
    if (!gone) {
      kept_syms++;
      if (i < sh[symtab_idx].sh_info && ELF64_ST_BIND(syms[i].st_info) == STB_LOCAL)
        kept_locals++;
    }
  }
  /* size the new image */
  size_t off = sizeof (Elf64_Ehdr);
  new_sec_off = malloc(keep * sizeof *new_sec_off);
  new_sec_size = malloc(keep * sizeof *new_sec_size);
  size_t kept_sym_off = 0;
  if (new_sec_off == NULL || new_sec_size == NULL) {
    snprintf(err, err_len, "out of memory");
    goto done;
  }
  for (size_t i = 0; i < shnum; i++) {
    if (drop[i]) continue;
    size_t j = (size_t)map[i];
    size_t sz = sh[i].sh_type == SHT_SYMTAB ? kept_syms * sizeof (Elf64_Sym) : sh[i].sh_size;
    if (sh[i].sh_type != SHT_NOBITS && sz > 0) {
      if (sh[i].sh_offset == 0) {
        snprintf(err, err_len, "section %s carries bytes at file offset 0", names[i]);
        goto done;
      }
      if (sh[i].sh_offset > in_len || sz > in_len - sh[i].sh_offset) {
        snprintf(err, err_len, "section %s runs past the image end", names[i]);
        goto done;
      }
      off = align_up(off, sh[i].sh_addralign > 1 ? sh[i].sh_addralign : 1);
      new_sec_off[j] = off;
      off += sz;
    } else {
      new_sec_off[j] = sz == 0 ? 0 : align_up(off, sh[i].sh_addralign > 1 ? sh[i].sh_addralign : 1);
      if (sz > 0) off = new_sec_off[j] + sz; /* NOBITS: no file bytes, still no room used */
    }
    new_sec_size[j] = sz;
    if (i == symtab_idx) kept_sym_off = new_sec_off[j];
  }
  (void)kept_sym_off;
  off = align_up(off, 8);
  size_t shoff = off;
  size_t total = shoff + keep * sizeof (Elf64_Shdr);
  out = malloc(total);
  if (out == NULL) {
    snprintf(err, err_len, "out of memory");
    goto done;
  }
  memset(out, 0, total);
  memcpy(out, in, sizeof (Elf64_Ehdr));
  for (size_t i = 0; i < shnum; i++) {
    if (drop[i] || sh[i].sh_type == SHT_NOBITS || sh[i].sh_size == 0) continue;
    memcpy(out + new_sec_off[(size_t)map[i]], in + sh[i].sh_offset, sh[i].sh_size);
  }
  /* rebuild the symtab with st_shndx remapped and dropped symbols removed */
  {
    Elf64_Sym *ns = (Elf64_Sym *)(out + new_sec_off[(size_t)map[symtab_idx]]);
    size_t w = 0;
    for (size_t i = 0; i < nsyms; i++) {
      if (dropped_sym[i]) continue;
      ns[w] = syms[i];
      if (ns[w].st_shndx < shnum) ns[w].st_shndx = (Elf64_Section)map[ns[w].st_shndx];
      w++;
    }
    if (w != kept_syms) {
      snprintf(err, err_len, "internal symtab rebuild inconsistency");
      goto done;
    }
  }
  /* section headers */
  {
    Elf64_Shdr *nh = (Elf64_Shdr *)(out + shoff);
    for (size_t i = 0; i < shnum; i++) {
      if (drop[i]) continue;
      size_t j = (size_t)map[i];
      nh[j] = sh[i];
      nh[j].sh_offset = new_sec_off[j];
      nh[j].sh_size = new_sec_size[j];
      if (i == symtab_idx) {
        nh[j].sh_info = (Elf64_Word)kept_locals;
      } else if (sh[i].sh_type == SHT_RELA || sh[i].sh_type == SHT_REL) {
        if (sh[i].sh_info < shnum && drop[sh[i].sh_info]) nh[j].sh_info = 0;
        else if (sh[i].sh_info < shnum) nh[j].sh_info = (Elf64_Word)map[sh[i].sh_info];
      }
      if (nh[j].sh_link < shnum && drop[nh[j].sh_link]) nh[j].sh_link = 0;
      else if (nh[j].sh_link < shnum) nh[j].sh_link = (Elf64_Word)map[nh[j].sh_link];
    }
  }
  {
    Elf64_Ehdr *ne = (Elf64_Ehdr *)out;
    ne->e_shoff = shoff;
    ne->e_shnum = (Elf64_Half)keep;
    ne->e_shstrndx = (Elf64_Half)map[eh->e_shstrndx];
  }
  *outp = out;
  *out_lenp = total;
  out = NULL;
  rc = 0;
done:
  free(names);
  free(drop);
  free(new_sec_off);
  free(new_sec_size);
  free(dropped_sym);
  free(map);
  free(out);
  return rc;
}

/* ------------------------------------------------------------------ */

int main(int argc, char **argv) {
  const char *map_path = NULL;
  if (argc != 4 && argc != 6) {
    fprintf(stderr, "usage: %s -f IN.mir OUT.o [--debug-map MAP]\n", argv[0]);
    return 2;
  }
  if (strcmp(argv[1], "-f") != 0) {
    fprintf(stderr, "usage: %s -f IN.mir OUT.o [--debug-map MAP]\n", argv[0]);
    return 2;
  }
  if (argc == 6) {
    if (strcmp(argv[4], "--debug-map") != 0) {
      fprintf(stderr, "mir2o: unknown option %s (expected --debug-map MAP)\n", argv[4]);
      return 2;
    }
    map_path = argv[5];
  }
  const char *in_path = argv[2];
  const char *out_path = argv[3];
  size_t sz;
  char *src = read_whole(in_path, &sz);
  if (src == NULL) {
    fprintf(stderr, "mir2o: cannot read input %s\n", in_path);
    return 3;
  }
  the_ctx = MIR_init();
  MIR_scan_string(the_ctx, src);
  for (MIR_module_t mod = DLIST_HEAD(MIR_module_t, *MIR_get_module_list(the_ctx)); mod != NULL;
       mod = DLIST_NEXT(MIR_module_t, mod))
    MIR_load_module(the_ctx, mod);

  /* ADDITIVE (P1-mD §P1-mD.4 steps 1-3): read + validate the sidecar and
   * stamp the source locations BEFORE any code generation.  On the default
   * path (no --debug-map) NONE of this runs. */
  dbgmap_t map;
  int map_active = 0;
  MIR_item_t dbg_func_item = NULL;
  char merr[512];
  merr[0] = '\0';
  memset(&map, 0, sizeof map);
  if (map_path != NULL) {
    size_t msz;
    char *mtext = read_whole(map_path, &msz);
    if (mtext == NULL) {
      fprintf(stderr, "mir2o: cannot read debug map %s\n", map_path);
      free(src);
      mir_finish_all();
      return 7;
    }
    if (parse_map(mtext, &map, merr, sizeof merr) != 0) {
      fprintf(stderr, "mir2o: %s\n", merr);
      free(mtext);
      dbgmap_free(&map);
      free(src);
      mir_finish_all();
      return 8;
    }
    /* §P1-mD.3: the sha is over the EXACT input .mir bytes. */
    char want[65], got[65];
    sha256_hex(src, sz, got);
    memcpy(want, map.sha, 65);
    if (strcmp(want, got) != 0) {
      fprintf(stderr, "mir2o: debug map sha MISMATCH for %s: map says %s, the input bytes "
                      "digest to %s\n",
              in_path, want, got);
      free(mtext);
      dbgmap_free(&map);
      free(src);
      mir_finish_all();
      return 8;
    }
    dbg_func_item = find_func_item(map.func);
    if (dbg_func_item == NULL) {
      fprintf(stderr, "mir2o: debug map names function %s which the parsed module does not "
                      "define\n",
              map.func);
      free(mtext);
      dbgmap_free(&map);
      free(src);
      mir_finish_all();
      return 8;
    }
    if (validate_map(&map, dbg_func_item->u.func, merr, sizeof merr) != 0) {
      fprintf(stderr, "mir2o: %s\n", merr);
      free(mtext);
      dbgmap_free(&map);
      free(src);
      mir_finish_all();
      return 8;
    }
    free(mtext);
    /* stamp: the public insn fields; line 0 => file_id 0 too (measured
     * hop 2: gen_record_line skips ONLY the 0/0 pair). */
    size_t i = 0;
    for (MIR_insn_t insn = DLIST_HEAD(MIR_insn_t, dbg_func_item->u.func->insns); insn != NULL;
         insn = DLIST_NEXT(MIR_insn_t, insn), i++) {
      insn->file_id = map.lines[i] == 0 ? 0u : 1u;
      insn->line = map.lines[i];
    }
    map_active = 1;
  }

  for (MIR_module_t mod = DLIST_HEAD(MIR_module_t, *MIR_get_module_list(the_ctx)); mod != NULL;
       mod = DLIST_NEXT(MIR_module_t, mod))
    for (MIR_item_t it = DLIST_HEAD(MIR_item_t, mod->items); it != NULL;
         it = DLIST_NEXT(MIR_item_t, it))
      if (it->item_type == MIR_import_item)
        MIR_load_external(the_ctx, it->u.import_id, (void *)pli_ext_dummy);
  MIR_gen_init(the_ctx);
  gen_inited = 1;
  MIR_gen_set_object_mode(the_ctx, 1);
  if (map_active) {
    /* §P1-mD.1 fact 3 (measured): the gen DEFAULT optimize level is 2; the
     * debug path MUST explicitly drop it to 0.  spill_all + homes_only +
     * one debug home per sidecar var, inline permission 0. */
    MIR_gen_set_optimize_level(the_ctx, 0);
    MIR_set_inline_permission(the_ctx, 0);
    MIR_set_spill_all(the_ctx, 1);
    MIR_func_t f = dbg_func_item->u.func;
    MIR_func_debug_homes_only(the_ctx, f);
    for (size_t k = 0; k < map.n_vars; k++) {
      MIR_reg_t r = find_reg_by_name(f, map.var_mir[k]);
      MIR_set_reg_debug_home(the_ctx, r, f);
    }
  }
  MIR_link(the_ctx, MIR_set_gen_interface, NULL);
  int generated = 0;
  for (MIR_module_t mod = DLIST_HEAD(MIR_module_t, *MIR_get_module_list(the_ctx)); mod != NULL;
       mod = DLIST_NEXT(MIR_module_t, mod))
    for (MIR_item_t it = DLIST_HEAD(MIR_item_t, mod->items); it != NULL;
         it = DLIST_NEXT(MIR_item_t, it))
      if (it->item_type == MIR_func_item) {
        MIR_gen(the_ctx, it);
        generated++;
      }
  if (generated == 0) {
    fprintf(stderr, "mir2o: no functions generated (empty module?)\n");
    if (map_active) dbgmap_free(&map);
    free(src);
    mir_finish_all();
    return 4;
  }
  void *buf = NULL;
  size_t obj_size = 0;
  if (MIR_gen_object_emit(the_ctx, &buf, &obj_size) != 0 || buf == NULL) {
    fprintf(stderr, "mir2o: MIR_gen_object_emit failed\n");
    if (map_active) dbgmap_free(&map);
    free(src);
    mir_finish_all();
    return 5;
  }

  if (!map_active) {
    /* DEFAULT PATH — the historical §P1-m0/§P1-m1 bytes, untouched. */
    FILE *out = fopen(out_path, "wb");
    if (out == NULL || fwrite(buf, 1, obj_size, out) != obj_size) {
      fprintf(stderr, "mir2o: cannot write object %s\n", out_path);
      if (out != NULL) fclose(out);
      free(src);
      mir_finish_all();
      return 6;
    }
    fclose(out);
    mir_finish_all();
    fprintf(stderr, "mir2o: wrote %zu bytes (%d function(s))\n", obj_size, generated);
    free(src);
    return 0;
  }

  /* DEBUG PATH (§P1-mD.4 steps 6-8). */
  static const char *const drops[2] = {".eh_frame", ".rela.eh_frame"};
  unsigned char *stripped = NULL;
  size_t stripped_len = 0;
  if (elf_drop_named((const unsigned char *)buf, obj_size, drops, 2, &stripped, &stripped_len,
                     merr, sizeof merr)
      != 0) {
    fprintf(stderr, "mir2o: .eh_frame drop failed: %s\n", merr);
    dbgmap_free(&map);
    free(src);
    mir_finish_all();
    return 9;
  }
  MIR_object_t o2 = MIR_object_create();
  if (o2 == NULL || MIR_object_read(o2, stripped, stripped_len, merr, sizeof merr) != 0) {
    fprintf(stderr, "mir2o: read-back of the stripped image failed: %s\n", merr);
    free(stripped);
    dbgmap_free(&map);
    free(src);
    mir_finish_all();
    return 10;
  }
  fprintf(stderr,
          "mir2o: stripped image read back (%zu -> %zu bytes, .eh_frame + .rela.eh_frame "
          "dropped in C)\n",
          obj_size, stripped_len);
  MIR_debug_t dbg = MIR_debug_init();
  uint32_t fid = MIR_debug_add_file(dbg, map.file);
  if (fid != 1u) {
    fprintf(stderr, "mir2o: debug add_file returned id %u, expected 1\n", (unsigned)fid);
    MIR_object_destroy(o2);
    free(stripped);
    dbgmap_free(&map);
    free(src);
    mir_finish_all();
    return 10;
  }
  /* Carrier type law (§P1-mD.4): every integer of this backend rides an
   * 8-byte i64 holding a fixed bin(15) value (window law §P1-m0.3); the
   * label wording is MEASURED-FIRST from the readelf output. */
  MIR_debug_type_t ty = MIR_debug_base_type(dbg, "fixed bin(15)", MIR_DEBUG_ENC_SIGNED, 8);
  MIR_func_t f = dbg_func_item->u.func;
  int sec = -1;
  uint64_t text_off = 0, sym_size = 0;
  if (!MIR_object_find_symbol(o2, f->name, &sec, &text_off, &sym_size)
      || sec != MIR_OBJ_SEC_TEXT) {
    fprintf(stderr, "mir2o: find_symbol on the read-back object failed for %s (sec=%d)\n",
            f->name, sec);
    MIR_debug_destroy(dbg);
    MIR_object_destroy(o2);
    free(stripped);
    dbgmap_free(&map);
    free(src);
    mir_finish_all();
    return 10;
  }
  MIR_debug_add_func(dbg, f->name, (void *)(uintptr_t)text_off, f->code_len, f->line_map,
                     f->line_map_len, f->cfi, f->cfi_len);
  for (size_t k = 0; k < map.n_vars; k++) {
    MIR_reg_t r = find_reg_by_name(f, map.var_mir[k]);
    int64_t slot = 0;
    if (!MIR_reg_frame_offset(f, r, &slot)) {
      fprintf(stderr, "mir2o: var %s (reg %u) is not stack-homed — refusing, never an "
                      "un-homed debug var\n",
              map.var_mir[k], (unsigned)r);
      MIR_debug_destroy(dbg);
      MIR_object_destroy(o2);
      free(stripped);
      dbgmap_free(&map);
      free(src);
      mir_finish_all();
      return 10;
    }
    MIR_debug_add_var(dbg, map.var_src[k], 0, ty, slot, 0, 0);
  }
  MIR_object_set_debug(o2, dbg);
  void *fbuf = NULL;
  size_t fsize = 0;
  if (MIR_object_emit(o2, &fbuf, &fsize) != 0 || fbuf == NULL) {
    fprintf(stderr, "mir2o: MIR_object_emit (debug merge) failed\n");
    MIR_debug_destroy(dbg);
    MIR_object_destroy(o2);
    free(stripped);
    dbgmap_free(&map);
    free(src);
    mir_finish_all();
    return 10;
  }
  FILE *out = fopen(out_path, "wb");
  if (out == NULL || fwrite(fbuf, 1, fsize, out) != fsize) {
    fprintf(stderr, "mir2o: cannot write object %s\n", out_path);
    if (out != NULL) fclose(out);
    free(fbuf);
    MIR_debug_destroy(dbg);
    MIR_object_destroy(o2);
    free(stripped);
    dbgmap_free(&map);
    free(src);
    mir_finish_all();
    return 6;
  }
  fclose(out);
  fprintf(stderr,
          "mir2o: wrote %zu debug bytes to %s (%d function(s), %zu stamped insns, %zu vars)\n",
          fsize, out_path, generated, map.n_insns, map.n_vars);
  free(fbuf);
  MIR_debug_destroy(dbg);
  MIR_object_destroy(o2);
  free(stripped);
  dbgmap_free(&map);
  free(src);
  mir_finish_all();
  return 0;
}
