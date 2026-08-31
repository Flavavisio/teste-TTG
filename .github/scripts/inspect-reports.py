from pathlib import Path
import re
text=Path('app.html').read_text(encoding='utf-8')
markers=['function renderizarReports(', 'function renderizarRelatorios(', 'function renderizarRelatorio(']
found=[m for m in markers if m in text]
print('FOUND',found)
if not found: raise AssertionError('renderizador de relatórios não encontrado')
marker=found[0]; assert text.count(marker)==1
start=text.index(marker); brace=text.index('{',start)
def scan_end(text, brace):
    depth=0; mode='normal'; escape=False; stack=[]; tdepth=[]; i=brace
    while i<len(text):
        c=text[i]; n=text[i+1] if i+1<len(text) else ''
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
end=scan_end(text,brace); block=text[start:end]
Path('.github/diagnostics/renderizarReports.txt').parent.mkdir(parents=True,exist_ok=True)
Path('.github/diagnostics/renderizarReports.txt').write_text(block,encoding='utf-8')
print('MARKER',marker,'LINES',len(block.splitlines()),'CHARS',len(block))
for token in ['document','window','dados','usuarioLogado','adminAtual()','innerHTML','querySelector','getElementById','map(','filter(','reduce(','sort(','Chart','alert(','confirm(','await ','supabase','fetch(','localStorage']:
    print(token,block.count(token))
print('FUNCTIONS',','.join(re.findall(r'function\s+([_$A-Za-z][\w$]*)\s*\(',block)))
print('CONSTS',','.join(re.findall(r'\bconst\s+([_$A-Za-z][\w$]*)\s*=\s*(?:\([^)]*\)|[_$A-Za-z][\w$]*)\s*=>',block)))
