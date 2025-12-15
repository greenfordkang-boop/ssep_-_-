import pandas as pd
import os
import numpy as np

DATA_FILE = "sample_db.xlsx"

# Mapping: English (Old) -> Korean (New)
MAPPING = {
    "ID": "관리번호",
    "Request Date": "요청일",
    "Requester": "요청자",
    "Company": "업체명",
    "Project/Model": "차종/프로젝트",
    "Part Name": "품명",
    "Spec": "규격",
    "Quantity": "수량",
    "Target Date": "납기요청일",
    "Status": "진행상태",
    "Remarks": "비고",
    "Attachment": "첨부"
}

# The target schema order
NEW_COLUMNS = [
    "관리번호", "요청일", "요청자", "요청부서", "업체명", "이메일", "연락처", 
    "차종/프로젝트", "품명", "규격", "수량", "납기요청일", 
    "진행상태", "비고", "첨부"
]

def fix_database():
    if not os.path.exists(DATA_FILE):
        print("File not found.")
        return

    try:
        df = pd.read_excel(DATA_FILE)
        print("Initial columns:", df.columns.tolist())
        
        # Prepare a dictionary for the new data
        new_data = {}

        for col_kr in NEW_COLUMNS:
            # Find the corresponding English counterpart if it exists
            col_en = None
            for en, kr in MAPPING.items():
                if kr == col_kr:
                    col_en = en
                    break
            
            # Logic to merge data
            series_kr = df[col_kr] if col_kr in df.columns else None
            series_en = df[col_en] if col_en and col_en in df.columns else None

            if series_kr is not None and series_en is not None:
                # Merge: Use Korean data first, fill gaps with English data
                # Ensure we are working with consistent types (object usually safe)
                combined = series_kr.combine_first(series_en)
                new_data[col_kr] = combined
            elif series_kr is not None:
                new_data[col_kr] = series_kr
            elif series_en is not None:
                new_data[col_kr] = series_en
            else:
                # Neither exists, initialize empty
                new_data[col_kr] = ""

        # Create new DataFrame
        new_df = pd.DataFrame(new_data)
        
        # Order columns explicitly just to be sure
        new_df = new_df[NEW_COLUMNS]

        # Save
        new_df.to_excel(DATA_FILE, index=False)
        print("Database repaired and saved.")
        print("Final columns:", new_df.columns.tolist())
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_database()
