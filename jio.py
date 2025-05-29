
import streamlit as st

# --- Page Setup ---
st.set_page_config(page_title="Reliance Intern & Policy Issue Portal", layout="wide")
st.title("🚀 Reliance Intern & Policy Issue Portal")
st.image("https://raw.githubusercontent.com/Zishanmallick/Zishan/main/L.1.jpg", width=200)

# --- Roles and Passwords ---
INTERN_NAMES = [
    "Admin", "Chairman", "Policy", "Jio Retail Manager", "Jio Platforms Manager",
    "Jio Financial Manager", "Jio Legal Services",
    "Zishan Mallick", "Satvik Ahlawat", "Trapti Singh", "Ujjwal Akshith Mondreti",
    "Aanchal Verma", "Rohit Mishra"
]
ROLE_PASSWORDS = {
    "admin@jio": "admin",
    "retail@jio": "manager",
    "platforms@jio": "manager",
    "financial@jio": "manager",
    "legal@jio": "manager",
    "jio2025": "intern"
}

# --- Session Initialization ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_name = ""
    st.session_state.user_role = ""

# --- Dummy Component Functions ---
def display_tasks():
    st.header("🗓️ Weekly Tasks")
    st.write("Task content here.")

def display_blog_board():
    st.header("📰 Blog Board")
    st.write("Blog content and edit/post if role is admin/chairman/manager.")

def display_intern_profiles():
    st.header("👥 Intern Profiles")
    st.write("List of intern profiles here.")

def display_issue_tracker():
    st.header("📊 Issue Tracker")
    st.write("Admin/Chairman/Manager can view and edit issues here.")

# --- Login ---
def login():
    st.sidebar.header("Login")
    username = st.sidebar.selectbox("Select Your Name", INTERN_NAMES)
    password = st.sidebar.text_input("Password", type="password")
    login_btn = st.sidebar.button("Login")

    if login_btn:
        role = ROLE_PASSWORDS.get(password)
        if role:
            st.session_state.logged_in = True
            st.session_state.user_name = username
            st.session_state.user_role = role if username not in ["Admin", "Chairman"] else "admin"
            st.success(f"Welcome, {username}!")
            st.experimental_rerun()
        else:
            st.error("Invalid credentials.")

# --- Logout ---
def logout():
    if st.sidebar.button("Logout"):
        for key in ["logged_in", "user_name", "user_role"]:
            st.session_state.pop(key, None)
        st.experimental_rerun()

# --- Main App ---
def main():
    if not st.session_state.logged_in:
        login()
        return

    st.sidebar.write(f"Logged in as: **{st.session_state.user_name} ({st.session_state.user_role})**")
    logout()

    # Tabs based on roles
    tabs = ["Tasks"]
    if st.session_state.user_role in ["admin", "manager"]:
        tabs += ["Blog Board", "Intern Profiles", "Issue Tracker"]
    elif st.session_state.user_role == "intern":
        tabs += ["Blog Board", "Intern Profiles"]

    selection = st.selectbox("Select a section", tabs)

    if selection == "Tasks":
        display_tasks()
    elif selection == "Blog Board":
        display_blog_board()
    elif selection == "Intern Profiles":
        display_intern_profiles()
    elif selection == "Issue Tracker":
        display_issue_tracker()

if __name__ == "__main__":
    main()
