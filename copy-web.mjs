import { cp, mkdir, rm } from 'node:fs/promises';
const web = new URL('./www/', import.meta.url);
await rm(web, { recursive: true, force: true });
await mkdir(web, { recursive: true });
for (const item of ['index.html', 'site.css', 'app.js', 'sw.js', 'manifest.webmanifest', 'icon.svg', 'docs']) {
  await cp(new URL(`./${item}`, import.meta.url), new URL(`./www/${item}`, import.meta.url), { recursive: true });
}
console.log('Faran web assets copied to www/');
