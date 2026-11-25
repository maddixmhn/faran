const archive = require('../docs/seminar-results.json');
const trace = require('../docs/registration-trace.json');

function snapshot() {
  const { stages } = trace;
  if (trace.verified !== true || stages.length !== 3) throw new Error('Trace is not verified');
  const n8n = stages.find(stage => stage.name === 'n8n');
  if (!n8n) throw new Error('Missing n8n stage');
  const start = stages[0].submitted;
  const elapsed = stages.at(-1).ended - start;
  const wait = n8n.started - n8n.submitted;
  if (!Number.isSafeInteger(elapsed) || elapsed <= 0 || !Number.isSafeInteger(wait) || wait < 0 || wait > elapsed) {
    throw new Error('Invalid timing evidence');
  }
  const verified = archive.roster.filter(row => row.receipt_matches === true && row.membership_verified === true).length;
  const occupancy = archive.race?.verified === true ? archive.race.occupancy : null;
  return {
    schema: 'project-status/v1', scope: 'archived-synthetic',
    recordedAt: new Date(start).toISOString(), run: String(trace.n8n_execution),
    metrics: [
      { label: 'پروندهٔ ساختگی تأییدشده', value: verified, unit: 'count' },
      { label: 'اشغال مقصد در آزمون آخرین صندلی', value: occupancy, unit: 'count' },
      { label: 'زمان کل ثبت‌نام', value: elapsed / 1000, unit: 'seconds' },
      { label: 'تحویل تا شروع n8n', value: wait / 1000, unit: 'seconds' },
    ],
    source: '/docs/registration-trace.json',
  };
}

function visit(req, res) {
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'public, max-age=0, s-maxage=300');
  if (!['GET', 'HEAD'].includes(req.method)) {
    res.setHeader('Allow', 'GET, HEAD');
    res.statusCode = 405;
    res.end(JSON.stringify({ error: 'method-not-allowed' }));
    return;
  }
  try {
    const data = snapshot();
    res.end(req.method === 'HEAD' ? undefined : JSON.stringify(data));
  } catch {
    res.setHeader('Cache-Control', 'no-store');
    res.statusCode = 503;
    res.end(req.method === 'HEAD' ? undefined : JSON.stringify({ error: 'evidence-unavailable' }));
  }
}

module.exports = visit;
module.exports.snapshot = snapshot;
module.exports.evidence = ["registration-trace.json", "seminar-results.json"];
