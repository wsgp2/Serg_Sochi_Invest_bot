#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Медиа-менеджер для Sochi Invest Bot
Управление фотографиями и видео в боте
"""

from aiogram.types import InputMediaPhoto, InputMediaVideo, FSInputFile
from typing import List, Dict, Any
import os
import logging

logger = logging.getLogger(__name__)

# Структура медиа файлов
VILLA_MEDIA = {
    "villa1": {
        "photos": [
            "media/villa1/photo1.jpg",
            "media/villa1/photo2.jpg", 
            "media/villa1/photo3.jpg",
            "media/villa1/photo4.jpg",
            "media/villa1/photo5.jpg"
        ],
        "videos": [
            "media/villa1/video1.mp4",  # Главное видео дня
            "media/villa1/video2.mp4"   # Видео заката
        ],
        "video": "media/villa1/video1.mp4",  # Главное видео для совместимости
    },
    "villa2": {
        "photos": [
            "media/villa2/photo1.jpg",
            "media/villa2/photo2.jpg",
            "media/villa2/photo3.jpg", 
            "media/villa2/photo4.jpg",
            "media/villa2/photo5.jpg",
            "media/villa2/photo6.jpg",
            "media/villa2/photo7.jpg"
        ],
        "videos": [
            "media/villa2/video1.mp4",  # Главное видео
            "media/villa2/video2.mp4",  # Вертикальное видео
            "media/villa2/video3.mp4"   # Дополнительное видео
        ],
        "video": "media/villa2/video1.mp4",  # Главное видео для совместимости
    },
    "common": {
        "presentation": "media/common/presentation.pdf",
        "location_photos": [
            "media/location/sirius1.jpg",
            "media/location/sirius2.jpg",
            "media/location/sirius3.jpg",
            "media/location/sirius4.jpg"
        ],
        "promo_video": "media/common/promo_video.mp4",
        "concept_video": "media/common/concept_video.mp4",
        "comparison_image": "media/common/comparison.jpg"
    }
}

def create_media_directories():
    """Создание директорий для медиа файлов"""
    directories = [
        "media/villa1",
        "media/villa2", 
        "media/common",
        "media/location"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Создана директория: {directory}")

def get_villa_photos(villa_id: str, max_photos: int = 4) -> List[InputMediaPhoto]:
    """Получение фотографий виллы для отправки медиагруппой (ограничено 4 фото для стабильности)"""
    if villa_id not in VILLA_MEDIA:
        return []
    
    photos = []
    villa_photos = VILLA_MEDIA[villa_id]["photos"][:max_photos]  # Ограничиваем количество
    
    for i, photo_path in enumerate(villa_photos):
        if os.path.exists(photo_path):
            try:
                # Проверяем размер файла (не больше 10MB для стабильности)
                file_size = os.path.getsize(photo_path)
                if file_size > 10 * 1024 * 1024:  # 10MB
                    logger.warning(f"Файл {photo_path} слишком большой: {file_size / 1024 / 1024:.1f}MB")
                    continue
                
                if i == 0:
                    # Первое фото с подписью
                    caption = f"📸 Фотогалерея {villa_id.upper()}"
                    photos.append(InputMediaPhoto(
                        media=FSInputFile(photo_path),
                        caption=caption
                    ))
                else:
                    photos.append(InputMediaPhoto(media=FSInputFile(photo_path)))
            except Exception as e:
                logger.error(f"Ошибка загрузки фото {photo_path}: {e}")
        else:
            logger.warning(f"Файл не найден: {photo_path}")
    
    return photos

def get_remaining_villa_photos(villa_id: str, start_from: int = 4) -> List[InputMediaPhoto]:
    """Получение оставшихся фотографий виллы (после первых 4)"""
    if villa_id not in VILLA_MEDIA:
        return []
    
    photos = []
    villa_photos = VILLA_MEDIA[villa_id]["photos"][start_from:]
    
    for photo_path in villa_photos:
        if os.path.exists(photo_path):
            try:
                # Проверяем размер файла
                file_size = os.path.getsize(photo_path)
                if file_size > 10 * 1024 * 1024:  # 10MB
                    logger.warning(f"Файл {photo_path} слишком большой: {file_size / 1024 / 1024:.1f}MB")
                    continue
                
                photos.append(InputMediaPhoto(media=FSInputFile(photo_path)))
            except Exception as e:
                logger.error(f"Ошибка загрузки фото {photo_path}: {e}")
        else:
            logger.warning(f"Файл не найден: {photo_path}")
    
    return photos

def get_villa_video(villa_id: str, video_index: int = 0) -> str:
    """Получение пути к видео виллы"""
    if villa_id not in VILLA_MEDIA:
        return None
    
    # Получаем видео по индексу или главное видео
    if "videos" in VILLA_MEDIA[villa_id] and len(VILLA_MEDIA[villa_id]["videos"]) > video_index:
        video_path = VILLA_MEDIA[villa_id]["videos"][video_index]
    else:
        video_path = VILLA_MEDIA[villa_id]["video"]
    
    if os.path.exists(video_path):
        # Проверяем размер видео
        file_size = os.path.getsize(video_path)
        if file_size > 45 * 1024 * 1024:  # 45MB (лимит Telegram 50MB, оставляем запас)
            logger.warning(f"Видеофайл {video_path} слишком большой: {file_size / 1024 / 1024:.1f}MB")
            return None
        return video_path
    else:
        logger.warning(f"Видео файл не найден: {video_path}")
        return None

def get_all_villa_videos(villa_id: str) -> List[str]:
    """Получение всех видео виллы"""
    if villa_id not in VILLA_MEDIA or "videos" not in VILLA_MEDIA[villa_id]:
        return []
    
    videos = []
    for video_path in VILLA_MEDIA[villa_id]["videos"]:
        if os.path.exists(video_path):
            # Проверяем размер видео
            file_size = os.path.getsize(video_path)
            if file_size <= 45 * 1024 * 1024:  # 45MB
                videos.append(video_path)
            else:
                logger.warning(f"Видеофайл {video_path} слишком большой: {file_size / 1024 / 1024:.1f}MB")
        else:
            logger.warning(f"Видео файл не найден: {video_path}")
    
    return videos

def get_presentation_file() -> str:
    """Получение файла презентации"""
    file_path = VILLA_MEDIA["common"]["presentation"]
    if os.path.exists(file_path):
        return file_path
    else:
        logger.warning(f"Файл презентации не найден: {file_path}")
        return None

def get_location_photos() -> List[InputMediaPhoto]:
    """Получение фотографий локации для carousel"""
    photos = []
    location_photos = VILLA_MEDIA["common"]["location_photos"]
    
    captions = [
        "🏛 Поющие фонтаны Сириуса - в 10 минутах от вилл",
        "🎢 Сочи-Парк - крупнейший тематический парк России", 
        "🏒 Олимпийский парк - наследие Игр 2014",
        "🏔 Красная Поляна - горнолыжные курорты"
    ]
    
    for i, photo_path in enumerate(location_photos):
        if os.path.exists(photo_path):
            try:
                caption = captions[i] if i < len(captions) else ""
                photos.append(InputMediaPhoto(
                    media=FSInputFile(photo_path),
                    caption=caption
                ))
            except Exception as e:
                logger.error(f"Ошибка загрузки фото локации {photo_path}: {e}")
        else:
            logger.warning(f"Файл не найден: {photo_path}")
    
    return photos

def add_media_file(villa_id: str, media_type: str, file_path: str):
    """Добавление нового медиа файла в структуру"""
    if villa_id not in VILLA_MEDIA:
        VILLA_MEDIA[villa_id] = {"photos": [], "video": None}
    
    if media_type == "photo":
        VILLA_MEDIA[villa_id]["photos"].append(file_path)
    elif media_type == "video":
        VILLA_MEDIA[villa_id]["video"] = file_path
    
    logger.info(f"Добавлен медиа файл: {villa_id} -> {media_type} -> {file_path}")

def check_media_files() -> Dict[str, Any]:
    """Проверка наличия всех медиа файлов"""
    status = {
        "missing_files": [],
        "existing_files": [],
        "total_photos": 0,
        "total_videos": 0,
        "large_files": []
    }
    
    for villa_id, media_data in VILLA_MEDIA.items():
        if isinstance(media_data, dict):
            # Проверка фотографий
            if "photos" in media_data:
                for photo_path in media_data["photos"]:
                    if os.path.exists(photo_path):
                        file_size = os.path.getsize(photo_path)
                        status["existing_files"].append(photo_path)
                        status["total_photos"] += 1
                        if file_size > 10 * 1024 * 1024:  # 10MB
                            status["large_files"].append(f"{photo_path} ({file_size / 1024 / 1024:.1f}MB)")
                    else:
                        status["missing_files"].append(photo_path)
            
            # Проверка видео
            if "videos" in media_data:
                for video_path in media_data["videos"]:
                    if os.path.exists(video_path):
                        file_size = os.path.getsize(video_path)
                        status["existing_files"].append(video_path)
                        status["total_videos"] += 1
                        if file_size > 45 * 1024 * 1024:  # 45MB
                            status["large_files"].append(f"{video_path} ({file_size / 1024 / 1024:.1f}MB)")
                    else:
                        status["missing_files"].append(video_path)
    
    return status

# Создание директорий при импорте модуля
create_media_directories() 