"""Build the pinned Homelable standalone editor from a disposable checkout."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
REVISION = '0c0418f2588dd34922354603dc11066f9129fb5b'


def edit(path, before, after):
    source = path.read_text(encoding='utf-8')
    if source.count(before) != 1:
        raise ValueError(f'Expected one upstream anchor in {path}')
    path.write_text(source.replace(before, after), encoding='utf-8')


def license_notices(frontend):
    packages = json.loads((frontend / 'package-lock.json').read_text(encoding='utf-8'))['packages']
    notices = []
    for package, metadata in packages.items():
        if not package.startswith('node_modules/') or metadata.get('dev'):
            continue
        folder = frontend / package
        if not folder.is_dir():
            continue
        for file in sorted(folder.iterdir()):
            if file.is_file() and file.name.upper().startswith(('LICENSE', 'COPYING', 'NOTICE', 'OFL')):
                text = file.read_text(encoding='utf-8', errors='replace')
                notices.append(f"{package.removeprefix('node_modules/')} {metadata['version']} · {file.name}\n\n{text.strip()}")
    return '\n\n' + ('\n\n' + '-' * 72 + '\n\n').join(notices) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('checkout', type=Path, help='Clean, disposable checkout of Homelable v3.8.0')
    parser.add_argument('--evaluator', type=Path, help='Optional local evaluator repository')
    args = parser.parse_args()
    checkout = args.checkout.resolve()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=checkout, text=True).strip()
    if revision != REVISION:
        parser.error(f'Expected upstream revision {REVISION}, got {revision}')
    dirty = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=checkout, text=True)
    if dirty:
        parser.error('Use a clean disposable upstream checkout')

    frontend = checkout / 'frontend'
    storage = frontend / 'src/utils/standaloneStorage.ts'
    shutil.copy2(HERE / 'faran-designs.ts', storage.parent / 'faranDesigns.ts')
    shutil.copy2(HERE / 'university-designs.ts', storage.parent / 'universityDesigns.ts')
    shutil.copy2(HERE / 'institution-designs.ts', storage.parent / 'institutionDesigns.ts')
    shutil.copy2(HERE / 'CampusNav.tsx', storage.parent / 'CampusNav.tsx')
    roster = json.loads((PROJECT / 'infra/workflow/data/semester/roster.json').read_text(encoding='utf-8'))
    placement = {entry['id']: entry for entry in roster['staff']}
    assert len(roster['staff']) == len(placement) == 2000
    assert len(roster['students']) == len({entry['id'] for entry in roster['students']}) == 100
    assert all(entry['instructor'] in placement for entry in roster['students'])
    safe_roster = {
        'majors': roster['majors'],
        'staff': [{key: person[key] for key in ('id', 'role', 'manager', 'major')} for person in roster['staff']],
        'students': [{key: person[key] for key in ('id', 'major', 'group', 'instructor')} for person in roster['students']],
    }
    (storage.parent / 'universityRoster.json').write_text(json.dumps(safe_roster, ensure_ascii=False), encoding='utf-8')
    edit(storage, "import { FURNITURE_TYPES } from '@/utils/nodeTypeGroups'",
         "import { FURNITURE_TYPES } from '@/utils/nodeTypeGroups'\nimport { faranDesigns, universityDesigns } from './faranDesigns'")
    for key in ('homelable_designs', 'homelable_canvas', 'homelable_rack'):
        edit(storage, f"= '{key}'", f"= 'faran_{key}'")
    start = '  const design: Design = {\n    id: generateUUID(),\n    name: \'My Homelab\','
    source = storage.read_text(encoding='utf-8')
    offset = source.index(start)
    end = source.index('\n}\n\nexport function createDesign', offset)
    replacement = '''  const timestamp = nowIso()
  const seeds = [...faranDesigns, ...universityDesigns]
  const designs: Design[] = seeds.map(({ id, name }) => ({
    id, name, design_type: 'network', icon: null, created_at: timestamp, updated_at: timestamp,
  }))
  writeDesigns(designs)
  return designs'''
    storage.write_text(source[:offset] + replacement + source[end:], encoding='utf-8')
    edit(storage, '  if (existing.length > 0) return existing',
         '''  const marker = 'faran_homelable_university_v2'
  if (localStorage.getItem(marker) && existing.length) return existing
  if (existing.length) {
    const knownIds = new Set(existing.map(design => design.id))
    const timestamp = nowIso()
    const missing: Design[] = universityDesigns.filter(({ id }) => !knownIds.has(id)).map(({ id, name }) => ({
      id, name, design_type: 'network', icon: null, created_at: timestamp, updated_at: timestamp,
    }))
    const updated = [...existing, ...missing]
    writeDesigns(updated)
    localStorage.setItem(marker, '1')
    return updated
  }
  localStorage.setItem(marker, '1')''')
    edit(storage, '  return stored ? hoistFurnitureDescriptions(hydrateDevices(stored)) : null',
         '''  if (stored) return hoistFurnitureDescriptions(hydrateDevices(stored))
  const base = faranDesigns.find(design => design.id === designId)
  if (base) return structuredClone(base)
  return universityDesigns.find(design => design.id === designId)?.getCanvas() ?? null''')
    edit(frontend / 'index.html', '<title>Homelable</title>', '<title>Faran · Homelable</title>')
    app = frontend / 'src/App.tsx'
    edit(app, "import * as standaloneStorage from '@/utils/standaloneStorage'",
         "import * as standaloneStorage from '@/utils/standaloneStorage'\nimport { CampusNav, campusUrl } from '@/utils/CampusNav'\nimport { campusRoutes } from '@/utils/universityDesigns'")
    edit(app, '<WalkthroughInvite />', '{!STANDALONE && <WalkthroughInvite />}')
    edit(app, "withBase(\x60view?design=${encodeURIComponent(activeDesignId)}\x60)\n        : withBase('view')",
         "withBase(\x60view.html?design=${encodeURIComponent(activeDesignId)}\x60)\n        : withBase('view.html')")
    edit(app, '<div className="flex flex-col flex-1 min-w-0">',
         '''<div className="flex flex-col flex-1 min-w-0">
            {STANDALONE && <CampusNav design={activeDesignId} />}''')
    edit(app, '  const handleNodeDoubleClick = useCallback((node: Node<NodeData>) => {',
         '''  useEffect(() => {
    if (!STANDALONE || !activeDesignId) return
    const focus = new URLSearchParams(window.location.search).get('focus')
    if (!focus || !nodes.some(node => node.id === focus)) return
    const url = new URL(window.location.href)
    url.searchParams.delete('focus')
    window.history.replaceState(window.history.state, '', url)
    handleEditNode(focus)
  }, [activeDesignId, nodes, handleEditNode])

  const handleNodeDoubleClick = useCallback((node: Node<NodeData>) => {
    if (STANDALONE && activeDesignId?.startsWith('faran-')) {
      const target = Object.hasOwn(campusRoutes, node.id) && campusRoutes[node.id]
      if (target && target !== activeDesignId) {
        window.location.href = campusUrl(target)
        return
      }
    }''')
    edit(app, '  }, [handleEditNode])\n\n  const handleEdgeUpdate', '  }, [activeDesignId, handleEditNode])\n\n  const handleEdgeUpdate')
    edit(app, '<CanvasContainer\n                    onConnect=', '<CanvasContainer\n                    campusLayout={STANDALONE && !!activeDesignId?.startsWith(\'faran-\') && activeDesignId !== \'faran-infrastructure\'}\n                    onConnect=')
    canvas = frontend / 'src/components/canvas/CanvasContainer.tsx'
    edit(canvas, '  useReactFlow,\n', '  useReactFlow,\n  useNodesInitialized,\n')
    edit(canvas, 'interface CanvasContainerProps {', 'interface CanvasContainerProps {\n  campusLayout?: boolean')
    edit(canvas, 'function CanvasContainer({ onConnect:', 'function CanvasContainer({ campusLayout = false, onConnect:')
    edit(canvas, '  // React Flow reads defaultViewport', '  const nodesInitialized = useNodesInitialized()\n\n  // React Flow reads defaultViewport')
    edit(canvas, 'if (!fitViewPending || nodes.length === 0) return',
         'if (!fitViewPending || nodes.length === 0 || (campusLayout && !nodesInitialized)) return')
    edit(canvas, '[fitViewPending, nodes.length, fitView, getViewport, setSavedViewport, clearFitViewPending]',
         '[fitViewPending, nodes.length, fitView, getViewport, setSavedViewport, clearFitViewPending, campusLayout, nodesInitialized]')
    edit(canvas, 'minZoom={0.25}', 'minZoom={campusLayout ? 0.1 : 0.25}')
    edit(frontend / 'src/utils/basePath.ts', "return pathname === withBase('view', base)",
         "return pathname === withBase('view', base) || pathname === withBase('view.html', base)")

    npm = shutil.which('npm.cmd') or shutil.which('npm')
    if not npm:
        parser.error('npm is required')
    if not (frontend / 'node_modules/typescript/bin/tsc').exists():
        subprocess.run([npm, 'ci', '--ignore-scripts', '--no-audit', '--no-fund'], cwd=frontend, check=True)
    env = {**os.environ, 'VITE_STANDALONE': 'true', 'VITE_BASE_PATH': '/topology/'}
    subprocess.run([npm, 'run', 'build'], cwd=frontend, env=env, check=True)

    dist = frontend / 'dist'
    edit(dist / 'index.html', '</head>', '  <link rel="stylesheet" href="/topology/campus-brand.css">\n  </head>')
    edit(dist / 'index.html', '</head>', '<style>#root>.h-screen{height:calc(100dvh - 2rem)}html,body{margin:0}</style></head>')
    edit(dist / 'index.html', '</body>', '<footer class="publisher-credit" dir="ltr" style="box-sizing:border-box;height:2rem;line-height:2rem;text-align:center;font-size:.8rem;background:var(--background,#fff);color:var(--foreground,#17343e);border-top:1px solid #829098"><bdi lang="en" dir="ltr">Powered by</bdi> <a href="https://github.com/maddixmhn" rel="me" style="color:inherit;text-decoration:underline"><bdi dir="rtl">محمد مهرانی</bdi></a></footer>\n  </body>')
    shutil.copy2(dist / 'index.html', dist / 'view.html')
    for asset in ('term-review.html', 'term-review.mjs', 'campus-brand.css', 'campus-sources.html'):
        shutil.copy2(HERE / asset, dist / asset)
    shutil.copytree(HERE / 'brand', dist / 'brand', dirs_exist_ok=True)
    shutil.copy2(checkout / 'LICENSE', dist / 'LICENSE.txt')
    (dist / 'THIRD-PARTY-NOTICES.txt').write_text(license_notices(frontend), encoding='utf-8')
    for project in (PROJECT, args.evaluator):
        if project is not None:
            target = project / 'topology'
            if target.exists() and (target / 'LICENSE.txt').is_file():
                before = {item.name for item in (target / 'assets').iterdir() if item.is_file()}
                after = {item.name for item in (dist / 'assets').iterdir() if item.is_file()}
                for obsolete in before - after:
                    (target / 'assets' / obsolete).unlink()
            shutil.copytree(dist, target, dirs_exist_ok=True)


if __name__ == '__main__':
    main()
