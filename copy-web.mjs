import { cp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
const web = new URL('./www/', import.meta.url);
await rm(web, { recursive: true, force: true });
await mkdir(web, { recursive: true });
const files = ['index.html', 'login.html', 'dashboard.html', 'site.css', 'university.css', 'app.js', 'sw.js', 'manifest.webmanifest', 'icon.svg'];
files.push(
  'docs/AGENT-SKILLS-CATALOG.md',
  'docs/ARTICLE.md',
  'docs/CLOUDFLARE-AND-AGENT-RESEARCH.md',
  'docs/DELIVERY-STATUS.md',
  'docs/LMS-LOCAL.md',
  'docs/PROJECT-PLAN.md',
  'docs/QUICKSTART-FA.md',
  'docs/RESEARCH.md',
  'docs/ROADMAP.md',
  'docs/SEMINAR-MANUSCRIPT.md',
  'docs/WORKFLOW-ARCHITECTURE.md',
  'docs/WORKFLOW-ROADMAP.md',
  'docs/article.html',
  'docs/presentation.html',
  'docs/presentation.css',
  'docs/seminar-presentation.pdf',
  'docs/verified-evaluation-lab.jpg',
  'docs/verified-organization.jpg',
  'docs/homelable-infrastructure.jpg',
  'docs/code-graph.json',
  'docs/docker-desktop.jpg',
  'docs/execution-evidence.json',
  'docs/execution-evidence.png',
  'docs/faculty-home.png',
  'docs/faculty-semester.png',
  'docs/faran-seminar.pdf',
  'docs/n8n-execution-19.jpg',
  'docs/paperclip-console.png',
  'docs/registration-trace.json',
  'docs/semester-web.html',
  'docs/semester-web.json',
  'docs/semester-workflow.svg',
  'docs/seminar-results.json',
  'docs/seminar.html',
  'docs/service-graph.svg'
);
for (const file of files) {
  const target = new URL(file, web);
  await mkdir(new URL('.', target), { recursive: true });
  if (file.endsWith('.html')) {
    const content = await readFile(new URL(file, import.meta.url), 'utf8');
    const adapter = '<script src="/android-documents.js" defer></script>';
    await writeFile(target, content.includes('</body>') ? content.replace('</body>', adapter + '</body>') : content + adapter);
  } else {
    await cp(new URL(file, import.meta.url), target);
  }
}
await cp(new URL('./android-documents.js', import.meta.url), new URL('android-documents.js', web));
await cp(new URL('./university/', import.meta.url), new URL('university/', web), { recursive: true });
await cp(new URL('./topology/', import.meta.url), new URL('topology/', web), { recursive: true });
console.log('Android web assets synced.');
