import json
from pathlib import Path
root=Path('data/youtube');out=root/'transcripts';backup=root/'incomplete';backup.mkdir(exist_ok=True)
for p in list(out.glob('*.json')):
    meta=root/'audio'/(p.stem+'.info.json')
    if not meta.exists():continue
    duration=json.loads(meta.read_text(encoding='utf-8'))['duration']
    progress=p.with_suffix('.jsonl')
    segments=[json.loads(line) for line in progress.read_text(encoding='utf-8').splitlines()] if progress.exists() else json.loads(p.read_text(encoding='utf-8'))
    end=max((s['end'] for s in segments),default=0)
    if abs(duration-end)>3:
        print('Incomplete, requeue:',p.stem,end,duration)
        for ext in ('.json','.jsonl','.txt','.srt'):
            file=out/(p.stem+ext)
            if file.exists():file.replace(backup/file.name)
    else:print('Complete:',p.stem,round(end,2))
