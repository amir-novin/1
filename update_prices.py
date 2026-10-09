import json
from datetime import datetime
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright


def تبدیل_عدد(text):
    جدول = str.maketrans(
        "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
        "01234567890123456789"
    )

    text = text.translate(جدول)
    text = text.replace(",", "")
    text = text.replace("٬", "")
    text = text.strip()

    return int(text)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page(
        viewport={"width": 1400, "height": 1000},
        locale="fa-IR"
    )

    page.goto(
        "https://www.tala.ir/",
        wait_until="networkidle",
        timeout=60000
    )

    # صبر برای نمایش قیمت‌ها
    page.wait_for_timeout(5000)

    قیمت‌ها = page.locator("span.price.green").all_inner_texts()

    browser.close()


if len(قیمت‌ها) < 2:
    raise Exception("قیمت طلا و سکه پیدا نشد. تعداد قیمت‌ها: " + str(len(قیمت‌ها)))


قیمت_طلا = تبدیل_عدد(قیمت‌ها[0])
قیمت_سکه = تبدیل_عدد(قیمت‌ها[1])

اطلاعات = {
    "updated_at": datetime.now(
        ZoneInfo("Asia/Tehran")
    ).strftime("%Y/%m/%d - %H:%M"),

    "prices": [
        {
            "title": "طلای ۱۸ عیار",
            "price": قیمت_طلا,
            "unit": "تومان / گرم"
        },
        {
            "title": "سکه امامی",
            "price": قیمت_سکه,
            "unit": "تومان"
        }
    ]
}

with open("data.json", "w", encoding="utf-8") as file:
    json.dump(اطلاعات, file, ensure_ascii=False, indent=2)

print("قیمت طلا:", قیمت_طلا)
print("قیمت سکه:", قیمت_سکه)
