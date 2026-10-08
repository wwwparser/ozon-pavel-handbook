"""Read-only Telegram client. Credentials stay in local .env; session is shared."""
import os
from pathlib import Path
from urllib.parse import urlparse


def client():
    from telethon import TelegramClient
    import socks
    env = Path('.env')
    if env.exists():
        for line in env.read_text(encoding='utf-8-sig').splitlines():
            if line.strip() and not line.lstrip().startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    api_id, api_hash = os.getenv('TELEGRAM_API_ID'), os.getenv('TELEGRAM_API_HASH')
    session = Path(os.getenv('TELEGRAM_SESSION', str(Path.home()/'.claude/secrets/telegram.session')))
    if not api_id or not api_hash:
        raise SystemExit('Заполните TELEGRAM_API_ID и TELEGRAM_API_HASH в .env.')
    if not session.is_file():
        raise SystemExit('Нет Telegram-сессии. Укажите TELEGRAM_SESSION в .env.')
    url = os.getenv('TELEGRAM_PROXY') or os.getenv('PROXY_LOCAL')
    proxy = None
    if url:
        p = urlparse(url)
        proxy = (socks.SOCKS5 if p.scheme.startswith('socks5') else socks.HTTP, p.hostname, p.port)
    return TelegramClient(str(session), int(api_id), api_hash, proxy=proxy,
                          timeout=30, connection_retries=2, request_retries=2,
                          flood_sleep_threshold=0)
