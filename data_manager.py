import pandas as pd
import os
from datetime import datetime

DATA_FILE = "sample_db.xlsx"

def init_db():
    """Initialize the Excel database if it doesn't exist."""
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=[
            "관리번호", "요청일", "요청자", "요청부서", "업체명", "이메일", "연락처", 
            "차종/프로젝트", "품명", "규격", "수량", "납기요청일", 
            "진행상태", "비고", "첨부"
        ])
        # Add some sample data for visualization
        sample_data = [
            {
                "관리번호": "REQ-20241215-001",
                "요청일": "2024-12-15",
                "요청자": "Client User 1",
                "요청부서": "개발팀",
                "업체명": "Client A",
                "이메일": "user@client.com",
                "연락처": "010-1234-5678",
                "차종/프로젝트": "EV-X1",
                "품명": "Battery Connector",
                "규격": "50A Gold Plated",
                "수량": 100,
                "납기요청일": "2024-12-25",
                "진행상태": "접수 (Received)",
                "비고": "Urgent",
                "첨부": ""
            }
        ]
        df = pd.concat([df, pd.DataFrame(sample_data)], ignore_index=True)
        df.to_excel(DATA_FILE, index=False)

def load_data():
    """Load data from Excel."""
    if not os.path.exists(DATA_FILE):
        init_db()
    
    # Reload in case it was just created
    try:
        df = pd.read_excel(DATA_FILE)
        
        # Auto-migration: Check for missing columns and add them
        expected_cols = [
            "관리번호", "요청일", "요청자", "요청부서", "업체명", "이메일", "연락처", 
            "차종/프로젝트", "품명", "규격", "수량", "납기요청일", 
            "진행상태", "비고", "첨부"
        ]
        
        updated = False
        for col in expected_cols:
            if col not in df.columns:
                df[col] = "" # Add missing column with empty string
                updated = True
        
        if updated:
            save_data(df)
            
        # Ensure ID column is treated as string
        if '관리번호' in df.columns:
            df['관리번호'] = df['관리번호'].astype(str)
        return df
    except Exception as e:
        print(f"Error loading DB: {e}")
        return pd.DataFrame()

def save_data(df):
    """Save dataframe to Excel."""
    try:
        df.to_excel(DATA_FILE, index=False)
        return True
    except Exception as e:
        print(f"Error saving DB: {e}")
        return False

def add_request(data_dict):
    """Add a new request to the database."""
    df = load_data()
    
    # Generate ID
    date_str = datetime.now().strftime("%Y%m%d")
    count = len(df) + 1
    new_id = f"REQ-{date_str}-{count:03d}"
    
    data_dict["관리번호"] = new_id
    data_dict["요청일"] = datetime.now().strftime("%Y-%m-%d")
    data_dict["진행상태"] = "접수대기"
    
    new_row = pd.DataFrame([data_dict])
    df = pd.concat([df, new_row], ignore_index=True)
    
    return save_data(df)


def merge_data(new_df):
    """Merge new data from uploaded Excel into the existing DB."""
    current_df = load_data()
    
    # Ensure ID column exists in new data, if not generate them or handle appropriately
    # For this simple version, we will just Append new rows that don't look like duplicates
    # A simple check: if 'ID' exists in new_df, update those rows. If not, append.
    
    if '관리번호' not in new_df.columns:
        # Assume these are NEW requests without IDs
        # We need to assign IDs to them
        start_count = len(current_df) + 1
        date_str = datetime.now().strftime("%Y%m%d")
        
        new_ids = []
        for i in range(len(new_df)):
            new_ids.append(f"REQ-{date_str}-{(start_count + i):03d}")
        new_df['관리번호'] = new_ids
        
    # Concatenate and save
    # Note: This is a simple append. For a real system, we might want to check for duplicates based on ID.
    # If ID exists, we update.
    
    updated_df = current_df.copy()
    
    # Separate into rows to update vs rows to append
    # This logic assumes new_df has 'ID' column populated now
    
    for index, row in new_df.iterrows():
        rid = row['관리번호']
        if rid in updated_df['관리번호'].values:
            # Update existing row
            # Find index of this ID
            idx = updated_df.index[updated_df['관리번호'] == rid].tolist()[0]
            # Update columns
            for col in new_df.columns:
                updated_df.at[idx, col] = row[col]
        else:
            # Append new row
            updated_df = pd.concat([updated_df, pd.DataFrame([row])], ignore_index=True)
            
    return save_data(updated_df)

def delete_requests_by_ids(ids_to_delete):
    """Delete requests that match the given list of IDs."""
    if not ids_to_delete:
        return False
        
    df = load_data()
    
    # Filter out the rows to be deleted
    # We keep rows where '관리번호' is NOT in ids_to_delete
    if '관리번호' in df.columns:
        # Ensure string comparison
        df = df[~df['관리번호'].astype(str).isin([str(x) for x in ids_to_delete])]
        return save_data(df)
    
    return False

def get_filtered_data(user_role, user_company):
    """Get data filtered by role and company."""
    df = load_data()
    
    if df.empty:
        return df

    if user_role == "admin":
        return df
    else:
        # Filter where Company matches user's company
        if "업체명" in df.columns:
            return df[df["업체명"] == user_company]
        return pd.DataFrame() # Return empty if column missing
