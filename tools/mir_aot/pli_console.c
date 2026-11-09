/* pli_console.c — E2E-54/P1-m1 console runtime for the native MIR path.
 *
 * DRPLi's OWN minimal console layer (PLAN §P1-m1.6): it is NOT PLILIB, NOT a
 * stdio passthrough beyond getc/putc-level use, and NOT judged against the DR
 * oracle — PL/I I/O semantics stay distinct from libc. Committed from the
 * MEASURED scratch probe build/p1m1-scratch/pli_console2.c (hop 2), body
 * unchanged; only this header documents the ABI.
 *
 * ABI (the MIR protos the backend emits, §P1-m1.5):
 *   long pli_console_put_i64(i64 v);           p_put:  i64, i64:v
 *   long pli_console_get_i64(i64 *out, i64 lo, i64 hi);
 *                                              p_get:  i64, i64:out, i64:lo, i64:hi
 *   long pli_console_put_text(const char *s, i64 n);
 *                                              p_text: i64, i64:s, i64:n
 *   long pli_console_put_nl(void);             p_nl:   i64
 *
 * Status codes: OK=0 EOF=1 BAD=2 RANGE=3 IOERR=4. EVERY value returned by a
 * put/get is the status, never the data; the caller branches on it (bne Lfail)
 * and fail-fasts through exit(status), so an I/O failure is an observable
 * nonzero process code and EOF NEVER masquerades as success.
 *
 * The put functions emit NO newline — the backend closes every PUT statement
 * with a pli_console_put_nl call (line-oriented statements). Get skips leading
 * blanks/tabs/CR/LF, accepts one optional sign, requires at least one digit,
 * reads the digit run (a run longer than the scan buffer is RANGE), and the
 * parsed value must lie inside [lo,hi] = W(p) of the target's declared
 * precision or it is RANGE; a stray non-digit is BAD. */
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <ctype.h>
typedef long long i64;
#define PLI_OK 0
#define PLI_EOF 1
#define PLI_BAD 2
#define PLI_RANGE 3
#define PLI_IOERR 4

long pli_console_put_i64(i64 v) {
  char b[24];
  int n = snprintf(b, sizeof b, "%lld", v);
  if (n <= 0 || fwrite(b, 1, (size_t)n, stdout) != (size_t)n) return PLI_IOERR;
  return PLI_OK;
}

long pli_console_put_text(const char *s, i64 n) {
  if (n < 0) return PLI_BAD;
  if (n > 0 && fwrite(s, 1, (size_t)n, stdout) != (size_t)n) return PLI_IOERR;
  return PLI_OK;
}

long pli_console_put_nl(void) {
  if (putc('\n', stdout) == EOF) return PLI_IOERR;
  return PLI_OK;
}

long pli_console_get_i64(i64 *out, i64 lo, i64 hi) {
  char b[24];
  size_t i = 0;
  int c;
  do {
    c = getc(stdin);
    if (c == EOF) return PLI_EOF;
  } while (c == ' ' || c == '\t' || c == '\r' || c == '\n');
  if (c == '-' || c == '+') { b[i++] = (char)c; c = getc(stdin); }
  if (!isdigit(c)) return PLI_BAD;
  while (isdigit(c)) {
    if (i >= sizeof b - 1) {            /* digit run longer than any window: out of range */
      do { c = getc(stdin); } while (isdigit(c));
      return PLI_RANGE;
    }
    b[i++] = (char)c;
    c = getc(stdin);
  }
  b[i] = 0;
  errno = 0;
  char *end;
  i64 v = strtoll(b, &end, 10);
  if (*end != '\0' || errno == ERANGE) return PLI_BAD;
  if (v < lo || v > hi) return PLI_RANGE;
  *out = v;
  return PLI_OK;
}
