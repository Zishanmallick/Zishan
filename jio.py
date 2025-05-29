# Updated version integrating 3 Google Sheets (Tracker, Blog, Responses)
# and ensuring full access control with Intern, Manager, Admin logins

import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Reliance Intern & Policy Issue Portal", layout="wide")
st.title("🚀 Reliance Intern & Policy Issue Portal")
st.image("https://raw.githubusercontent.com/Zishanmallick/Zishan/main/L.1.jpg", width=200)

# --- Configuration ---
SHEET_CONFIG = {
    "tracker": {"id": "1tq_g6q7tnS2OQjhehSu4lieR3wTOJ-_s0RfItq0XzWI", "name": "Sheet1"},
    "response": {"id": "1pdfnjg9gzRSpecLyw6kXzVmuPCj1ozq_DJGstQHEzdY", "name": "Form Responses 1"},
    "blog": {"id": "1uyURjMiA8C1A7Yb5ZVAtUurb7ChCIKwKN7XeJhDP0Cg", "name": "Sheet1"},
}

GOOGLE_CREDS_FILE = "reliance-jio-461118-34d43c8520bf.json"

# Passwords for access control
PASSWORDS = {
    "admin": "admin@jio",
    "user": "jio2025",
    "Jio Retail Manager": "retail@jio",
    "Jio Platforms Manager": "platforms@jio",
    "Jio Financial Manager": "financial@jio",
    "Jio Legal Services": "legal@jio",
}

# Define roles
ADMINS = ["Admin", "Chairman"]
MANAGERS = ["Jio Retail Manager", "Jio Platforms Manager", "Jio Financial Manager", "Jio Legal Services"]
INTERN_NAMES = ADMINS + MANAGERS + [
    "Zishan Mallick", "Satvik Ahlawat", "Trapti Singh", "Ujjwal Akshith Mondreti",
    "Aanchal Verma", "Rohit Mishra"]

# --- Google Sheets Client ---
@st.cache_resource
def init_gspread():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDS_FILE, scope)
    return gspread.authorize(creds)

gclient = init_gspread()

def get_df(sheet_id, name):
    ws = gclient.open_by_key(sheet_id).worksheet(name)
    data = ws.get_all_records()
    return pd.DataFrame(data)

def append_row(sheet_id, name, row):
    ws = gclient.open_by_key(sheet_id).worksheet(name)
    ws.append_row(row)

# --- Login ---
def login():
    st.sidebar.header("Login")
    user = st.sidebar.selectbox("Select User", INTERN_NAMES)
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        correct = PASSWORDS.get(user, PASSWORDS['user']) == password
        if correct:
            st.session_state.user = user
            st.session_state.logged_in = True
            st.success(f"Welcome, {user}!")
            st.rerun()
        else:
            st.error("Invalid credentials")

def logout():
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.success("Logged out")
        st.rerun()

# --- Role Check ---
def is_admin(): return st.session_state.user in ADMINS

def is_manager(): return st.session_state.user in MANAGERS

# --- Blog Section ---
def blog_board():
    st.header("📢 Blog Board")
    blogs = get_df(SHEET_CONFIG["blog"]["id"], SHEET_CONFIG["blog"]["name"])
    if not blogs.empty:
        for _, row in blogs.iterrows():
            st.subheader(row['title'])
            st.markdown(f"**By:** {row['author']}  ⏰ {row['time']}")
            st.info(row['content'])
            st.markdown("---")

    if is_admin() or is_manager():
        st.subheader("➕ Post a Blog")
        title = st.text_input("Title")
        content = st.text_area("Content")
        if st.button("Post"):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            append_row(SHEET_CONFIG["blog"]["id"], SHEET_CONFIG["blog"]["name"], [st.session_state.user, title, content, now])
            st.success("Blog posted!")
            st.rerun()

# --- Tasks Section ---
def task_board():
    st.header("📘 Weekly Tasks")
    st.write("Week 1: Submit form")
    st.write("Week 2: Research Jio's AI strategy")
    st.write("Week 3: Group Presentation")
    st.subheader("📤 Submit your task")
    week = st.selectbox("Select Week", ["Week 1", "Week 2", "Week 3"])
    file = st.file_uploader("Upload file", type=["pdf", "docx"])
    if st.button("Submit Task"):
        if file:
            st.success(f"Submitted for {week}!")
        else:
            st.warning("Upload a file to submit")

# --- Intern Profiles ---
def intern_profiles():
    st.header("👨‍🎓 Intern Profiles")
    df = pd.DataFrame([
        {"Name": "Zishan Mallick", "Dept": "Business Analytics", "LinkedIn": "https://linkedin.com/in/zishan-mallick-5809a6181"},
        {"Name": "Satvik Ahlawat", "Dept": "Marketing", "LinkedIn": "https://linkedin.com/in/satvik-ahlawat"},
        {"Name": "Trapti Singh", "Dept": "Strategy", "LinkedIn": "https://linkedin.com/in/trapti-singh"},
        {"Name": "Ujjwal Akshith", "Dept": "Legal", "LinkedIn": "https://linkedin.com/in/ujjwal-mondreti"},
        {"Name": "Aanchal Verma", "Dept": "Finance", "LinkedIn": "https://linkedin.com/in/aanchal-verma"},
        {"Name": "Rohit Mishra", "Dept": "Business Analytics", "LinkedIn": "https://linkedin.com/in/rohit-mishra"},
    ])
    st.dataframe(df)

# --- Main App ---
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        login()
        return

    logout()

    tabs = ["Tasks", "Blog Board", "Intern Profiles"]
    if is_admin() or is_manager():
        tabs.append("Issue Tracker")

    selected = st.selectbox("Select Tab", tabs)
    if selected == "Tasks": task_board()
    elif selected == "Blog Board": blog_board()
    elif selected == "Intern Profiles": intern_profiles()
    elif selected == "Issue Tracker":
        st.header("🛠️ Issue Tracker")
        st.dataframe(get_df(SHEET_CONFIG["tracker"]["id"], SHEET_CONFIG["tracker"]["name"]))

if __name__ == '__main__':
    main()
