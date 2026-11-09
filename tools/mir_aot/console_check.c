/* console_check.c — E2E-54/P1-m1 run driver for the console fixtures
 * (PLAN §P1-m1.6). Committed from the MEASURED scratch probe
 * build/p1m1-scratch/console_check_probe.c, body unchanged.
 *
 * Contract:
 *   -DENTRY=<pli80_name> is REQUIRED (#error otherwise); there is deliberately
 *     NO -DEXPECTED here — the runner judges the bytes, not this driver.
 *   The entry is declared extern long long ENTRY(void): the MIR functions return
 *     i64, so a long (32-bit) declaration would truncate the PL/I result.
 *   STDOUT belongs to the program alone: the driver writes NOTHING on stdout.
 *   The entry's return value is reported on stderr as driver-return=<v> and the
 *     driver itself returns rc 0 on normal completion. An I/O failure NEVER
 *     returns — the MIR failure tail calls exit(status), so the process code is
 *     the runtime status (OK0/EOF1/BAD2/RANGE3/IOERR4 with 0 never reached here).
 * This file is DIFFERENT from tools/mir_aot/native_check.c on purpose: that
 * driver declares extern long ENTRY(void) and compares -DEXPECTED. */
#include <stdio.h>
#ifndef ENTRY
#error "console_check: -DENTRY=<pli80_name> is required"
#endif
#define STR2(x) #x
#define STR(x) STR2(x)
extern long long ENTRY(void);
int main(void) {
  long long r = ENTRY();
  fprintf(stderr, "driver-return=%lld\n", r);
  return 0;
}
