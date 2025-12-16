import streamlit as st
import time
import json
import os

USERS_FILE = "users.json"

# Hardcoded users for MVP (기본 관리자 계정)
# Structure: username: {password, role, company, name}
DEFAULT_USERS = {
    "admin": {
        "password": "admin",
        "role": "admin",
        "company": "Sinsung",
        "name": "관리자 (Admin)"
    },
    "manager": {
        "password": "manager123",
        "role": "admin",
        "company": "Sinsung",
        "name": "매니저 (Manager)"
    }
}

def load_users():
    """Load users from JSON file."""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                users = json.load(f)
                # 기본 관리자 계정 병합 (기본 계정이 우선)
                users.update(DEFAULT_USERS)
                return users
        except:
            return DEFAULT_USERS.copy()
    else:
        # 파일이 없으면 기본 사용자만 반환하고 파일 생성
        save_users(DEFAULT_USERS.copy())
        return DEFAULT_USERS.copy()

def save_users(users):
    """Save users to JSON file."""
    try:
        # 기본 관리자 계정은 파일에 저장하지 않음 (항상 메모리에 유지)
        users_to_save = {k: v for k, v in users.items() if k not in DEFAULT_USERS.keys()}
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_to_save, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving users: {e}")
        return False

def register_user(username, password, company, name):
    """Register a new user (client role only)."""
    users = load_users()
    
    if username in users:
        return False, "이미 존재하는 아이디입니다."
    
    if not username or not password or not company or not name:
        return False, "모든 필드를 입력해주세요."
    
    users[username] = {
        "password": password,
        "role": "client",
        "company": company,
        "name": name
    }
    
    if save_users(users):
        return True, "회원가입이 완료되었습니다."
    else:
        return False, "회원가입 중 오류가 발생했습니다."

def change_password(username, old_password, new_password):
    """Change user password."""
    users = load_users()
    
    if username not in users:
        return False, "사용자를 찾을 수 없습니다."
    
    if users[username]["password"] != old_password:
        return False, "현재 비밀번호가 올바르지 않습니다."
    
    if not new_password:
        return False, "새 비밀번호를 입력해주세요."
    
    users[username]["password"] = new_password
    
    if save_users(users):
        return True, "비밀번호가 변경되었습니다."
    else:
        return False, "비밀번호 변경 중 오류가 발생했습니다."

def login(username, password):
    """Simple login check."""
    users = load_users()
    if username in users and users[username]["password"] == password:
        return users[username]
    return None

def logout():
    """Logout handler."""
    st.session_state["logged_in"] = False
    st.session_state["user_info"] = None
    st.rerun()

def check_auth():
    """Check if user is logged in, return user info or None."""
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["user_info"] = None
    
    return st.session_state["user_info"]
