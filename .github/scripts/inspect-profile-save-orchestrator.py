from pathlib import Path

text = Path('app.html').read_text(encoding='utf-8')
marker = 'function salvarPerfil(e) {'
assert text.count(marker) == 1
start = text.index(marker)
end_marker = '// =============================================================\n        //  INICIALIZAÇÃO'
end = text.index(end_marker, start)
block = text[start:end]
out = Path('.github/diagnostics/profile-save-orchestrator.txt')
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(block, encoding='utf-8')
print('salvarPerfil chars:', len(block))
print('salvarPerfil lines:', block.count('\n') + 1)
for token in [
    'TotalGestProfileSaveSuperadmin.run({',
    'TotalGestProfileSaveDistributor.run({',
    'TotalGestProfileSaveAdmin.run({',
    'TotalGestProfileSaveWorker.run({'
]:
    print(token, block.count(token))
