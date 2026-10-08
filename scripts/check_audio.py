import json
import subprocess
from pathlib import Path
for p in Path('data/youtube/audio').glob('*.mp3'):
    meta=p.with_suffix('.info.json')
    if not meta.exists():continue
    expected=json.loads(meta.read_text(encoding='utf-8'))['duration']
    actual=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p)],text=True))
    print(p.stem,'expected',expected,'actual',round(actual,2),'complete',abs(expected-actual)<3)
