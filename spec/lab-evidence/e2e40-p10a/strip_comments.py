import sys, io
def strip(t):
    out=[]; i=0; depth=0; n=len(t)
    while i<n:
        if depth==0 and t.startswith('(*',i):
            depth=1; i+=2; continue
        if depth>0:
            if t.startswith('*)',i):
                depth-=1; i+=2
                if depth==0: out.append(' ')
            elif t.startswith('(*',i):
                depth+=1; i+=2
            else: i+=1
            continue
        if t[i]=='"':
            j=i+1
            while j<n:
                if t[j]=='\\': j+=2; continue
                if t[j]=='"': break
                j+=1
            out.append(t[i:j+1]); i=j+1; continue
        out.append(t[i]); i+=1
    return '\n'.join(''.join(out).splitlines()).strip()
a=strip(io.open(sys.argv[1],encoding='utf-8').read())
b=strip(io.open(sys.argv[2],encoding='utf-8').read())
if a==b:
    print("CODE (comments stripped) IS IDENTICAL between the two revisions")
else:
    import difflib
    d=[l for l in difflib.unified_diff(a.split('\n'), b.split('\n'), lineterm='', n=1)]
    print("CODE DIFFERS -- %d diff lines:" % len(d))
    print('\n'.join(d[:40]))
