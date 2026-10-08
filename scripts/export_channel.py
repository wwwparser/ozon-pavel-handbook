"""Snapshot all accessible messages, including media-only and service messages.

Run from project root: python scripts/export_channel.py [--probe]
Small channels are fetched again on updates, so edited posts are refreshed too.
An interrupted refresh never replaces the last complete snapshot.
"""
import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.services.telegram_client import client
from telethon.errors import FloodWaitError

OUT = Path('data/telegram/prodavecpavel')


async def run(probe=False):
    tg = client()
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        await asyncio.wait_for(tg.connect(), timeout=45)
        if not await tg.is_user_authorized():
            raise SystemExit('Сессия Telegram не авторизована.')
        entity = await tg.get_entity('prodavecpavel')
        newest = await tg.get_messages(entity, limit=1)
        total = newest.total
        if probe:
            oldest = await tg.get_messages(entity, limit=1, reverse=True)
            print(json.dumps({'count':total,'first':str(oldest[0].date) if oldest else None,
                              'last':str(newest[0].date) if newest else None},ensure_ascii=False))
            return
        pending = OUT/'snapshot.pending.jsonl'
        count, offset = 0, 0
        with pending.open('w', encoding='utf-8') as f:
            while True:
                batch = await tg.get_messages(entity, limit=200, offset_id=offset)
                if not batch:
                    break
                for msg in batch:
                    doc = getattr(msg, 'document', None)
                    media = None
                    if doc:
                        names = [a.file_name for a in doc.attributes if hasattr(a,'file_name')]
                        media = {'kind':'document','mime':doc.mime_type,'size':doc.size,
                                 'name':names[0] if names else ''}
                    elif getattr(msg,'photo',None):
                        media = {'kind':'photo'}
                    elif getattr(msg,'media',None):
                        media = {'kind':type(msg.media).__name__}
                    record = {'id':msg.id,'date':msg.date.isoformat(),
                              'text':getattr(msg,'message',None) or '',
                              'link':f'https://t.me/prodavecpavel/{msg.id}',
                              'media':media,'grouped_id':getattr(msg,'grouped_id',None),
                              'service':type(msg.action).__name__ if getattr(msg,'action',None) else None}
                    f.write(json.dumps(record,ensure_ascii=False)+'\n')
                    count += 1
                f.flush()
                offset = batch[-1].id
                await asyncio.sleep(0.6)
        pending.replace(OUT/'snapshot.jsonl')
        (OUT/'manifest.json').write_text(json.dumps({'channel':'prodavecpavel',
            'fetched_at':datetime.now(timezone.utc).isoformat(),'telegram_count':total,
            'exported':count,'complete':count==total,'media_downloaded':False},
            ensure_ascii=False,indent=2),encoding='utf-8')
        print(f'Snapshot: {count}/{total}; media metadata only.')
    except FloodWaitError as exc:
        raise SystemExit(f'Telegram FloodWait: повторите через {exc.seconds} секунд. Полный архив сохранён.')
    finally:
        await tg.disconnect()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--probe',action='store_true')
    asyncio.run(run(parser.parse_args().probe))
