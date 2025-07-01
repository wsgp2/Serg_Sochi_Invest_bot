#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FSM обработчики форм для Sochi Invest Bot
"""

from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from bot import (
    dp, send_to_service_chat, VILLA_DATA,
    PDFForm, ViewingForm,
    get_villas_keyboard, get_contact_keyboard, get_budget_keyboard, get_menu_keyboard
)
import config
import logging

logger = logging.getLogger(__name__)

# Обработчики FSM форм для PDF
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
    elif message.text and message.text != "✍️ Ввести номер вручную":
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
            "📎 **Презентация готова!**\n\n" +
            "📥 Ссылка на полную презентацию с фотографиями и планировками:\n" +
            f"{config.PDF_DRIVE_URL}\n\n" +
            "Теперь посмотрите наши виллы подробнее:",
            reply_markup=ReplyKeyboardRemove()
        )
        
        # Показ вилл
        await message.answer(
            "🏘 **Выберите виллу для подробного просмотра**\n\n" +
            "Обе виллы расположены в премиальном районе ФТ «Сириус» с панорамным видом на море:",
            reply_markup=get_villas_keyboard()
        )
    else:
        await message.answer(
            "📱 Пожалуйста, отправьте корректный номер телефона или нажмите кнопку 'Отправить контакт'"
        )

# Обработчики FSM форм для записи на просмотр
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
    elif message.text and message.text != "✍️ Ввести номер вручную":
        phone = message.text
    
    if phone:
        await state.update_data(phone=phone)
        
        data = await state.get_data()
        
        # Проверяем, это запрос расчёта ипотеки
        if data.get("calculation_request"):
            # Завершаем запрос расчёта
            await state.clear()
            await send_to_service_chat("viewing", {
                "name": data["name"],
                "phone": phone,
                "villa": "Расчёт ипотеки",
                "budget": "Индивидуальный расчёт",
                "time": "В рабочее время",
                "utm_source": "Direct"
            })
            
            await message.answer(
                "✅ **Запрос принят!**\n\n" +
                "Наш менеджер подготовит индивидуальный расчёт ипотеки и свяжется с вами в течение 15 минут.\n\n" +
                "💡 А пока изучите информацию о виллах:",
                reply_markup=ReplyKeyboardRemove()
            )
            
            await message.answer(
                "Дополнительные возможности:",
                reply_markup=get_menu_keyboard()
            )
            return
        
        await message.answer(
            "💰 Какой у вас предполагаемый бюджет?",
            reply_markup=get_budget_keyboard()
        )
        await state.set_state(ViewingForm.waiting_budget)
    else:
        await message.answer(
            "📱 Пожалуйста, отправьте корректный номер телефона или нажмите кнопку 'Отправить контакт'"
        )

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
    
    # Определяем виллу
    villa_id = data.get("villa", "Не указана")
    villa_info = VILLA_DATA.get(villa_id, {})
    
    # Отправка в служебный чат
    await send_to_service_chat("viewing", {
        "name": data["name"],
        "phone": data["phone"],
        "villa": villa_id,
        "budget": data["budget"],
        "time": message.text,
        "utm_source": "Direct"
    })
    
    # Формируем ответ пользователю
    villa_text = ""
    if villa_info:
        villa_text = f"\n\n🏡 **Выбранная вилла:** {villa_info['name']} ({villa_info['area']} · {villa_info['price']})"
    
    await message.answer(
        f"✅ **Спасибо! Заявка принята**{villa_text}\n\n" +
        "Наш менеджер свяжется с вами в течение 15 минут для подтверждения просмотра 👌\n\n" +
        "🏡 А пока можете изучить дополнительную информацию:",
        reply_markup=ReplyKeyboardRemove()
    )
    
    await message.answer(
        "Дополнительные возможности:",
        reply_markup=get_menu_keyboard()
    ) 