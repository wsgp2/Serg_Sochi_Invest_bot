#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конфигурация Sochi Invest Bot
"""

import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Telegram Bot Settings
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
SERVICE_CHAT_ID = os.getenv("SERVICE_CHAT_ID", "YOUR_SERVICE_CHAT_ID")

# Ограничения
RATE_LIMIT_PHOTOS = 3  # максимум фото в минуту на пользователя
RATE_LIMIT_WINDOW = 60  # окно в секундах

# URLs
PDF_DRIVE_URL = "https://drive.google.com/drive/folders/1q4osO5PDLhwJig8cMY97g_hnQZP4sm9_"
DEVELOPER_URL = "https://t.me/m/KL5XwR0sMWEy"
DEVELOPER_USERNAME = "@sergei_dyshkant"

# Сообщения
MESSAGES = {
    "developer_info": "💡 **Хотите такого же бота для вашего бизнеса?**\nОбращайтесь к разработчику: @sergei_dyshkant",
    "rate_limit": "⏱ Пожалуйста, подождите немного перед следующим запросом фотографий"
}

# Логирование
LOG_LEVEL = "INFO"
LOG_FILE = "logs/sochi_invest_bot.log" 