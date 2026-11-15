import asyncio
import logging
import os
from threading import Thread
from flask import Flask
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import Message

# ==== НАСТРОЙКИ ====
BOT_TOKEN = os.getenv("BOT_TOKEN", "ВАШ_НОВЫЙ_ТОКЕН_СЮДА")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789")) # ВАШ ID ЦИФРАМИ
# ===================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# --- Заглушка-сайт для хостинга (чтобы Render не отключал бота) ---
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

# --- Логика бота ---
@router.message(Command("start"))
async def cmd_start(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("👋 Привет! Сюда будут приходить анонимные сообщения.\nЧтобы ответить, используйте:\n<code>/reply ID текст</code>")
    else:
        await message.answer("👋 Привет! Отправь мне сообщение — я передам его анонимно.")

@router.message(Command("reply"))
async def cmd_reply(message: Message):
    if message.from_user.id != ADMIN_ID: return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("Использование: <code>/reply ID текст</code>")
        return
    try:
        user_id = int(parts[1])
        await bot.send_message(user_id, f"💌 <b>Анонимный ответ:</b>\n\n{parts[2]}")
        await message.answer("✅ Ответ отправлен.")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@router.message(F.text | F.photo | F.video | F.voice | F.document | F.sticker)
async def forward_anon(message: Message):
    if message.from_user.id == ADMIN_ID: return
    header = f"📨 <b>Анонимное сообщение</b>\n🆔 ID: <code>{message.from_user.id}</code>\n━━━━━━━━━━━━━━━"
    try:
        await bot.send_message(ADMIN_ID, header)
        await bot.copy_message(chat_id=ADMIN_ID, from_chat_id=message.chat.id, message_id=message.message_id)
        await message.answer("✅ Отправлено анонимно.")
    except Exception:
        await message.answer("❌ Ошибка отправки.")

async def main():
    Thread(target=run_flask, daemon=True).start() # Запуск сайта
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())