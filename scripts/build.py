"""Build static GitHub Pages book; no raw secrets or audio in publication folder."""
import csv
import html
import json
import re
import shutil
from pathlib import Path
import markdown

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs';OUT.mkdir(exist_ok=True)
research=ROOT/'research';research.mkdir(exist_ok=True)
POST_MAP={}
for chapter,ids in {
 '01-model-vhoda':[51,52,54,55,57,64,79], '02-ekonomika':[7,25,34,35,43,44,46,65,69,76,77],
 '03-zakupka':[19,78], '04-logistika':[33,38,47,56,68], '05-kartochka':[28,37,48,50,53],
 '06-reklama':[12,40], '07-masshtab':[49,59,67,71,72,74],
}.items():
 for ident in ids:POST_MAP[ident]=chapter

VIDEO_MAP={
 'R9QqHOpkPJk':'02-ekonomika','PfzqK5xaT3U':'01-model-vhoda','h1Iyeg07sKM':'03-zakupka',
 'w7Gorr71oJo':'02-ekonomika','r_W0hQF1-0w':'01-model-vhoda','GRduweMa3OE':'02-ekonomika',
 'ZhPrYZtZfzg':'04-logistika','5LWoeD1PnF0':'02-ekonomika','foRs1dH6vhA':'06-reklama',
 'r4HEn3aRqNQ':'01-model-vhoda','TMColfY8fwU':'12-zapusk','vjDBncRob38':'04-logistika',
 'zgY799rxUZU':'06-reklama','T8YzYZZeEdM':'11-drugie-ploshchadki','FOoPjRwkLIc':'11-drugie-ploshchadki',
 'Srlpcm-Kr_A':'11-drugie-ploshchadki','9R34ZL8W8AQ':'03-zakupka','C5mPLeO1Dus':'01-model-vhoda',
 'DzpYdE7bTHA':'12-zapusk','z0ubRHDt17M':'04-logistika','3SOoGVZh1DY':'04-logistika',
 'P3WdwnjzUGI':'11-drugie-ploshchadki','Wg7WXQY7AX0':'05-kartochka','8RXvFYvru0k':'02-ekonomika'}

def render(text):return markdown.markdown(text,extensions=['tables','fenced_code','toc'])
def write_csv(path,rows):
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

post_source=ROOT/'data/telegram/prodavecpavel/snapshot.jsonl'
if not post_source.exists():post_source=ROOT/'sources/telegram.jsonl'
posts=sorted([json.loads(line) for line in post_source.read_text(encoding='utf-8').splitlines()],key=lambda r:r['id'])
registry=[]
appendix=['# 9. Реестр всех Telegram-сообщений','',
 'Все доступные сообщения учтены ниже. «В главе» означает переработку текста. Фото просмотрены и разобраны в главе 13; Excel — в главе 10. Служебные записи Telegram не являются учебными постами. Исходные удалённые сообщения восстановить нельзя.','',
 '| Пост и дата | Содержание / тип | Где использован |','|---|---|---|']
for p in posts:
 ident=p['id'];text=p['text'];media=p.get('media');chapter=POST_MAP.get(ident)
 if p.get('service'):status='Служебная запись Telegram'
 elif ident in (9,20,22,24,58):status='Другая площадка / реклама; справочное приложение'
 elif chapter:status='Текст переработан в главе'
 elif re.search(r'youtu|youtube',text):status='Видеоматериал; см. реестр YouTube'
 elif media and not text:status='Фото просмотрено; см. главу 13'
 elif text.strip() in ('⬇️','⬇️⬇️⬇️','⬆️'):status='Указатель на соседний пост'
 else:status='Анонс / услуги / повтор; сохранён в реестре'
 title=re.sub(r'\s+',' ',text).strip()[:110] or (media.get('name') or media.get('kind') if media else p.get('service') or 'Без текста')
 row={'id':ident,'date':p['date'],'link':p['link'],'summary':title,'chapter':chapter or '09-istochniki',
      'status':status,'media':json.dumps(media,ensure_ascii=False) if media else ''}
 registry.append(row)
 loc=f'[{chapter}]({chapter}.md)' if chapter else status
 if media and media.get('kind')=='photo':loc+=' · [Иллюстрация](13-illyustracii.md)'
 appendix.append(f"| [{ident}]({p['link']}) · {p['date'][:10]} | {title.replace('|','/')} | {loc} |")
appendix+=['','## Дополнительные публикации','',
 'Пост 9 — историческая новость WB о регистрации. Посты 20–24 посвящены Яндекс Маркету и WB DBS. Пост 58 — рекламный анонс стороннего эфира. Эти материалы не устанавливают правила Ozon.','',
 'Пост 70 — налоговая новость июля 2026 года. Номер дела и первичные документы не приведены, поэтому выводы о текущей налоговой обязанности и лимиты не перенесены в практическую инструкцию. Проверка — по документам ФНС и обстоятельствам конкретного продавца.','',
 'Посты 39 и 63 сообщают об изменении цен услуг автора; 55 и 64 во многом повторяют друг друга. Рекламные призывы сжаты, учебная мысль о проверке до закупки сохранена.','',
 'Фото без подписи в постах 45, 60–62 и 66 разобраны в главе 13. Таблицы из постов 7, 25, 34 и 35 разобраны в разделе расчётов.']
(ROOT/'book/09-istochniki.md').write_text('\n'.join(appendix)+'\n',encoding='utf-8')
write_csv(research/'posts.csv',registry)

inventory_source=ROOT/'data/youtube/inventory.json'
if not inventory_source.exists():inventory_source=ROOT/'sources/youtube.json'
inventory=json.loads(inventory_source.read_text(encoding='utf-8'))
video_rows=[];video_html=[];transdir=OUT/'transcripts';transdir.mkdir(exist_ok=True)
for v in inventory['videos']:
 ident=v['id'];raw=ROOT/'data/youtube/transcripts'/(ident+'.json')
 if not raw.exists():raw=OUT/'transcripts'/(ident+'.json')
 metadata=ROOT/'data/youtube/audio'/(ident+'.info.json')
 title=v['title'];date=v.get('upload_date','');duration=v.get('duration')
 if metadata.exists():
  info=json.loads(metadata.read_text(encoding='utf-8'));date=info.get('upload_date','');duration=info.get('duration')
 chapter=VIDEO_MAP.get(ident,'13-video')
 ready=raw.exists()
 status='Транскрипт получен локально GigaAM' if ready else 'Транскрипт ещё не получен'
 video_rows.append({'id':ident,'title':title,'date':date,'duration_seconds':duration,'tab':v['tab'],'url':v['url'],'chapter':chapter,'transcript_status':status})
 if ready:
  segments=json.loads(raw.read_text(encoding='utf-8'))
  paragraphs=[]
  for s in segments:
   start=int(s['start']);label=f'{start//60:02}:{start%60:02}'
   paragraphs.append(f'<p id="t{start}"><a class="time" href="{html.escape(v["url"])}&amp;t={start}s">{label}</a> {html.escape(s["text"])}</p>')
  downloads=' · '.join(f'<a href="{ident}.{ext}" download>{ext.upper()}</a>' for ext in ('txt','srt','json'))
  body=f'<p><a href="../index.html#{chapter}">Вернуться в учебник</a></p><h1>{html.escape(title)}</h1><p>Автоматическая расшифровка GigaAM. Возможны ошибки в названиях, числах и терминах; точные значения проверяйте в видео. Таймкоды соответствуют исходному русскому аудио.</p><p>Скачать: {downloads}</p>'+''.join(paragraphs)
  (transdir/(ident+'.html')).write_text(f'<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><link rel="stylesheet" href="../style.css"><main class="transcript">{body}</main></html>',encoding='utf-8')
  for ext in ('.txt','.srt','.json'):
   source=raw.with_suffix(ext);target=transdir/(ident+ext)
   if source.resolve()!=target.resolve():shutil.copy2(source,target)
 link=f'<a href="transcripts/{ident}.html">Читать транскрипт</a>' if ready else status
 video_html.append(f'<tr><td><a href="{v["url"]}">{html.escape(title)}</a></td><td>{v["tab"]}</td><td><a href="#{chapter}">Глава</a></td><td>{link}</td></tr>')
write_csv(research/'videos.csv',video_rows)
coverage={'telegram_messages':len(posts),'telegram_with_text':sum(bool(p['text'].strip()) for p in posts),
          'telegram_registered':len(registry),'youtube_videos':len(video_rows),
          'youtube_transcripts':sum('GigaAM' in r['transcript_status'] for r in video_rows),
          'youtube_tabs':inventory['tabs'],'tables_analyzed':4,'telegram_photos_reviewed':27}
(research/'coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2),encoding='utf-8')

chapters=sorted((ROOT/'book').glob('*.md'));sections=[];nav=[]
for p in chapters:
 text=p.read_text(encoding='utf-8');title=text.splitlines()[0].lstrip('# ')
 for chapter in chapters:text=text.replace(f'({chapter.name})',f'(#{chapter.stem})')
 body=render(text)
 # Namespace heading IDs: Markdown's default IDs repeat across chapters.
 body=re.sub(r'id="([^"]+)"',lambda m:f'id="{p.stem}-{m[1]}"',body)
 body=re.sub(r'href="#([^"]+)"',lambda m:m[0] if any(m[1]==c.stem for c in chapters) else f'href="#{p.stem}-{m[1]}"',body)
 # Keep chapter/subsection hierarchy under the single page-level h1.
 body=re.sub(r'<(/?)h([1-5])(?=[ >])',lambda m:f'<{m[1]}h{int(m[2])+1}',body)
 sections.append(f'<section id="{p.stem}" class="chapter">{body}</section>')
 nav.append(f'<a href="#{p.stem}">{html.escape(title)}</a>')
calc=(ROOT/'site/calculators.html').read_text(encoding='utf-8')
sections.append('<section id="calculators" class="chapter">'+calc+'</section>')
nav.append('<a href="#calculators">Калькуляторы</a>')
sections.append('<section id="video-library" class="chapter"><h2>Все видео и транскрипты</h2><p>24 доступных видео, включая Shorts. Русская аудиодорожка распознана локально. Содержание переработано в тематических главах; полная автоматическая расшифровка доступна отдельно.</p><table><thead><tr><th>Видео</th><th>Раздел канала</th><th>В учебнике</th><th>Транскрипт</th></tr></thead><tbody>'+''.join(video_html)+'</tbody></table></section>')
nav.append('<a href="#video-library">Видео и транскрипты</a>')
page=(ROOT/'site/layout.html').read_text(encoding='utf-8').replace('{{NAV}}',''.join(nav)).replace('{{CONTENT}}',''.join(sections))
(OUT/'index.html').write_text(page,encoding='utf-8')
for name in ('style.css','calculator.js','models.js','calculator-ui.js','reader.js','extra-calculators.js'):
 shutil.copy2(ROOT/'site'/name,OUT/name)
downloads=OUT/'downloads';downloads.mkdir(exist_ok=True)
for p in (ROOT/'data/tables').glob('*.xlsx'):shutil.copy2(p,downloads/p.name)
for p in (research/'posts.csv',research/'videos.csv',ROOT/'book/cards.csv',ROOT/'templates/unit-economics.csv'):shutil.copy2(p,downloads/p.name)
(OUT/'.nojekyll').write_text('',encoding='utf-8')
print(json.dumps(coverage,ensure_ascii=False,indent=2))
