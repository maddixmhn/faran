import http from 'node:http';

const company = '15af0af3-1b60-4bbb-8dc3-f969c2206ea4';
const api = 'http://host.docker.internal:3100/api/companies/' + company;

http.createServer(async (request, response) => {
  response.setHeader('Cache-Control', 'no-store');
  response.setHeader('Content-Type', 'application/json');
  if (request.url !== '/api/runtime-summary' || request.method !== 'GET') {
    response.writeHead(404).end('{}');
    return;
  }
  try {
    const upstream = await fetch(api + '/heartbeat-runs?summary=true&limit=100', {
      signal: AbortSignal.timeout(6000),
      redirect: 'error',
    });
    if (!upstream.ok) throw new Error('Paperclip unavailable');
    const runs = await upstream.json();
    if (!Array.isArray(runs)) throw new Error('Unexpected history format');
    const statuses = new Map([['succeeded', 'completed'], ['completed', 'completed'], ['failed', 'failed'], ['timed_out', 'failed'], ['cancelled', 'cancelled'], ['canceled', 'cancelled']]);
    const events = [];
    for (const run of runs.slice(0, 100)) {
      const status = statuses.get(run?.status);
      const end = Date.parse(run?.finishedAt ?? run?.endedAt);
      const start = Date.parse(run?.startedAt);
      const ids = [run?.id, run?.agentId, run?.issueId ?? run?.contextSnapshot?.issueId];
      if (!status || !Number.isFinite(end) || !ids.every(id => typeof id === 'string' && /^[a-zA-Z0-9_-]{1,100}$/.test(id))) continue;
      events.push({
        event_id: 'paperclip:' + ids[0], agent_id: ids[1], task_id: ids[2],
        occurred_at: new Date(end).toISOString(), status, synthetic: false,
        duration_ms: Number.isFinite(start) && start <= end ? end - start : null,
        evidence_refs: ['paperclip-run:' + ids[0]], policy_version: null,
      });
    }
    response.end(JSON.stringify({ contract: 'faran-event-schema/1.0', observedAt: new Date().toISOString(), recentRuns: runs.length, limit: 100, events }));
  } catch {
    response.writeHead(503).end('{"status":"unavailable"}');
  }
}).listen(8080, '0.0.0.0');
