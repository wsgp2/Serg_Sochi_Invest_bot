#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Обработчики команд и callback-ов для Sochi Invest Bot
"""

from aiogram import F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
from aiogram.fsm.context import FSMContext
from bot import (
    dp, bot, send_to_service_chat, VILLA_DATA,
    PDFForm, ViewingForm,
    get_start_keyboard, get_villas_keyboard, get_villa_keyboard,
    get_contact_keyboard, get_budget_keyboard, get_menu_keyboard
)
import config
import logging
from datetime import datetime
from user_manager import log_user_interaction

logger = logging.getLogger(__name__)

# Обработчики команд
@dp.message(CommandStart())
async def start_handler(message: Message):
    """Обработчик команды /start"""
    # Записываем пользователя в статистику
    await log_user_interaction(message.from_user, "start", message.chat.id)
    
    # Отправляем фото виллы с приветствием
    welcome_text = """🌅 Добро пожаловать в ПАНОРАМА 240!

Премиальные виллы в Сочи (ФТ «Сириус») с панорамным видом на море и горы.

✨ <b>WOW-факты:</b>
• 180° вид на Черное море и Олимпийский парк
• 10 минут до центра Сириуса
• Готовые к проживанию с бассейном и премиальной отделкой

Выберите действие:"""
    
    # Отправляем фото первой виллы
    from media_manager import get_villa_photos
    photos = get_villa_photos("villa1", max_photos=1)
    
    if photos:
        # Меняем caption на приветственный текст
        photos[0].caption = welcome_text
        await message.answer_photo(
            photo=photos[0].media,
            caption=welcome_text,
            reply_markup=get_start_keyboard()
        )
    else:
        # Если фото не найдено, отправляем только текст
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

@dp.message(Command("villa1"))
async def villa1_command_handler(message: Message):
    """Обработчик команды /villa1"""
    villa = VILLA_DATA.get("villa1")
    if villa:
        await message.answer(
            villa["description"],
            reply_markup=get_villa_keyboard("villa1")
        )

@dp.message(Command("villa2"))
async def villa2_command_handler(message: Message):
    """Обработчик команды /villa2"""
    villa = VILLA_DATA.get("villa2")
    if villa:
        await message.answer(
            villa["description"],
            reply_markup=get_villa_keyboard("villa2")
        )

@dp.message(Command("location"))
async def location_command_handler(message: Message):
    """Обработчик команды /location"""
    text = """🗺 <b>О локации ФТ «Сириус»</b>

🎯 <b>Уникальное расположение:</b>
• 10 минут до центра Сириуса
• 15 минут до Олимпийского парка
• 20 минут до аэропорта Сочи
• Панорамный вид на Черное море

🏛 <b>Инфраструктура рядом:</b>
• Поющие фонтаны Сириуса
• Сочи-Парк (крупнейший тематический парк России)
• Ледовый дворец «Большой»
• Трасса «Формула-1»
• Красная Поляна (45 минут)

🌊 <b>Природа и отдых:</b>
• Собственный пляж в 5 минутах
• Горные маршруты
• Субтропический климат круглый год

💎 <b>Инвестиционная привлекательность:</b>
• Высокий спрос на аренду
• Стабильный рост цен на недвижимость
• Развитая туристическая инфраструктура"""

    keyboard = [
        [InlineKeyboardButton(text="📸 Фото локации", callback_data="location_photos")],
        [InlineKeyboardButton(text="🏠 Смотреть виллы", callback_data="show_villas")],
        [InlineKeyboardButton(text="📅 Записаться на просмотр", callback_data="book_viewing")]
    ]
    
    await message.answer(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

@dp.message(Command("compare"))
async def compare_command_handler(message: Message):
    """Обработчик команды /compare"""
    text = """🔄 <b>Сравнение вилл ПАНОРАМА 240</b>

| Параметр | Вилла №1 | Вилла №2 |
|----------|----------|----------|
| <b>Площадь</b> | 244 м² | 242 м² |
| <b>Участок</b> | 4,08 сот. | 4,05 сот. |
| <b>Цена</b> | 280 млн ₽ | 200 млн ₽ |
| <b>Статус</b> | Готова | Готова |
| <b>Бассейн</b> | Compass Brilliant 77 | Compass Brilliant 77 |
| <b>Вид</b> | 180° море + горы | 180° море + горы |

<b>Общие характеристики:</b>
• Панорамные окна Alutech
• Премиальный фасад KMEW
• Все коммуникации подведены
• 10 минут до центра Сириуса"""

    keyboard = [
        [InlineKeyboardButton(text="🏠 Выбрать Виллу №1", callback_data="villa1")],
        [InlineKeyboardButton(text="🏠 Выбрать Виллу №2", callback_data="villa2")],
        [InlineKeyboardButton(text="🔙 К выбору вилл", callback_data="show_villas")]
    ]
    
    await message.answer(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

@dp.message(Command("mortgage"))
async def mortgage_command_handler(message: Message):
    """Обработчик команды /mortgage"""
    text = """💳 <b>Ипотека и рассрочка</b>

🏦 <b>Ипотечные программы:</b>
• Льготная ипотека от 8,9%
• Первоначальный взнос от 20%
• Срок кредитования до 25 лет
• Возможность рефинансирования

💰 <b>Рассрочка от застройщика:</b>
• Без процентов до 24 месяцев
• Первоначальный взнос от 30%
• Гибкий график платежей

📊 <b>Пример расчёта (Вилла №1 - 280 млн ₽):</b>
• Первоначальный взнос: 56 млн ₽ (20%)
• Сумма кредита: 224 млн ₽
• Ежемесячный платёж: ~2,1 млн ₽ (при 9% на 15 лет)

📈 <b>Окупаемость через аренду:</b>
• Доходность: 8-12% годовых
• Стоимость суток: 50-80 тыс. ₽
• Загрузка: 150-200 дней в году

*Расчёт индивидуален и зависит от банка"""

    keyboard = [
        [InlineKeyboardButton(text="📊 Запросить точный расчёт", callback_data="request_calculation")],
        [InlineKeyboardButton(text="🏠 Смотреть виллы", callback_data="show_villas")]
    ]
    
    await message.answer(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

@dp.message(Command("contact"))
async def contact_command_handler(message: Message):
    """Обработчик команды /contact"""
    text = """📞 <b>Связаться с экспертом</b>

Наш специалист ответит на все вопросы о виллах ПАНОРАМА 240:

👨‍💼 <b>Семён</b>
📱 Telegram: @mareevsv

🕐 <b>График работы:</b>
Понедельник - Воскресенье: 9:00 - 21:00 (МСК)

💬 <b>Консультации:</b>
• Подбор виллы под ваши требования
• Расчёт ипотеки и доходности
• Организация просмотра
• Юридическое сопровождение сделки"""

    keyboard = [
        [InlineKeyboardButton(text="💬 Написать в Telegram", url="https://t.me/mareevsv")],
        [InlineKeyboardButton(text="📅 Записаться на просмотр", callback_data="book_viewing")],
        [InlineKeyboardButton(text="🏠 Смотреть виллы", callback_data="show_villas")]
    ]
    
    await message.answer(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

@dp.message(Command("help"))
async def help_command_handler(message: Message):
    """Обработчик команды /help"""
    text = """❓ <b>Помощь по боту</b>

🤖 <b>Доступные команды:</b>
/start - 🏠 Начать знакомство с ПАНОРАМА 240
/villa1 - 🏘️ Вилла №1 (244 м², 280 млн ₽)
/villa2 - 🏘️ Вилла №2 (242 м², 200 млн ₽)
/location - 📍 Локация и инфраструктура Сириуса
/compare - ⚖️ Сравнить виллы
/mortgage - 💳 Ипотечные программы
/contact - 📞 Связаться с экспертом
/menu - ☰ Дополнительное меню

🔧 <b>Возможности бота:</b>
• Просмотр фотогалерей вилл
• Скачивание презентации с планировками
• Запись на просмотр объектов
• Расчёт ипотеки и доходности
• Информация о локации Сириус

📞 <b>Нужна помощь?</b>
Свяжитесь с нашим экспертом: @mareevsv"""

    keyboard = [
        [InlineKeyboardButton(text="🏠 Смотреть виллы", callback_data="show_villas")],
        [InlineKeyboardButton(text="📥 Скачать презентацию", callback_data="get_pdf")],
        [InlineKeyboardButton(text="📞 Связаться с экспертом", url="https://t.me/mareevsv")]
    ]
    
    await message.answer(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

# Обработчики callback-ов
@dp.callback_query(F.data == "get_pdf")
async def get_pdf_handler(callback: CallbackQuery, state: FSMContext):
    """Начало процесса получения PDF"""
    text = """📥 <b>Скачайте презентацию с 20 фото, планировками и расчётом доходности</b>

Получите полную информацию о виллах:
• Детальные планировки всех этажей
• Профессиональные фотографии
• Расчёт доходности от посуточной аренды
• Информация о локации и инфраструктуре

Для получения презентации укажите ваше имя:"""
    
    # Проверяем тип сообщения - фото или текст
    if callback.message.photo:
        await callback.message.edit_caption(caption=text, reply_markup=None)
    else:
        await callback.message.edit_text(text, reply_markup=None)
    
    await state.set_state(PDFForm.waiting_name)
    await callback.answer()

@dp.callback_query(F.data == "show_villas")
async def show_villas_handler(callback: CallbackQuery):
    """Показ витрины вилл"""
    text = """🏘 <b>Выберите виллу для подробного просмотра</b>

Обе виллы расположены в премиальном районе ФТ «Сириус» с панорамным видом на море:"""
    
    # Проверяем тип сообщения - фото или текст
    if callback.message.photo:
        await callback.message.edit_caption(
            caption=text,
            reply_markup=get_villas_keyboard()
        )
    else:
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
        # Проверяем тип сообщения - фото или текст
        if callback.message.photo:
            await callback.message.edit_caption(
                caption=villa["description"],
                reply_markup=get_villa_keyboard(villa_id)
            )
        else:
            await callback.message.edit_text(
                villa["description"],
                reply_markup=get_villa_keyboard(villa_id)
            )
    await callback.answer()

@dp.callback_query(F.data.startswith("photos_"))
async def photos_handler(callback: CallbackQuery):
    """Показ фотогалереи виллы"""
    villa_id = callback.data.replace("photos_", "")
    villa = VILLA_DATA.get(villa_id)
    
    if villa:
        # Импортируем медиа-менеджер
        from media_manager import get_villa_photos, get_remaining_villa_photos, get_villa_video
        
        try:
            # Получаем первые 4 фотографии виллы
            photos = get_villa_photos(villa_id, max_photos=4)
            
            if photos:
                # Отправляем первую группу фотографий
                await bot.send_media_group(callback.message.chat.id, photos)
                
                # Получаем оставшиеся фотографии (для villa2 их может быть 3 дополнительных)
                remaining_photos = get_remaining_villa_photos(villa_id, start_from=4)
                if remaining_photos:
                    # Отправляем вторую группу с небольшой задержкой
                    import asyncio
                    await asyncio.sleep(1)
                    await bot.send_media_group(callback.message.chat.id, remaining_photos)
                
                # Проверяем наличие видео
                video_path = get_villa_video(villa_id)
                if video_path:
                    await asyncio.sleep(1)  # Задержка перед отправкой видео
                    await bot.send_video(
                        callback.message.chat.id,
                        video=FSInputFile(video_path),
                        caption=f"🎥 Видеообзор {villa['name']}",
                        request_timeout=60  # Увеличиваем таймаут для больших видео
                    )
            else:
                # Если фото не загружены, показываем ссылку
                await callback.message.answer(
                    f"📸 Фотогалерея {villa['name']}\n\n" +
                    "Профессиональные фотографии виллы доступны по ссылке:\n\n" +
                    f"🔗 {config.PDF_DRIVE_URL}\n\n" +
                    "⬇️ Добавьте фотографии в папку media/ для автоматического показа"
                )
                
        except Exception as e:
            logger.error(f"Ошибка при отправке фотографий {villa_id}: {e}")
            await callback.message.answer(
                f"📸 Фотогалерея {villa['name']}\n\n" +
                "Возникла ошибка при загрузке фотографий.\n" +
                f"Посмотрите фото и планировки здесь: {config.PDF_DRIVE_URL}"
            )
    await callback.answer()

@dp.callback_query(F.data.startswith("video_"))
async def video_handler(callback: CallbackQuery):
    """Показ видеообзора виллы"""
    villa_id = callback.data.replace("video_", "")
    villa = VILLA_DATA.get(villa_id)
    
    if villa:
        from media_manager import get_all_villa_videos
        
        try:
            videos = get_all_villa_videos(villa_id)
            if videos:
                # Отправляем все доступные видео виллы
                for i, video_path in enumerate(videos):
                    if i > 0:
                        import asyncio
                        await asyncio.sleep(2)  # Задержка между видео
                    
                    video_captions = {
                        0: f"🎥 <b>Основной видеообзор {villa['name']}</b>\n\nДетальный осмотр виллы и территории",
                        1: f"🌅 <b>Дополнительное видео {villa['name']}</b>\n\nВиды и атмосфера локации",
                        2: f"🏠 <b>Архитектурный обзор {villa['name']}</b>\n\nДетали фасада и планировки"
                    }
                    
                    caption = video_captions.get(i, f"🎥 <b>Видео {villa['name']}</b>")
                    
                    await bot.send_video(
                        callback.message.chat.id,
                        video=FSInputFile(video_path),
                        caption=caption,
                        request_timeout=60  # Увеличенный таймаут
                    )
            else:
                await callback.message.answer(
                    f"🎥 <b>Видеообзор {villa['name']}</b>\n\n" +
                    "Видеообзор виллы будет доступен в ближайшее время.\n\n" +
                    f"🔗 А пока смотрите фотографии: {config.PDF_DRIVE_URL}\n\n" +
                    "⬇️ Добавьте видео в папку media/ для автоматической отправки"
                )
        except Exception as e:
            logger.error(f"Ошибка при отправке видео {villa_id}: {e}")
            await callback.message.answer(
                f"🎥 <b>Видеообзор {villa['name']}</b>\n\n" +
                "Возникла ошибка при загрузке видео.\n" +
                f"Посмотрите материалы здесь: {config.PDF_DRIVE_URL}"
            )
    await callback.answer()



@dp.callback_query(F.data.startswith("book"))
async def book_viewing_handler(callback: CallbackQuery, state: FSMContext):
    """Начало записи на просмотр"""
    if callback.data.startswith("book_"):
        villa_id = callback.data.replace("book_", "")
        villa = VILLA_DATA.get(villa_id)
        
        if villa:
            await state.update_data(villa=villa_id)
            text = f"📅 <b>Запись на просмотр {villa['name']}</b>\n\nДля записи на просмотр укажите ваше имя:"
        else:
            # Если villa_id неверный, используем общий текст
            text = "📅 <b>Запись на просмотр</b>\n\nДля записи на просмотр укажите ваше имя:"
    else:
        text = "📅 <b>Запись на просмотр</b>\n\nДля записи на просмотр укажите ваше имя:"
    
    # Проверяем тип сообщения - фото или текст
    if callback.message.photo:
        await callback.message.edit_caption(caption=text, reply_markup=None)
    else:
        await callback.message.edit_text(text, reply_markup=None)
    
    await state.set_state(ViewingForm.waiting_name)
    
    # Защита от истекших callback query
    try:
        await callback.answer()
    except Exception as e:
        logger.warning(f"Не удалось ответить на callback query: {e}")

@dp.callback_query(F.data == "compare_villas")
async def compare_villas_handler(callback: CallbackQuery):
    """Сравнение вилл"""
    text = """🔄 <b>Сравнение вилл ПАНОРАМА 240</b>

| Параметр | Вилла №1 | Вилла №2 |
|----------|----------|----------|
| <b>Площадь</b> | 244 м² | 242 м² |
| <b>Участок</b> | 4,08 сот. | 4,05 сот. |
| <b>Цена</b> | 280 млн ₽ | 200 млн ₽ |
| <b>Статус</b> | Готова | Готова |
| <b>Бассейн</b> | Compass Brilliant 77 | Compass Brilliant 77 |
| <b>Вид</b> | 180° море + горы | 180° море + горы |

<b>Общие характеристики:</b>
• Панорамные окна Alutech
• Премиальный фасад KMEW
• Все коммуникации подведены
• 10 минут до центра Сириуса"""

    keyboard = [
        [InlineKeyboardButton(text="🏠 Выбрать Виллу №1", callback_data="villa1")],
        [InlineKeyboardButton(text="🏠 Выбрать Виллу №2", callback_data="villa2")],
        [InlineKeyboardButton(text="🔙 К выбору вилл", callback_data="show_villas")]
    ]
    
    # Проверяем тип сообщения - фото или текст
    if callback.message.photo:
        await callback.message.edit_caption(
            caption=text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
    else:
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
    await callback.answer()

@dp.callback_query(F.data == "location_info")
async def location_info_handler(callback: CallbackQuery):
    """Информация о локации"""
    text = """🗺 <b>О локации ФТ «Сириус»</b>

🎯 <b>Уникальное расположение:</b>
• 10 минут до центра Сириуса
• 15 минут до Олимпийского парка
• 20 минут до аэропорта Сочи
• Панорамный вид на Черное море

🏛 <b>Инфраструктура рядом:</b>
• Поющие фонтаны Сириуса
• Сочи-Парк (крупнейший тематический парк России)
• Ледовый дворец «Большой»
• Трасса «Формула-1»
• Красная Поляна (45 минут)

🌊 <b>Природа и отдых:</b>
• Собственный пляж в 5 минутах
• Горные маршруты
• Субтропический климат круглый год

💎 <b>Инвестиционная привлекательность:</b>
• Высокий спрос на аренду
• Стабильный рост цен на недвижимость
• Развитая туристическая инфраструктура"""

    keyboard = [
        [InlineKeyboardButton(text="📸 Фото локации", callback_data="location_photos")],
        [InlineKeyboardButton(text="🏠 Смотреть виллы", callback_data="show_villas")],
        [InlineKeyboardButton(text="📅 Записаться на просмотр", callback_data="book_viewing")]
    ]
    
    # Проверяем тип сообщения - фото или текст
    if callback.message.photo:
        await callback.message.edit_caption(
            caption=text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
    else:
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
    await callback.answer()

@dp.callback_query(F.data == "location_photos")
async def location_photos_handler(callback: CallbackQuery):
    """Показ фотографий локации"""
    from media_manager import get_location_photos
    
    photos = get_location_photos()
    
    if photos:
        await bot.send_media_group(callback.message.chat.id, photos)
        await callback.message.answer(
            "🗺 <b>Все это в 10-15 минутах от ваших вилл!</b>\n\n" +
            "Идеальное расположение для инвестиций и отдыха."
        )
    else:
        await callback.message.answer(
            "📸 <b>Фотографии локации ФТ «Сириус»</b>\n\n" +
            "Поющие фонтаны, Олимпийский парк, Сочи-Парк - все в нескольких минутах от вилл!\n\n" +
            f"🔗 Больше фото: {config.PDF_DRIVE_URL}\n\n" +
            "⬇️ Добавьте фото локации в папку media/location/ для автоматического показа"
        )
    await callback.answer()

@dp.callback_query(F.data == "mortgage_info")
async def mortgage_info_handler(callback: CallbackQuery):
    """Информация об ипотеке"""
    text = """💳 <b>Ипотека и рассрочка</b>

🏦 <b>Ипотечные программы:</b>
• Льготная ипотека от 8,9%
• Первоначальный взнос от 20%
• Срок кредитования до 25 лет
• Возможность рефинансирования

💰 <b>Рассрочка от застройщика:</b>
• Без процентов до 24 месяцев
• Первоначальный взнос от 30%
• Гибкий график платежей

📊 <b>Пример расчёта (Вилла №1 - 280 млн ₽):</b>
• Первоначальный взнос: 56 млн ₽ (20%)
• Сумма кредита: 224 млн ₽
• Ежемесячный платёж: ~2,1 млн ₽ (при 9% на 15 лет)

📈 <b>Окупаемость через аренду:</b>
• Доходность: 8-12% годовых
• Стоимость суток: 50-80 тыс. ₽
• Загрузка: 150-200 дней в году

*Расчёт индивидуален и зависит от банка"""

    keyboard = [
        [InlineKeyboardButton(text="📊 Запросить точный расчёт", callback_data="request_calculation")],
        [InlineKeyboardButton(text="🏠 Смотреть виллы", callback_data="show_villas")]
    ]
    
    # Проверяем тип сообщения - фото или текст
    if callback.message.photo:
        await callback.message.edit_caption(
            caption=text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
    else:
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
    await callback.answer()

@dp.callback_query(F.data == "request_calculation")
async def request_calculation_handler(callback: CallbackQuery, state: FSMContext):
    """Запрос расчёта ипотеки"""
    text = "📊 <b>Запрос расчёта ипотеки</b>\n\nДля подготовки индивидуального расчёта укажите ваше имя:"
    
    # Проверяем тип сообщения - фото или текст
    if callback.message.photo:
        await callback.message.edit_caption(caption=text, reply_markup=None)
    else:
        await callback.message.edit_text(text, reply_markup=None)
    
    await state.set_state(ViewingForm.waiting_name)
    await state.update_data(calculation_request=True)
    await callback.answer()

@dp.callback_query(F.data == "back_to_start")
async def back_to_start_handler(callback: CallbackQuery):
    """Возврат в стартовое меню"""
    welcome_text = """🌅 Добро пожаловать в ПАНОРАМА 240!

Премиальные виллы в Сочи (ФТ «Сириус») с панорамным видом на море и горы.

✨ <b>WOW-факты:</b>
• 180° вид на Черное море и Олимпийский парк
• 10 минут до центра Сириуса
• Готовые к проживанию с бассейном и премиальной отделкой

Выберите действие:"""
    
    # Проверяем тип сообщения - фото или текст
    if callback.message.photo:
        await callback.message.edit_caption(
            caption=welcome_text,
            reply_markup=get_start_keyboard()
        )
    else:
        await callback.message.edit_text(
            welcome_text,
            reply_markup=get_start_keyboard()
        )
    await callback.answer()

# Команды статистики (только для служебного чата)
@dp.message(Command("stats"))
async def stats_handler(message: Message):
    """Получение статистики пользователей (только для служебного чата)"""
    from user_manager import get_user_stats
    from config import SERVICE_CHAT_ID
    
    # Проверяем, что команда вызвана из служебного чата
    logger.info(f"Команда /stats вызвана в чате {message.chat.id}, служебный чат: {SERVICE_CHAT_ID}")
    
    if message.chat.id != SERVICE_CHAT_ID:
        await message.answer("❌ Команда доступна только в служебном чате")
        return
    
    try:
        stats = get_user_stats()
        
        stats_text = f"""📊 <b>Статистика Sochi Invest Bot</b>

👥 <b>Пользователи:</b>
• Всего пользователей: {stats['total_users']}
• Активных сегодня: {stats['today_users']}

🎯 <b>Лиды:</b>
• Всего лидов: {stats['total_leads']}
• PDF загрузок: {stats['pdf_leads']}
• Записей на просмотр: {stats['viewing_leads']}

📈 <b>Конверсия:</b>
• Общая конверсия: {stats['conversion_rate']}%

⏰ Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"""
        
        await message.answer(stats_text)
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        await message.answer("❌ Ошибка получения статистики")

@dp.message(Command("users"))
async def users_handler(message: Message):
    """Получение списка последних пользователей (только для служебного чата)"""
    from user_manager import get_recent_users
    from config import SERVICE_CHAT_ID
    
    # Проверяем, что команда вызвана из служебного чата
    logger.info(f"Команда /users вызвана в чате {message.chat.id}, служебный чат: {SERVICE_CHAT_ID}")
    
    if message.chat.id != SERVICE_CHAT_ID:
        await message.answer("❌ Команда доступна только в служебном чате")
        return
    
    try:
        recent_users = get_recent_users(15)
        
        if not recent_users:
            await message.answer("👥 Пользователей пока нет")
            return
        
        users_text = "👥 <b>Последние пользователи:</b>\n\n"
        
        for i, user in enumerate(recent_users, 1):
            name = user['name'] or 'Без имени'
            username = f"@{user['username']}" if user['username'] else 'Без username'
            last_time = user['last_interaction']
            interactions = user['total_interactions']
            
            # Форматируем время
            if last_time:
                last_date = datetime.fromisoformat(last_time)
                time_str = last_date.strftime('%d.%m %H:%M')
            else:
                time_str = 'Неизвестно'
            
            users_text += f"{i}. {name} ({username})\n"
            users_text += f"   ID: {user['user_id']}\n"
            users_text += f"   Последняя активность: {time_str}\n"
            users_text += f"   Всего взаимодействий: {interactions}\n\n"
        
        await message.answer(users_text)
        
    except Exception as e:
        logger.error(f"Ошибка получения пользователей: {e}")
        await message.answer("❌ Ошибка получения списка пользователей")

# Команда отладки
@dp.message(Command("debug"))
async def debug_handler(message: Message):
    """Отладочная информация о чате и настройках"""
    from config import SERVICE_CHAT_ID
    
    debug_text = f"""🔧 <b>Отладочная информация</b>

💬 <b>Текущий чат:</b>
• ID: {message.chat.id}
• Тип: {message.chat.type}
• Название: {message.chat.title or 'Личный чат'}

⚙️ <b>Настройки бота:</b>
• Служебный чат ID: {SERVICE_CHAT_ID}
• Доступ к статистике: {'✅ Да' if message.chat.id == SERVICE_CHAT_ID else '❌ Нет'}

👤 <b>Пользователь:</b>
• ID: {message.from_user.id}
• Имя: {message.from_user.first_name}
• Username: @{message.from_user.username or 'Не указан'}"""
    
    await message.answer(debug_text)

# Универсальные команды статистики для администраторов
@dp.message(Command("admin_stats"))
async def admin_stats_handler(message: Message):
    """Статистика для администраторов (работает в любом чате для разрешенных пользователей)"""
    from user_manager import get_user_stats
    from config import SERVICE_CHAT_ID
    
    # Список ID администраторов (добавьте свои ID)
    ADMIN_IDS = [531712920]  # Добавьте ID администраторов
    
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ У вас нет прав администратора")
        return
    
    try:
        stats = get_user_stats()
        
        stats_text = f"""📊 <b>Статистика Sochi Invest Bot</b>

👥 <b>Пользователи:</b>
• Всего пользователей: {stats['total_users']}
• Активных сегодня: {stats['today_users']}

🎯 <b>Лиды:</b>
• Всего лидов: {stats['total_leads']}
• PDF загрузок: {stats['pdf_leads']}
• Записей на просмотр: {stats['viewing_leads']}

📈 <b>Конверсия:</b>
• Общая конверсия: {stats['conversion_rate']}%

💬 <b>Чаты:</b>
• Текущий чат: {message.chat.id}
• Служебный чат: {SERVICE_CHAT_ID}

⏰ Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"""
        
        await message.answer(stats_text)
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики админом: {e}")
        await message.answer("❌ Ошибка получения статистики")

@dp.message(Command("admin_users"))
async def admin_users_handler(message: Message):
    """Список пользователей для администраторов"""
    from user_manager import get_recent_users
    
    # Список ID администраторов
    ADMIN_IDS = [531712920]  # Добавьте ID администраторов
    
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ У вас нет прав администратора")
        return
    
    try:
        recent_users = get_recent_users(10)
        
        if not recent_users:
            await message.answer("👥 Пользователей пока нет")
            return
        
        users_text = "👥 <b>Последние пользователи:</b>\n\n"
        
        for i, user in enumerate(recent_users, 1):
            name = user['name'] or 'Без имени'
            username = f"@{user['username']}" if user['username'] else 'Без username'
            last_time = user['last_interaction']
            interactions = user['total_interactions']
            
            # Форматируем время
            if last_time:
                last_date = datetime.fromisoformat(last_time)
                time_str = last_date.strftime('%d.%m %H:%M')
            else:
                time_str = 'Неизвестно'
            
            users_text += f"{i}. {name} ({username})\n"
            users_text += f"   ID: {user['user_id']}\n"
            users_text += f"   Активность: {time_str} ({interactions} взаим.)\n\n"
        
        await message.answer(users_text)
        
    except Exception as e:
        logger.error(f"Ошибка получения пользователей админом: {e}")
        await message.answer("❌ Ошибка получения списка пользователей")

 