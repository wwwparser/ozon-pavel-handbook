import sys
from pathlib import Path
sys.path.insert(0,str(Path.home()/'.codex/skills/browser-bridge'))
import bridge
bridge.set_session('pavel-book')
r=bridge.cdp('Network.getAllCookies')
cookies=r.get('result',{}).get('cookies',[])
lines=['# Netscape HTTP Cookie File','']
for c in cookies:
    domain=c['domain']
    if not (domain.lstrip('.')=='youtube.com' or domain.endswith('.youtube.com')):continue
    lines.append('\t'.join([domain,'TRUE' if domain.startswith('.') else 'FALSE',c.get('path','/'),
            'TRUE' if c.get('secure') else 'FALSE',str(max(0,int(c.get('expires',0)))),c['name'],c['value']]))
if len(lines)<5:raise SystemExit('No YouTube cookies from browser.')
(Path.home()/'.claude/secrets/youtube_cookies.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Refreshed YouTube cookies; values excluded from logs.')
