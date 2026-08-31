from pathlib import Path
text=Path('app.html').read_text(encoding='utf-8')
start=text.index('function renderizarReports(')
# template-aware function end scanner
brace=text.index('{',start)
def endfn(t,b):
 d=0; mode='n'; esc=False; stack=[]; td=[]; i=b
 while i<len(t):
  c=t[i]; n=t[i+1] if i+1<len(t) else ''
  if mode=='lc':
   if c=='\n': mode=stack.pop()
  elif mode=='bc':
   if c=='*' and n=='/': mode=stack.pop(); i+=1
  elif mode in ('s','q'):
   if esc: esc=False
   elif c=='\\': esc=True
   elif (mode=='s' and c=="'") or (mode=='q' and c=='"'): mode=stack.pop()
  elif mode=='t':
   if esc: esc=False
   elif c=='\\': esc=True
   elif c=='`': mode=stack.pop()
   elif c=='$' and n=='{': stack.append('t'); mode='te'; td.append(1); d+=1; i+=1
  else:
   cur=mode
   if c=='/' and n=='/': stack.append(cur); mode='lc'; i+=1
   elif c=='/' and n=='*': stack.append(cur); mode='bc'; i+=1
   elif c=="'": stack.append(cur); mode='s'
   elif c=='"': stack.append(cur); mode='q'
   elif c=='`': stack.append(cur); mode='t'
   elif c=='{': d+=1; td[-1]+=1 if cur=='te' else 0
   elif c=='}':
    d-=1
    if cur=='te':
     td[-1]-=1
     if td[-1]==0: td.pop(); mode=stack.pop()
    elif d==0: return i+1
  i+=1
 raise AssertionError('unclosed')
block=text[start:endfn(text,brace)]
lines=block.splitlines()
out=[]
for idx,line in enumerate(lines):
 low=line.lower()
 if any(k in low for k in ['erp','ronda']):
  a=max(0,idx-8); z=min(len(lines),idx+12)
  out.append(f'--- context line {idx+1} ---\n'+'\n'.join(f'{j+1}: {lines[j]}' for j in range(a,z)))
Path('.github/diagnostics').mkdir(parents=True,exist_ok=True)
Path('.github/diagnostics/reports-erp-rounds.txt').write_text('\n\n'.join(out),encoding='utf-8')
print('REPORT_LINES',len(lines),'MATCH_CONTEXTS',len(out))
