import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
import asyncio
from aiogram.client.default import DefaultBotProperties

from app.graph import graph
from app.settings import settings
from frontend.sessions import load_sessions, save_sessions

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

sessions = load_sessions()

bot = Bot(
    token=settings.TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

@dp.message(Command("start"))
async def handle_start(message: types.Message):
    await message.answer("Olá! Sou seu assistente virtual. Como posso ajudar?")

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    logger.info(f"[Entrada] Usuario {user_id}: {text}")

    if user_id not in sessions:
        sessions[user_id] = {"messages": []}

    sessions[user_id]["messages"].append({"role": "user", "content": text})

    result = await graph.ainvoke(sessions[user_id])
    messages = result.pop("messages", [])

    response = messages[-1].content if messages else "Desculpe, não entendi sua solicitação."
    sessions[user_id]["messages"].append({"role": "assistant", "content": response})
    save_sessions(sessions)

    logger.info(f"[Salida] Usuario {user_id}: {response}")
    await message.answer(response)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())