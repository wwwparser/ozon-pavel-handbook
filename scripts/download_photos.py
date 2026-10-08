"""Fetch public Telegram illustrations for editorial review, never execute media."""
import asyncio
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.services.telegram_client import client

async def run():
    out=Path('data/photos');out.mkdir(parents=True,exist_ok=True)
    posts=map(json.loads,Path('data/telegram/prodavecpavel/snapshot.jsonl').read_text(encoding='utf-8').splitlines())
    ids=[p['id'] for p in posts if (p.get('media') or {}).get('kind')=='photo']
    tg=client()
    try:
        await asyncio.wait_for(tg.connect(),45)
        for ident in ids:
            path=out/f'{ident}.jpg'
            if not path.exists():
                msg=await tg.get_messages('prodavecpavel',ids=ident)
                await msg.download_media(file=str(path))
                await asyncio.sleep(.7)
            print(ident,path.stat().st_size,flush=True)
    finally:await tg.disconnect()

if __name__=='__main__':asyncio.run(run())
