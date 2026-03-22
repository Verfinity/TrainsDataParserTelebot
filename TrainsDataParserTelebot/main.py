import asyncio
from dotenv import load_dotenv
from os import getenv

from handlers import router

from aiogram import Bot, Dispatcher


load_dotenv()
TOKEN = getenv('BOT_TOKEN')


async def main() -> None:
    bot = Bot(token=TOKEN)

    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())
