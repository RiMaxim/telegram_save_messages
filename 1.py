from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import csv
import time
import os
from datetime import datetime, timezone

# === 🔧 ВСТАВЬ СЮДА СВОИ ДАННЫЕ ===
api_id =       # <-- замени на свой API ID
api_hash = '' # <-- замени на свой API Hash
phone = ''  # <-- твой номер Telegram в международном формате
invite_link = ''

# === Задаём диапазон дат ===
start_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
end_date = datetime(2025, 7, 10, 1, 59, 59, tzinfo=timezone.utc)

current_offset_date = end_date  # начинаем с конца

# === ПОДКЛЮЧЕНИЕ ===
client = TelegramClient('anon_session', api_id, api_hash)
client.start(phone)

channel = client.get_entity(invite_link)
print(f"📥 Загрузка сообщений из: {channel.title}")

# === ВЫГРУЗКА СООБЩЕНИЙ ===
all_messages = []
limit = 100

while True:
    history = client(GetHistoryRequest(
        peer=channel,
        limit=limit,
        offset_id=0,
        offset_date=current_offset_date,
        add_offset=0,
        max_id=0,
        min_id=0,
        hash=0
    ))

    messages = history.messages
    if not messages:
        print("\n⏹ Конец сообщений или ничего не найдено.")
        break

    stop = False
    for message in messages:
        if message.message and message.date:
            if start_date <= message.date <= end_date:
                all_messages.append([
                    message.id,
                    message.date.strftime("%Y-%m-%d %H:%M:%S"),
                    message.sender_id,
                    message.message.replace('\n', ' ')
                ])
            elif message.date < start_date:
                stop = True
                break

    current_offset_date = messages[-1].date
    print(f"🔄 Последняя дата: {current_offset_date} | Всего: {len(all_messages)}", end='\r')

    if stop:
        print("\n⏹ Достигнута нижняя граница по дате.")
        break

    time.sleep(0.25)

client.disconnect()

# === СОХРАНЕНИЕ В CSV ===
filename = f'messages_{start_date.date()}_to_{end_date.date()}.csv'
filepath = os.path.abspath(filename)
try:
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'date', 'sender_id', 'message'])
        writer.writerows(all_messages)
    print(f"\n✅ Сохранено {len(all_messages)} сообщений в файл: {filepath}")
except Exception as e:
    print(f"\n❌ Ошибка при сохранении файла: {e}")
