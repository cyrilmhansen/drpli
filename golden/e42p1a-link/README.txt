THE COLLISION EVIDENCE FOR [C289].  Four linked images: two colliding, two not.

  E46D4.COM  dcl abcdef1, abcdefghij.  LINK prints "/ABCDEF/ FIRST COMMON NOT LARGEST".
             ONE control block survives in the group and it carries length byte 0x0A with
             only 7 of its 10 name characters present -- ABCDEFG at 1989..198F -- because the
             size LINK keeps is the FIRST group's, 41 bytes.
  E46D5.COM  dcl abcdef1, abcdef2.  No message (equal sizes).  The block reads 07 ABCDEF2:
             the SECOND record won at the shared base, so abcdef1 aliases onto abcdef2.
  E46F4.COM  dcl abcdefghij ALONE.  0A ABCDEFGHIJ, COMPLETE.  The no-collision control.
  E46D6.COM  dcl averylongname ALONE.  0D AVERYLONGNAME, COMPLETE.  The second control.

Reproduce:
  python3 oracle/linkrun.py link --tag e42p1b --out e42p1a-link --names E46D4 E46D5 E46D6
  python3 oracle/linkrun.py link --tag e42p1c --out e42p1a-link --names E46F4 --reuse
Analysis: spec/lab-evidence/e2e42-p1a/LINK-COLLISION.txt
