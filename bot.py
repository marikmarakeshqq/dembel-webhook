import requests
import time
from datetime import datetime, timezone
import os
import threading
from flask import Flask

# ---------- МИНИ-СЕРВЕР ДЛЯ ПОДДЕРЖКИ ЖИЗНИ ----------
app = Flask('')

@app.route('/')
def home():
    return "Дембелёвочка в эфире! 🎖️"

def run_web():
    # Render автоматически назначает порт через переменную окружения PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    """Запускает веб-сервер в отдельном потоке"""
    t = threading.Thread(target=run_web, daemon=True)
    t.start()

# ---------- КОНФИГУРАЦИЯ ЧЕРЕЗ ПЕРЕМЕННЫЕ ----------
# Теперь скрипт берет данные из настроек хостинга
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
MESSAGE_ID = os.getenv("MESSAGE_ID")

# Данные пользователя (имя будет ровно таким, как ты вписал)
USER_NAME = "ubialex'а"
START_DATE = datetime(2025, 11, 3, tzinfo=timezone.utc)
END_DATE = datetime(2027, 5, 4, tzinfo=timezone.utc)
THUMBNAIL_URL = "https://i.imgur.com/Fz4BbJj.jpeg" # Твой кот в каске

# ----------------------------------

def get_progress_bar(percent: float) -> str:
    """Сверхточная полоска прогресса"""
    length = 18
    filled = int(length * percent / 100)
    
    # Фишка: если служба идет, последний кубик не закрасится до самой последней секунды
    if filled == length and percent < 100:
        filled = length - 1
        
    return "🟦" * filled + "⬜" * (length - filled)

def create_embed():
    """Создает структуру сообщения (плитку)"""
    now = datetime.now(timezone.utc)
    total_duration = END_DATE - START_DATE
    served_duration = now - START_DATE
    remaining_duration = END_DATE - now
    
    # Расчет процента с 4 знаками
    percent = max(0, min(100, (served_duration.total_seconds() / total_duration.total_seconds()) * 100))
    
    # Цвет плитки: Синий (старт) -> Желтый (экватор) -> Зеленый (финиш)
    if percent < 50:
        color = 0x3498db # Синий
    elif percent < 90:
        color = 0xf1c40f # Желтый
    else:
        color = 0x2ecc71 # Зеленый

    # Расчет времени для таймера
    ts = int(remaining_duration.total_seconds())
    
    # Если время вышло
    if ts <= 0:
        return {
            "title": f"🎉 ДЕМБЕЛЬ: {USER_NAME}",
            "description": "# 🦅 СВОБОДА! \nПриказ Генерала Гавса выполнен. Солдат дома!",
            "color": 0x2ecc71,
            "thumbnail": {"url": THUMBNAIL_URL}
        }

    days, rem = divmod(ts, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)

    # Формируем итоговую плитку (без футера)
    embed = {
        "title": f"        :fire: ubiq's rebirth :fire:   ",
        "color": color,
        "fields": [
            {
                "name": "📊 Общий прогресс",
                "value": f"{get_progress_bar(percent)} **{percent:.4f}%**",
                "inline": False
            },
            {
                "name": "⏳ Обратный отсчет (LIVE)",
                "value": f"```fix\n{days}д {hours:02d}:{minutes:02d}:{seconds:02d}```",
                "inline": False
            },
            {
                "name": "📅 Ключевые даты",
                "value": f"**Старт:** {START_DATE.strftime('%d.%m.%Y')}\n**Дембель:** {END_DATE.strftime('%d.%m.%Y')}",
                "inline": True
            },
            {
                "name": "🌓 Статистика",
                "value": f"**Прошло:** {served_duration.days} дн.\n**Осталось:** {remaining_duration.days} дн.",
                "inline": True
            }
        ],
        "thumbnail": {"url": THUMBNAIL_URL}
    }
    return embed

def run_timer():
    """Главный цикл обновления Вебхука"""
    print(f"🚀 Скрипт запущен.")
    print(f"📊 Отслеживаем службу: {USER_NAME}")
    url = f"{WEBHOOK_URL}/messages/{MESSAGE_ID}"
    
    while True:
        try:
            # Подготовка данных
            payload = {"embeds": [create_embed()]}
            
            # Обновление сообщения
            r = requests.patch(url, json=payload)
            
            if r.status_code == 429:
                # Если Discord ограничил скорость
                retry_after = r.json().get('retry_after', 1)
                time.sleep(retry_after)
            elif r.status_code in [200, 204]:
                # Успешно — ждем 1 секунду и повторяем
                time.sleep(1)
            else:
                print(f"⚠️ Ошибка Discord: {r.status_code}")
                time.sleep(5)
                
        except Exception as e:
            # Если пропал интернет или другая беда
            print(f"❌ Ошибка соединения: {e}")
            time.sleep(5)

if __name__ == "__main__":
    # Сначала запускаем веб-сервер для Render
    keep_alive() 
    
    # Затем запускаем основной цикл таймера
    try:
        run_timer()
    except KeyboardInterrupt:

        print("\n🛑 Мониторинг остановлен. Служба продолжается!")




