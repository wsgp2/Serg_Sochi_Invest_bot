#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Менеджер пользователей для Sochi Invest Bot
Отслеживание всех пользователей и статистика
"""

import json
import os
import logging
from datetime import datetime
from aiogram.types import User
from typing import Dict, Any, List
from config import SERVICE_CHAT_ID

logger = logging.getLogger(__name__)

# Путь к файлу с данными пользователей
USERS_FILE = "data/users.json"
LEADS_FILE = "data/leads.json"

def ensure_data_directory():
    """Создание директории data если не существует"""
    os.makedirs("data", exist_ok=True)

def load_users() -> Dict[str, Any]:
    """Загрузка данных пользователей из файла"""
    ensure_data_directory()
    
    if not os.path.exists(USERS_FILE):
        return {}
    
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки пользователей: {e}")
        return {}

def save_users(users_data: Dict[str, Any]):
    """Сохранение данных пользователей в файл"""
    ensure_data_directory()
    
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения пользователей: {e}")

def load_leads() -> Dict[str, Any]:
    """Загрузка данных лидов из файла"""
    ensure_data_directory()
    
    if not os.path.exists(LEADS_FILE):
        return {}
    
    try:
        with open(LEADS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки лидов: {e}")
        return {}

def save_leads(leads_data: Dict[str, Any]):
    """Сохранение данных лидов в файл"""
    ensure_data_directory()
    
    try:
        with open(LEADS_FILE, 'w', encoding='utf-8') as f:
            json.dump(leads_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения лидов: {e}")

async def log_user_interaction(user: User, action: str, chat_id: int):
    """Логирование взаимодействия пользователя с ботом"""
    users_data = load_users()
    user_id = str(user.id)
    current_time = datetime.now().isoformat()
    
    # Создаем или обновляем данные пользователя
    if user_id not in users_data:
        users_data[user_id] = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "first_interaction": current_time,
            "interactions": [],
            "total_interactions": 0,
            "is_bot": user.is_bot,
            "language_code": user.language_code
        }
        
        # Уведомляем о новом пользователе в служебный чат
        from bot import bot
        try:
            new_user_text = f"""👤 <b>Новый пользователь!</b>

🆔 ID: {user.id}
👤 Имя: {user.first_name or 'Не указано'}
👤 Фамилия: {user.last_name or 'Не указано'}
📱 Username: @{user.username or 'Не указано'}
🗣 Язык: {user.language_code or 'Не указан'}
⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
🎯 Первое действие: {action}"""
            
            await bot.send_message(
                chat_id=SERVICE_CHAT_ID,
                text=new_user_text
            )
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления о новом пользователе: {e}")
    
    # Обновляем данные
    users_data[user_id]["last_interaction"] = current_time
    users_data[user_id]["total_interactions"] += 1
    users_data[user_id]["interactions"].append({
        "action": action,
        "time": current_time,
        "chat_id": chat_id
    })
    
    # Ограничиваем историю взаимодействий последними 50 действиями
    if len(users_data[user_id]["interactions"]) > 50:
        users_data[user_id]["interactions"] = users_data[user_id]["interactions"][-50:]
    
    save_users(users_data)
    logger.info(f"Взаимодействие пользователя {user_id} ({action}) сохранено")

async def log_lead(user_id: int, lead_type: str, lead_data: Dict[str, Any]):
    """Логирование лида (заявки)"""
    leads_data = load_leads()
    lead_id = f"{user_id}_{lead_type}_{int(datetime.now().timestamp())}"
    current_time = datetime.now().isoformat()
    
    leads_data[lead_id] = {
        "user_id": user_id,
        "type": lead_type,
        "data": lead_data,
        "created_at": current_time
    }
    
    save_leads(leads_data)
    logger.info(f"Лид {lead_type} от пользователя {user_id} сохранен")

def get_user_stats() -> Dict[str, Any]:
    """Получение статистики пользователей"""
    users_data = load_users()
    leads_data = load_leads()
    
    total_users = len(users_data)
    total_leads = len(leads_data)
    
    # Подсчитываем уникальных пользователей за сегодня
    today = datetime.now().date()
    today_users = 0
    
    for user_data in users_data.values():
        last_interaction = user_data.get("last_interaction")
        if last_interaction:
            interaction_date = datetime.fromisoformat(last_interaction).date()
            if interaction_date == today:
                today_users += 1
    
    # Подсчитываем лиды по типам
    pdf_leads = sum(1 for lead in leads_data.values() if lead["type"] == "pdf")
    viewing_leads = sum(1 for lead in leads_data.values() if lead["type"] == "viewing")
    
    return {
        "total_users": total_users,
        "today_users": today_users,
        "total_leads": total_leads,
        "pdf_leads": pdf_leads,
        "viewing_leads": viewing_leads,
        "conversion_rate": round((total_leads / total_users * 100) if total_users > 0 else 0, 2)
    }

def get_recent_users(limit: int = 10) -> List[Dict[str, Any]]:
    """Получение последних пользователей"""
    users_data = load_users()
    
    # Сортируем по времени последнего взаимодействия
    sorted_users = sorted(
        users_data.items(),
        key=lambda x: x[1].get("last_interaction", ""),
        reverse=True
    )
    
    recent_users = []
    for user_id, user_data in sorted_users[:limit]:
        recent_users.append({
            "user_id": user_id,
            "name": f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
            "username": user_data.get('username'),
            "last_interaction": user_data.get('last_interaction'),
            "total_interactions": user_data.get('total_interactions', 0)
        })
    
    return recent_users 