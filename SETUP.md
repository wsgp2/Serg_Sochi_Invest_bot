# 🔧 Настройка Sochi Invest Bot

## 📝 Создание .env файла

После клонирования репозитория создайте файл `.env` в корневой папке:

```bash
cp env_production .env
```

Или создайте файл `.env` вручную с содержимым:

```
# Telegram Bot Configuration for Sochi Invest Bot
BOT_TOKEN=END
SERVICE_CHAT_ID=END

# Дополнительные настройки
DEBUG=False
ENVIRONMENT=production
```

## 🚀 Быстрый старт

### На локальной машине:
```bash
git clone https://github.com/wsgp2/Serg_Sochi_Invest_bot.git
cd Serg_Sochi_Invest_bot
cp env_production .env
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 start_bot.py
```

### На сервере:
```bash
cd /home/ubuntu/bots/sochi_invest_bot
cp env_production .env
chmod +x deploy.sh
bash deploy.sh
```

## 📱 Контакты

- **Автор**: @sergei_dyshkant
- **Разработчик**: https://t.me/m/KL5XwR0sMWEy
- **Материалы**: https://drive.google.com/drive/folders/1q4osO5PDLhwJig8cMY97g_hnQZP4sm9_ 