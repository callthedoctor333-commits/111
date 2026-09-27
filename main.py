import asyncio
import logging
import os
import threading
from flask import Flask

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ====== НАСТРОЙКИ ======
BOT_TOKEN = os.getenv("BOT_TOKEN", "8629669264:AAGAB4kwARQXx6yY3QDpTFQACMGrBSnbXCg")
CHANNEL_ID = os.getenv("CHANNEL_ID", "-1003943064024")
INTERVAL = int(os.getenv("INTERVAL", "20"))
LINK = "https://gclick.su?ref=tgstarsss"
PORT = int(os.getenv("PORT", "10000"))
# =======================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)

# ---------- Flask-заглушка для Render ----------
app = Flask(__name__)


@app.route("/")
@app.route("/health")
def health():
    return "Bot is alive", 200


def run_flask():
    app.run(host="0.0.0.0", port=PORT)
# -----------------------------------------------


def a(text: str) -> str:
    """Жирная кликабельная ссылка."""
    return f'<b><a href="{LINK}">{text}</a></b>'


MESSAGES = [
    (f'🧸 {a("Мишка за старт бота")}', LINK),
    (f'🌹 {a("Ваш подарок")} {a("готов к получению")}', LINK),
    (f'{a("Забери подарок за старт бота")}\n🎁🎁 {a("два подарка")} {a("на выбор!")}', LINK),
    (f'{a("Выбери подарок на вывод 👇")}', LINK),
    (f'{a("Кольцо 💍 за /start")} {a("в БОТЕ")} 😱', LINK),
    (f'{a("Сегодня 💍кольцо")} {a("выдаем тут")}', LINK),
    (f'{a("🎁 Раздача бесплатных мишек")}\n\n<i>*Осталось 63 мишки</i>', LINK),
]


def build_keyboard(url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="ЗАБРАТЬ 🎁", url=url)]]
    )


async def bot_loop():
    try:
        chat = await bot.get_chat(CHANNEL_ID)
        logging.info(f"Канал найден: {chat.title}")
    except Exception as e:
        logging.error(f"Не могу получить канал: {e}")
        return

    last_message_id = None
    index = 0

    while True:
        try:
            if last_message_id is not None:
                try:
                    await bot.delete_message(CHANNEL_ID, last_message_id)
                except TelegramBadRequest as e:
                    logging.warning(f"Не удалось удалить: {e}")

            text, url = MESSAGES[index % len(MESSAGES)]
            msg = await bot.send_message(
                CHANNEL_ID,
                text,
                parse_mode="HTML",
                reply_markup=build_keyboard(url),
                disable_web_page_preview=True,
            )
            last_message_id = msg.message_id
            index += 1
            logging.info(f"Отправлено #{index} (id={last_message_id})")

        except Exception as e:
            logging.error(f"Ошибка: {e}")

        await asyncio.sleep(INTERVAL)


def main():
    # Flask запускаем в отдельном потоке, чтобы он не блокировал бота
    threading.Thread(target=run_flask, daemon=True).start()
    # Запускаем бота
    asyncio.run(bot_loop())


if __name__ == "__main__":
    main()