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
 */
#include "mir.h"
#include "mir-gen.h"
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

int main(int argc, char **argv) {
  size_t sz;
  char *src;
  MIR_module_t mod;
  MIR_item_t it;
  int generated = 0;
  void *buf = NULL;
  size_t obj_size = 0;
  FILE *out;

  if (argc != 4 || strcmp(argv[1], "-f") != 0) {
    fprintf(stderr, "usage: %s -f IN.mir OUT.o\n", argv[0]);
    return 2;
  }
  src = read_whole(argv[2], &sz);
  if (src == NULL) {
    fprintf(stderr, "mir2o: cannot read input %s\n", argv[2]);
    return 3;
  }
  the_ctx = MIR_init();
  MIR_scan_string(the_ctx, src);
  for (mod = DLIST_HEAD(MIR_module_t, *MIR_get_module_list(the_ctx)); mod != NULL;
       mod = DLIST_NEXT(MIR_module_t, mod))
    MIR_load_module(the_ctx, mod);
  /* ADDITIVE (P1-m1 §P1-m1.6): register every import as an external BEFORE
   * MIR_link so the link resolves it to the environment entry instead of
   * aborting with "import of undefined item". */
  for (mod = DLIST_HEAD(MIR_module_t, *MIR_get_module_list(the_ctx)); mod != NULL;
       mod = DLIST_NEXT(MIR_module_t, mod))
    for (it = DLIST_HEAD(MIR_item_t, mod->items); it != NULL;
         it = DLIST_NEXT(MIR_item_t, it))
      if (it->item_type == MIR_import_item)
        MIR_load_external(the_ctx, it->u.import_id, (void *)pli_ext_dummy);
  MIR_gen_init(the_ctx);
  gen_inited = 1;
  MIR_gen_set_object_mode(the_ctx, 1);
  MIR_link(the_ctx, MIR_set_gen_interface, NULL);
  for (mod = DLIST_HEAD(MIR_module_t, *MIR_get_module_list(the_ctx)); mod != NULL;
       mod = DLIST_NEXT(MIR_module_t, mod))
    for (it = DLIST_HEAD(MIR_item_t, mod->items); it != NULL;
         it = DLIST_NEXT(MIR_item_t, it))
      if (it->item_type == MIR_func_item) {
        MIR_gen(the_ctx, it);
        generated++;
      }
  if (generated == 0) {
    fprintf(stderr, "mir2o: no functions generated (empty module?)\n");
    mir_finish_all();
    return 4;
  }
  if (MIR_gen_object_emit(the_ctx, &buf, &obj_size) != 0 || buf == NULL) {
    fprintf(stderr, "mir2o: MIR_gen_object_emit failed\n");
    mir_finish_all();
    return 5;
  }
  out = fopen(argv[3], "wb");
  if (out == NULL || fwrite(buf, 1, obj_size, out) != obj_size) {
    fprintf(stderr, "mir2o: cannot write object %s\n", argv[3]);
    if (out != NULL) fclose(out);
    mir_finish_all();
    return 6;
  }
  fclose(out);
  mir_finish_all();
  fprintf(stderr, "mir2o: wrote %zu bytes (%d function(s))\n", obj_size, generated);
  return 0;
}
