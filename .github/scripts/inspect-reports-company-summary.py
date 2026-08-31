from pathlib import Path
text=Path('app.html').read_text(encoding='utf-8')
start=text.index('function renderizarReports(')
needle="admins.forEach(admin => {"
pos=text.index(needle,start)
end=text.index("html += `</tbody></table></div>`",pos)
block=text[pos:end]
print('BLOCK_CHARS',len(block),'LINES',len(block.splitlines()))
print(block)
