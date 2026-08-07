import requests
import time
import json
import os


TOKEN = "8701043369:AAG2JR4Tkwob2R4m1V8eoKyJPUGTCj7U35Y"
CHAT_ID = "825979008"


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

    requests.post(url, data=data)


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
        params=PARAMS
    )

    data = response.json()

    return data["ads"]


def check_new_ads():

    seen = load_seen()

    ads = get_ads()

    # Первый запуск
    if not seen:

        first_ids = []

        for ad in ads:
            first_ids.append(str(ad["ad_id"]))

        save_seen(first_ids)

        send_message(
            "✅ Первый запуск завершён.\n"
            "Старые объявления сохранены.\n"
            "Теперь буду отправлять только новые квартиры."
        )

        return


    new_ads = []


    for ad in ads:

        ad_id = str(ad["ad_id"])


        if ad_id not in seen:
            new_ads.append(ad)
            seen.append(ad_id)



    save_seen(seen)



    for ad in new_ads:

        message = (
            f"🏠 Новая квартира!\n\n"
            f"{ad['subject']}\n"
            f"💰 Цена: {ad.get('price_byn', 'нет')} BYN\n"
            f"📍 Витебск\n\n"
            f"{ad.get('body_short', '')}\n\n"
            f"🔗 {ad['ad_link']}"
        )

        send_message(message)


try:
    check_new_ads()

except Exception as e:
    send_message(f"❌ Ошибка: {e}")