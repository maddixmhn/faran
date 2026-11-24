// Loaded only in the Android bundle.
function saveOnAndroid(blob, name) {
  const plugin = window.Capacitor?.Plugins?.StudyDocuments;
  if (!plugin) return false;
  const reader = new FileReader();
  reader.onload = () => {
    const data = String(reader.result).split(',', 2)[1];
    plugin.save({ name, type: blob.type.split(';')[0], data })
      .catch(() => alert('ذخیرهٔ فایل انجام نشد.'));
  };
  reader.onerror = () => alert('خواندن فایل انجام نشد.');
  reader.readAsDataURL(blob);
  return true;
}
window.saveOnAndroid = saveOnAndroid;

window.addEventListener('DOMContentLoaded', () => {
  const plugin = window.Capacitor?.Plugins?.StudyDocuments;
  if (!plugin) return;
  window.print = () => plugin.printPage().catch(() => alert('گفت‌وگوی چاپ باز نشد.'));
  document.addEventListener('click', event => {
    const anchor = event.target.closest('a[href]');
    if (!anchor || event.defaultPrevented) return;
    const url = new URL(anchor.href);
    if (url.origin !== location.origin || !/\.(pdf|json|csv)$/i.test(url.pathname)
        || (!anchor.hasAttribute('download') && !url.pathname.endsWith('.pdf'))) return;
    event.preventDefault();
    fetch(url).then(response => {
      if (!response.ok) throw Error('Unavailable');
      const mime = url.pathname.endsWith('.pdf') ? 'application/pdf'
        : url.pathname.endsWith('.csv') ? 'text/csv' : 'application/json';
      return response.arrayBuffer().then(data => new Blob([data], { type: mime }));
    }).then(blob => saveOnAndroid(blob, url.pathname.split('/').pop()))
      .catch(() => alert('فایل در دسترس نیست.'));
  });
});
