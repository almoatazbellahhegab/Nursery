/** Local synthetic review host. It exposes no production API or child records. */
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';
import { randomUUID } from 'node:crypto';
import { execFile } from 'node:child_process';

export const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const publicFiles = new Map([
  ['/', ['index.html', 'text/html']], ['/dashboard', ['dashboard.html', 'text/html']],
  ['/mobile', ['mobile.html', 'text/html']], ['/style.css', ['style.css', 'text/css']],
  ['/review.mjs', ['review.mjs', 'text/javascript']], ['/preview.mjs', ['preview.mjs', 'text/javascript']],
  ['/messages.json', ['messages.json', 'application/json']],
]);
const caseIds = ['UAT-S01-01', 'UAT-S01-02', 'UAT-S01-03', 'UAT-S01-04', 'UAT-S01-05', 'UAT-S01-06'];
const devices = ['Windows 11 browser', 'Physical iPhone Safari', 'Emulated mobile browser', 'Native iPhone app'];
const results = ['Pass', 'Fail', 'Blocked'];
const headers = {
  'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
  'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'no-referrer', 'Cache-Control': 'no-store',
};

/** Validate review evidence. Passing a preview never constitutes sprint approval. */
export function validateResult(value) {
  if (!value || !caseIds.includes(value.caseId) || !devices.includes(value.device) || !results.includes(value.result)) return false;
  if (typeof value.note !== 'string' || value.note.length > 1000) return false;
  // No native application exists yet. Do not permit a misleading pass record.
  return value.device !== 'Native iPhone app' || value.result === 'Blocked';
}

/** Create an isolated host; tests can provide a temporary evidence directory. */
export function createReviewServer({ evidenceDirectory = path.join(root, 'review-results') } = {}) {
  return http.createServer(async (req, res) => {
    const send = (status, body, type = 'application/json') => {
      res.writeHead(status, { ...headers, 'Content-Type': `${type}; charset=utf-8` });
      res.end(typeof body === 'string' ? body : JSON.stringify(body));
    };
    try {
      const url = new URL(req.url ?? '/', 'http://local');
      if (req.method === 'GET' && url.pathname === '/review/plan') {
        send(200, await fs.readFile(path.join(root, 'docs/delivery/plan.json'), 'utf8')); return;
      }
      if (req.method === 'GET' && url.pathname === '/review/results') {
        let text = '';
        try { text = await fs.readFile(path.join(evidenceDirectory, 'uat.jsonl'), 'utf8'); }
        catch (error) { if (error.code !== 'ENOENT') throw error; }
        send(200, text.trim() ? text.trim().split('\n').map(line => JSON.parse(line)) : []); return;
      }
      if (req.method === 'POST' && url.pathname === '/review/uat') {
        // Reject cross-origin writes, including forms and cross-site fetches.
        if (req.headers.origin !== `http://${req.headers.host}` || !req.headers['content-type']?.startsWith('application/json')) {
          send(403, { code: 'REVIEW_ORIGIN_DENIED' }); return;
        }
        let body = '';
        for await (const part of req) { body += part; if (Buffer.byteLength(body) > 8192) { send(413, { code: 'REVIEW_TOO_LARGE' }); return; } }
        let value;
        try { value = JSON.parse(body); } catch { send(400, { code: 'REVIEW_INVALID_JSON' }); return; }
        if (!validateResult(value)) { send(422, { code: 'REVIEW_INVALID_RESULT' }); return; }
        const record = { id: randomUUID(), recordedAt: new Date().toISOString(), sprint: 'S01', caseId: value.caseId, device: value.device, result: value.result, note: value.note };
        await fs.mkdir(evidenceDirectory, { recursive: true });
        await fs.appendFile(path.join(evidenceDirectory, 'uat.jsonl'), JSON.stringify(record) + '\n');
        send(201, record); return;
      }
      const file = publicFiles.get(url.pathname);
      if (req.method !== 'GET' || !file) { send(404, { code: 'REVIEW_NOT_FOUND' }); return; }
      send(200, await fs.readFile(path.join(root, 'tools/review', file[0]), 'utf8'), file[1]);
    } catch (error) {
      console.error('review_request_failed', error.code ?? 'unexpected');
      send(500, { code: 'REVIEW_UNAVAILABLE' });
    }
  });
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const port = Number(process.env.PORT ?? 3100);
  const server = createReviewServer();
  server.on('error', error => { console.error(error.code === 'EADDRINUSE' ? `Port ${port} is in use. Close the other review server or choose PORT.` : error.message); process.exitCode = 1; });
  server.listen(port, '0.0.0.0', () => {
    console.log(`Nursery review: http://localhost:${port}`);
    for (const entries of Object.values(os.networkInterfaces())) for (const address of entries ?? []) {
      if (address.family === 'IPv4' && !address.internal) console.log(`iPhone on the same Wi-Fi: http://${address.address}:${port}`);
    }
    console.log('Synthetic local review only. Keep this terminal open. Ctrl+C stops it.');
    if (process.platform === 'win32' && process.argv.includes('--open')) {
      execFile('explorer.exe', [`http://localhost:${port}`], error => {
        if (error) console.log(`Open http://localhost:${port} in your browser.`);
      });
    }
  });
}
