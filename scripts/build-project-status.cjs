/** Refresh the local snapshot and optionally supply the same endpoint to a prebuilt Vercel output. */
const { readFileSync, writeFileSync, mkdirSync, copyFileSync } = require('node:fs');
const { join, resolve } = require('node:path');
const root = resolve(__dirname, '..');
const { snapshot: buildSnapshot, evidence } = require('../api/project-status.js');
const snapshot = buildSnapshot();
const json = JSON.stringify(snapshot, null, 2) + '\n';
writeFileSync(join(root, 'docs/project-status.json'), json);
if (process.argv[2]) {
  const output = resolve(process.argv[2]);
  const config = JSON.parse(readFileSync(join(output, 'config.json'), 'utf8'));
  if (config.version !== 3) throw Error('Expected an existing Vercel output v3');
  const func = join(output, 'functions/api/project-status.func');
  mkdirSync(join(func, 'api'), { recursive: true });
  mkdirSync(join(func, 'docs'), { recursive: true });
  copyFileSync(join(root, 'api/project-status.js'), join(func, 'api/project-status.js'));
  for (const path of evidence) copyFileSync(join(root, 'docs', path), join(func, 'docs', path));
  writeFileSync(join(func, '.vc-config.json'), JSON.stringify({
    runtime: 'nodejs22.x', handler: 'api/project-status.js', launcherType: 'Nodejs',
  }));
  writeFileSync(join(output, 'static/docs/project-status.json'), json);
}
