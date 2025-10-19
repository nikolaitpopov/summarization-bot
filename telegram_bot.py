from typing import List, Dict, Union
from datetime import datetime, timezone
import asyncio
from dotenv import load_dotenv
import os

from telethon import TelegramClient
# pip install telethon

from dotenv import load_dotenv

load_dotenv("settings.env")

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_PATH = os.getenv("SESSION_PATH", "session")


def _parse_date(dt: Union[datetime, str]) -> datetime:
    if isinstance(dt, datetime):
        return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt
    # ожидается ISO-строка, например "2025-10-19T12:00:00"
    return datetime.fromisoformat(dt)


async def get_channel_messages_after(channel_id: Union[int, str],
                                     last_summary_date: Union[datetime, str]) -> List[Dict]:
    """
    Возвращает список сообщений канала newer than last_summary_date.
    result: [{'date': '2025-10-19T12:34:56+00:00', 'text': '...'}, ...]
    """
    since = _parse_date(last_summary_date)
    results: List[Dict] = []

    async with TelegramClient(SESSION_PATH, API_ID, API_HASH) as client:
        entity = await client.get_entity(channel_id)
        # iter_messages возвращает от новых к старым — можно прерывать при попадании на старые
        async for msg in client.iter_messages(entity):
            if not msg.date:
                continue
            # Приведение msg.date к UTC для корректного сравнения
            msg_date = msg.date.astimezone(timezone.utc)
            if msg_date <= since:
                break
            text = msg.message or ''
            results.append({'date': msg.date.isoformat(), 'text': text})

    # вернуть в хронологическом порядке (от старых к новым)
    results.reverse()
    return results


# Пример использования
if __name__ == '__main__':
    async def main():
        channel = '@muzika_chtivo'  # или numeric id, или '@username'
        last = '2025-10-18T00:00:00'  # пример
        msgs = await get_channel_messages_after(channel, last)
        for m in msgs:
            print(m['date'], m['text'][:80])

    asyncio.run(main())