import json, os, time
from pathlib import Path
from urllib.request import urlopen
last=None
for attempt in range(30):
    try:
        with urlopen('http://127.0.0.1:3000/health', timeout=5) as response:
            health=json.load(response)
        assert health['commit']==os.environ['GITHUB_SHA']
        assert health['status']=='ok'
        with urlopen('http://127.0.0.1:3000/', timeout=5) as response:
            assert 'Portal de pedidos B2B' in response.read().decode()
        Path('evidence/validation/container-smoke.json').write_text(json.dumps(health, indent=2))
        print('PASS: imagem local identifica o commit da execução')
        break
    except Exception as error:
        last=error
        time.sleep(2)
else:
    raise RuntimeError('Smoke do container falhou') from last
