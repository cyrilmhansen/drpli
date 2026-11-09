/*
 * native_check.c — minimal P1-m0 native test driver (PLAN §P1-m0.5).
 *
 * Compiled with -DENTRY=<exported symbol> -DEXPECTED=<long> (harness
 * convention; the C ABI contract is documented in PLAN §P1-m0.5: zero
 * arguments, return in the SysV x86-64 i64 slot, no PL/I startup, no
 * descriptor, no runtime).  Calls ENTRY once, prints the returned value
 * as decimal, exits 0 iff it equals EXPECTED.  The expected value lives
 * ONLY in the build line the runner supplies from its hand-computed
 * table (PLAN §P1-m0.6) — never in this file and never in any generated
 * artifact.
 */
#include <stdio.h>

#ifndef ENTRY
#error "native_check.c requires -DENTRY=<exported symbol>"
#endif
#ifndef EXPECTED
#error "native_check.c requires -DEXPECTED=<independent expected value>"
#endif

extern long ENTRY(void);

int main(void) {
  long got = ENTRY();
  printf("%ld\n", got);
  return got == (long)EXPECTED ? 0 : 1;
}
