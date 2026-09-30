import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from '../server.js';
let server, base;
before(async () => {
  server = createServer();
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  base = 'http://127.0.0.1:' + server.address().port;
});
after(async () => { await new Promise(resolve => server.close(resolve)); });
test('health responde 200 e identifica serviço', async () => {
  const r = await fetch(base + '/health'); assert.equal(r.status, 200);
  const data = await r.json(); assert.equal(data.status, 'ok'); assert.equal(data.service, 'carparts-b2b');
});
test('version expõe o commit sem cache', async () => {
  const r = await fetch(base + '/api/version'); assert.equal(r.headers.get('cache-control'), 'no-store');
  assert.equal((await r.json()).commit, process.env.GIT_COMMIT || 'local');
});
test('catálogo possui IDs distintos e estoque não negativo', async () => {
  const r = await fetch(base + '/api/parts'); assert.equal(r.status, 200);
  const parts = await r.json(); assert.equal(parts.length, 2);
  assert.equal(new Set(parts.map(x => x.id)).size, parts.length);
  assert.ok(parts.every(x => Number.isInteger(x.stock) && x.stock >= 0));
});
test('front-end renderiza portal B2B', async () => {
  const r = await fetch(base); assert.match(r.headers.get('content-type'), /text\/html/);
  assert.match(await r.text(), /Portal de pedidos B2B/);
});
test('rota inexistente retorna 404', async () => {
  const r = await fetch(base + '/inexistente'); assert.equal(r.status, 404);
});
test('método de escrita é recusado', async () => {
  const r = await fetch(base + '/api/parts', {method: 'POST'}); assert.equal(r.status, 405);
  assert.equal(r.headers.get('allow'), 'GET');
});
test('resposta tem cabeçalhos de segurança', async () => {
  const r = await fetch(base); assert.equal(r.headers.get('x-content-type-options'), 'nosniff');
  assert.match(r.headers.get('content-security-policy'), /default-src 'self'/);
});
