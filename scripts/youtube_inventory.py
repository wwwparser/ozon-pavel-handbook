import json
import os
import sys
from pathlib import Path
for key in ('HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy'):
    os.environ.pop(key,None)
sys.path.insert(0,str(Path.home()/'.codex/skills/youtube-fetch/scripts'))
import yt_fetch
import yt_dlp
out=Path('data/youtube');out.mkdir(parents=True,exist_ok=True)
records={};tabs={}
for tab in ('videos','shorts','streams'):
    opts=yt_fetch._opts(cookies=False)|{'extract_flat':'in_playlist','skip_download':True,'proxy':'http://127.0.0.1:10809','socket_timeout':15,'retries':1}
    try:
        with yt_dlp.YoutubeDL(opts) as y:
            info=y.extract_info('https://www.youtube.com/@prodavec_pavel/'+tab,download=False)
        entries=list(info.get('entries') or [])
        tabs[tab]={'count':len(entries),'channel':info.get('channel'),'channel_id':info.get('channel_id')}
        for r in entries:
            if not r or not r.get('id'):continue
            records[r['id']]={'id':r['id'],'title':r.get('title'), 'duration':r.get('duration'),
                              'url':'https://www.youtube.com/watch?v='+r['id'],'tab':tab}
    except Exception as e:
        tabs[tab]={'error':str(e)[:400]}
(out/'inventory.json').write_text(json.dumps({'tabs':tabs,'videos':list(records.values())},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(tabs,ensure_ascii=False));print('Unique videos:',len(records))
