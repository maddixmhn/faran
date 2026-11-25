// Run with the built upstream frontend directory as the sole argument.
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { resolve } = require('node:path');
const { Module } = require('node:module');

const frontend = resolve(process.argv[2]);
const ts = require(resolve(frontend, 'node_modules/typescript'));
function compile(name, imports = {}) {
  const file = resolve(frontend, 'src/utils', name + '.ts');
  const code = ts.transpileModule(readFileSync(file, 'utf8'), {
    compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.CommonJS, esModuleInterop: true },
  }).outputText;
  const built = new Module(file, module);
  built.filename = file;
  const originalRequire = built.require.bind(built);
  built.require = dependency => Object.hasOwn(imports, dependency) ? imports[dependency] : originalRequire(dependency);
  built._compile(code, file);
  return built.exports;
}

const { universityMaps, memberMaps, campusRoutes } = compile('universityDesigns', {
  './institutionDesigns': compile('institutionDesigns'),
});
const roster = require(resolve(frontend, 'src/utils/universityRoster.json'));
const maps = new Map(universityMaps.map(map => [map.id, map]));
assert.equal(maps.size, universityMaps.length);
assert.equal(Object.keys(memberMaps).length, 2100);
for (const member of [...roster.staff, ...roster.students]) {
  const map = maps.get(memberMaps[member.id]);
  const matches = map.entries.filter(entry => entry[0] === member.id);
  assert.equal(matches.length, 1, member.id);
  if (member.instructor) {
    assert.ok(matches[0][5].includes(member.instructor), member.id);
    assert.ok(map.links.some(([source, target]) =>
      source.endsWith('-group-' + member.group) && target === member.id), member.id);
  }
}
for (const map of maps.values()) {
  const ids = new Set(map.entries.map(entry => entry[0]));
  assert.equal(ids.size, map.entries.length, map.id);
  for (const [from, to] of map.links) assert.ok(ids.has(from) && ids.has(to), map.id);
}
for (const id of ['support', 'bot', 'social']) {
  assert.ok(maps.get(campusRoutes[id]).entries.some(entry => entry[0].startsWith('role-')), id);
}
const overview = maps.get('faran-university');
const official = maps.get('faran-official-structure');
assert.equal(official.entries.length, 30);
assert.equal(official.links.length, 29);
for (const [parent, child] of [
  ['deputy', 'finance-office'], ['deputy', 'research-office'],
  ['technical', 'virtual-portal'], ['academic-office', 'academic-groups'],
  ['academic-head', 'academic-operations'],
]) assert.ok(official.links.some(([from, to]) => from === parent && to === child));
assert.equal(maps.get(campusRoutes['academic-groups']).entries.length, 7);
console.log(JSON.stringify({ agents: roster.staff.length, students: roster.students.length,
  maps: maps.size, overviewNodes: overview.entries.length, overviewEdges: overview.links.length,
  officialNodes: official.entries.length, officialEdges: official.links.length }));
