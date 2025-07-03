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
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    InputMediaPhoto, FSInputFile, Contact
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import config
import json
from typing import List, Dict, Any

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/sochi_invest_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# FSM States для форм
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

💰 **Цена: 280 млн ₽**""",
        "photos": [
            "https://drive.google.com/file/d/1_example_villa1_photo1/view",
            "https://drive.google.com/file/d/1_example_villa1_photo2/view",
            "https://drive.google.com/file/d/1_example_villa1_photo3/view"
        ],
        "planning": "https://drive.google.com/file/d/1_villa1_planning/view"
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

💰 **Цена: 200 млн ₽**""",
        "photos": [
            "https://drive.google.com/file/d/1_example_villa2_photo1/view",
            "https://drive.google.com/file/d/1_example_villa2_photo2/view",
            "https://drive.google.com/file/d/1_example_villa2_photo3/view"
        ],
        "planning": "https://drive.google.com/file/d/1_villa2_planning/view"
    }
}

# Клавиатуры
def get_start_keyboard() -> InlineKeyboardMarkup:
    """Стартовая клавиатура"""
    keyboard = [
        [InlineKeyboardButton(text="📄 Смотреть виллы", callback_data="show_villas")],
        [InlineKeyboardButton(text="📥 Скачать презентацию", callback_data="get_pdf")],
        [InlineKeyboardButton(text="📅 Записаться на просмотр", callback_data="book_viewing")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_villas_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора вилл"""
    keyboard = [
        [InlineKeyboardButton(text="Вилла №1 · 244 м² · 280 млн ₽", callback_data="villa1")],
        [InlineKeyboardButton(text="Вилла №2 · 242 м² · 200 млн ₽", callback_data="villa2")],
        [InlineKeyboardButton(text="🔄 Сравнить виллы", callback_data="compare_villas")],
        [InlineKeyboardButton(text="🏛 Назад в меню", callback_data="back_to_start")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_villa_keyboard(villa_id: str) -> InlineKeyboardMarkup:
    """Клавиатура для конкретной виллы"""
    keyboard = [
        [InlineKeyboardButton(text="📸 Показать фото", callback_data=f"photos_{villa_id}")],
        [InlineKeyboardButton(text="📋 Планировка", callback_data=f"planning_{villa_id}")],
        [InlineKeyboardButton(text="📅 Записаться на просмотр", callback_data=f"book_{villa_id}")],
        [InlineKeyboardButton(text="🔙 К выбору вилл", callback_data="show_villas")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_budget_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура выбора бюджета"""
    keyboard = [
        [KeyboardButton(text="200 млн ₽"), KeyboardButton(text="280 млн ₽")],
        [KeyboardButton(text="Другой бюджет")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_contact_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для отправки контакта"""
    keyboard = [
        [KeyboardButton(text="📲 Отправить контакт", request_contact=True)],
        [KeyboardButton(text="✍️ Ввести номер вручную")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_menu_keyboard() -> InlineKeyboardMarkup:
    """Дополнительное меню"""
    keyboard = [
        [InlineKeyboardButton(text="📄 Смотреть виллы", callback_data="show_villas")],
        [InlineKeyboardButton(text="🔄 Сравнить виллы", callback_data="compare_villas")],
        [InlineKeyboardButton(text="🗺 О локации Сириус", callback_data="location_info")],
        [InlineKeyboardButton(text="👨‍💻 Хочешь такого бота?", url="https://t.me/m/KL5XwR0sMWEy")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Функции для отправки в служебный чат
async def send_to_service_chat(lead_type: str, data: Dict[str, Any]):
    """Отправка лида в служебный чат"""
    try:
        if lead_type == "pdf":
            message = f"""🔔 Новый лид (PDF)
Имя: {data['name']}
Телефон: {data['phone']}
Источник: {data.get('utm_source', 'Direct')}
Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"""
        
        elif lead_type == "viewing":
            villa_info = VILLA_DATA.get(data['villa'], {})
            message = f"""🏡 Лид на просмотр
Объект: {villa_info.get('name', data['villa'])} ({villa_info.get('area', '')} · {villa_info.get('price', '')})
Имя: {data['name']}
Телефон: {data['phone']}
Бюджет: {data['budget']}
Время звонка: {data['time']}
UTM: {data.get('utm_source', 'Direct')}
Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"""
        
        await bot.send_message(config.SERVICE_CHAT_ID, message)
        logger.info(f"Лид отправлен в служебный чат: {lead_type}")
        
    except Exception as e:
        logger.error(f"Ошибка отправки в служебный чат: {e}")

# Обработчики команд
@dp.message(CommandStart())
async def start_handler(message: Message):
    """Обработчик команды /start"""
    welcome_text = """🌅 Добро пожаловать в ПАНОРАМА 240!

Премиальные виллы в Сочи (ФТ «Сириус») с панорамным видом на море и горы.

✨ **WOW-факты:**
• 180° вид на Черное море и Олимпийский парк
• 10 минут до центра Сириуса
• Готовые к проживанию с бассейном и премиальной отделкой

Выберите действие:"""
    
    await message.answer(
        welcome_text,
        reply_markup=get_start_keyboard()
    )

@dp.message(Command("menu"))
async def menu_handler(message: Message):
    """Обработчик команды /menu"""
    await message.answer(
        "☰ Дополнительное меню:",
        reply_markup=get_menu_keyboard()
    )

# Обработчики callback-ов
@dp.callback_query(F.data == "get_pdf")
async def get_pdf_handler(callback: CallbackQuery, state: FSMContext):
    """Начало процесса получения PDF"""
    text = """📥 **Скачайте презентацию с 20 фото, планировками и расчётом доходности**

Получите полную информацию о виллах:
• Детальные планировки всех этажей
• Профессиональные фотографии
• Расчёт доходности от посуточной аренды
• Информация о локации и инфраструктуре

Для получения презентации укажите ваше имя:"""
    
    await callback.message.edit_text(text)
    await state.set_state(PDFForm.waiting_name)
    await callback.answer()

@dp.callback_query(F.data == "show_villas")
async def show_villas_handler(callback: CallbackQuery):
    """Показ витрины вилл"""
    text = """🏘 **Выберите виллу для подробного просмотра**

Обе виллы расположены в премиальном районе ФТ «Сириус» с панорамным видом на море:"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_villas_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("villa"))
async def villa_handler(callback: CallbackQuery):
    """Показ карточки виллы"""
    villa_id = callback.data
    villa = VILLA_DATA.get(villa_id)
    
    if villa:
        await callback.message.edit_text(
            villa["description"],
            reply_markup=get_villa_keyboard(villa_id),
            parse_mode="Markdown"
        )
    await callback.answer()

@dp.callback_query(F.data.startswith("photos_"))
async def photos_handler(callback: CallbackQuery):
    """Показ фотогалереи виллы"""
    villa_id = callback.data.replace("photos_", "")
    villa = VILLA_DATA.get(villa_id)
    
    if villa:
        # В реальной версии здесь будут реальные media_group с фотографиями
        await callback.message.answer(
            f"📸 Фотогалерея {villa['name']}\n\n" +
            "Здесь будет отображена галерея из 3-5 профессиональных фотографий виллы.\n\n" +
            "🔗 Все фото доступны по ссылке: https://drive.google.com/drive/folders/1q4osO5PDLhwJig8cMY97g_hnQZP4sm9_"
        )
    await callback.answer()

@dp.callback_query(F.data.startswith("planning_"))
async def planning_handler(callback: CallbackQuery):
    """Показ планировки виллы"""
    villa_id = callback.data.replace("planning_", "")
    villa = VILLA_DATA.get(villa_id)
    
    if villa:
        await callback.message.answer(
            f"📋 Планировка {villa['name']}\n\n" +
            "Здесь будет отправлен файл с подробной планировкой всех этажей виллы."
        )
    await callback.answer()

@dp.callback_query(F.data.startswith("book"))
async def book_viewing_handler(callback: CallbackQuery, state: FSMContext):
    """Начало записи на просмотр"""
    if callback.data.startswith("book_"):
        villa_id = callback.data.replace("book_", "")
        await state.update_data(villa=villa_id)
        villa = VILLA_DATA.get(villa_id)
        text = f"📅 **Запись на просмотр {villa['name']}**\n\nДля записи на просмотр укажите ваше имя:"
    else:
        text = "📅 **Запись на просмотр**\n\nДля записи на просмотр укажите ваше имя:"
    
    await callback.message.edit_text(text)
    await state.set_state(ViewingForm.waiting_name)
    await callback.answer()

@dp.callback_query(F.data == "compare_villas")
async def compare_villas_handler(callback: CallbackQuery):
    """Сравнение вилл"""
    text = """🔄 **Сравнение вилл ПАНОРАМА 240**

| Параметр | Вилла №1 | Вилла №2 |
|----------|----------|----------|
| **Площадь** | 244 м² | 242 м² |
| **Участок** | 4,08 сот. | 4,05 сот. |
| **Цена** | 280 млн ₽ | 200 млн ₽ |
| **Статус** | Готова | Строится |
| **Бассейн** | Compass Brilliant 77 | Compass Brilliant 77 |
| **Вид** | 180° море + горы | 180° море + горы |

**Общие характеристики:**
• Панорамные окна Alutech
• Премиальный фасад KMEW
• Все коммуникации подведены
• 10 минут до центра Сириуса"""

    keyboard = [
        [InlineKeyboardButton(text="🏠 Выбрать Виллу №1", callback_data="villa1")],
        [InlineKeyboardButton(text="🏠 Выбрать Виллу №2", callback_data="villa2")],
        [InlineKeyboardButton(text="🔙 К выбору вилл", callback_data="show_villas")]
    ]
    
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback.answer()

@dp.callback_query(F.data == "location_info")
async def location_info_handler(callback: CallbackQuery):
    """Информация о локации"""
    text = """🗺 **О локации ФТ «Сириус»**

🎯 **Уникальное расположение:**
• 10 минут до центра Сириуса
• 15 минут до Олимпийского парка
• 20 минут до аэропорта Сочи
• Панорамный вид на Черное море

🏛 **Инфраструктура рядом:**
• Поющие фонтаны Сириуса
• Сочи-Парк (крупнейший тематический парк России)
• Ледовый дворец «Большой»
• Трасса «Формула-1»
• Красная Поляна (45 минут)

🌊 **Природа и отдых:**
• Собственный пляж в 5 минутах
• Горные маршруты
• Субтропический климат круглый год

💎 **Инвестиционная привлекательность:**
• Высокий спрос на аренду
• Стабильный рост цен на недвижимость
• Развитая туристическая инфраструктура"""

    keyboard = [
        [InlineKeyboardButton(text="🏠 Смотреть виллы", callback_data="show_villas")],
        [InlineKeyboardButton(text="📅 Записаться на просмотр", callback_data="book_viewing")]
    ]
    
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback.answer()



@dp.callback_query(F.data == "back_to_start")
async def back_to_start_handler(callback: CallbackQuery):
    """Возврат в стартовое меню"""
    welcome_text = """🌅 Добро пожаловать в ПАНОРАМА 240!

Премиальные виллы в Сочи (ФТ «Сириус») с панорамным видом на море и горы.

✨ **WOW-факты:**
• 180° вид на Черное море и Олимпийский парк
• 10 минут до центра Сириуса
• Готовые к проживанию с бассейном и премиальной отделкой

Выберите действие:"""
    
    await callback.message.edit_text(
        welcome_text,
        reply_markup=get_start_keyboard()
    )
    await callback.answer()

# Обработчики FSM форм
@dp.message(PDFForm.waiting_name)
async def pdf_name_handler(message: Message, state: FSMContext):
    """Обработка имени для PDF"""
    await state.update_data(name=message.text)
    await message.answer(
        "📱 Отлично! Теперь укажите ваш номер телефона:",
        reply_markup=get_contact_keyboard()
    )
    await state.set_state(PDFForm.waiting_phone)

@dp.message(PDFForm.waiting_phone)
async def pdf_phone_handler(message: Message, state: FSMContext):
    """Обработка телефона для PDF"""
    phone = None
    
    if message.contact:
        phone = message.contact.phone_number
    elif message.text:
        phone = message.text
    
    if phone:
        data = await state.get_data()
        await state.clear()
        
        # Отправка в служебный чат
        await send_to_service_chat("pdf", {
            "name": data["name"],
            "phone": phone,
            "utm_source": "Direct"
        })
        
        # Отправка PDF пользователю
        await message.answer(
            "📎 Презентация отправлена!\n\n" +
            "📥 Ссылка на полную презентацию:\n" +
            "https://drive.google.com/drive/folders/1q4osO5PDLhwJig8cMY97g_hnQZP4sm9_\n\n" +
            "Теперь посмотрите наши виллы:",
            reply_markup=ReplyKeyboardRemove()
        )
        
        # Показ вилл
        await message.answer(
            "🏘 **Выберите виллу для подробного просмотра**\n\n" +
            "Обе виллы расположены в премиальном районе ФТ «Сириус» с панорамным видом на море:",
            reply_markup=get_villas_keyboard()
        )
    else:
        await message.answer("Пожалуйста, отправьте корректный номер телефона")

@dp.message(ViewingForm.waiting_name)
async def viewing_name_handler(message: Message, state: FSMContext):
    """Обработка имени для записи"""
    await state.update_data(name=message.text)
    await message.answer(
        "📱 Отлично! Теперь укажите ваш номер телефона:",
        reply_markup=get_contact_keyboard()
    )
    await state.set_state(ViewingForm.waiting_phone)

@dp.message(ViewingForm.waiting_phone)
async def viewing_phone_handler(message: Message, state: FSMContext):
    """Обработка телефона для записи"""
    phone = None
    
    if message.contact:
        phone = message.contact.phone_number
    elif message.text:
        phone = message.text
    
    if phone:
        await state.update_data(phone=phone)
        
        await message.answer(
            "💰 Какой у вас предполагаемый бюджет?",
            reply_markup=get_budget_keyboard()
        )
        await state.set_state(ViewingForm.waiting_budget)
    else:
        await message.answer("Пожалуйста, отправьте корректный номер телефона")

@dp.message(ViewingForm.waiting_budget)
async def viewing_budget_handler(message: Message, state: FSMContext):
    """Обработка бюджета"""
    await state.update_data(budget=message.text)
    
    time_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Сегодня 14:00-15:00"), KeyboardButton(text="Сегодня 16:00-17:00")],
            [KeyboardButton(text="Завтра утром"), KeyboardButton(text="Завтра вечером")],
            [KeyboardButton(text="В рабочее время")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        "⏰ Когда вам удобно получить звонок менеджера?",
        reply_markup=time_keyboard
    )
    await state.set_state(ViewingForm.waiting_time)

@dp.message(ViewingForm.waiting_time)
async def viewing_time_handler(message: Message, state: FSMContext):
    """Завершение записи на просмотр"""
    data = await state.get_data()
    await state.clear()
    
    # Отправка в служебный чат
    await send_to_service_chat("viewing", {
        "name": data["name"],
        "phone": data["phone"],
        "villa": data.get("villa", "Не указана"),
        "budget": data["budget"],
        "time": message.text,
        "utm_source": "Direct"
    })
    
    await message.answer(
        "✅ **Спасибо! Заявка принята**\n\n" +
        "Наш менеджер свяжется с вами в течение 15 минут для подтверждения просмотра 👌\n\n" +
        "🏡 А пока можете изучить дополнительную информацию:",
        reply_markup=ReplyKeyboardRemove()
    )
    
    await message.answer(
        "Дополнительные возможности:",
        reply_markup=get_menu_keyboard()
    )

# Обработчик всех остальных сообщений
@dp.message()
async def unknown_message_handler(message: Message):
    """Обработчик неизвестных сообщений"""
    await message.answer(
        "🤔 Не понимаю ваш запрос.\n\n" +
        "Используйте кнопки меню или команду /start для начала работы.\n\n" +
        "💡 **Хотите такого же бота для вашего бизнеса?**\n" +
        "Обращайтесь к разработчику: @sergei_dyshkant",
        reply_markup=get_start_keyboard()
    )

async def main():
    """Главная функция запуска бота"""
    logger.info("🚀 Запуск Sochi Invest Bot...")
    
    # Создание директорий
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    try:
        # Запуск polling
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main()) 