import sys
# value -> name (the six initializations, identical in all seven probes)
VAL={'a':7,'b':11,'c':13,'h':17,'k':19,'n':23}
for p in sys.argv[1:]:
    b=open('golden/e45l/%s.COM'%p,'rb').read()
    n={'E45S1':0x54,'E45S2':0x53,'E45S3':0x52,'E45S4':0x53,'E45S5':0x52,'E45S6':0x54,'E45S7':0x53}[p]
    body=b[:n]
    # name cells by their initializers
    addr2name={}
    i=0
    while i < n-6:
        if body[i]==0x21 and body[i+3]==0x36 and body[i+4]==0x23 and body[i+5]==0x36:   # LXI H,addr/MVI M,lo/INX H/MVI M,hi  (MEMBER)
            a=body[i+1]|(body[i+2]<<8); v=body[i+3]|(body[i+5]<<8)
            nm=[k for k,x in VAL.items() if x==v]
            if nm: addr2name[a]=nm[0]+"(member)"
        if body[i]==0x21 and body[i+3]==0x22:                                            # LXI H,value / SHLD addr      (ORDINARY)
            v=body[i+1]|(body[i+2]<<8); a=body[i+4]|(body[i+5]<<8)
            nm=[k for k,x in VAL.items() if x==v]
            if nm: addr2name[a]=nm[0]+"(ordinary)"
        i+=1
    print("=== %s  cell map: %s"%(p,{hex(k):v for k,v in sorted(addr2name.items())}))
    simple={0xE5:"PUSH H",0xD1:"POP D",0x19:"DAD D",0xEB:"XCHG",0x23:"INX H",0x0B:"DCX H",
            0x73:"MOV M,E",0x72:"MOV M,D",0x09:"DAD B",0xC9:"RET"}
    out=[]; i=0
    def nmv(v):
        return "k=%d"%v if v<=32767 else "k=%d"%(v-65536)
    while i < n:
        op=body[i]
        if op==0x2A:
            a=body[i+1]|(body[i+2]<<8); out.append("%02X: LHLD %s"%(i,addr2name.get(a,'0x%04X'%a))); i+=3
        elif op==0x22:
            a=body[i+1]|(body[i+2]<<8); out.append("%02X: SHLD %s"%(i,addr2name.get(a,'0x%04X'%a))); i+=3
        elif op==0x21:
            a=body[i+1]|(body[i+2]<<8); out.append("%02X: LXI H,%s"%(i,addr2name.get(a,'0x%04X'%a) if a>=0x1A00 else str(a))); i+=3
        elif op==0x11:
            out.append("%02X: LXI B,%s"%(i,nmv(body[i+1]|(body[i+2]<<8)))); i+=3
        elif op in (0xCD,0xC3):
            out.append("%02X: %s 0x%04X"%(i,'CALL' if op==0xCD else 'JMP',body[i+1]|(body[i+2]<<8))); i+=3
        elif op==0x3E:
            out.append("%02X: MVI A,%d"%(i,body[i+1])); i+=2
        elif op==0x36:
            out.append("%02X: MVI M,%d"%(i,body[i+1])); i+=2
        elif op in simple:
            out.append("%02X: %s"%(i,simple[op])); i+=1
        else:
            out.append("%02X: db %02X"%(i,op)); i+=1
    print("    "+" | ".join(out))
