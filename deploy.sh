#!/bin/bash
# 🚀 Скрипт автоматического развертывания Sochi Invest Bot
# Автор: SergD (@sergei_dyshkant)

set -e  # Остановка при ошибках

echo "🏡 Начинаем развертывание Sochi Invest Bot..."

# Переменные
BOT_DIR="/home/ubuntu/bots/sochi_invest_bot"
SERVICE_NAME="sochi-invest-bot"

# Проверка прав
if [ "$EUID" -eq 0 ]; then
    echo "❌ Не запускайте скрипт от root! Используйте: bash deploy.sh"
    exit 1
fi

# 1. Создание папки проекта
echo "📁 Создание директории проекта..."
sudo mkdir -p $BOT_DIR
sudo chown ubuntu:ubuntu $BOT_DIR
cd $BOT_DIR

# 2. Создание виртуального окружения
echo "🐍 Настройка Python окружения..."
python3 -m venv venv
source venv/bin/activate

# 3. Обновление pip и установка зависимостей
echo "📦 Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Создание директорий
echo "📂 Создание необходимых директорий..."
mkdir -p logs
mkdir -p data

# 5. Проверка .env файла
if [ ! -f ".env" ]; then
    echo "⚠️ Файл .env не найден! Создаю из примера..."
    cat > .env << EOF
# Telegram Bot Configuration
BOT_TOKEN=YOUR_BOT_TOKEN_HERE
SERVICE_CHAT_ID=YOUR_SERVICE_CHAT_ID

# ВАЖНО: Замените значения выше на реальные!
# BOT_TOKEN - получите от @BotFather
# SERVICE_CHAT_ID - ID чата для лидов
EOF
    chmod 600 .env
    echo "📝 Файл .env создан. ОБЯЗАТЕЛЬНО отредактируйте его!"
else
    echo "✅ Файл .env найден"
fi

# 6. Установка systemd сервиса
echo "⚙️ Настройка systemd сервиса..."
sudo cp ${SERVICE_NAME}.service /etc/systemd/system/
sudo systemctl daemon-reload

# 7. Проверка конфигурации
echo "🔍 Проверка конфигурации..."
python3 -c "import config; print('✅ Конфигурация загружена')" || {
    echo "❌ Ошибка в конфигурации! Проверьте файлы .env и config.py"
    exit 1
}

# 8. Тестовый запуск (без systemd)
echo "🧪 Тестовый запуск бота..."
timeout 10s python3 start_bot.py || true

# 9. Запуск через systemd
echo "🚀 Запуск сервиса..."
sudo systemctl enable ${SERVICE_NAME}.service
sudo systemctl start ${SERVICE_NAME}.service

# 10. Проверка статуса
sleep 3
echo "📊 Статус сервиса:"
sudo systemctl status ${SERVICE_NAME}.service --no-pager -l

# 11. Проверка автообнаружения Bot Monitor
echo "🤖 Проверка интеграции с Bot Monitor..."
if command -v curl &> /dev/null; then
    if curl -s localhost:8002/status > /dev/null 2>&1; then
        echo "✅ Bot Monitor доступен"
        echo "🔍 Проверка автообнаружения (через 30 секунд)..."
        sleep 30
        curl -s localhost:8002/status | jq '.bots.active_services' 2>/dev/null || echo "Сервис должен появиться в мониторинге"
    else
        echo "⚠️ Bot Monitor недоступен (это нормально)"
    fi
fi

# 12. Финальная информация
echo ""
echo "🎉 Развертывание завершено!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Отредактируйте файл .env с реальными токенами:"
echo "   nano $BOT_DIR/.env"
echo ""
echo "2. Перезапустите сервис после редактирования:"
echo "   sudo systemctl restart ${SERVICE_NAME}.service"
echo ""
echo "3. Мониторинг логов:"
echo "   tail -f $BOT_DIR/logs/sochi_invest_bot.log"
echo ""
echo "4. Управление сервисом:"
echo "   sudo systemctl status ${SERVICE_NAME}.service"
echo "   sudo systemctl restart ${SERVICE_NAME}.service"
echo "   sudo systemctl stop ${SERVICE_NAME}.service"
echo ""
echo "5. Проверка мониторинга:"
echo "   curl -s localhost:8002/status | jq '.bots'"
echo ""
echo "✅ Sochi Invest Bot готов к работе!"
echo "👨‍💻 Разработчик: @sergei_dyshkant"
echo "🔗 https://t.me/m/KL5XwR0sMWEy" 