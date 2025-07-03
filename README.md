# 🏡 Sochi Invest Bot

Telegram-бот для продажи премиальных вилл "ПАНОРАМА 240" в Сочи (ФТ «Сириус»)

**Автор:** SergD (@sergei_dyshkant)  
**Разработчик:** @sergei_dyshkant

## 📋 Описание

Лидогенерирующий Telegram-бот для конвертации трафика из VK-Ads и МТС Маркетолога в тёплые лиды на покупку премиальных вилл.

### ⚡ Основные функции:
- 📥 **Лид-магнит**: Скачивание PDF-презентации с планировками и фото
- 🏠 **Витрина объектов**: Подробная информация о 2 виллах
- 📅 **Запись на просмотр**: Сбор контактных данных через формы
- 📊 **Расчёт доходности**: Консультации по инвестиционному потенциалу
- 🗺 **О локации**: Информация о ФТ «Сириус»
- 🔄 **Сравнение объектов**: Таблица характеристик

### 🎯 Объекты продажи:
- **Вилла №1**: 244 м² · 280 млн ₽
- **Вилла №2**: 242 м² · 200 млн ₽

## 🚀 Развертывание на сервере

### 1. Подключение к серверу
```bash
ssh -i "/Users/wsgp/Searching projects/telegram_voice_translator/ssh-key-2025-06-05.key" ubuntu@168.110.208.184
```

### 2. Создание папки проекта
```bash
sudo mkdir -p /home/ubuntu/bots/sochi_invest_bot
sudo chown ubuntu:ubuntu /home/ubuntu/bots/sochi_invest_bot
cd /home/ubuntu/bots/sochi_invest_bot
```

### 3. Загрузка файлов проекта
Скопируйте все файлы проекта в папку `/home/ubuntu/bots/sochi_invest_bot/`

### 4. Настройка Python окружения
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Создание директорий
```bash
mkdir -p logs
mkdir -p data
```

### 6. Настройка переменных окружения
```bash
# Создайте файл .env
nano .env

# Добавьте в него:
BOT_TOKEN=YOUR_BOT_TOKEN_HERE
SERVICE_CHAT_ID=YOUR_SERVICE_CHAT_ID
```

### 7. Настройка systemd сервиса
```bash
# Копирование файла сервиса
sudo cp sochi-invest-bot.service /etc/systemd/system/

# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение автозапуска
sudo systemctl enable sochi-invest-bot.service

# Запуск сервиса
sudo systemctl start sochi-invest-bot.service
```

### 8. Проверка работы
```bash
# Статус сервиса
sudo systemctl status sochi-invest-bot.service

# Логи в реальном времени
tail -f logs/sochi_invest_bot.log

# Проверка автообнаружения Bot Monitor
curl -s localhost:8002/status | jq '.bots.new_services'
```

## 🔧 Конфигурация

### Обязательные настройки:
1. **BOT_TOKEN** - токен от @BotFather
2. **SERVICE_CHAT_ID** - ID чата для получения лидов

### Получение SERVICE_CHAT_ID:
1. Создайте групповой чат с менеджерами
2. Добавьте бота в чат как администратора
3. Получите chat_id через @userinfobot

## 📊 Мониторинг

Бот автоматически обнаруживается системой мониторинга Bot Monitor:

```bash
# Проверка статуса через API
curl -s localhost:8002/status

# Логи мониторинга
tail -f /home/ubuntu/bots/bot_monitor/logs/monitor.log
```

## 📱 Функционал бота

### 🔄 Сценарий работы:
1. **Приветствие** - WOW-факты о виллах
2. **Лид-магнит** - PDF с планировками и фото
3. **Витрина** - выбор между 2 виллами
4. **Карточка объекта** - детальная информация
5. **Запись на просмотр** - сбор контактов
6. **Отправка лидов** - в служебный чат

### 📋 Данные лидов:
- Имя
- Телефон (с кнопкой "Отправить контакт")
- Бюджет (200/280 млн ₽/другой)
- Удобное время звонка

## 🛡️ Безопасность

- Все логи записываются в `logs/sochi_invest_bot.log`
- Переменные окружения в `.env` файле
- Автоматический перезапуск при сбоях
- Мониторинг ресурсов сервера

## 📞 Поддержка

- **Автор проекта**: @sergei_dyshkant
- **Разработчик**: https://t.me/m/KL5XwR0sMWEy
- **Презентация**: https://drive.google.com/drive/folders/1q4osO5PDLhwJig8cMY97g_hnQZP4sm9_

## 🔗 Полезные команды

```bash
# Перезапуск бота
sudo systemctl restart sochi-invest-bot.service

# Остановка бота
sudo systemctl stop sochi-invest-bot.service

# Просмотр логов с ошибками
journalctl -u sochi-invest-bot.service -f

# Проверка используемых портов
ss -tulpn | grep python

# Очистка старых логов
find logs/ -name "*.log" -mtime +7 -delete
``` 