from pathlib import Path
import html,json,re,collections
from pypdf import PdfReader
import os,subprocess

d=Path('docs').resolve()
data=Path('infra/workflow/data/semester')
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
roster=load(data/'roster.json')['students']
receipts={x['id']:x for x in load(data/'enrolled.json')}
queue=load(data/'public/queue-comparison.json')
race=load(data/'public/seat-race.json')
esc=lambda x:html.escape(str(x))
def table(headers,rows):
 return '<table><thead><tr>'+''.join(f'<th>{esc(x)}</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(f'<td><bdi>{esc(x)}</bdi></td>' for x in r)+'</tr>' for r in rows)+'</tbody></table>'
def page(title,body): return f'<section><h2>{title}</h2>{body}</section>'
def fig(name,label): return f'<figure><img src="{name}" alt="{label}"><figcaption>{label}</figcaption></figure>'
pages=[page('گزارش سمینار دانشگاه دیجیتال فاران','<h1>طراحی و ارزیابی گردش‌کار آموزشی چندعاملی</h1><p>محمد مهرانی · استاد درس سمینار دکتر سعید شکراللهی</p><h3>راهنمای مطالعه</h3><p>بدنهٔ گزارش، روش و نتایج آزمایش را توضیح می‌دهد. پیوست، صد برگهٔ مستقل برای تطبیق برنامهٔ ثبت‌نام با رسید Moodle دارد. پرونده‌ها ساختگی‌اند و بازتاب تصمیم‌های آموزشی دانشگاه واقعی نیستند.</p>')]
for block in re.split(r'^## ',(d/'SEMINAR-MANUSCRIPT.md').read_text(encoding='utf-8-sig'),flags=re.M)[1:]:
 title,_,body=block.partition('\n')
 content=[]
 for text in body.strip().split('\n\n'):
  m=re.fullmatch(r'!?\[([^]]+)\]\(([^)]+)\)',text.strip())
  if m and text.startswith('!'):content.append(fig(m[2],m[1]))
  elif m:content.append(f'<p>سند همراه <bdi>{esc(m[2])}</bdi></p>')
  else:content.append('<p>'+esc(text)+'</p>')
 pages.append(page(esc(title),''.join(content)))
counts=collections.Counter(s['major'] for s in roster)
pages.append(page('نتایج ثبت‌نام در رشته‌ها',table(['رشته','تعداد در برنامه','تعداد رسید منطبق'],[(m,n,sum(s['major']==m and all(receipts.get(s['id'],{}).get(k)==s[k] for k in ('major','group','instructor')) for s in roster)) for m,n in counts.items()])+'<p>تطبیق بر سه فیلد رشته، گروه و مدرس انجام شده است. نتیجه از خروجی ذخیره‌شده گرفته شد و وضعیت امروزی Moodle را اندازه نمی‌گیرد.</p>'))
pages.append(page('نتایج مقایسهٔ صف و اجرا',table(['مسیر','اجرا','تحویل تا گره (ms)','صف Redis (ms)'],[(r['mode'],r['execution'],r['dispatch_ms'],r['redis_queue_ms'] if r['redis_queue_ms'] is not None else 'خارج از مسیر Redis') for r in queue['registrations']])+'<p>اجرای گرم‌کردن در جدول هست و در میانه‌ها لحاظ نشده است. میانه‌های ثبت‌شده برای CLI و worker به ترتیب ۴۶۹۳۷ و ۴۸۱۱ میلی‌ثانیه‌اند. نمونه‌ها اندک و بار ورودی تک‌درخواستی بود.</p>'))
pages.append(page('راستی‌آزمایی رقابت برای آخرین صندلی',table(['درخواست','اجرای n8n','عضویت مبدأ','عضویت مقصد'],[(r['request_id'],r['execution'],r['origin'],r['target']) for r in race['requests']])+'<p>قفل ردیف مقصد، بررسی ظرفیت و اعمال عضویت را در یک تراکنش هماهنگ می‌کند. بازخوانی جداگانه پس از پایان هر دو تراکنش یک عضویت در مقصد نشان داد.</p>'))
pages.append(page('منابع علمی و فنی','<ol><li>Little, J. D. C. (1961). A Proof for the Queuing Formula L = λW. Operations Research, 9(3), 383–387. <bdi>doi:10.1287/opre.9.3.383</bdi>. کاربرد در پژوهش، تفکیک مرز صف از کل سامانه و لزوم اندازه‌گیری هم‌زمان نرخ ورود و جمعیت صف است.</li><li>Lamport, L. (1978). Time, Clocks, and the Ordering of Events in a Distributed System. Communications of the ACM, 21(7), 558–565. <bdi>doi:10.1145/359545.359563</bdi>. تقدم علّی با شناسهٔ درخواست و مدارک تحویل تفسیر می‌شود.</li><li>n8n، راهنمای رسمی Queue mode، برای معماری worker و Redis.</li><li>Moodle Developer Resources، Group API، برای خواندن عضویت و عملیات گروه.</li></ol>'))
pages.append(page('کنسول عامل‌های Paperclip',fig('paperclip-console.png','تصویر مستقیم کنسول محلی و چهار نقش مدیریتی آزمایشی')))
pages.append(page('اجرای موفق گردش‌کار نیمسال در n8n',fig('n8n-execution-19.jpg','اسکرین‌شات مستقیم n8n؛ اجرای موفق شمارهٔ ۱۹ در ۸٫۳۲۴ ثانیه و نمودار پنج‌گرهی نیمسال')))
pages.append(page('کانتینرهای روشن در Docker Desktop',fig('docker-desktop.jpg','نمای مستقیم Docker Desktop؛ چراغ سبز کنار ردیف‌ها نشان می‌دهد کانتینرهای n8n، Moodle، پایگاه‌های داده و داشبوردها هنگام ثبت تصویر در حال اجرا بودند.')))
for index,s in enumerate(roster,1):
 r=receipts.get(s['id'],{})
 keys=[('major','رشته'),('group','شمارهٔ گروه'),('instructor','نقش مدرس')]
 matches=all(s[k]==r.get(k) for k,_ in keys)
 body=f'<p>پروندهٔ ساختگی <bdi>{esc(s["id"])}</bdi> · برگهٔ {index} از {len(roster)}</p>'
 body+=table(['فیلد','برنامهٔ نیمسال','رسید Moodle'],[(label,s[k],r.get(k,'ثبت نشده')) for k,label in keys])
 body+=f'<p>درس Moodle <bdi>{esc(r.get("courseid","—"))}</bdi> · گروه Moodle <bdi>{esc(r.get("groupid","—"))}</bdi></p><h3>نتیجهٔ آزمون انطباق</h3><p>{"سه فیلد برنامه با رسید هم‌خوان است." if matches else "اختلاف در رسید شناسایی شد."} شمارهٔ گروه داخلی Moodle با شمارهٔ گروه در برنامه دو شناسهٔ متفاوت است.</p>'
 pages.append(page('پیوست تطبیق پروندهٔ ثبت‌نام',body))
document='<!doctype html><html lang="fa" dir="rtl"><meta charset="utf-8"><title>سمینار فاران</title><style>@page{size:A4;margin:18mm}body{font:15px/1.95 Tahoma,Arial;color:#18352f}section{break-after:page}section:last-child{break-after:auto}h2{border-bottom:2px solid #176952;padding-bottom:8px}h1{font-size:35px}figure{margin:10px;text-align:center;break-inside:avoid}img{max-width:95%;max-height:85mm}table{border-collapse:collapse;width:100%}td,th{border:1px solid #a9beb8;padding:7px;text-align:start}th{background:#e3efeb}</style>'+''.join(pages)+'</html>'
tmp=d/'SEMINAR-PRINT.html';tmp.write_text(document,encoding='utf8')
pdf=d/'faran-seminar.pdf'
subprocess.run([r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe','--headless','--disable-gpu',f'--user-data-dir={os.environ["TEMP"]}/seminar-print',f'--print-to-pdf={pdf}',tmp.as_uri()],timeout=90,check=True)
reader=PdfReader(pdf)
assert len(reader.pages)>=100
print('PDF pages',len(reader.pages),'size',pdf.stat().st_size)

