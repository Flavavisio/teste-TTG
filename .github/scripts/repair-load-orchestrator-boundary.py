from pathlib import Path
import subprocess

APP = Path('app.html')
app = APP.read_text(encoding='utf-8')
parent = subprocess.check_output(['git','show','af2ac8b97f6c194297306c2fd15267b5b78ea058:app.html'], text=True)

marker = '        // -------- sincronização por diferenças (substitui o antigo guardarDados) --------\n'
end_token = '        function registarAuditoria('

p_start = parent.index(marker)
p_end = parent.index(end_token, p_start)
restore = parent[p_start:p_end]

c_end = app.index(end_token)

for token in [
    "const FICHEIRO_CAMPOS = {",
    "async function uploadDataURL(dataUrl, pasta)",
    "function registarHistoricoLicenca("
]:
    if app.count(token) != 0:
        raise SystemExit(f'{token} já existe no estado atual: {app.count(token)}')
    if restore.count(token) != 1:
        raise SystemExit(f'{token} não foi encontrado exatamente uma vez no bloco a restaurar')

if app.count('window.TotalGestLoadOrchestrator.run({') != 1:
    raise SystemExit('A nova orquestração de carregarDados não está intacta')

app = app[:c_end] + restore + app[c_end:]

for token in [
    'async function carregarDados(',
    'window.TotalGestLoadOrchestrator.run({',
    'const FICHEIRO_CAMPOS = {',
    'async function uploadDataURL(dataUrl, pasta)',
    'function registarHistoricoLicenca(',
    'function registarAuditoria('
]:
    if app.count(token) != 1:
        raise SystemExit(f'Invariante falhou para {token}: {app.count(token)}')

APP.write_text(app, encoding='utf-8')
