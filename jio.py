import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- Streamlit Configuration ---
st.set_page_config(page_title="Reliance Intern Portal", layout="wide")
st.title("🚀 Reliance Intern Portal")
st.image("https://raw.githubusercontent.com/Zishanmallick/Zishan/main/L.1.jpg", width=200)

# --- Interns and Login Credentials ---
INTERN_NAMES = [
    "Admin", "Chairman", "Policy", "Jio Retail Manager", "Jio Platforms Manager",
    "Jio Financial Manager", "Jio Legal Services",
    "Zishan Mallick", "Satvik Ahlawat", "Trapti Singh", "Ujjwal Akshith Mondreti",
    "Aanchal Verma", "Rohit Mishra"
]

ADMIN_PASSWORD = "admin@jio"
USER_PASSWORD = "jio2025"

# --- Google Sheets Setup from Streamlit Secrets ---
@st.cache_resource

def init_gspread_client():
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds_dict = st.secrets["GOOGLE_SHEETS_CREDENTIALS"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Google Sheets connection failed: {e}")
        st.stop()

client = init_gspread_client()

# --- Sample Dashboard Tabs ---
def show_tasks():
    st.header("📌 Weekly Tasks")
    tasks = {
        "Week 1": "Intro to Jio Platforms + Submit project preference form",
        "Week 2": "Research Jio's AI Strategy and write 500-word report",
        "Week 3": "Group presentation on Jio Digital Transformation"
    }
    for week, task in tasks.items():
        st.subheader(week)
        st.write(task)

def show_profiles():
    st.header("👥 Intern Profiles")
    interns = [
        {"Name": "Zishan Mallick", "Department": "Business Analytics", "LinkedIn": "https://linkedin.com/in/zishan-mallick-5809a6181"},
        {"Name": "Satvik Ahlawat", "Department": "Marketing", "LinkedIn": "https://linkedin.com/in/satvik-ahlawat"},
        {"Name": "Trapti Singh", "Department": "Strategy", "LinkedIn": "https://linkedin.com/in/trapti-singh"},
        {"Name": "Ujjwal Akshith Mondreti", "Department": "Legal", "LinkedIn": "https://linkedin.com/in/ujjwal-mondreti"},
        {"Name": "Aanchal Verma", "Department": "Finance", "LinkedIn": "https://linkedin.com/in/aanchal-verma"},
        {"Name": "Rohit Mishra", "Department": "Business Analytics", "LinkedIn": "https://linkedin.com/in/rohit-mishra"}
    ]
    for intern in interns:
        st.markdown(f"**{intern['Name']}** – {intern['Department']}  ")
        st.markdown(f"[LinkedIn Profile]({intern['LinkedIn']})")

# --- Login and Main App ---
def main():
    st.sidebar.header("Login")
    username = st.sidebar.selectbox("Select Your Name", INTERN_NAMES)
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if password == ADMIN_PASSWORD:
            st.session_state.user_name = username
            st.session_state.logged_in = True
            st.session_state.is_admin = True
            st.success(f"Welcome, Admin {username}!")
            st.rerun()
        elif password == USER_PASSWORD:
            st.session_state.user_name = username
            st.session_state.logged_in = True
            st.session_state.is_admin = False
            st.success(f"Welcome, {username}!")
            st.rerun()
        else:
            st.error("Incorrect credentials")

    if st.session_state.get("logged_in"):
        st.sidebar.success(f"Logged in as: {st.session_state.user_name}")
        if st.sidebar.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        selected_tab = st.selectbox("Select Tab", ["Tasks", "Intern Profiles"])
        if selected_tab == "Tasks":
            show_tasks()
        elif selected_tab == "Intern Profiles":
            show_profiles()

if __name__ == "__main__":
    main()
