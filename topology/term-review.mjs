export const sourceUrl = 'https://faran.ac.ir/?page_id=3489';

function time(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(value)) return null;
  const timestamp = Date.parse(value + ':00Z');
  if (!Number.isFinite(timestamp) || new Date(timestamp).toISOString().slice(0, 16) !== value) return null;
  return timestamp;
}

export function reviewTermWithdrawal({ written, requestAt, examsAt, council, decisionAt, reference }) {
  const requested = time(requestAt);
  const exams = time(examsAt);
  if (!written) return { code: 'missing-written', text: 'درخواست کتبی در پرونده ثبت نشده است.' };
  if (requested === null || exams === null) {
    return { code: 'missing-dates', text: 'زمان دریافت درخواست و زمان شروع امتحانات را از پرونده وارد کنید.' };
  }
  if (requested >= exams) {
    return { code: 'late-request', text: 'زمان دریافت درخواست پیش از شروع امتحانات نیست. پرونده برای بررسی استثنا به واحد آموزش ارجاع می‌شود.' };
  }
  if (council !== 'approved' && council !== 'rejected') {
    return { code: 'pending-council', text: 'درخواست کتبی پیش از شروع امتحانات ثبت شده و در انتظار تصمیم شورای آموزشی است.' };
  }
  const decision = time(decisionAt);
  if (decision === null || decision < requested || !String(reference ?? '').trim()) {
    return { code: 'missing-decision', text: 'شمارهٔ مصوبه و زمان معتبر تصمیم شورا برای ثبت نتیجه لازم است.' };
  }
  if (council === 'rejected') {
    return { code: 'rejected', text: 'رد درخواست با شاهد تصمیم شورا در پرونده ثبت شده است.' };
  }
  if (decision >= exams) {
    return { code: 'late-decision', text: 'تصمیم شورا پس از شروع امتحانات یا هم‌زمان با آن ثبت شده است. تاریخ اثر تصمیم را از آموزش استعلام کنید.' };
  }
  return { code: 'documented-approval', text: 'طبق دادهٔ واردشده، شرایط مستند و تأیید شورا موجود است. راهنمای فاران حذف را با احتساب در سنوات توصیف می‌کند.' };
}
