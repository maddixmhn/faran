import { useState, type FormEvent } from 'react'
import { memberMaps } from './universityDesigns'

export function campusUrl(design: string, focus?: string) {
  const url = new URL(window.location.href)
  url.search = new URLSearchParams({ design }).toString()
  if (focus) url.searchParams.set('focus', focus)
  return url.toString()
}

export function CampusNav({ design }: { design: string | null }) {
  const [error, setError] = useState('')
  function lookup(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const value = String(new FormData(event.currentTarget).get('member') || '').trim().toLowerCase()
    const id = /^(role|student)-\d{3,4}$/.test(value) ? value : ''
    if (!id || !memberMaps[id]) {
      setError('شناسه‌ای مثل role-2000 یا student-100 وارد کنید.')
      return
    }
    window.location.href = campusUrl(memberMaps[id], id)
  }
  return (
    <nav dir="rtl" aria-label="نقشهٔ پروژه" className="campus-nav flex flex-wrap items-center gap-x-4 gap-y-1 border-b px-3 py-2 text-xs">
      <div className="campus-identity">
        <a href="https://faran.ac.ir/" aria-label="سایت مرجع مؤسسهٔ فاران مهر دانش">
          <img src="/topology/brand/faran-reference.webp" width="42" height="42" alt="نشان مؤسسهٔ فاران مهر دانش" />
        </a>
        <div><strong>درگاه دانشگاهی فاران</strong><small>نقشه‌های دانشگاه و پروژهٔ سمینار</small></div>
      </div>
      <a href={campusUrl('faran-official-structure')} className="font-semibold underline">ساختار رسمی فاران</a>
      <a href="/topology/campus-sources.html" className="underline">راهنما و منابع دانشگاه</a>
      <a href={campusUrl('faran-university')} className="underline">آرشیو مدل پژوهشی</a>
      {design?.startsWith('faran-official-') ? (
        <>
          <a href="https://faran.ac.ir/faran-chart/" className="underline">منبع چارت مؤسسه</a>
          <a href="/topology/term-review.html" className="underline">بررسی حذف نیمسال</a>
        </>
      ) : design?.startsWith('faran-') && design !== 'faran-infrastructure' && <span>طرح پیشنهادی · دادهٔ ساختگی</span>}
      {design?.startsWith('faran-') && !design.startsWith('faran-official-') && design !== 'faran-infrastructure' && <form onSubmit={lookup} className="flex flex-wrap items-center gap-2">
        <input name="member" dir="ltr" aria-label="شناسهٔ ایجنت یا دانشجو" placeholder="role-2000 / student-100"
          required maxLength={16} onChange={() => setError('')} className="w-44 rounded border bg-transparent px-2 py-1.5" />
        <button type="submit" className="rounded border px-2 py-1.5">پیدا کن</button>
        {error && <span role="status">{error}</span>}
      </form>}
      <a href="/" className="underline">درگاه دانشگاه</a>
    </nav>
  )
}
