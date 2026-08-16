from __future__ import annotations

import csv
import math
import random
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DIR = ROOT / "data" / "sample"
SAMPLE_FILE = SAMPLE_DIR / "walmart_sales_sample.csv"


def weekly_dates(start: date, weeks: int) -> list[date]:
    return [start + timedelta(weeks=i) for i in range(weeks)]


def is_holiday_week(day: date) -> int:
    holiday_windows = {(2, 10), (9, 7), (11, 25), (12, 25)}
    return int((day.month, day.day) in holiday_windows or day.month == 12 and day.day >= 18)


def main() -> None:
    random.seed(42)
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

    stores = range(1, 16)
    departments = [1, 3, 5, 7, 10, 12, 16, 20, 24, 28]
    regions = ["Northeast", "Midwest", "South", "West"]
    store_types = ["A", "B", "C"]
    categories = {
        1: ("Grocery", ["Great Value Cereal", "Fresh Produce Bundle", "Bakery Value Pack"]),
        3: ("Household", ["Laundry Detergent", "Kitchen Towels", "Cleaning Starter Kit"]),
        5: ("Technology", ["Wireless Headphones", "Smart TV 43 Inch", "Tablet Essentials Kit"]),
        7: ("Apparel", ["Denim Jeans", "Athletic Shoes", "Winter Jacket"]),
        10: ("Pharmacy", ["Wellness Pack", "First Aid Kit", "Vitamin Bundle"]),
        12: ("Home", ["Bedding Set", "Cookware Combo", "Storage Organizer"]),
        16: ("Toys", ["Building Blocks", "Board Game Pack", "Outdoor Play Set"]),
        20: ("Automotive", ["Motor Oil Pack", "Car Care Kit", "All-Weather Mats"]),
        24: ("Garden", ["Patio Planter", "Garden Tool Set", "Outdoor Lighting"]),
        28: ("Seasonal", ["Holiday Decor Box", "Back-to-School Kit", "Summer Cooler"]),
    }

    store_profile = {
        store: {
            "Region": random.choice(regions),
            "Type": random.choices(store_types, weights=[0.45, 0.35, 0.20])[0],
            "Size": random.randint(45_000, 210_000),
            "Base": random.uniform(21_000, 62_000),
        }
        for store in stores
    }

    rows: list[dict[str, object]] = []
    for current_date in weekly_dates(date(2021, 1, 1), 156):
        week_of_year = current_date.isocalendar().week
        holiday = is_holiday_week(current_date)
        temperature = 56 + 23 * math.sin((week_of_year / 52) * 2 * math.pi) + random.normalvariate(0, 5)
        fuel_price = 2.65 + 0.55 * math.sin((week_of_year / 52) * 2 * math.pi + 1.2) + random.normalvariate(0, 0.08)
        cpi = 211 + ((current_date.year - 2021) * 5.1) + random.normalvariate(0, 0.7)
        unemployment = 6.8 - ((current_date.year - 2021) * 0.45) + random.normalvariate(0, 0.25)

        for store in stores:
            profile = store_profile[store]
            type_multiplier = {"A": 1.18, "B": 1.0, "C": 0.82}[profile["Type"]]
            size_multiplier = profile["Size"] / 110_000

            for dept in departments:
                category, product_options = categories[dept]
                product = random.choice(product_options)
                dept_multiplier = 0.55 + (dept % 9) * 0.08
                seasonal_lift = 1 + 0.12 * math.sin((week_of_year / 52) * 2 * math.pi + dept / 5)
                holiday_lift = 1.32 if holiday else 1.0
                sales = (
                    profile["Base"]
                    * type_multiplier
                    * size_multiplier
                    * dept_multiplier
                    * seasonal_lift
                    * holiday_lift
                )
                sales += random.normalvariate(0, sales * 0.08)
                quantity = random.randint(40, 420)
                discount = round(max(0, random.normalvariate(0.09 if holiday else 0.055, 0.035)), 3)
                unit_price = round(max(sales / max(quantity, 1) / max(1 - discount, 0.65), 2), 2)
                revenue = round(max(sales, 1000), 2)
                cost_rate = random.uniform(0.68, 0.86)
                profit = round(revenue - (revenue * cost_rate) - (revenue * discount * 0.55), 2)
                profit_margin = round(profit / revenue, 4)

                rows.append(
                    {
                        "Store": store,
                        "Dept": dept,
                        "Product": product,
                        "Date": current_date.isoformat(),
                        "Weekly_Sales": revenue,
                        "Revenue": revenue,
                        "Quantity": quantity,
                        "Unit_Price": unit_price,
                        "Discount": discount,
                        "Holiday_Flag": holiday,
                        "Temperature": round(temperature, 2),
                        "Fuel_Price": round(fuel_price, 3),
                        "CPI": round(cpi, 3),
                        "Unemployment": round(unemployment, 3),
                        "Type": profile["Type"],
                        "Size": profile["Size"],
                        "Region": profile["Region"],
                        "Category": category,
                        "Profit": profit,
                        "Profit_Margin": profit_margin,
                        "Customer_Segment": random.choice(["Family", "Value", "Convenience", "Premium"]),
                    }
                )

    with SAMPLE_FILE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created {SAMPLE_FILE} with {len(rows):,} rows")


if __name__ == "__main__":
    main()
