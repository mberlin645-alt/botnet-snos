import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.messages import ReportRequest
from telethon.tl.types import InputReportReasonSpam
from telethon import Button
from re import compile as compile_link
from os import listdir
from datetime import datetime, timedelta
import random

# Ваши данные для API и бота
api_id = '27702639'
api_hash = '81aa9fda07354b85ad3e8a9fc87dcebb'
bot_token = '8662224782:AAFjDRRGTXWzD62LnC-u3rwr-vt-VkK1__s'

# Инициализация клиента бота
bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

admins_id = [8264264137]
owner_id = 8264264137
log_chat_id = -1003716441746  # ID чата для логов

subscriptions = {}
premium_subscriptions = {}
whitelist = set()  # Используем множество для вайтлиста
path: str = "sessions/"

# Загрузка администраторов
def load_admins():
    global admins_id
    try:
        with open("adm.txt", "r") as file:
            admins_id = [int(line.strip())for line in file.readlines()]
    except FileNotFoundError:
        admins_id = [8264264137]

# Загрузка подписок
def load_subscriptions():
    try:
        with open('sub.txt', 'r') as file:
            for line in file:
                user_id, end_date_str = line.strip().split(',')
                user_id = int(user_id)
                end_date = datetime.fromisoformat(end_date_str)
                subscriptions[user_id] = end_date
    except FileNotFoundError:
        open('sub.txt', 'w').close()

# Загрузка премиум подписок
def load_premium_subscriptions():
    try:
        with open('prem_sub.txt', 'r') as file:
            for line in file:
                user_id = int(line.strip())
                premium_subscriptions[user_id] = True
    except FileNotFoundError:
        open('prem_sub.txt', 'w').close()

# Загрузка вайтлиста
def load_whitelist():
    global whitelist
    try:
        with open('white.txt', 'r') as file:
            whitelist = {int(line.strip()) for line in file if line.strip()}
    except FileNotFoundError:
        open('white.txt', 'w').close()

# Сохранение подписки
def save_subscription(user_id, days):
    end_date = datetime.now() + timedelta(days=days)
    with open('sub.txt', 'a') as file:
        file.write(f"{user_id},{end_date.isoformat()}\n")
    subscriptions[user_id] = end_date

# Сохранение премиум подписки
def save_premium_subscription(user_id, days):
    end_date = datetime.now() + timedelta(days=days)
    with open('prem_sub.txt', 'a') as file:
        file.write(f"{user_id}\n")
    premium_subscriptions[int(user_id)] = True

# Проверка подписки
async def check_subscription(user_id):
    if user_id in subscriptions:
        if subscriptions[user_id] > datetime.now():
            return True
        else:
            del subscriptions[user_id]  # Удаляем истекшую подписку
            return False
    return False

# Проверка премиум подписки
async def check_premium_subscription(user_id):
    return user_id in premium_subscriptions

# Отправка жалоб
from telethon.errors import FloodWaitError, SessionPasswordNeededError
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import ReportRequest
from telethon.tl.types import InputReportReasonSpam
import re
from os import listdir


# Функция для компиляции ссылки
def compile_link(pattern):
    return re.compile(pattern)

async def report_message(link) -> (int, int):
    message_link_pattern = compile_link(r'https://t.me/(?P<username_or_chat>.+)/(?P<message_id>\d+)')
    match = message_link_pattern.search(link)

    if not match:
        print(f"Неверный формат ссылки: {link}")
        return 0, 0

    chat = match.group("username_or_chat")
    message_id = int(match.group("message_id"))

    # Остальной код остается без изменений


    session_path = "sessions/"  # Замените на путь к вашим сессиям
    files = listdir(session_path)
    sessions = [s for s in files if s.endswith(".session")]


    successful_reports = 0
    failed_reports = 0

    for session in sessions:
        try:
            async with TelegramClient(f"{path}{session}", api_id, api_hash) as client:
                if not await client.is_user_authorized():
                    print(f"Сессия {session} не авторизована, пропуск.")
                    failed_reports += 1
                    await client.disconnect()
                    continue

                try:
                    # Получаем сущность для жалобы
                    entity = await client.get_entity(chat)

                    # Отправляем жалобу с текстовым сообщением
                    await client(ReportRequest(
                        peer=entity,
                        id=[message_id],
                        reason=InputReportReasonSpam(),
                        message="Эти действия не только доставляют значительный дискомфорт, но и отнимают огромное количество времени, которое могло бы быть потрачено на более важные и полезные задачи. Я считаю, что подобные сообщения являются ничем иным, как СПАМОМ, который мешает нормальной работе и отвлекает от действительно важных дел."
                    ))

                    print(f"Жалоба отправлена через сессию {session}.")
                    successful_reports += 1

                #except FloodWaitError as e:
                    #wait_time = e.seconds
                    #print(f"Flood wait error: необходимо подождать {wait_time} секунд. Пауза перед продолжением.")
                    #await asyncio.sleep(wait_time)

                except Exception as e:
                    print(f"Ошибка при отправке жалобы через сессию {session}: {e}")
                    failed_reports += 1

        except SessionPasswordNeededError:
            print(f"Сессия {session} требует ввода пароля или кода подтверждения, пропуск.")
            failed_reports += 1

        except Exception as e:
            print(f"Ошибка при инициализации сессии {session}: {e}")
            failed_reports += 1

    return successful_reports, failed_reports

# Обработка команды /start
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = event.sender.id
    first_name = event.sender.first_name or "Пользователь"

    photo_path = "image.mp4"
    description = "многофункциональный бот,упрощающий жизнь,овнер-@usikpas"

    buttons = [
        [Button.url("📜 soon", "https://t.me/"), Button.inline("📱 профиль", b"profile")],
        [Button.inline("🧨 запуск", b"new_snos"),  Button.url("📖 канал", "https://t.me/+RkJJLQ8FDUZiZThi")]
    ]

    await bot.send_file(event.chat_id, file=photo_path, caption=description, buttons=buttons)

@bot.on(events.CallbackQuery(data=b'new_snos'))
async def new_snos(event):
    user_id = event.sender.id
    if user_id in whitelist:
        await event.respond("🚫 вы находитесь в вайтлисте, сообщения от вас не будут обработаны.")
        return

    if not await check_subscription(user_id):
        await event.respond("❌ у вас отсутствует подписка!")
        return

    await event.respond("⚡️ отправьте ссылку на нарушения:")

@bot.on(events.CallbackQuery(data=b"profile"))
async def profile(event):
    user_id = event.sender.id
    first_name = event.sender.first_name or "Пользователь"
    username = event.sender.username if event.sender.username else "Нет"

    days_left = await check_subscription(user_id)
    is_premium = await check_premium_subscription(user_id)
    is_whitelisted = user_id in whitelist

    response_text = (
        f"📱 ваш профиль\n\n"
        f"🗣 имя: {first_name}\n"
        f"🗄 данные: {user_id} |@{username}\n"
        f"💎 подписка: {'да' if days_left else 'нет'}\n"
        f"✨ премиум подписка: {'на' if is_premium else 'нет'}\n"
        f"🚫 вайтлист: {'да' if is_whitelisted else 'нет'}"
    )

    await event.respond(response_text)

@bot.on(events.NewMessage)
async def handle_message(event):
    user_id = event.sender.id
    link = event.message.message.strip()  # Убираем лишние пробелы по краям

    # Проверка на наличие подписки
    if not await check_subscription(user_id):
        await event.respond("❌ у вас отсутствует подписка!")
        return

    # Проверка на наличие ссылки
    if 'https://t.me/' not in link:
        return  # Просто игнорируем сообщение, если нет корректной ссылки

    await event.respond('Отправка жалоб началась...')
    
    successful_reports, failed_reports = await report_message(link)

    response_text = f'⚡️ все жалобы отправлены\n\nУспешно: {successful_reports}\nНе успешные: {failed_reports}'
    await event.respond(response_text)

    log_text = f"Log\n\nЮзер сносящий {user_id}\n{link}\n✅ успешно: {successful_reports}\n❌ не успешно: {failed_reports}"
    await bot.send_message(log_chat_id, log_text)

@bot.on(events.NewMessage(pattern='/give_sub'))
async def give_subscription(event):
    user_id = event.sender.id
    if user_id != owner_id and user_id not in admins_id:
        await event.respond("У вас нет прав для выдачи подписок.")
        return
    
    try:
        target_user_id, days = event.message.message.split(" ")[1:3]
        save_subscription(int(target_user_id), int(days))
        await event.respond(f"Подписка на {days} дней выдана пользователю с ID {target_user_id}.")
    except Exception as e:
        await event.respond("Произошла ошибка при выдаче подписки. Проверьте правильность ввода.")
        print(f"Ошибка: {e}")

@bot.on(events.NewMessage(pattern='/add_premium'))
async def add_premium_subscription(event):
    user_id = event.sender.id
    if user_id != owner_id and user_id not in admins_id:
        await event.respond("У вас нет прав для выдачи премиум подписок.")
        return

    try:
        target_user_id, days = event.message.message.split(" ")[1:3]
        save_premium_subscription(int(target_user_id), int(days))
        await event.respond(f"Премиум подписка на {days} дней выдана пользователю с ID {target_user_id}.")
    except Exception as e:
        await event.respond("Произошла ошибка при выдаче премиум подписки.")
        print(f"Ошибка: {e}")

@bot.on(events.NewMessage(pattern='/whitelist'))
async def whitelist_user(event):
    user_id = event.sender.id
    if user_id != owner_id and user_id not in admins_id:
        await event.respond("У вас нет прав для добавления пользователей в вайтлист.")
        return

    try:
        target_user_id = int(event.message.message.split(" ")[1])
        whitelist.add(target_user_id)
        with open('white.txt', 'a') as file:
            file.write(f"{target_user_id}\n")

        await event.respond(f"Пользователь с ID {target_user_id} добавлен в вайтлист.")
    except Exception as e:
        await event.respond("Произошла ошибка при добавлении пользователя в вайтлист.")
        print(f"Ошибка: {e}")

async def main():
    while True:
        await asyncio.sleep(86400)  # Ждем 24 часа

if __name__ == "__main__":
    load_admins()
    load_subscriptions()
    load_premium_subscriptions()
    load_whitelist()
    bot.start()
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    bot.run_until_disconnected()