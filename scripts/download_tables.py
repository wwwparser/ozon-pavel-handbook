"""Download the four spreadsheet attachments, without opening or executing them."""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.services.telegram_client import client

async def run():
    out=Path('data/tables'); out.mkdir(parents=True,exist_ok=True)
    tg=client()
    try:
        await asyncio.wait_for(tg.connect(),45)
        for ident in (7,25,34,35):
            msg=await tg.get_messages('prodavecpavel',ids=ident)
            path=out/f'{ident}.xlsx'
            if not path.exists():
                await msg.download_media(file=str(path))
                await asyncio.sleep(1.2)
            print(ident,path.stat().st_size)
    finally:
        await tg.disconnect()

if __name__=='__main__': asyncio.run(run())
