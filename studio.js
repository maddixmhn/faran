(() => {
  const normalize = value => value.toLowerCase().replace(/ي/g, 'ی').replace(/ك/g, 'ک')
    .replace(/[\u200c\s]+/g, '').replace(/اندروید|آندروید/g, 'android');
  for (const directory of document.querySelectorAll('[data-studio-directory]')) {
    const search = directory.querySelector('[data-studio-search]');
    const field = search.querySelector('input');
    const cards = [...directory.querySelectorAll('[data-studio-tool]')];
    const more = directory.querySelector('[data-studio-more]');
    let wasOpen = false;
    let searching = false;
    field.addEventListener('input', () => {
      const query = normalize(field.value);
      if (query && !searching) wasOpen = more.open;
      if (!query && searching) more.open = wasOpen;
      searching = !!query;
      if (searching) more.open = true;
      for (const card of cards) card.hidden = !normalize(card.textContent).includes(query);
      directory.querySelector('[data-studio-empty]').hidden = cards.some(card => !card.hidden);
    });
    search.hidden = false;
  }

  const sections = document.querySelectorAll('[data-project-status]');
  if (!sections.length) return;

  async function get(url) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 2500);
    try {
      const response = await fetch(url, { signal: controller.signal });
      if (!response.ok) throw new Error('Summary unavailable');
      const data = await response.json();
      if (data.schema !== 'project-status/v1' || data.scope !== 'archived-synthetic' || !Array.isArray(data.metrics)) {
        throw new Error('Invalid public summary');
      }
      return data;
    } finally {
      clearTimeout(timeout);
    }
  }

  function show(data, fallback) {
    const format = new Intl.NumberFormat('fa-IR', { maximumFractionDigits: 3 });
    const percentage = new Intl.NumberFormat('fa-IR', { style: 'percent', maximumFractionDigits: 1 });
    const day = new Intl.DateTimeFormat('fa-IR', { dateStyle: 'medium', timeZone: 'Asia/Tehran' });
    for (const section of sections) {
      const list = section.querySelector('[data-studio-metrics]');
      list.replaceChildren();
      for (const item of data.metrics) {
        const box = document.createElement('div');
        const title = document.createElement('dt');
        const value = document.createElement('dd');
        title.textContent = item.label;
        value.textContent = !Number.isFinite(item.value) ? '—' : item.unit === 'ratio'
          ? percentage.format(item.value) : format.format(item.value) + (item.unit === 'seconds' ? ' ثانیه' : '');
        box.append(title, value);
        list.append(box);
      }
      list.hidden = false;
      section.dataset.evidenceSource = fallback ? 'snapshot' : 'api';
      section.querySelector('[data-studio-message]').textContent =
        'آزمایش محلی با دادهٔ ساختگی · ثبت‌نام شمارهٔ ' + format.format(Number(data.run))
        + ' · ' + day.format(new Date(data.recordedAt))
        + (fallback ? ' · نسخهٔ پشتیبان' : '');
    }
  }

  get('/api/project-status').then(data => show(data, false))
    .catch(() => get('/docs/project-status.json').then(data => show(data, true)))
    .catch(() => {
      for (const section of sections) {
        section.querySelector('[data-studio-message]').textContent =
          'خلاصه در دسترس نیست. رد خام در پیوند زیر موجود است.';
      }
    });
})();
