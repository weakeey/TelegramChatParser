
# GitHub - https://github.com/weakeey
# Lolz - https://lolz.live/members/10026182/
# Telegram - @italicoff

from telethon import TelegramClient, errors
from telethon.tl.functions.messages import GetHistoryRequest
import pandas as pd
import asyncio
from colorama import Fore, init

init(autoreset=True)

api_id = api_id # my.telegram.org
api_hash = "api_hash" # my.telegram.org

client = TelegramClient('session', api_id, api_hash)

chat_input = input(Fore.GREEN + "Введите ссылку на канал (@username или ID): ")
limit = int(input(Fore.GREEN + "Сколько сообщений просмотреть: "))

async def main():
    await client.start()
    users_data = {}
    total_messages = 0
    bots_skipped = 0
    system_messages_skipped = 0

    try:
        if chat_input.startswith('@'):
            chat_entity = await client.get_entity(chat_input)
        else:
            chat_entity = await client.get_entity(int(chat_input))
    except errors.UsernameInvalidError:
        print(Fore.RED + "Неверный username или ID")
        return

    offset_id = 0
    while total_messages < limit:
        history = await client(GetHistoryRequest(
            peer=chat_entity,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=min(100, limit - total_messages),
            max_id=0,
            min_id=0,
            hash=0
        ))
        if not history.messages:
            break

        for message in reversed(history.messages):
            total_messages += 1
            if not message.from_id:
                system_messages_skipped += 1
                continue
            sender = await client.get_entity(message.from_id)
            if sender.username and sender.username.lower().endswith('bot'):
                bots_skipped += 1
                continue
            user_id = sender.id
            if user_id not in users_data:
                users_data[user_id] = {
                    'Имя': sender.first_name or '',
                    'Username': sender.username or '',
                    'Телефон': getattr(sender, 'phone', None),
                    'Сообщение': message.message,
                    'Дата': message.date.replace(tzinfo=None)
                }

            if total_messages % 20 == 0:
                print(Fore.CYAN + f"Пройдено сообщений: {total_messages} | "
                      f"Уникальных пользователей: {len(users_data)} | "
                      f"Пропущено ботов: {bots_skipped} | "
                      f"Системных сообщений: {system_messages_skipped}")

        offset_id = history.messages[-1].id

    if users_data:
        df = pd.DataFrame(users_data.values())
        df.to_excel("parsed_users.xlsx", index=False)
        print(Fore.GREEN + f"Парсинг завершен! Всего сообщений обработано: {total_messages}")
        print(Fore.GREEN + f"Уникальных пользователей собрано: {len(users_data)}")
        print(Fore.GREEN + f"Пропущено ботов: {bots_skipped}")
        print(Fore.GREEN + f"Пропущено системных сообщений: {system_messages_skipped}")
    else:
        print(Fore.RED + "Пользователи не найдены.")

with client:
    client.loop.run_until_complete(main())
