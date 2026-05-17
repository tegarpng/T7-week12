import pandas as pd

def load_sales_data(csv_path):
    try:
        df = pd.read_csv(csv_path)
        # Parse kolom Date dan buat kolom bulan (1-12)
        df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y")
        df["bulan"] = df["Date"].dt.month
        return df
    except FileNotFoundError:
        print(f"File tidak ditemukan: {csv_path}")
        return None

def get_city(df):
    city = sorted(df["City"].unique())
    return ["All"] + city

def get_product(df):
    product = sorted(df["Product line"].unique())
    return ["All"] + product

def get_cust_type(df):
    cust_type = sorted(df["Customer type"].unique())
    return ["All"] + cust_type

def filter_by_city(df, city):
    if city == "All":
        return df
    return df[df["City"] == city]

def filter_by_cust(df, cust):
    if cust == "All":
        return df
    return df[df["Customer type"] == cust]

def filter_by_product(df, product):
    if product == "All":
        return df
    return df[df["Product line"] == product]

def get_monthly_summary(df):
    summary = df.groupby("bulan")["Sales"].sum().reset_index()
    all_months = pd.DataFrame({"bulan": range(1, 4)})
    summary = all_months.merge(summary, on="bulan", how="left").fillna(0)
    return summary
