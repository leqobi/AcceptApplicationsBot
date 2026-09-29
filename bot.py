import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, Router
from aiogram.types import ChatJoinRequest

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("join_bot")

router = Router()


@router.chat_join_request()
async def approve_all(request: ChatJoinRequest):
    try:
        await request.approve()
        log.info(
            "Одобрена заявка: user_id=%s username=%s chat=%s",
            request.from_user.id,
            request.from_user.username,
            request.chat.title,
        )
    except Exception:
        # Если Telegram на секунду ограничил скорость одобрений при
        # массовом наплыве заявок — не роняем бота, пробуем ещё раз.
        log.exception("Не удалось одобрить заявку, пробую ещё раз через 2 сек")
        await asyncio.sleep(2)
        try:
            await request.approve()
        except Exception:
            log.exception("Повторная попытка тоже не удалась, заявка пропущена: user_id=%s", request.from_user.id)


async def main():
    if not BOT_TOKEN:
        raise SystemExit("Не задан BOT_TOKEN. Укажи его в переменных окружения или в .env")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    log.info("Бот запущен, жду заявки на вступление...")
    await dp.start_polling(bot, allowed_updates=["chat_join_request"])


if __name__ == "__main__":
    asyncio.run(main())
