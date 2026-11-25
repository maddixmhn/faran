import type { NodeType } from '@/types'

const chartUrl = 'https://faran.ac.ir/faran-chart/'
const programsUrl = 'https://faran.ac.ir/عنوان-رشتهها/'
const regulationUrl = 'https://faran.ac.ir/آیین-نامه-و-مقررات/'
const faqUrl = 'https://faran.ac.ir/?page_id=3489'
const graduateAdmissionUrl = 'https://faran.ac.ir/پذیرفته-شدگان-کارشناسی-ارشد-سال-1405/'
type Shape = [id: string, label: string, type: NodeType, x: number, y: number, notes: string]
type Link = [source: string, target: string, label: string]
type Map = { id: string; name: string; entries: Shape[]; links: Link[] }

// Each parent is the junction observed in the official chart. A connecting line
// describes chart placement, not an undocumented delegation or approval policy.
const organization: [string, string | null, string, number, number][] = [
  ['founders', null, 'هیئت مؤسس', 1120, 40],
  ['trustees', 'founders', 'هیئت امنا', 1120, 160],
  ['trustees-chair', 'trustees', 'ریاست هیئت امنا', 1500, 160],
  ['new-programs', 'trustees', 'نیازسنجی و توسعهٔ رشته‌های جدید', 700, 160],
  ['president', 'trustees', 'ریاست', 1120, 290],
  ['protection', 'president', 'حراست', 740, 290],
  ['university-council', 'president', 'هیئت رئیسه و شورای دانشگاه', 1500, 290],
  ['deputy', 'president', 'قائم‌مقام', 1120, 425],
  ['president-office', 'deputy', 'دفتر ریاست', 400, 555],
  ['public-relations', 'deputy', 'روابط عمومی', 400, 685],
  ['strategic-quality', 'deputy', 'دفتر نظارت راهبردی و کیفیت آموزشی', 400, 815],
  ['international', 'deputy', 'دفتر توسعهٔ روابط بین‌الملل علمی–پژوهشی', 400, 945],
  ['technical', 'deputy', 'مدیریت فنی', 1430, 555],
  ['research-club', 'deputy', 'باشگاه پژوهشی', 2050, 555],
  ['open-learning', 'deputy', 'مرکز آموزش‌های آزاد و مهارتی', 2400, 555],
  ['virtual-portal', 'technical', 'واحد پرتال آموزش مجازی', 1250, 720],
  ['content-production', 'technical', 'واحد تولید محتوای الکترونیکی', 1600, 720],
  ['student-affairs', 'deputy', 'معاونت فرهنگی و دانشجویی', 40, 1110],
  ['research-office', 'deputy', 'معاونت پژوهشی', 650, 1110],
  ['academic-office', 'deputy', 'معاونت آموزشی', 1550, 1110],
  ['finance-office', 'deputy', 'معاونت اداری‌مالی', 2410, 1110],
  ['associations', 'student-affairs', 'دفتر انجمن‌ها و فوق‌برنامه‌ها', 40, 1280],
  ['industry-relations', 'research-office', 'ارتباط با صنعت و جامعه', 450, 1280],
  ['research-publication', 'research-office', 'امور پژوهشی و نشر', 760, 1280],
  ['academic-groups', 'academic-office', 'گروه‌های آموزشی', 1110, 1280],
  ['academic-head', 'academic-office', 'مدیر آموزش', 1460, 1280],
  ['graduate-studies', 'academic-office', 'تحصیلات تکمیلی', 1810, 1280],
  ['academic-council', 'academic-office', 'شورای آموزشی دانشگاه', 2170, 1280],
  ['academic-operations', 'academic-head', 'کادر اجرایی آموزش', 1310, 1450],
  ['academic-quality', 'academic-head', 'نظارت و سنجش بر کیفیت', 1610, 1450],
]

const chart: Map = {
  id: 'faran-official-structure',
  name: 'ساختار رسمی منتشرشدهٔ فاران',
  entries: organization.map(([id, , title, x, y]) => [id, title, 'server', x, y, 'عنوان و جایگاه در نمودار رسمی مؤسسه · ' + chartUrl]),
  links: organization.flatMap(([id, parent]) => parent ? [[parent, id, 'پیوند در چارت']] : []),
}

type Service = [id: string, title: string, observed: string, source: string]
const services: [unit: string, services: Service[]][] = [
  ['academic-office', [
    ['admissions-doc', 'پذیرش و پروندهٔ آموزشی', 'صفحهٔ مقررات فاران فرم ثبت‌نام و مقررات کارشناسی و کارشناسی ارشد را منتشر کرده است.', regulationUrl],
    ['graduate-admission', 'ثبت‌نام ورودی ارشد مهر ۱۴۰۵', 'اطلاعیهٔ همان ورودی ثبت‌نام الکترونیکی، وصول اصل مدارک، بررسی و رفع نقص را قبل از نهایی‌شدن ثبت‌نام و فعال‌شدن شمارهٔ دانشجویی قرار می‌دهد. بازه‌ها وابسته به همان ورودی‌اند.', graduateAdmissionUrl],
    ['student-desk', 'میزکار و انتخاب واحد', 'در میزکار دانشجو، ارائهٔ دروس، انتخاب واحد، حذف و اضافه، برنامهٔ هفتگی و کارنامه مسیرهای جداگانه دارند.', 'https://faranlms.com/'],
    ['exam-guide', 'آزمون تحت نظارت', 'راهنمای رسمی آزمون، فایل و ویدئو و مسیر ورود به سامانهٔ آموزش را معرفی می‌کند.', 'https://faran.ac.ir/amnazmoon'],
    ['group-duties', 'مسئولیت مدیر گروه', 'فاران تنظیم ترم‌بندی رشته را وظیفهٔ مدیر گروه همان رشته معرفی می‌کند. فهرست حکم‌ها و نام مدیران همهٔ رشته‌ها در منابع بررسی‌شده در دسترس نبود.', faqUrl],
    ['term-withdrawal', 'حذف نیمسال با نظر شورا', 'صفحهٔ پرسش‌های کارشناسی ارشد درخواست کتبی، بررسی پیش از شروع امتحانات و تأیید شورای آموزشی را ذکر می‌کند. ثبت نتیجه با احتساب در سنوات توصیف شده است.', faqUrl],
  ]],
  ['finance-office', [
    ['tuition', 'جدول شهریه', 'فاران جدول شهریه را از منوی سایت منتشر کرده است. این گره مرجع مشاهده است و مبلغ یا اطلاعات بانکی ذخیره نمی‌کند.', 'https://faran.ac.ir/jadval-shahrieh/'],
    ['project-tuition', 'شهریهٔ پایان‌نامه و پروژه', 'در صفحهٔ مقررات مدرک مستقلی برای شهریهٔ پایان‌نامه و پروژه معرفی شده است. اعمال آن به نسخهٔ معتبر و مقطع وابسته است.', regulationUrl],
  ]],
  ['research-office', [
    ['research-role', 'مرجع معاونت پژوهشی', 'سایت فاران برای معاونت پژوهشی صفحهٔ مستقل دارد. اتصال داخلی پرونده‌های پژوهشی به امور نشر و ارتباط با صنعت از چارت خوانده شده است.', 'https://faran.ac.ir/r-assistant/'],
    ['research-library', 'کتابخانهٔ دیجیتال', 'فاران فهرست عمومی آثار و جست‌وجوی موضوعی منتشر کرده است. جایگاه سازمانی کتابخانه در تصویر چارت مشخص نیست.', 'https://faran.ac.ir/digital-library/'],
    ['thesis-doc', 'مقررات تحصیلات تکمیلی', 'صفحهٔ مقررات آموزش و شهریهٔ پایان‌نامه منبع اولیه است. گردش داخلی تصویب، داوری، دفاع و تسویه باید با سند داخلی جداگانه تأیید شود.', regulationUrl],
  ]],
  ['technical', [
    ['lms-service', 'پورتال آموزشی دانشجویان', 'پیوند پورتال دانشجو در صفحهٔ رسمی مؤسسه وجود دارد. در چارت، پرتال آموزش مجازی از تولید محتوای الکترونیکی جدا است.', 'https://faranlms.com/'],
    ['lecturer-service', 'پرتال استادان', 'صفحهٔ رسمی ورود استادان را از درگاه دانشجو جدا کرده است.', 'https://faran.ac.ir/teachers-portal/'],
    ['class-booking', 'رزرو زمان کلاس استادان', 'صفحهٔ ورود رزرو کلاس به حساب استاد نیاز دارد. دسترسی به تقویم داخلی و قواعد تأیید رزرو در بررسی عمومی ممکن نبود.', 'https://faran.ac.ir/ocr/'],
    ['recorded-learning', 'محتوای آموزش الکترونیکی', 'صفحهٔ معرفی مؤسسه، مطالعهٔ آفلاین و جلسات آنلاین را در شیوهٔ یادگیری مجازی ذکر می‌کند.', 'https://faran.ac.ir/faran/'],
  ]],
  ['student-affairs', [
    ['association-call', 'فراخوان انجمن‌های علمی دانشجویی', 'سایت فاران فراخوان ثبت‌نام در انجمن‌های علمی را منتشر کرده است. وضعیت عضویت دانشجویان داخلی است.', 'https://faran.ac.ir/wp-content/uploads/2024/01/Anjoman-scaled.jpg'],
  ]],
]

const groups: [string, string, string][] = [
  ['engineering', 'مهندسی', 'مهندسی کامپیوتر، مهندسی حرفه‌ای کامپیوتر نرم‌افزار، تجارت الکترونیکی، شبکه‌های کامپیوتری، یادگیری الکترونیکی'],
  ['law', 'حقوق', 'حقوق، حقوق خصوصی، حقوق بین‌الملل، حقوق جزا و جرم‌شناسی'],
  ['languages', 'زبان‌های خارجی', 'مترجمی زبان انگلیسی، آموزش زبان انگلیسی'],
  ['economics', 'اقتصاد و حسابداری', 'اقتصاد، اقتصاد انرژی، حسابداری'],
  ['management', 'مدیریت', 'مدیریت صنعتی، بازرگانی، کسب‌وکار، امور بانکی، مالی، مدیریت فناوری'],
  ['social-sciences', 'خدمات اجتماعی', 'مددکاری اجتماعی'],
]
const route: Record<string, string> = {}
export const institutionMaps: Map[] = [chart]
export const institutionRoutes = route

for (const [unit, rows] of services) {
  const [, , title] = organization.find(([id]) => id === unit)!
  const id = 'faran-official-' + unit
  route[unit] = id
  const children = organization.filter(([, parent]) => parent === unit)
  institutionMaps.push({
    id, name: title + ' · خدمات و شواهد',
    entries: [
      [unit, title, 'server', 575, 20, 'جایگاه در چارت منتشرشده · ' + chartUrl],
      ...children.map<Shape>(([key, , label], i) => [key, label, 'server', 50 + i * 350, 175, 'زیرشاخه در نمودار منتشرشده · ' + chartUrl]),
      ...rows.map<Shape>(([key, label, fact, url], i) => [key, label, 'computer', 50 + (i % 5) * 350, 360 + Math.floor(i / 5) * 135, fact + ' · منبع ' + url]),
    ],
    links: [
      ...children.map<Link>(([key]) => [unit, key, 'پیوند در چارت']),
      ...rows.map<Link>(([key]) => [unit, key, 'مرجع خدمت، بدون ادعای خط گزارش‌دهی']),
    ],
  })
}

route['academic-groups'] = 'faran-official-programs'
institutionMaps.push({
  id: route['academic-groups'], name: 'گروه‌های آموزشی و رشته‌های منتشرشده',
  entries: [
    ['academic-groups', 'گروه‌های آموزشی', 'server', 910, 25, 'جایگاه گروه‌های آموزشی در چارت رسمی ' + chartUrl + ' · دانشکده‌ها در معرفی فاران آمده‌اند. نام و حکم مدیر هر رشته نیاز به سند جداگانه دارد.'],
    ...groups.map<Shape>(([id, title, programs], i) => [
      id, title, 'computer', 50 + i * 340, 210, 'برنامه‌های منتشرشده · ' + programs + ' · ' + programsUrl + ' | مسئول ثبت‌شدهٔ هر رشته: در انتظار سند انتصاب.',
    ]),
  ],
  links: groups.map(([id]) => ['academic-groups', id, 'حوزهٔ تحصیلی منتشرشده']),
})
