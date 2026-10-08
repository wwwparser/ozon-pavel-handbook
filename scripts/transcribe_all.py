"""Transcribe downloaded Russian audio locally, reuse model and resume segments."""
import json
import sys
import time
import subprocess
from pathlib import Path
sys.path.insert(0,str(Path.home()/'.codex/skills/gigaam-transcribe/scripts'))
import transcribe
import gigaam
root=Path('data/youtube'); out=root/'transcripts';out.mkdir(exist_ok=True)
videos=json.loads((root/'inventory.json').read_text(encoding='utf-8'))['videos']
model=gigaam.load_model('v3_e2e_ctc')
pending=[v for v in videos if not (out/(v['id']+'.json')).exists()]
while pending:
    progressed=False
    for v in pending[:]:
        path=root/'audio'/(v['id']+'.mp3')
        if not path.exists():continue
        meta=root/'audio'/(v['id']+'.info.json')
        if meta.exists():
            expected=json.loads(meta.read_text(encoding='utf-8')).get('duration')
            try:
                actual=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(path)],text=True,stderr=subprocess.DEVNULL))
            except (ValueError,subprocess.CalledProcessError):continue
            if expected and abs(actual-expected)>3:continue
        # FFmpeg postprocessor may be writing the final mp3: wait for stable size.
        size=path.stat().st_size;time.sleep(2)
        if path.stat().st_size!=size:continue
        print('TRANSCRIBE',v['id'],v['title'],flush=True)
        segments=transcribe.transcribe(path,out,model=model)
        transcribe.write_outputs(path,out,segments)
        pending.remove(v);progressed=True
    if not progressed:
        if (root/'download-complete.json').exists():
            raise SystemExit('Missing audio: '+','.join(v['id'] for v in pending))
        print('Waiting for audio; remaining',len(pending),flush=True)
        time.sleep(10)
print('All',len(videos),'transcripts ready.',flush=True)
