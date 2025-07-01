#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏡 Sochi Invest Bot - Главный файл запуска
Автор: SergD (@sergei_dyshkant)
Разработчик: @sergei_dyshkant
"""

import asyncio
import logging
import os
from bot import bot, dp
import config
import handlers
import fsm_handlers

logger = logging.getLogger(__name__)

async def on_startup():
    """Функция при запуске"""
    logger.info("🚀 Запуск Sochi Invest Bot...")
    bot_info = await bot.get_me()
    logger.info(f"📊 Бот: @{bot_info.username} (ID: {bot_info.id})")
    
    if config.SERVICE_CHAT_ID != "YOUR_SERVICE_CHAT_ID":
        try:
            await bot.send_message(
                config.SERVICE_CHAT_ID,
                f"🤖 <b>Sochi Invest Bot запущен!</b>\n\n✅ Готов к работе\n🔗 @{bot_info.username}"
            )
        except:
            pass
    
    logger.info("✅ Бот запущен успешно!")

async def main():
    """Главная функция"""
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    try:
        await on_startup()
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        logger.error(f"Ошибка: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main()) 