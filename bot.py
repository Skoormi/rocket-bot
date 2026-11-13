import asyncio
import os
import random
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Фейковый сайт, чтобы Render видел открытый порт и не вырубал бота
def run_server():
    port = int(os.getenv("PORT", 10000))
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is running")
        def log_message(self, *args):
            pass
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

threading.Thread(target=run_server, daemon=True).start()

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

stats = {"total": 0, "win": 0}

def get_signal():
    choice = random.choices(["SAFE", "MEDIUM", "RISKY"], weights=[65, 25, 10], k=1)[0]
    if choice == "SAFE":
        target = round(random.uniform(1.3, 1.8), 2)
        text = f"🚀 СИГНАЛ: РАКЕТКА\n\nЦель: выйти на {target}x\nТип: SAFE\nСмысл: низкий кэф доходит чаще. Ставим маленькую сумму, выходим строго на цели."
    elif choice == "MEDIUM":
        target = round(random.uniform(2.0, 3.0), 2)
        text = f"🚀 СИГНАЛ: РАКЕТКА\n\nЦель: выйти на {target}x\nТип: MEDIUM\nСмысл: баланс между шансом и выплатой."
    else:
        target = round(random.uniform(5.0, 10.0), 2)
        text = f"🚀 СИГНАЛ: РАКЕТКА\n\nЦель: выйти на {target}x\nТип: RISKY, фан\nСмысл: заходит редко, только мелкая сумма."
    text += "\n\nБот не подключен к 1win и не знает исход раунда. Это не гарантия, а цель выхода. 18+"
    return text, target

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Привет! Бот сигналов по Ракетке.\n\n"
        "Флоу такой:\n"
        "1. Жмешь /signal в боте\n"
        "2. Получаешь цель\n"
        "3. Идешь в 1win, жмешь Старт в Ракетке\n"
        "4. Возвращаешься сюда и жмешь Зашел / Не зашел\n\n"
        "Команды: /signal - сигнал, /stats - статистика"
    )

@dp.message(Command("signal"))
async def signal(message: types.Message):
    text, target = get_signal()
    stats["total"] += 1
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Понял, иду играть", callback_data="go")],
        [InlineKeyboardButton(text="Перейти в Ракетку", url="https://1win - СЮДА ВСТАВИШЬ СВОЮ РЕФ ССЫЛКУ")],
    ])
    await message.answer(text, reply_markup=keyboard)

@dp.callback_query(F.data == "go")
async def go(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "Ок, жду тебя после раунда. Как сыграешь, отметь:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Зашел", callback_data="win"),
             InlineKeyboardButton(text="❌ Не зашел", callback_data="lose")]
        ])
    )

@dp.callback_query(F.data.in_(["win", "lose"]))
async def result(callback: types.CallbackQuery):
    if callback.data == "win":
        stats["win"] += 1
    await callback.answer("Записал")
    await callback.message.edit_reply_markup(reply_markup=None)

@dp.message(Command("stats"))
async def show_stats(message: types.Message):
    if stats["total"] == 0:
        await message.answer("Пока нет сигналов")
        return
    percent = round(stats["win"] / stats["total"] * 100, 1)
    await message.answer(f"Всего сигналов: {stats['total']}\nЗашло: {stats['win']}\nПроходимость: {percent}%")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
