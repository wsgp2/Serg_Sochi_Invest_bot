#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏡 Sochi Invest Bot - Telegram Bot для продажи вилл "ПАНОРАМА 240"
Автор: SergD (@sergei_dyshkant)
Разработчик: @sergei_dyshkant
"""

import asyncio
import logging
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, Contact
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import config
from typing import Dict, Any

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация бота
from aiogram.client.default import DefaultBotProperties
bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# FSM States
class PDFForm(StatesGroup):
    waiting_name = State()
    waiting_phone = State()

class ViewingForm(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_budget = State()
    waiting_time = State()

# Данные о виллах
VILLA_DATA = {
    "villa1": {
        "name": "Вилла №1 — «Панорама 240»",
        "area": "244 м²",
        "plot": "4,08 сот.",
        "price": "280 млн ₽",
        "description": """🏡 Вилла №1 — «Панорама 240»
244 м² | участок 4,08 сот. | готова к проживанию

💎 Панорамные окна Alutech (Sun Guardian 60/40)
🏊‍♂️ Композитный бассейн Compass Brilliant 77
🌅 180° вид на море, Олимпийский парк и Сириус (10 мин)
🛠 Премиальный фасад KMEW · CLADBOARD
💡 Все центральные коммуникации (газ, вода, эл-во)

💰 <b>Цена: 280 млн ₽</b>"""
    },
    "villa2": {
        "name": "Вилла №2 — «Панорама 240»",
        "area": "242 м²",
        "plot": "4,05 сот.",
        "price": "200 млн ₽",
        "description": """🏡 Вилла №2 — «Панорама 240»
242 м² | участок 4,05 сот. | готова к проживанию

💎 Панорамные окна Alutech (Sun Guardian 60/40)
🏊‍♂️ Композитный бассейн Compass Brilliant 77
🌅 180° вид на море, Олимпийский парк и Сириус (10 мин)
🛠 Премиальный фасад KMEW · CLADBOARD
💡 Все центральные коммуникации (газ, вода, эл-во)

💰 <b>Цена: 200 млн ₽</b>"""
    }
}

def format_phone(phone: str) -> str:
    """Форматирование телефона - добавление + в начале"""
    if phone and not phone.startswith('+'):
        return f"+{phone}"
    return phone

async def send_to_service_chat(lead_type: str, data: Dict[str, Any]):
    """Отправка лида в служебный чат"""
    try:
        # Форматируем телефон
        phone = format_phone(data.get('phone', ''))
        
        # Форматируем username
        username = data.get('username', '')
        username_text = f"@{username}" if username else 'Не указан'
        
        if lead_type == "pdf":
            message = f"""🔔 Новый лид (PDF)
Имя: {data['name']}
Телефон: {phone}
Телеграм: {username_text}
Источник: {data.get('utm_source', 'Direct')}
Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"""
        
        elif lead_type == "viewing":
            villa_info = VILLA_DATA.get(data['villa'], {})
            
            # Определяем название объекта
            if villa_info:
                villa_name = villa_info['name']
                villa_details = f"{villa_info['area']} · {villa_info['price']}"
                object_text = f"{villa_name} ({villa_details})"
            elif data['villa'] == "Расчёт ипотеки":
                object_text = "Расчёт ипотеки"
            else:
                object_text = "Общий запрос"
            
            message = f"""🏡 Лид на просмотр
Объект: {object_text}
Имя: {data['name']}
Телефон: {phone}
Телеграм: {username_text}
Бюджет: {data['budget']}
Время звонка: {data['time']}
UTM: {data.get('utm_source', 'Direct')}
Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"""
        
        await bot.send_message(config.SERVICE_CHAT_ID, message)
        logger.info(f"Лид отправлен в служебный чат: {lead_type}")
        
    except Exception as e:
        logger.error(f"Ошибка отправки в служебный чат: {e}")

# Клавиатуры
def get_start_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="📄 Смотреть виллы", callback_data="show_villas")],
        [InlineKeyboardButton(text="📥 Скачать презентацию", callback_data="get_pdf")],
        [InlineKeyboardButton(text="📅 Записаться на просмотр", callback_data="book_viewing")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_villas_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="Вилла №1 · 244 м² · 280 млн ₽", callback_data="villa1")],
        [InlineKeyboardButton(text="Вилла №2 · 242 м² · 200 млн ₽", callback_data="villa2")],
        [InlineKeyboardButton(text="🔄 Сравнить виллы", callback_data="compare_villas")],
        [InlineKeyboardButton(text="🏛 Назад в меню", callback_data="back_to_start")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_villa_keyboard(villa_id: str) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="📸 Показать фото", callback_data=f"photos_{villa_id}")],
        [InlineKeyboardButton(text="🎥 Видеообзор", callback_data=f"video_{villa_id}")],
        [InlineKeyboardButton(text="📅 Записаться на просмотр", callback_data=f"book_{villa_id}")],
        [InlineKeyboardButton(text="🔙 К выбору вилл", callback_data="show_villas")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_contact_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="📲 Отправить контакт", request_contact=True)],
        [KeyboardButton(text="✍️ Ввести номер вручную")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_budget_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="200 млн ₽"), KeyboardButton(text="280 млн ₽")],
        [KeyboardButton(text="Другой бюджет")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="📄 Смотреть виллы", callback_data="show_villas")],
        [InlineKeyboardButton(text="🔄 Сравнить виллы", callback_data="compare_villas")],
        [InlineKeyboardButton(text="🗺 О локации Сириус", callback_data="location_info")],
        [InlineKeyboardButton(text="💳 Ипотека / рассрочка", callback_data="mortgage_info")],
        [InlineKeyboardButton(text="👨‍💻 Хочешь такого бота?", url=config.DEVELOPER_URL)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 