from pathlib import Path
text=Path('app.html').read_text(encoding='utf-8')
start=text.index('function renderizarReports(')
brace=text.index('{',start)
def endfn(t,b):
    depth=0; mode='normal'; escape=False; stack=[]; tdepth=[]; i=b
    while i<len(t):
        c=t[i]; n=t[i+1] if i+1<len(t) else ''
        if mode=='line_comment':
            if c=='\n': mode=stack.pop() if stack else 'normal'
        elif mode=='block_comment':
            if c=='*' and n=='/': mode=stack.pop() if stack else 'normal'; i+=1
        elif mode in ('single','double'):
            if escape: escape=False
            elif c=='\\': escape=True
            elif (mode=='single' and c=="'") or (mode=='double' and c=='"'): mode=stack.pop() if stack else 'normal'
        elif mode=='template':
            if escape: escape=False
            elif c=='\\': escape=True
            elif c=='`': mode=stack.pop() if stack else 'normal'
            elif c=='$' and n=='{': stack.append('template'); mode='template_expr'; tdepth.append(1); depth+=1; i+=1
        else:
            current=mode
            if c=='/' and n=='/': stack.append(current); mode='line_comment'; i+=1
            elif c=='/' and n=='*': stack.append(current); mode='block_comment'; i+=1
            elif c=="'": stack.append(current); mode='single'
            elif c=='"': stack.append(current); mode='double'
            elif c=='`': stack.append(current); mode='template'
            elif c=='{':
                depth+=1
                if current=='template_expr': tdepth[-1]+=1
            elif c=='}':
                depth-=1
                if current=='template_expr':
                    tdepth[-1]-=1
                    if tdepth[-1]==0: tdepth.pop(); mode=stack.pop()
                elif depth==0: return i+1
        i+=1
    raise AssertionError('unclosed')
block=text[start:endfn(text,brace)]
lines=block.splitlines(); out=[]
for idx,line in enumerate(lines):
    low=line.lower()
    if any(k in low for k in ['erp','ronda']):
        a=max(0,idx-8); z=min(len(lines),idx+12)
        out.append(f'--- context line {idx+1} ---\n'+'\n'.join(f'{j+1}: {lines[j]}' for j in range(a,z)))
Path('.github/diagnostics').mkdir(parents=True,exist_ok=True)
Path('.github/diagnostics/reports-erp-rounds.txt').write_text('\n\n'.join(out),encoding='utf-8')
print('REPORT_LINES',len(lines),'MATCH_CONTEXTS',len(out))
