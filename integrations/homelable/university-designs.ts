import type { NodeType } from '@/types'
import roster from './universityRoster.json'
import { institutionMaps, institutionRoutes } from './institutionDesigns'

type Entry = [id: string, name: string, type: NodeType, x: number, y: number, notes: string]
type Connection = [from: string, to: string, label: string]
type CampusMap = { id: string; name: string; entries: Entry[]; links: Connection[] }

const count = new Intl.NumberFormat('fa-IR')
const campus: CampusMap = { id: 'faran-university', name: 'دانشگاه ایجنتیک فاران', entries: [], links: [] }
const maps: CampusMap[] = [campus]
export const memberMaps: Record<string, string> = {}
export const campusRoutes: Record<string, string> = { ...institutionRoutes }

const divisions = [
  { key: 'ceo', label: 'مدیریت ارشد', x: 900, teams: [] },
  { key: 'pm', label: 'معاونت آموزش و خدمات دانشگاهی', x: 50, teams: [
    ['admission', 'پذیرش و پرونده', 'راستی‌آزمایی مدارک، رفع نقص و پذیرش ورودی'],
    ['enrollment', 'انتخاب واحد و ظرفیت', 'کنترل پیش‌نیاز، حذف و اضافه و رقابت برای آخرین صندلی'],
    ['calendar', 'تقویم و برنامه‌ریزی کلاس', 'ساخت گروه، کنترل تداخل و اطلاع‌رسانی تغییر ساعت'],
    ['exam', 'امتحانات و نمرات', 'کارت آزمون، هماهنگی مراقبت، رسید نمره و اعتراض'],
    ['graduation', 'دانش‌آموختگی و کارنامه', 'بررسی واحدها، تعلیق در اعتراض باز و صدور پروندهٔ نهایی'],
    ['advising', 'مشاوره و امور دانشجویی', 'راهنمای نیمسال، پیگیری پرونده و ارجاع تحصیلی'],
    ['library', 'کتابخانه و پژوهش', 'منابع درسی، سمینار، گزارش و ارجاع علمی'],
    ['support', 'پاسخ‌گوی آنلاین', 'صف گفتگو، پاسخ با دانش‌نامه، ارجاع و پیگیری تیکت'],
    ['social', 'شبکه‌های اجتماعی', 'تقویم محتوا، پیش‌نویس اطلاعیه، تأیید انتشار و رسیدگی به پیام‌ها'],
  ] },
  { key: 'cto', label: 'دپارتمان فناوری اطلاعات', x: 710, teams: [
    ['helpdesk', 'میز خدمت فنی', 'عیب‌یابی دسترسی، بازیابی حساب و راهنمای LMS'],
    ['identity', 'هویت و دسترسی', 'نقش‌ها، حداقل دسترسی و ثبت تغییر مجوز'],
    ['lms', 'عملیات Moodle', 'همگام‌سازی درس، عضویت و بازخوانی رسید'],
    ['automation', 'اتوماسیون n8n', 'صف، تکرار امن، واگذاری وظیفه و ثبت شناسهٔ اجرا'],
    ['platform', 'زیرساخت و پایداری', 'پایش سرویس، پشتیبان‌گیری و بازیابی'],
    ['security', 'امنیت دفاعی و حریم خصوصی', 'ممیزی دسترسی، پالایش دادهٔ نمایش و پاسخ به هشدار'],
    ['data', 'کیفیت داده و مشاهده‌پذیری', 'شناسهٔ مشترک، شمارش مغایرت و تحلیل تأخیر'],
    ['bot', 'ربات راهنمای دانشگاه', 'مسیریابی گفت‌وگو، پاسخ از دانش‌نامه و تحویل به پشتیبانی'],
  ] },
  { key: 'engineer', label: 'دپارتمان مهندسی کامپیوتر', x: 1370, teams: [
    ['curriculum', 'طراحی برنامهٔ درسی', 'سرفصل، پیش‌نیاز و تطبیق با تقویم'],
    ['labs', 'آزمایشگاه‌ها و پروژه‌ها', 'آماده‌سازی تمرین، محیط کدنویسی و تحویل پروژه'],
    ['web', 'توسعهٔ وب و اندروید', 'درگاه دانشجو، نمایش مراحل و دسترس‌پذیری'],
    ['testing', 'تضمین کیفیت', 'آزمون پذیرش، رقابت هم‌زمان و بازپخش حالات مرزی'],
    ['research', 'پژوهش و بازتولید', 'ثبت روش، داده، محدودیت و شواهد تکرارپذیر'],
    ['evaluation', 'مهندسی قرارداد شواهد', 'ثبت رویداد، کنترل سازگاری و ارسال به ارزیاب مستقل'],
  ] },
] as const

function add(map: CampusMap, ...entry: Entry) { map.entries.push(entry) }
function link(map: CampusMap, from: string, to: string, label: string) { map.links.push([from, to, label]) }
function create(id: string, name: string) {
  const map: CampusMap = { id, name, entries: [], links: [] }
  maps.push(map)
  return map
}

add(campus, 'portal', 'درگاه دانشگاه · وب و اندروید', 'computer', 900, 20, 'دانشجو، مدرس و کارشناس از درگاه دانشگاه وارد چرخهٔ آموزشی می‌شوند. نقشه طرح نهایی روی دادهٔ ساختگی است.')
add(campus, 'intake', 'درخواست و کارتابل', 'server', 580, 165, 'دریافت درخواست، تعیین شناسه، مسیریابی به واحد و پیگیری نتیجه')
add(campus, 'publication', 'اطلاعیه و ارتباطات', 'computer', 1220, 165, 'درگاه، شبکه‌های اجتماعی و کانال پیام. انتشار عمومی به تأیید مسئول ارتباطات وابسته است.')
link(campus, 'portal', 'intake', 'درخواست')
link(campus, 'portal', 'publication', 'اطلاع‌رسانی')

for (const division of divisions) {
  const people = roster.staff.filter(person => person.manager === division.key)
  const manager = people.find(person => person.role === 'مدیر')!
  const y = division.key === 'ceo' ? 310 : 465
  add(campus, manager.id, division.label + ' · ' + count.format(people.length), 'ai_server', division.x, y,
    manager.id + ' | اولویت‌بندی، واگذاری و پیگیری مسئولیت‌ها در ساختار پیشنهادی.')
  if (division.key === 'ceo') {
    memberMaps[manager.id] = campus.id
    link(campus, 'intake', manager.id, 'نظارت')
    continue
  }
  const department = create('faran-' + division.key, division.label)
  campusRoutes[manager.id] = department.id
  memberMaps[manager.id] = department.id
  add(department, manager.id, division.label, 'ai_server', 590, 20, manager.id + ' | مدیر دپارتمان')
  link(campus, 'role-0001', manager.id, 'مسئولیت')

  const offices = people.filter(person => person.role === 'کارشناس')
  const teamDefs: { id: string; title: string; duty: string; ids: string[] }[] = division.teams.map(([id, title, duty], index) => ({
    id, title, duty, ids: offices.filter((_, i) => i % division.teams.length === index).map(person => person.id),
  }))
  const lecturers = people.filter(person => person.role === 'استاد')
  for (const major of [...new Set(lecturers.map(person => person.major))]) {
    const ids = lecturers.filter(person => person.major === major).map(person => person.id)
    for (let start = 0; start < ids.length; start += 50) {
      const part = ids.slice(start, start + 50)
      teamDefs.push({ id: 'faculty-' + part[0], title: 'مدرسان ' + major + ' · ' + count.format(start / 50 + 1),
        duty: 'طرح درس، تدریس، تمرین، آزمون و ثبت شواهد نمره', ids: part })
    }
  }
  teamDefs.forEach(({ id, title, duty, ids }, index) => {
    const label = title + ' · ' + count.format(ids.length)
    const team = create('faran-team-' + id, title)
    campusRoutes[id] = team.id
    add(campus, id, label, id === 'bot' ? 'ai_server' : 'generic', division.x + (index % 2) * 290, 620 + Math.floor(index / 2) * 135, duty)
    link(campus, manager.id, id, 'مسئولیت تیم')
    add(department, id, label, 'generic', 35 + (index % 5) * 290, 185 + Math.floor(index / 5) * 155, duty)
    link(department, manager.id, id, 'مسئولیت تیم')
    add(team, id, title, 'server', 890, 10, duty)
    ids.forEach((personId, i) => {
      memberMaps[personId] = team.id
      add(team, personId, personId, 'ai_server', 25 + (i % 7) * 285, 150 + Math.floor(i / 7) * 110,
        title + ' | ' + duty + ' | نقش طراحی‌شده در فهرست ساختگی')
      link(team, id, personId, '')
    })
  })
}

const stages = [
  ['register', '۱ · پذیرش و رفع نقص', 'admission', 'مدارک ناقص به کارتابل برمی‌گردد و پرونده پس از تکمیل بررسی می‌شود.'],
  ['select', '۲ · انتخاب واحد و حذف‌واضافه', 'enrollment', 'پیش‌نیاز، تداخل و ظرفیت ارزیابی می‌شوند. رد انتقال باید عضویت قبلی را حفظ کند.'],
  ['learn', '۳ · شروع کلاس و تکلیف', 'lms', 'عضویت درس در Moodle بازخوانی می‌شود و تکلیف و برنامه در درگاه نمایش داده می‌شوند.'],
  ['assess', '۴ · آزمون و ثبت نمره', 'exam', 'کارت آزمون، تغییر برنامه، ثبت نمره و رسید آزمون در پرونده ثبت می‌شوند.'],
  ['appeal', '۵ · اعتراض و رسیدگی', 'advising', 'اعتراض شناسهٔ پیگیری می‌گیرد و تا رأی نهایی پرونده باز می‌ماند.'],
  ['finish', '۶ · تسویه و دانش‌آموختگی', 'graduation', 'سوابق، اعتراض باز و شرایط فراغت پیش از صدور کنترل می‌شوند.'],
] as const
stages.forEach(([id, title, unit, duty], i) => {
  add(campus, id, title, 'computer', 50 + i * 330, 1750, duty)
  link(campus, unit, id, 'مسئول مرحله')
  if (i) link(campus, stages[i - 1][0], id, 'چرخهٔ دانشجو')
})
link(campus, 'publication', 'social', 'اطلاعیهٔ قابل تأیید')
link(campus, 'intake', 'bot', 'راهنمای خودکار')
link(campus, 'bot', 'support', 'ارجاع به پاسخ‌گو')
link(campus, 'automation', 'lms', 'اجرای عضویت')
link(campus, 'automation', 'evaluation', 'شناسهٔ اجرا')
add(campus, 'evaluator', 'ارزیاب مستقل دکتر سلیمانی', 'computer', 1370, 2220, 'رد هم‌شناسه، P95 صف و خدمت، بررسی ظرفیت و صحت نتیجه در آزمایشگاه ارزیابی.')
link(campus, 'evaluation', 'evaluator', 'انتقال شواهد')
link(campus, 'finish', 'evaluator', 'نتیجهٔ پرونده')

roster.majors.forEach((major, index) => {
  const id = 'faran-students-' + (index + 1)
  const students = roster.students.filter(student => student.major === major)
  const cohort = create(id, 'دانشجویان ' + major)
  campusRoutes[id] = id
  add(campus, id, major + ' · ' + count.format(students.length) + ' دانشجو', 'computer',
    50 + index * 383, 1980, 'دو گروه آزمایشی و شناسهٔ مدرس از فهرست نیمسال')
  link(campus, 'learn', id, 'گروه آموزشی')
  add(cohort, id, major, 'server', 625, 20, 'فهرست دانشجویان ساختگی نیمسال')
  for (const group of [...new Set(students.map(student => student.group))]) {
    const classId = id + '-group-' + group
    const classMembers = students.filter(student => student.group === group)
    add(cohort, classId, 'گروه ' + count.format(group), 'server', 75 + (group - 1) * 1000, 185, 'گروه درسی | ' + count.format(classMembers.length) + ' دانشجو')
    link(cohort, id, classId, 'کلاس')
    classMembers.forEach((student, i) => {
      memberMaps[student.id] = id
      add(cohort, student.id, student.id, 'computer', 15 + (group - 1) * 1000 + (i % 4) * 235,
        340 + Math.floor(i / 4) * 125, major + ' | گروه ' + count.format(group) + ' | مدرس ' + student.instructor)
      link(cohort, classId, student.id, 'عضویت')
    })
    for (const [i, instructor] of [...new Set(classMembers.map(student => student.instructor))].entries()) {
      const instructorId = classId + '-' + instructor
      add(cohort, instructorId, 'مدرس · ' + instructor, 'ai_server', 305 + (group - 1) * 1000 + i * 240, 185, 'مدرس معرفی‌شده در فهرست ساختگی')
      link(cohort, instructorId, classId, 'تدریس')
    }
  }
})

export const universityMaps = [...institutionMaps, ...maps]
