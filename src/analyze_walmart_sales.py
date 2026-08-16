from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
OUTPUT_DIR = ROOT / "outputs"

COLUMN_ALIASES = {
    "store": "Store",
    "dept": "Dept",
    "department": "Dept",
    "date": "Date",
    "weekly_sales": "Weekly_Sales",
    "weekly sales": "Weekly_Sales",
    "sales": "Weekly_Sales",
    "holiday_flag": "Holiday_Flag",
    "isholiday": "Holiday_Flag",
    "is_holiday": "Holiday_Flag",
    "temperature": "Temperature",
    "fuel_price": "Fuel_Price",
    "fuel price": "Fuel_Price",
    "cpi": "CPI",
    "unemployment": "Unemployment",
    "type": "Type",
    "size": "Size",
    "region": "Region",
    "category": "Category",
    "product": "Product",
    "quantity": "Quantity",
    "unit_price": "Unit_Price",
    "discount": "Discount",
    "revenue": "Revenue",
    "profit": "Profit",
    "profit_margin": "Profit_Margin",
    "customer_segment": "Customer_Segment",
}


def normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    for column in frame.columns:
        key = column.strip().lower()
        rename_map[column] = COLUMN_ALIASES.get(key, column.strip().replace(" ", "_"))
    return frame.rename(columns=rename_map)


def load_and_clean(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    frame = normalize_columns(frame)
    frame = frame.drop_duplicates()

    required = {"Store", "Date", "Weekly_Sales"}
    missing = required.difference(frame.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(f"Missing required columns: {missing_text}")

    frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce")
    frame["Weekly_Sales"] = pd.to_numeric(frame["Weekly_Sales"], errors="coerce")
    frame = frame.dropna(subset=["Store", "Date", "Weekly_Sales"])

    if "Holiday_Flag" in frame.columns:
        frame["Holiday_Flag"] = frame["Holiday_Flag"].replace({True: 1, False: 0, "TRUE": 1, "FALSE": 0})
        frame["Holiday_Flag"] = pd.to_numeric(frame["Holiday_Flag"], errors="coerce").fillna(0).astype(int)
    else:
        frame["Holiday_Flag"] = 0

    for column in [
        "Temperature",
        "Fuel_Price",
        "CPI",
        "Unemployment",
        "Size",
        "Revenue",
        "Quantity",
        "Unit_Price",
        "Discount",
        "Profit",
        "Profit_Margin",
    ]:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")

    if "Revenue" not in frame.columns:
        frame["Revenue"] = frame["Weekly_Sales"]
    else:
        frame["Revenue"] = frame["Revenue"].fillna(frame["Weekly_Sales"])

    if "Profit" not in frame.columns:
        default_margin = 0.16
        frame["Profit"] = frame["Revenue"] * default_margin
    else:
        frame["Profit"] = frame["Profit"].fillna(frame["Revenue"] * 0.16)

    if "Discount" not in frame.columns:
        frame["Discount"] = 0
    else:
        frame["Discount"] = frame["Discount"].fillna(0)

    frame["Profit_Margin"] = (frame["Profit"] / frame["Revenue"].replace(0, pd.NA)).fillna(0)

    frame["Year"] = frame["Date"].dt.year
    frame["Month"] = frame["Date"].dt.to_period("M").astype(str)
    frame["Quarter"] = frame["Date"].dt.to_period("Q").astype(str)
    frame["Week"] = frame["Date"].dt.isocalendar().week.astype(int)

    return frame


def write_summary(frame: pd.DataFrame) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    frame.to_csv(PROCESSED_DIR / "walmart_sales_clean.csv", index=False)

    total_revenue = frame["Revenue"].sum()
    total_profit = frame["Profit"].sum()

    kpis = pd.DataFrame(
        [
            {
                "total_sales": total_revenue,
                "total_profit": total_profit,
                "profit_margin": total_profit / total_revenue if total_revenue else 0,
                "average_weekly_sales": frame["Weekly_Sales"].mean(),
                "store_count": frame["Store"].nunique(),
                "department_count": frame["Dept"].nunique() if "Dept" in frame.columns else None,
                "holiday_sales_share": frame.loc[frame["Holiday_Flag"] == 1, "Revenue"].sum() / total_revenue
                if total_revenue
                else 0,
                "start_date": frame["Date"].min().date(),
                "end_date": frame["Date"].max().date(),
            }
        ]
    )
    kpis.to_csv(OUTPUT_DIR / "kpi_summary.csv", index=False)

    frame.groupby("Store", as_index=False).agg(
        total_sales=("Revenue", "sum"),
        total_profit=("Profit", "sum"),
        profit_margin=("Profit_Margin", "mean"),
        average_weekly_sales=("Weekly_Sales", "mean"),
        sales_volatility=("Weekly_Sales", "std"),
    ).sort_values("total_sales", ascending=False).to_csv(OUTPUT_DIR / "sales_by_store.csv", index=False)

    frame.groupby("Month", as_index=False).agg(total_sales=("Revenue", "sum"), total_profit=("Profit", "sum")).to_csv(
        OUTPUT_DIR / "monthly_sales_trend.csv", index=False
    )

    frame.groupby("Holiday_Flag", as_index=False).agg(
        total_sales=("Revenue", "sum"),
        total_profit=("Profit", "sum"),
        average_weekly_sales=("Weekly_Sales", "mean"),
        average_discount=("Discount", "mean"),
    ).to_csv(OUTPUT_DIR / "holiday_sales_impact.csv", index=False)

    optional_groups = ["Dept", "Product", "Category", "Region", "Type", "Customer_Segment"]
    for column in optional_groups:
        if column in frame.columns:
            frame.groupby(column, as_index=False).agg(
                total_sales=("Revenue", "sum"),
                total_profit=("Profit", "sum"),
                average_discount=("Discount", "mean"),
                profit_margin=("Profit_Margin", "mean"),
            ).sort_values(
                "total_sales", ascending=False
            ).to_csv(OUTPUT_DIR / f"sales_by_{column.lower()}.csv", index=False)

    frame.assign(discount_band=pd.cut(frame["Discount"], bins=[-0.01, 0.03, 0.07, 0.12, 1.0], labels=["0-3%", "3-7%", "7-12%", "12%+"])).groupby(
        "discount_band", as_index=False, observed=False
    ).agg(
        total_sales=("Revenue", "sum"),
        total_profit=("Profit", "sum"),
        profit_margin=("Profit_Margin", "mean"),
    ).to_csv(OUTPUT_DIR / "discount_vs_profit.csv", index=False)

    numeric_columns = [
        column
        for column in [
            "Revenue",
            "Weekly_Sales",
            "Discount",
            "Temperature",
            "Fuel_Price",
            "CPI",
            "Unemployment",
            "Size",
            "Profit",
            "Profit_Margin",
        ]
        if column in frame.columns
    ]
    if len(numeric_columns) > 1:
        frame[numeric_columns].corr(numeric_only=True).to_csv(OUTPUT_DIR / "correlation_matrix.csv")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze Walmart sales data.")
    parser.add_argument("--input", required=True, help="Path to Walmart sales CSV file")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = ROOT / input_path

    frame = load_and_clean(input_path)
    write_summary(frame)
    print(f"Analyzed {len(frame):,} rows from {input_path}")
    print(f"Clean data: {PROCESSED_DIR / 'walmart_sales_clean.csv'}")
    print(f"Summaries: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
