from get_data import get_price_data

df = get_price_data("SQQQ", start="2014-01-01", end="2024-12-31", save_csv=True)
print(df.head())
