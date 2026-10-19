FFACT Tier-2 acceptance evidence (E2E-10 step 2, 2026-10-19)

my .REL  == golden/first8080u/FFACT/FFACT.REL      raw byte-identical (3072 B)
my .COM  == DR-linked .COM (golden/ffact/FFACT.COM) raw byte-identical (LINK 1.31)
console  == 1415 bytes, byte-identical between the DR-built and my-built images
           (same program text: `Factorial( n )= <E14.7>` for n=0..33, then
            `Factorial(        34 )=` with NO value, `OVERFLOW (1)`, traceback)
simulator: CPU t-states recorded in run.transcript.txt

Numeric validation: 34 printed values re-derived independently in Python by
accumulating 1*2*...*n with exact intermediate products rounded to binary24
(tools/floatmodel.py).  20 of 34 agree digit-for-digit; 14 differ ONLY in the
7th printed digit.  That residue is DR PLILIB binary->decimal / multiply
rounding, NOT this compiler: the arithmetic is executed by DR's own ?FM44M
because acceptance links DR's PLILIB.  Recorded as an open PLILIB property, so
nobody later "fixes" a hypothetical native print to match C 0,0000000e+00 and thereby
-diverges from PLILIB output.  34! = 2.9523e+38 exceeds the C100 range bound
(max |v| < 2**127*(1-2**-24) ~ 1.70e38), so the terminal OVERFLOW at n=34 is
the correct stop point -- and per C102 arithmetic faults are terminal here.
