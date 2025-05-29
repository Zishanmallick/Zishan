import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Reliance Intern & Policy Issue Portal", layout="wide")
st.title("🚀 Reliance Intern & Policy Issue Portal")
st.image("https://raw.githubusercontent.com/Zishanmallick/Zishan/main/L.1.jpg", width=200)

# --- Configuration ---
SHEET_CONFIG = {
    "tracker": {"id": "1tq_g6q7tnS2OQjhehSu4lieR3wTOJ-_s0RfItq0XzWI", "name": "Sheet1"},
    "response": {"id": "1pdfnjg9gzRSpecLyw6kXzVmuPCj1ozq_DJGstQHEzdY", "name": "Form Responses 1"},
    "blog": {"id": "1uyURjMiA8C1A7Yb5ZVAtUurb7ChCIKwKN7XeJhDP0Cg", "name": "Sheet1"},
    "profiles": {"id": "1aBCdEfGhIJKlmNoPQRstuVwXyZ1234567890abcdEFG", "name": "Sheet1"},
    "tasks": {"id": "1xyZabCdEFGhijKLmnOPQRStuvWXYz1234567890abcD", "name": "Sheet1"}
}

# --- Dummy Chat Messages Storage ---
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# --- Dummy Auth Configuration ---
USER_CREDENTIALS = {
    "Admin": "admin@jio",
    "Chairman": "admin@jio",
    "Policy": "policy@jio",
    "Jio Retail Manager": "retail@jio",
    "Jio Platforms Manager": "platforms@jio",
    "Jio Financial Manager": "finance@jio",
    "Jio Legal Services": "legal@jio",
    "Zishan Mallick": "jio2025",
    "Satvik Ahlawat": "jio2025",
    "Trapti Singh": "jio2025",
    "Ujjwal Akshith Mondreti": "jio2025",
    "Aanchal Verma": "jio2025",
    "Rohit Mishra": "jio2025"
}

# --- Sheets Setup ---
@st.cache_resource
def init_sheets_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("reliance-jio-461118-34d43c8520bf.json", scope)
    return gspread.authorize(creds)

client = init_sheets_client()

def get_worksheet(sheet_key):
    config = SHEET_CONFIG[sheet_key]
    return client.open_by_key(config["id"]).worksheet(config["name"])

def get_df(sheet_key):
    ws = get_worksheet(sheet_key)
    data = ws.get_all_records()
    return pd.DataFrame(data)

def append_to_sheet(sheet_key, row_data):
    ws = get_worksheet(sheet_key)
    ws.append_row(row_data)

# --- Login Logic ---
def login():
    st.sidebar.header("🔐 Login")
    username = st.sidebar.selectbox("Select Your Name", list(USER_CREDENTIALS.keys()))
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if USER_CREDENTIALS.get(username) == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome, {username}!")
            st.rerun()
        else:
            st.error("Invalid credentials")

# --- Logout Logic ---
def logout():
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- Chat Feature ---
def display_chat():
    st.header("💬 Intern Chat Room")
    for msg in st.session_state.chat_messages:
        st.markdown(f"**{msg['user']}**: {msg['message']}")
    with st.form("chat_form"):
        message = st.text_input("Your message")
        submitted = st.form_submit_button("Send")
        if submitted and message:
            st.session_state.chat_messages.append({"user": st.session_state.username, "message": message})
            st.rerun()

# --- Blog Board ---
def display_blog():
    st.header("📢 Blog Board")
    df = get_df("blog")
    for _, row in df.iterrows():
        st.markdown(f"### {row['title']}")
        st.markdown(f"**By {row['author']}** - {row['time']}")
        st.write(row['content'])
        st.markdown("---")
    if st.session_state.username in USER_CREDENTIALS and USER_CREDENTIALS[st.session_state.username].endswith("@jio"):
        title = st.text_input("Title")
        content = st.text_area("Content")
        if st.button("Post Blog"):
            append_to_sheet("blog", [st.session_state.username, title, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            st.success("Blog posted!")
            st.rerun()

# --- Task Submission ---
def display_tasks():
    st.header("🗂 Weekly Tasks")
    df = get_df("tasks")
    st.dataframe(df)
    st.subheader("Submit Your Task")
    week = st.selectbox("Week", df['Week'].unique())
    uploaded = st.file_uploader("Upload Task")
    if st.button("Submit") and uploaded:
        st.success(f"Task for {week} submitted successfully!")

# --- Intern Profiles ---
def display_profiles():
    st.header("👤 Intern Profiles")
    df = get_df("profiles")
    st.dataframe(df)

# --- Issue Tracker ---
def display_issue_tracker():
    st.header("🛠 Issue Tracker")
    df = get_df("tracker")
    st.dataframe(df)
    if st.session_state.username in USER_CREDENTIALS and USER_CREDENTIALS[st.session_state.username].endswith("@jio"):
        st.subheader("Update an Issue")
        issue_id = st.selectbox("Select Issue ID", df['id'].unique())
        row = df[df['id'] == issue_id].iloc[0]
        status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"], index=["Open", "In Progress", "Resolved", "Closed"].index(row['Status']))
        resolution = st.text_area("Resolution", row['Resolution'])
        if st.button("Save Changes"):
            ws = get_worksheet("tracker")
            idx = df.index[df['id'] == issue_id][0] + 2  # Account for header
            ws.update(f"N{idx}", status)
            ws.update(f"L{idx}", resolution)
            st.success("Issue updated successfully!")
            st.rerun()

# --- Main ---
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        login()
    else:
        st.sidebar.write(f"Logged in as: {st.session_state.username}")
        logout()
        tabs = ["Tasks", "Blog Board", "Intern Profiles", "Chat"]
        if USER_CREDENTIALS[st.session_state.username].endswith("@jio"):
            tabs.append("Issue Tracker")
        selected = st.selectbox("Choose a section", tabs)
        if selected == "Chat":
            display_chat()
        elif selected == "Tasks":
            display_tasks()
        elif selected == "Blog Board":
            display_blog()
        elif selected == "Intern Profiles":
            display_profiles()
        elif selected == "Issue Tracker":
            display_issue_tracker()

if __name__ == "__main__":
    main()
