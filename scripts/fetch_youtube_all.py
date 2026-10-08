"""Download audio for every inventory video; resume by existing output files."""
import json
import os
import sys
import time
import subprocess
from pathlib import Path
for key in ('HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy'):
    os.environ.pop(key,None)
sys.path.insert(0,str(Path.home()/'.codex/skills/youtube-fetch/scripts'))
import yt_fetch
import yt_dlp
root=Path('data/youtube'); audio=root/'audio'; audio.mkdir(exist_ok=True)
(root/'download-complete.json').unlink(missing_ok=True)
inventory=json.loads((root/'inventory.json').read_text(encoding='utf-8'))
for n,v in enumerate(inventory['videos'],1):
    path=audio/(v['id']+'.mp3')
    if path.exists():continue
    subprocess.run([sys.executable,'scripts/refresh_youtube_cookies.py'],check=True,capture_output=True)
    print(n,v['id'],v['title'],flush=True)
    opts=yt_fetch._opts()|{'proxy':'http://127.0.0.1:10809','format':'18/bestaudio/best',
        'extractor_args':{'youtube':{'player_client':['tv','web_safari','mweb'],'fetch_pot':['never']}},
        'outtmpl':str(audio/'%(id)s.%(ext)s'),'writesubtitles':False,'writeautomaticsub':False,
        'subtitleslangs':['ru'],'subtitlesformat':'json3','writeinfojson':True,
        'socket_timeout':20,'retries':2,'extractor_retries':1,'fragment_retries':2,
        'postprocessors':[{'key':'FFmpegExtractAudio','preferredcodec':'mp3','preferredquality':'64'}]}
    try:
        with yt_dlp.YoutubeDL(opts) as y: y.download([v['url']])
    except Exception as e:
        with (root/'errors.jsonl').open('a',encoding='utf-8') as f:
            f.write(json.dumps({'id':v['id'],'stage':'download','error':str(e)[:500]},ensure_ascii=False)+'\n')
    time.sleep(1)
(root/'download-complete.json').write_text(json.dumps({'downloaded':sum((audio/(v['id']+'.mp3')).exists() for v in inventory['videos']), 'expected':len(inventory['videos'])}),encoding='utf-8')
