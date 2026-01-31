import asyncio
from aiogram import Bot, Dispatcher
from data import TOKEN
from handlers import router
from data import init_databases
from reminder import scheduler_rem
from sendtask import scheduler_st
from deleteusers import scheduler_du


async def main():
    init_databases()
    print("Бот запущен и готов к работе")

    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    
    scheduler_st.start()
    scheduler_rem.start()
    scheduler_du.start()
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Работа бота завершена.")