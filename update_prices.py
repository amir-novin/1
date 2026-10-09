import json
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright


URL = "https://www.tala.ir/"


def clean_price(text):
    digits = str.maketrans(
        "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
        "01234567890123456789"
    )

    text = text.translate(digits)
    text = text.replace(",", "")
    text = text.replace("٬", "")
    text = text.replace(" ", "")

    numbers = re.findall(r"\d+", text)

    if not numbers:
        return None

    value = int("".join(numbers))

    if value < 1000:
        return None

    return value


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )

    page = browser.new_page(
        viewport={"width": 1440, "height": 1200},
        locale="fa-IR",
        user_agent=(
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 "
            "Chrome/131.0.0.0 Safari/537.36"
        )
    )

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=90000
    )

    # زمان برای اجرای JavaScript سایت
    page.wait_for_timeout(15000)

    raw_prices = page.locator("span.price.green").all_inner_texts()

    print("All price elements:", raw_prices)

    numeric_prices = []

    for item in raw_prices:
        value = clean_price(item)

        if value is not None and value not in numeric_prices:
            numeric_prices.append(value)

    print("Numeric prices:", numeric_prices)

    browser.close()


if len(numeric_prices) < 2:
    raise Exception(
        "قیمت عددی پیدا نشد. سایت برای GitHub مقدار '-' برگردانده است."
    )


gold_price = numeric_prices[0]
coin_price = numeric_prices[1]


data = {
    "updated_at": datetime.now(
        ZoneInfo("Asia/Tehran")
    ).strftime("%Y/%m/%d - %H:%M"),

    "prices": [
        {
            "title": "طلای ۱۸ عیار",
            "price": gold_price,
            "unit": "تومان / گرم"
        },
        {
            "title": "سکه امامی",
            "price": coin_price,
            "unit": "تومان"
        }
    ]
}


with open("data.json", "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=2)


print("Gold price:", gold_price)
print("Coin price:", coin_price)
print("data.json updated successfully")
