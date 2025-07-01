#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Обработчики команд и callback-ов для Sochi Invest Bot
"""

from aiogram import F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from bot import (
    dp, bot, send_to_service_chat, VILLA_DATA,
    PDFForm, ViewingForm,
    get_start_keyboard, get_villas_keyboard, get_villa_keyboard,
    get_contact_keyboard, get_budget_keyboard, get_menu_keyboard
)
import config
import logging

logger = logging.getLogger(__name__)

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
        await callback.message.answer(
            f"📸 Фотогалерея {villa['name']}\n\n" +
            "Здесь будет отображена галерея из 3-5 профессиональных фотографий виллы.\n\n" +
            f"🔗 Все фото доступны по ссылке: {config.PDF_DRIVE_URL}"
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
| **Статус** | Готова | Готова |
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

@dp.callback_query(F.data == "mortgage_info")
async def mortgage_info_handler(callback: CallbackQuery):
    """Информация об ипотеке"""
    text = """💳 **Ипотека и рассрочка**

🏦 **Ипотечные программы:**
• Льготная ипотека от 8,9%
• Первоначальный взнос от 20%
• Срок кредитования до 25 лет
• Возможность рефинансирования

💰 **Рассрочка от застройщика:**
• Без процентов до 24 месяцев
• Первоначальный взнос от 30%
• Гибкий график платежей

📊 **Пример расчёта (Вилла №1 - 280 млн ₽):**
• Первоначальный взнос: 56 млн ₽ (20%)
• Сумма кредита: 224 млн ₽
• Ежемесячный платёж: ~2,1 млн ₽ (при 9% на 15 лет)

📈 **Окупаемость через аренду:**
• Доходность: 8-12% годовых
• Стоимость суток: 50-80 тыс. ₽
• Загрузка: 150-200 дней в году

*Расчёт индивидуален и зависит от банка"""

    keyboard = [
        [InlineKeyboardButton(text="📊 Запросить точный расчёт", callback_data="request_calculation")],
        [InlineKeyboardButton(text="🏠 Смотреть виллы", callback_data="show_villas")]
    ]
    
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback.answer()

@dp.callback_query(F.data == "request_calculation")
async def request_calculation_handler(callback: CallbackQuery, state: FSMContext):
    """Запрос расчёта ипотеки"""
    await callback.message.edit_text(
        "📊 **Запрос расчёта ипотеки**\n\nДля подготовки индивидуального расчёта укажите ваше имя:"
    )
    await state.set_state(ViewingForm.waiting_name)
    await state.update_data(calculation_request=True)
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

# Обработчик неизвестных сообщений
@dp.message()
async def unknown_message_handler(message: Message):
    """Обработчик неизвестных сообщений"""
    await message.answer(
        "🤔 Не понимаю ваш запрос.\n\n" +
        "Используйте кнопки меню или команду /start для начала работы.\n\n" +
        config.MESSAGES["developer_info"],
        reply_markup=get_start_keyboard()
    ) 