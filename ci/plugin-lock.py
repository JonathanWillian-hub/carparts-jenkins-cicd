"""Extrai versões de manifests resolvidos, sem ler Jenkins home/segredos."""
import sys, zipfile
from pathlib import Path
plugins=[]
for path in Path(sys.argv[1]).glob('*.jpi'):
    with zipfile.ZipFile(path) as archive:
        text=archive.read('META-INF/MANIFEST.MF').decode()
    fields={}
    for line in text.splitlines():
        if ': ' in line and not line.startswith(' '):
            key,value=line.split(': ',1);fields[key]=value
    plugins.append(fields['Short-Name']+':'+fields['Plugin-Version'])
if not plugins: raise SystemExit('Nenhum plugin encontrado')
print('\n'.join(sorted(plugins)))
