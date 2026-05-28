import pandas as pd
import numpy as np

INPUT_FILE = r"C:\Users\loren\OneDrive\Documents\Codes\facility_data\data\raw\Health-Kenya-Facilities-2015-xls.xlsx"

OUTPUT_FILE = "clean_facilities.csv"

def load_data():
    return pd.read_excel(INPUT_FILE, engine="openpyxl", header=1)

def standardize_columns(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )
    df = df.rename(columns={"facility_name": "name"})
    return df



def clean_text_fields(df):
    text_cols = df.select_dtypes(include="object").columns
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()
    return df

def remove_duplicates(df):
    df = df.drop_duplicates(subset=["facility_code"])
    return df

def validate_schema(df):
    required = {"name"}
    current = set(df.columns)

    missing = required - current

    if missing:
        print("Available columns:", current)
        raise ValueError(f"Missing required columns: {missing}")

    return df

def run():
    df = load_data()
    print(f"Loaded {len(df)} records")

    df = standardize_columns(df)
    df = validate_schema(df)
    df = clean_text_fields(df)
    df = remove_duplicates(df)

    print(f"Final clean records: {len(df)}")

    df.to_csv(OUTPUT_FILE, index=False)
    print("Export complete.")

if __name__ == "__main__":
    run()