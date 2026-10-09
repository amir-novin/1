import json
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup


URL = "https://www.tala.ir/"


def normalize_number(text):
    """تبدیل اعداد فارسی و حذف جداکننده‌ها"""
    translate_table = str.maketrans(
        "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
        "01234567890123456789"
    )

    text = text.translate(translate_table)
    text = text.replace(",", "")
    text = text.replace("٬", "")
    text = text.replace(" ", "")

    return int(text)


def main():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120 Safari/537.36"
        )
    }

    response = requests.get(URL, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    prices = soup.select("span.price.green")

    if len(prices) < 2:
        raise Exception("قیمت‌ها در صفحه پیدا نشدند.")

    gold_price = normalize_number(prices[0].get_text(strip=True))
    coin_price = normalize_number(prices[1].get_text(strip=True))

    data = {
        "updated_at": datetime.now(
            ZoneInfo("Asia/Tehran")
        ).strftime("%Y/%m/%d - %H:%M"),

        "prices": [
            {
                "title": "قیمت طلا",
                "price": gold_price,
                "unit": "تومان"
            },
            {
                "title": "قیمت سکه",
                "price": coin_price,
                "unit": "تومان"
            }
        ]
    }

    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    print("قیمت طلا و سکه با موفقیت بروزرسانی شد.")


if __name__ == "__main__":
    main()
