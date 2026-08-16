# Data Notes

Place the original Walmart sales dataset in `data/raw/`.

Supported common schemas:

## Walmart weekly sales dataset

```text
Store,Date,Weekly_Sales,Holiday_Flag,Temperature,Fuel_Price,CPI,Unemployment
```

## Walmart recruiting/store forecasting style

```text
Store,Dept,Date,Weekly_Sales,IsHoliday
```

Optional fields such as `Type`, `Size`, `Region`, `Category`, `Profit`, and `Customer_Segment` will be used when present.

The scripts normalize known column names and produce cleaned data in `data/processed/`.

