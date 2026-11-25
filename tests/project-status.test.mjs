import test from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { once } from 'node:events';
import { readFileSync } from 'node:fs';
import handler from '../api/project-status.js';

test('status endpoint serves only the archived snapshot and rejects writes', async t => {
  const server = createServer(handler).listen(0, '127.0.0.1');
  t.after(() => server.close());
  await once(server, 'listening');
  const endpoint = 'http://127.0.0.1:' + server.address().port + '/api/project-status';
  const response = await fetch(endpoint);
  assert.equal(response.status, 200);
  assert.match(response.headers.get('content-type'), /application\/json/);
  const data = await response.json();
  assert.equal(data.schema, 'project-status/v1');
  assert.equal(data.scope, 'archived-synthetic');
  assert.equal(data.run, '20');
  assert.equal(data.metrics.find(item => item.label === 'زمان کل ثبت‌نام').value, 28.633);
  assert.deepEqual(data, JSON.parse(readFileSync(new URL('../docs/project-status.json', import.meta.url), 'utf8')));
  const head = await fetch(endpoint, { method: 'HEAD' });
  assert.equal(head.status, 200);
  assert.equal(await head.text(), '');
  const write = await fetch(endpoint, { method: 'POST' });
  assert.equal(write.status, 405);
  assert.equal(write.headers.get('allow'), 'GET, HEAD');
});
