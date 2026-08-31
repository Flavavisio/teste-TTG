from pathlib import Path
import re
text=Path('app.html').read_text(encoding='utf-8'); start=text.index('function renderizarOMeuDia('); brace=text.index('{',start)
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
            elif c=='{': depth+=1; tdepth[-1:]=[tdepth[-1]+1] if current=='template_expr' else tdepth[-1:]
            elif c=='}':
                depth-=1
                if current=='template_expr':
                    tdepth[-1]-=1
                    if tdepth[-1]==0: tdepth.pop(); mode=stack.pop()
                elif depth==0: return i+1
        i+=1
    raise AssertionError('unclosed')
end=scan_end(text,brace); block=text[start:end]
names=['document','window','alert','confirm','usuarioLogado','dados','_ehPerfilMobile','getDataHoje','escapeHtmlSimples','picarPonto','abrirSecao','picarPontoOS','abrirVerOS','_osMapaInfo','obterNomeCliente','_whatsappUrlOS','_registarKmViagemOS','obterNomeFuncionario','formatarData','formatarMoeda','renderizarHomeDashboard']
out=['LINES %d CHARS %d'%(len(block.splitlines()),len(block))]
for n in names:
    c=len(re.findall(r'(?<![\w$])'+re.escape(n)+r'(?![\w$])',block))
    if c: out.append(f'{n} {c}')
out.append('WINDOW_HANDLERS '+','.join(sorted(set(re.findall(r'window\.([_$A-Za-z][\w$]*)\s*=\s*function',block)))))
Path('.github/diagnostics/renderizarOMeuDia-deps.txt').write_text('\n'.join(out)+'\n',encoding='utf-8')
print('\n'.join(out))
