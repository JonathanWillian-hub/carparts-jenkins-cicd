import assert from 'node:assert/strict';
const [base, commit] = process.argv.slice(2);
if (!base || !commit || !base.startsWith('https://')) throw new Error('Informe URL HTTPS e commit esperado');
let last;
for (let attempt = 1; attempt <= 30; attempt++) {
  try {
    const r = await fetch(base + '/health', {signal: AbortSignal.timeout(10000)});
    assert.equal(r.status, 200);
    const data = await r.json(); assert.equal(data.status, 'ok'); assert.equal(data.commit, commit);
    const parts = await fetch(base + '/api/parts', {signal: AbortSignal.timeout(10000)});
    assert.equal(parts.status, 200); assert.ok((await parts.json()).length > 0);
    const page = await fetch(base, {signal: AbortSignal.timeout(10000)});
    assert.equal(page.status, 200); assert.match(await page.text(), /Portal de pedidos B2B/);
    console.log(JSON.stringify({event: 'smoke_pass', url: base, commit, timestamp: new Date().toISOString()}));
    process.exit(0);
  } catch (e) { last = e; await new Promise(resolve => setTimeout(resolve, 5000)); }
}
throw new Error('Smoke não passou após 30 tentativas: ' + last.message);
