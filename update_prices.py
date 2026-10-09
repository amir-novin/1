import json
from datetime import datetime
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright


URL = "https://www.tala.ir/"


def normalize_number(text):
    table = str.maketrans(
        "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
        "01234567890123456789"
    )

    text = text.translate(table)
    text = text.replace(",", "")
    text = text.replace("٬", "")
    text = text.replace(" ", "")
    text = text.strip()

    return int(text)


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)

    page = browser.new_page(
        viewport={"width": 1400, "height": 1000},
        locale="fa-IR"
    )

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(7000)

    price_texts = page.locator("span.price.green").all_inner_texts()

    browser.close()


print("Prices found:", price_texts)

if len(price_texts) < 2:
    raise Exception(
        "Gold and coin prices were not found. "
        "Number of prices: " + str(len(price_texts))
    )


gold_price = normalize_number(price_texts[0])
coin_price = normalize_number(price_texts[1])

data = {
    "updated_at": datetime.now(
        ZoneInfo("Asia/Tehran")
    ).strftime("%Y/%m/%d - %H:%M"),

    "prices": [
        {
            "title": "طلای 18 عیار",
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
