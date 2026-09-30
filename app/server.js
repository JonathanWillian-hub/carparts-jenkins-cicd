import http from 'node:http';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
const page = readFileSync(fileURLToPath(new URL('./public/index.html', import.meta.url)));
export function createServer() {
  return http.createServer((req, res) => {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('Content-Security-Policy', "default-src 'self'; style-src 'self' 'unsafe-inline'");
    if (req.method !== 'GET') {
      res.writeHead(405, {'Content-Type': 'application/json', Allow: 'GET'});
      return res.end(JSON.stringify({error: 'Método não permitido'}));
    }
    if (req.url === '/') {
      res.writeHead(200, {'Content-Type': 'text/html; charset=utf-8'});
      return res.end(page);
    }
    if (req.url === '/health' || req.url === '/api/version') {
      res.writeHead(200, {'Content-Type': 'application/json', 'Cache-Control': 'no-store'});
      return res.end(JSON.stringify({status: 'ok', service: 'carparts-b2b', commit: process.env.GIT_COMMIT || 'local'}));
    }
    if (req.url === '/api/parts') {
      res.writeHead(200, {'Content-Type': 'application/json'});
      return res.end(JSON.stringify([{id: 'CP-001', name: 'Filtro de óleo', stock: 120}, {id: 'CP-002', name: 'Pastilha de freio', stock: 80}]));
    }
    res.writeHead(404, {'Content-Type': 'application/json'});
    res.end(JSON.stringify({error: 'Não encontrado'}));
  });
}
if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const server = createServer();
  server.listen(Number(process.env.PORT || 3000), '0.0.0.0', () => console.log('Carparts disponível na porta ' + (process.env.PORT || 3000)));
  for (const signal of ['SIGTERM', 'SIGINT']) process.on(signal, () => server.close(() => process.exit(0)));
}
