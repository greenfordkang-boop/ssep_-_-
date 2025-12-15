import pandas as pd
import os

DATA_FILE = "sample_db.xlsx"

if os.path.exists(DATA_FILE):
    df = pd.read_excel(DATA_FILE)
    print("Current Columns:", df.columns.tolist())
    print("First row data:", df.iloc[0].to_dict() if not df.empty else "Empty")
else:
    print("File not found.")
