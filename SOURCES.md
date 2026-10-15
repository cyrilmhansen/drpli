# PL/I-80 research sources (checked on 2026-10-15)

## Primary documentation

1. **PL/I-80 Language Manual**, second printing December 1980, 115-page scan:
   - https://www.bitsavers.org/pdf/digitalResearch/pl1/PL1-80_Language_Manual_Dec80.pdf
   - https://bitsavers.trailing-edge.com/pdf/digitalResearch/pl1/PL1-80_Language_Manual_Dec80.pdf
   - SHA-256 of Runes Pass114 local copy: `85e09fc830a3520d2e5e24d051cdf74593b393b1851ee982196555e6435b848a`.

2. **PL/I-80 Applications Guide**, second printing December 1980, 185-page scan, system operation, compiler switches, examples:
   - https://www.bitsavers.org/pdf/digitalResearch/pl1/PL1-80_Applications_Guide_Dec80.pdf
   - https://bitsavers.trailing-edge.com/pdf/digitalResearch/pl1/PL1-80_Applications_Guide_Dec80.pdf

3. **LINK-80 Operator's Guide**, second printing December 1980, documented .REL/.IRL, link behavior, runtime ABI:
   - https://www.bitsavers.org/pdf/digitalResearch/cpm/LINK-80_Operators_Guide_Dec80.pdf
   - https://bitsavers.trailing-edge.com/pdf/digitalResearch/cpm/LINK-80_Operators_Guide_Dec80.pdf
   - Readable HTML mirror, including technical chapters:
     https://www.icl1900.co.uk/unix4fun/z80pack/link80/index.htm
   - REL / IRL formal definition: https://www.icl1900.co.uk/unix4fun/z80pack/link80/link80-1.htm

**Important correction**: IRL stands for *Indexed Relocatable* library / code, NOT compiler Intermediate Representation Language. The IRL format is header (128 bytes), symbol index, then relocatable REL modules. This is explicit in LINK-80 §1.7, and the Applications Guide calls it 'Indexed Relocatable Code'. Internal compiler IR, if any, is a separate research question.

## Alternative environment options

- `z80pack`: https://github.com/udo-munk/z80pack (CP/M 2.2 bootable test disks in repository, includes runnable emulator)
- `RunCPM`: https://github.com/MockbaTheBorg/RunCPM (host directory mapped as disks; no bootable system image needed)
- `cpmemu`: https://github.com/avwohl/cpmemu (host files, explicit 8080 and Z80 mode; no system disk needed)
- `Joyce` PCW emulator: https://www.seasip.info/Unix/Joyce/ and https://github.com/fdivitto/joyce-custom/blob/master/Docs/joyce.txt (requires compatible CP/M Plus start-of-day disk for full system)
- `MAME` PCW driver: https://github.com/mamedev/mame/blob/master/src/mame/amstrad/pcw.cpp
- `ZEsarPCW`: https://docs.libretro.com/library/zesarpcw/ (open startup environment; compatible disks supplied separately)

## Alternate historical distributions (manual download links, do not assume same release)

- https://www.cpm.z80.de/binary.html (PL/I-80 v1.4 distribution listing)
- https://www.z80.eu/pli.html (PL/I-80 1.0 and 1.3)
- https://winworldpc.com/product/digital-research-pl-i-compiler/1x (manual archive and older compiler images)

No historical CP/M disk image, commercial ROM or compiler binary is included with this bundle. Obtain such disks from collections you are entitled to use. The listed sources are archival scans of copyrighted manuals; consult their notices before redistributing copies.
