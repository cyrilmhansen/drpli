# golden/learn — original DRI toolchain evidence for LEARN.PLI

Full write-up: `spec/notes/learn-tutorial-dri-validation.md`, claims C102.

* `LEARN.PLI`            tutorial program, byte-identical to the repo code block, in CP/M text form (CRLF + ^Z)
* `LEARN.REL`             PL/I-80 v1.4 output, 3072 B (CODE SIZE 041A, DATA AREA 012B)
* `LEARN.COM`             LINK 1.31 output, 13952 B
* `LEARN.output.txt`      complete console output, verbatim
* `compile.transcript.txt`, `link.transcript.txt`, `run.transcript.txt`  raw CP/M sessions
* `compile-dir.txt`       D: directory after compilation
* `MANIFEST.sha256`       hashes of everything above

Run ended with `ZERO DIVIDE (0)` / `Traceback: 0498`: documented PL/I-80 behavior
(Applications Guide 7.5, p.65 -- arithmetic faults are terminal, the ON-body must
transfer to a global label), NOT a compiler or linker fault.
