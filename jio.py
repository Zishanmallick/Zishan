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
    "blog": {"id": "1uyURjMiA8C1A7Yb5ZVAtUurb7ChCIKwKN7XeJhDP0Cg", "name": "Blogs"},
    "profiles": {"id": "1pdfnjg9gzRSpecLyw6kXzVmuPCj1ozq_DJGstQHEzdY", "name": "Intern Profiles"},
    "tasks": {"id": "1pdfnjg9gzRSpecLyw6kXzVmuPCj1ozq_DJGstQHEzdY", "name": "Weekly Tasks"},
    "issues": {"id": "1K7myr-bi4ry3z_tQyGg25nRJrn9QrGupeP3Tem1z4kQ", "name": "Issues"}
}

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "username" not in st.session_state:
    st.session_state.username = ""

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
    return pd.DataFrame(ws.get_all_records())

def append_to_sheet(sheet_key, row_data):
    ws = get_worksheet(sheet_key)
    ws.append_row(row_data)

def update_sheet(sheet_key, df):
    ws = get_worksheet(sheet_key)
    ws.update([df.columns.tolist()] + df.values.tolist())

def display_blog():
    st.header("📢 Blog Board")
    try:
        df = get_df("blog")
        if not df.empty and {'title', 'author', 'content', 'time'}.issubset(df.columns):
            for _, row in df.iterrows():
                st.markdown(f"### {row['title']}")
                st.markdown(f"**By {row['author']}** - {row['time']}")
                st.write(row['content'])
                st.markdown("---")
        else:
            st.warning("Blog sheet missing required columns.")
    except Exception as e:
        st.error(f"Blog error: {e}")

    if st.session_state.username in USER_CREDENTIALS and USER_CREDENTIALS[st.session_state.username].endswith("@jio"):
        title = st.text_input("Title")
        content = st.text_area("Content")
        if st.button("Post Blog"):
            append_to_sheet("blog", [title, st.session_state.username, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            st.success("Blog posted!")
            st.rerun()

def display_profiles():
    st.header("🧑‍🎓 Intern Profiles")
    try:
        df = get_df("profiles")
        st.dataframe(df)
    except Exception as e:
        st.error(f"Profiles error: {e}")

def display_tasks():
    st.header("🗂 Weekly Tasks")
    try:
        df = get_df("tasks")
        st.dataframe(df)
    except Exception as e:
        st.error(f"Tasks error: {e}")

def display_issues():
    st.header("⚠️ Issue Tracker")
    try:
        df = get_df("issues")
        st.dataframe(df)
    except Exception as e:
        st.error(f"Issues error: {e}")

def chat_box():
    st.header("💬 Intern Chat Room")
    for chat in st.session_state.chat_messages:
        st.markdown(f"**{chat['user']}**: {chat['message']}")
    with st.form("chat_form"):
        message = st.text_input("Message")
        submitted = st.form_submit_button("Send")
        if submitted and message:
            st.session_state.chat_messages.append({"user": st.session_state.username, "message": message})
            st.rerun()

def login():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.username = username
            st.success(f"Welcome, {username}!")
            st.experimental_rerun()
        else:
            st.error("Invalid credentials.")

def main():
    if not st.session_state.username:
        login()
    else:
        role = st.session_state.username
        st.sidebar.title(f"👋 Welcome, {role}!")
        st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())

        st.sidebar.markdown("---")
        if role.startswith("Jio") or role in ["Admin", "Chairman", "Policy"]:
            tab = st.sidebar.radio("Select View", ["Blogs", "Profiles", "Tasks", "Issues", "Chat"])
        else:
            tab = st.sidebar.radio("Select View", ["Blogs", "Chat"])

        if tab == "Blogs": display_blog()
        elif tab == "Profiles": display_profiles()
        elif tab == "Tasks": display_tasks()
        elif tab == "Issues": display_issues()
        elif tab == "Chat": chat_box()

main()
