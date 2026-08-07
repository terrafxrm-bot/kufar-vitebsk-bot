import requests
import json
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

KUFAR_URL = "https://api.kufar.by/search-api/v2/search/rendered-paginated"

PARAMS = {
    "cat": "1010",
    "cur": "BYR",
    "gtsy": "country-belarus~province-vitebskaja_oblast~locality-vitebsk",
    "lang": "ru",
    "prc": "r:40000,65500",
    "size": "30",
    "typ": "let"
}

SEEN_FILE = "seen_ads.json"


def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": text
    }

    response = requests.post(url, data=data)

    print("Telegram:", response.text)


def load_seen():
    if not os.path.exists(SEEN_FILE):
        return []

    with open(SEEN_FILE, "r") as file:
        return json.load(file)


def save_seen(ads):
    with open(SEEN_FILE, "w") as file:
        json.dump(ads, file)


def get_ads():
    response = requests.get(
        KUFAR_URL,
        params=PARAMS,
        timeout=20
    )

    print("Kufar status:", response.status_code)

    data = response.json()

    print("Ответ Kufar:", data.keys())

    return data.get("ads", [])


def check_new_ads():

    seen = load_seen()

    ads = get_ads()

    print("Найдено объявлений:", len(ads))


    if not seen:

        first_ids = []

        for ad in ads:
            first_ids.append(str(ad["ad_id"]))

        save_seen(first_ids)

        send_message(
            "✅ Бот Kufar запущен.\n"
            f"Сохранено объявлений: {len(first_ids)}\n"
            "Теперь буду присылать только новые."
        )

        return


    new_ads = []

    for ad in ads:

        ad_id = str(ad["ad_id"])

        if ad_id not in seen:
            new_ads.append(ad)
            seen.append(ad_id)


    save_seen(seen)


    print("Новых объявлений:", len(new_ads))


    for ad in new_ads:

        message = (
            "🏠 Новая квартира!\n\n"
            f"{ad.get('subject','Без названия')}\n"
            f"💰 Цена: {ad.get('price_byn','нет')} BYN\n"
            "📍 Витебск\n\n"
            f"{ad.get('body_short','')}\n\n"
            f"🔗 {ad.get('ad_link','')}"
        )

        send_message(message)


if __name__ == "__main__":

    try:
        check_new_ads()

    except Exception as e:

        print("Ошибка:", e)

        send_message(
            f"❌ Ошибка Kufar бота:\n{e}"
        )
