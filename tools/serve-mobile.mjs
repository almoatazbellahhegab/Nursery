/** Serve only a compiled Flutter web build for local device review. No API/data. */
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../apps/mobile/build/web');
const types = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.wasm': 'application/wasm', '.png': 'image/png', '.svg': 'image/svg+xml', '.ico': 'image/x-icon', '.ttf': 'font/ttf', '.otf': 'font/otf', '.woff': 'font/woff', '.woff2': 'font/woff2', '.css': 'text/css' };

export function createMobileServer() {
  return http.createServer(async (request, response) => {
    try {
      if (!['GET', 'HEAD'].includes(request.method)) { response.writeHead(405); response.end(); return; }
      const pathname = decodeURIComponent(new URL(request.url, 'http://local').pathname);
      if (pathname.includes('\\') || pathname.includes('\0')) { response.writeHead(400); response.end(); return; }
      const relative = pathname === '/' ? 'index.html' : pathname.replace(/^\/+/, '');
      const file = path.resolve(root, relative);
      if (!file.startsWith(root + path.sep) || relative.split('/').some(part => part.startsWith('.'))) {
        response.writeHead(404); response.end(); return;
      }
      let data;
      try { data = await fs.readFile(file); }
      catch (error) {
        if (error.code === 'ENOENT') { response.writeHead(404); response.end(); return; }
        throw error;
      }
      response.writeHead(200, {
        'Content-Type': types[path.extname(file)] ?? 'application/octet-stream',
        'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'no-referrer',
        'Cache-Control': 'no-store', 'Content-Length': data.length,
      });
      response.end(request.method === 'HEAD' ? undefined : data);
    } catch { response.writeHead(500); response.end('Mobile build unavailable'); }
  });
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  await fs.access(path.join(root, 'index.html'));
  const server = createMobileServer();
  server.on('error', error => { console.error(error.message); process.exitCode = 1; });
  const port = Number(process.env.NURSERY_MOBILE_PORT ?? 3200);
  server.listen(port, '0.0.0.0', () => console.log(`Flutter web application: http://localhost:${port}`));
}
