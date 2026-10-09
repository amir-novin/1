import json
import re
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup


URL = "https://www.tala.ir/"


def normalize_digits(text):
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    arabic_digits = "٠١٢٣٤٥٦٧٨٩"

    for i, digit in enumerate(persian_digits):
        text = text.replace(digit, str(i))

    for i, digit in enumerate(arabic_digits):
        text = text.replace(digit, str(i))

    return text


def clean_number(value):
    value = normalize_digits(value)
    value = value.replace(",", "")
    value = value.replace("٬", "")
    value = value.replace(" ", "")
    return value


def find_price(text, labels):
    for label in labels:
        position = text.lower().find(label.lower())

        if position == -1:
            continue

        after_label = text[position + len(label):position + len(label) + 150]

        numbers = re.findall(
            r"\d{1,3}(?:[,\u٬\s]\d{3})+|\d{4,}",
            after_label
        )

        for number in numbers:
            number = clean_number(number)

            try:
                number = int(number)

                # حذف عددهای کوچک مانند ۱۸ موجود در عنوان
                if number > 1000:
                    return number

            except ValueError:
                continue

    return 0


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
    page_text = soup.get_text(" ", strip=True)
    page_text = normalize_digits(page_text)

    prices = [
        {
            "title": "گرم ۱۸",
            "price": find_price(page_text, ["گرم 18", "گرم۱۸"]),
            "unit": "تومان / گرم"
        },
        {
            "title": "سکه امامی",
            "price": find_price(page_text, ["سکه امامی"]),
            "unit": "تومان"
        },
        {
            "title": "نیم سکه",
            "price": find_price(page_text, ["نیم سکه", "نیم‌سکه"]),
            "unit": "تومان"
        },
        {
            "title": "ربع سکه",
            "price": find_price(page_text, ["ربع سکه", "ربع‌سکه"]),
            "unit": "تومان"
        },
        {
            "title": "سکه گرمی",
            "price": find_price(page_text, ["سکه گرمی", "سکه‌گرمی"]),
            "unit": "تومان"
        }
    ]

    tehran_time = datetime.now(
        ZoneInfo("Asia/Tehran")
    ).strftime("%Y/%m/%d - %H:%M")

    data = {
        "updated_at": tehran_time,
        "prices": prices
    }

    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    print("قیمت‌ها با موفقیت بروزرسانی شدند.")


if __name__ == "__main__":
    main()
