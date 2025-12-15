import pandas as pd
import os

DATA_FILE = "sample_db.xlsx"

# Mapping from English to Korean
COLUMN_MAPPING = {
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

def migrate():
    if not os.path.exists(DATA_FILE):
        print(f"File {DATA_FILE} not found.")
        return

    try:
        df = pd.read_excel(DATA_FILE)
        print("Columns before migration:", df.columns.tolist())
        
        # Check if migration is needed (if English columns exist)
        if "ID" in df.columns:
            df.rename(columns=COLUMN_MAPPING, inplace=True)
            df.to_excel(DATA_FILE, index=False)
            print("Migration successful. New columns:", df.columns.tolist())
        else:
            print("Migration already done or columns mismatch.")
            
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate()
