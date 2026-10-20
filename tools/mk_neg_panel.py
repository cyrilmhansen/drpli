import os, sys
sys.path.insert(0, os.path.join(os.getcwd(), "tools"))
import e2e_gate as G
os.makedirs("negsrc", exist_ok=True)
rows = []
for i, (name, val) in enumerate(sorted(G.REJECTS.items()), 1):
    short = "NG%02d" % i
    src = val[0]
    if not src.endswith("\n"): src += "\n"
    data = src.replace("\r\n", "\n").replace("\n", "\r\n").encode() + b"\x1a"
    open(os.path.join("negsrc", short + ".PLI"), "wb").write(data)
    rows.append("%s %s" % (short, name))
open("negsrc/MAP.txt", "w").write("\n".join(rows) + "\n")
print("wrote", len(rows))
