"""Check coverage and local site links before publication."""
import json
import re
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote,urlparse
import subprocess
root=Path(__file__).resolve().parents[1];docs=root/'docs'
coverage=json.loads((root/'research/coverage.json').read_text(encoding='utf-8'))
assert coverage['telegram_messages']==coverage['telegram_registered']==72
assert coverage['youtube_videos']==coverage['youtube_transcripts']==24
class Links(HTMLParser):
    def __init__(self):super().__init__();self.ids=set();self.links=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if 'id'in d:
            assert d['id'] not in self.ids,f'Duplicate HTML id: {d["id"]}'
            self.ids.add(d['id'])
        for k in ('href','src'):
            if k in d:self.links.append(d[k])
parsed={}
for p in docs.rglob('*.html'):
    parser=Links();parser.feed(p.read_text(encoding='utf-8'));parsed[p.resolve()]=parser
for p,parser in parsed.items():
    for link in parser.links:
        url=urlparse(link)
        if url.scheme or url.netloc:continue
        target=(p.parent/unquote(url.path)).resolve() if url.path else p
        assert target.exists(),f'{p}: missing {link}'
        if url.fragment and target in parsed:
            assert unquote(url.fragment) in parsed[target].ids,f'{p}: missing anchor {link}'
book=(docs/'index.html').read_text(encoding='utf-8')
assert len(re.findall(r'<h1(?:\s|>)',book))==1
for name in ('TELEGRAM_API_HASH','BEGIN OPENSSH PRIVATE KEY','ghp_','gho_'):
    assert name not in book
subprocess.run(['node','scripts/test_calculators.cjs'],cwd=root,check=True)
print('Coverage: 72 Telegram messages, 24 video transcripts; local links and formulas checked.')
