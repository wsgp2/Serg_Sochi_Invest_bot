#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FSM обработчики форм для Sochi Invest Bot
"""

from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from bot import (
    bot, dp, send_to_service_chat, VILLA_DATA,
    PDFForm, ViewingForm,
    get_start_keyboard, get_villas_keyboard, get_contact_keyboard, get_budget_keyboard, get_menu_keyboard
)
import config
import logging
from user_manager import log_lead

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
        
        # Сохраняем лид в файл
        await log_lead(message.from_user.id, "pdf", {
            "name": data["name"],
            "phone": phone,
            "username": message.from_user.username,
            "utm_source": "Direct"
        })
        
        # Отправка в служебный чат
        await send_to_service_chat("pdf", {
            "name": data["name"],
            "phone": phone,
            "username": message.from_user.username,
            "utm_source": "Direct"
        })
        
        # Отправка PDF пользователю
        from media_manager import get_presentation_file
        from aiogram.types import FSInputFile
        
        pdf_path = get_presentation_file()
        if pdf_path:
            await bot.send_document(
                message.chat.id,
                document=FSInputFile(pdf_path),
                caption="📎 <b>Презентация ПАНОРАМА 240</b>\n\nПолная информация о виллах, планировки и расчёт доходности"
            )
        else:
            await message.answer(
                "📎 <b>Презентация готова!</b>\n\n" +
                "📥 Ссылка на полную презентацию с фотографиями и планировками:\n" +
                f"{config.PDF_DRIVE_URL}\n\n" +
                "⬇️ Добавьте файл презентации в папку media/common/ для автоматической отправки"
            )
        
        await message.answer(
            "Теперь посмотрите наши виллы подробнее:",
            reply_markup=ReplyKeyboardRemove()
        )
        
        # Показ вилл
        await message.answer(
            "🏘 <b>Выберите виллу для подробного просмотра</b>\n\n" +
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
            
            # Сохраняем лид в файл
            await log_lead(message.from_user.id, "viewing", {
                "name": data["name"],
                "phone": phone,
                "username": message.from_user.username,
                "villa": "Расчёт ипотеки",
                "budget": "Индивидуальный расчёт",
                "time": "В рабочее время",
                "utm_source": "Direct"
            })
            
            await send_to_service_chat("viewing", {
                "name": data["name"],
                "phone": phone,
                "username": message.from_user.username,
                "villa": "Расчёт ипотеки",
                "budget": "Индивидуальный расчёт",
                "time": "В рабочее время",
                "utm_source": "Direct"
            })
            
            await message.answer(
                "✅ <b>Запрос принят!</b>\n\n" +
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
    
    # Сохраняем лид в файл
    await log_lead(message.from_user.id, "viewing", {
        "name": data["name"],
        "phone": data["phone"],
        "username": message.from_user.username,
        "villa": villa_id,
        "budget": data["budget"],
        "time": message.text,
        "utm_source": "Direct"
    })
    
    # Отправка в служебный чат
    await send_to_service_chat("viewing", {
        "name": data["name"],
        "phone": data["phone"],
        "username": message.from_user.username,
        "villa": villa_id,
        "budget": data["budget"],
        "time": message.text,
        "utm_source": "Direct"
    })
    
    # Формируем ответ пользователю
    villa_text = ""
    if villa_info:
        villa_text = f"\n\n🏡 <b>Выбранная вилла:</b> {villa_info['name']} ({villa_info['area']} · {villa_info['price']})"
    
    await message.answer(
        f"✅ <b>Спасибо! Заявка принята</b>{villa_text}\n\n" +
        "Наш менеджер свяжется с вами в течение 15 минут для подтверждения просмотра 👌\n\n" +
        "🏡 А пока можете изучить дополнительную информацию:",
        reply_markup=ReplyKeyboardRemove()
    )
    
    await message.answer(
        "Дополнительные возможности:",
        reply_markup=get_menu_keyboard()
    )

# Обработчик неизвестных сообщений (должен быть в самом конце)
@dp.message()
async def unknown_message_handler(message: Message):
    """Обработчик неизвестных сообщений"""
    await message.answer(
        "🤔 Не понимаю ваш запрос.\n\n" +
        "Используйте кнопки меню или команду /start для начала работы.\n\n" +
        config.MESSAGES["developer_info"],
        reply_markup=get_start_keyboard()
    ) 