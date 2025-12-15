import streamlit as st
import time

# Hardcoded users for MVP
# Structure: username: {password, role, company, name}
USERS = {
    "admin": {
        "password": "admin",
        "role": "admin",
        "company": "Sinsung",
        "name": "관리자 (Admin)"
    },
    "client": {
        "password": "client",
        "role": "client",
        "company": "Client A",
        "name": "고객사 (Client A)"
    },
    "infac": {
        "password": "infac",
        "role": "client",
        "company": "INFAC",
        "name": "INFAC 담당자"
    }
}

def login(username, password):
    """Simple login check."""
    if username in USERS and USERS[username]["password"] == password:
        return USERS[username]
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
