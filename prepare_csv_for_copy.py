# prepare_csv_for_copy.py
import pandas as pd
import csv
from pathlib import Path

def prepare_csv_for_postgres(input_file, output_file):
    """
    Prepare CSV for PostgreSQL COPY command:
    - Handle NULL values
    - Fix encoding
    - Clean special characters
    """
    
    print(f"📝 Preparing {input_file} for PostgreSQL COPY...")
    
    # Read CSV
    df = pd.read_csv(input_file)
    print(f"📊 Loaded {len(df)} records")
    
    # Replace NaN with empty string (will become NULL in PostgreSQL)
    df = df.fillna('')
    
    # Clean text fields - remove problematic characters
    text_columns = df.select_dtypes(include=['object']).columns
    for col in text_columns:
        df[col] = df[col].astype(str).str.replace('\n', ' ').str.replace('\r', ' ')
        df[col] = df[col].str.replace('"', '""')  # Escape quotes
        df[col] = df[col].str.strip()
    
    # Handle boolean fields
    if 'open_24_hours' in df.columns:
        df['open_24_hours'] = df['open_24_hours'].map({
            'yes': 't', 'true': 't', '1': 't', 'y': 't',
            'no': 'f', 'false': 'f', '0': 'f', 'n': 'f'
        }).fillna('f')
    
    if 'open_weekends' in df.columns:
        df['open_weekends'] = df['open_weekends'].map({
            'yes': 't', 'true': 't', '1': 't', 'y': 't',
            'no': 'f', 'false': 'f', '0': 'f', 'n': 'f'
        }).fillna('f')
    
    # Handle numeric fields
    numeric_columns = ['beds', 'cots', 'latitude', 'longitude']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Save with proper CSV formatting for COPY
    df.to_csv(output_file, 
              index=False, 
              quoting=csv.QUOTE_MINIMAL,
              encoding='utf-8',
              na_rep='\\N')  # PostgreSQL NULL representation
    
    print(f"✅ Prepared file saved to: {output_file}")
    print(f"   File size: {Path(output_file).stat().st_size / (1024*1024):.2f} MB")
    
    # Show sample
    print("\n📋 First 3 rows (preview):")
    print(df.head(3).to_string())
    
    return output_file

if __name__ == "__main__":
    input_file = "facility_data/final_facilities.csv"
    output_file = "facility_data/facilities_for_postgres.csv"
    prepare_csv_for_postgres(input_file, output_file)