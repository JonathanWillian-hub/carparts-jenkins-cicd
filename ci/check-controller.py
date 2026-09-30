"""Verificação de controller EFÊMERO: não executa builds no nó interno nem deploy Azure."""
import base64, http.cookiejar, json, time
from pathlib import Path
from urllib.request import Request, build_opener, HTTPCookieProcessor, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode
BASE='http://127.0.0.1:8080'
password=Path('secrets/admin_password').read_text().strip()
authorization='Basic '+base64.b64encode(('admin:'+password).encode()).decode()
opener=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
def request(path, data=None, crumb=None):
    headers={'Authorization':authorization}
    if crumb: headers[crumb['crumbRequestField']]=crumb['crumb']
    if data is not None: headers['Content-Type']='application/x-www-form-urlencoded'
    return opener.open(Request(BASE+path, data=data, headers=headers), timeout=15)
for attempt in range(90):
    try:
        with request('/computer/api/json') as response: computers=json.load(response)['computer']
        break
    except Exception:
        time.sleep(5)
else:
    raise RuntimeError('Controller não respondeu com autenticação em 450 segundos; inspecionar privadamente logs da instalação')
try:
    urlopen(BASE+'/api/json', timeout=10)
except HTTPError as error:
    assert error.code in (401,403), 'Status inesperado para acesso anônimo'
else:
    raise AssertionError('Acesso anônimo indevidamente liberado')
builtin=[node for node in computers if node['displayName'] not in ('ubuntu-ci','ubuntu-release')]
assert len(builtin)==1 and builtin[0]['numExecutors']==0
nodes={node['displayName']:node['numExecutors'] for node in computers}
assert nodes['ubuntu-ci']==2 and nodes['ubuntu-release']==1
with request('/crumbIssuer/api/json') as response: crumb=json.load(response)
proof={'controllerStarted':True, 'anonymousReadBlocked':True, 'nodes':nodes, 'pipelineValidation':{}}
for file in ('Jenkinsfile','Jenkinsfile.ci'):
    payload=urlencode({'jenkinsfile':Path(file).read_text()}).encode()
    with request('/pipeline-model-converter/validate', payload, crumb) as response:
        result=response.read().decode()
    print(file+': '+result.strip())
    assert 'Jenkinsfile successfully validated.' in result
    proof['pipelineValidation'][file]=result.strip()
Path('evidence/validation').mkdir(parents=True,exist_ok=True)
Path('evidence/validation/controller-check.json').write_text(json.dumps(proof,indent=2))
print('PASS: controller iniciou, anônimo bloqueado, zero executores internos, agents configurados e pipelines sintaticamente válidas')
