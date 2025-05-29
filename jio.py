import streamlit as st
import pandas as pd
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Reliance Intern & Policy Issue Portal", layout="wide")
st.title("\U0001F680 Reliance Intern & Policy Issue Portal")
st.image("https://raw.githubusercontent.com/Zishanmallick/Zishan/main/L.1.jpg", width=200)

# --- Configuration ---
SHEET_CONFIG = {
    "tracker": {"id": "1tq_g6q7tnS2OQjhehSu4lieR3wTOJ-_s0RfItq0XzWI", "name": "Sheet1"},
    "response": {"id": "1pdfnjg9gzRSpecLyw6kXzVmuPCj1ozq_DJGstQHEzdY", "name": "Form Responses 1"},
    "log": {"id": "1K7myr-bi4ry3z_tQyGg25nRJrn9QrGupeP3Tem1z4kQ", "name": "Sheet1"},
    "blog": {"id": "1uyURjMiA8C1A7Yb5ZVAtUurb7ChCIKwKN7XeJhDP0Cg", "name": "Sheet1"},
}

ADMIN_PASSWORD = "admin@jio"
USER_PASSWORD = "jio2025"
INTERN_NAMES = [
    "Admin", "Chairman", "Policy", "Jio Retail Manager", "Jio Platforms Manager",
    "Jio Financial Manager", "Jio Legal Services",
    "Zishan Mallick", "Satvik Ahlawat", "Trapti Singh", "Ujjwal Akshith Mondreti",
    "Aanchal Verma", "Rohit Mishra"
]

TASKS = {
    "Week 1": "Intro to Jio Platforms + Submit project preference form",
    "Week 2": "Research Jio's AI Strategy and write 500-word report",
    "Week 3": "Group presentation on Jio Digital Transformation"
}
CURRENT_WEEK = "Week 3"

INTERN_PROFILES = [
    {"Name": "Zishan Mallick", "Department": "Business Analytics", "LinkedIn": "https://linkedin.com/in/zishan-mallick-5809a6181"},
    {"Name": "Satvik Ahlawat", "Department": "Marketing", "LinkedIn": "https://linkedin.com/in/satvik-ahlawat"},
    {"Name": "Trapti Singh", "Department": "Strategy", "LinkedIn": "https://linkedin.com/in/trapti-singh"},
    {"Name": "Ujjwal Akshith Mondreti", "Department": "Legal", "LinkedIn": "https://linkedin.com/in/ujjwal-mondreti"},
    {"Name": "Aanchal Verma", "Department": "Finance", "LinkedIn": "https://linkedin.com/in/aanchal-verma"},
    {"Name": "Rohit Mishra", "Department": "Business Analytics", "LinkedIn": "https://linkedin.com/in/rohit-mishra"}
]

# --- Google Sheets Client from Environment Variable ---
@st.cache_resource
def init_sheets_client():
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
        if not creds_json:
            st.error("GOOGLE_SHEETS_CREDENTIALS not found in environment. Make sure it's set in Streamlit Secrets.")
            st.stop()
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Failed to initialize Google Sheets client from environment variable: {e}")
        st.stop()

client = init_sheets_client()

# --- Placeholder for future functions: tracker, blogs, uploads, profiles, issue tracker, etc. ---

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

        st.write("## Dashboard")
        st.write("Now you can display tasks, blog, tracker, etc. here based on roles.")

if __name__ == "__main__":
    main()
