import streamlit as st
import pandas as pd
import os
from PIL import Image
import requests
from io import BytesIO  # Required to open image from bytes
import datetime
import json
import uuid # For generating unique IDs for new issues

# --- Google Sheets API Imports ---
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Configuration for Google Sheet ---
# This is the base URL of your Google Sheet. gspread will use this to open it.
ISSUES_GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1tq_g6q7tnS2OQjhehSu4lieR3wTOJ-_s0RfItq0XzWI"

# --- IMPORTANT: Path to your Google Service Account Credentials JSON file ---
# Make sure this file is in the same directory as your Streamlit app or provide a full path.
# For deployment, consider using Streamlit Secrets for this sensitive file.
CREDENTIALS_FILE_PATH = "credentials.json" # <--- UPDATE THIS IF YOUR FILE IS NAMED DIFFERENTLY OR IS IN ANOTHER LOCATION

# -------------------------------
# PAGE CONFIGURATION
# -------------------------------
st.set_page_config(page_title="Reliance Intern + Policy Issue Tracker", layout="wide")

# -------------------------------
# SESSION SETUP
# -------------------------------
# Initialize session state variables if they don't exist
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "chat" not in st.session_state:
    st.session_state.chat = []
if "intern_data" not in st.session_state:
    st.session_state.intern_data = [
        {"Name": "Zishan Mallick", "Department": "Business Analytics", "LinkedIn": "https://linkedin.com/in/zishan-mallick-5809a6181"},
        {"Name": "Aanchal Verma", "Department": "Finance", "LinkedIn": "https://linkedin.com/in/aanchal-verma-084076325"},
        {"Name": "Trapti Singh", "Department": "Finance", "LinkedIn": "https://linkedin.com/in/trapti-singh16"},
        {"Name": "Ujjwal Akshith Mondreti", "Department": "Machine Learning", "LinkedIn": "https://linkedin.com/in/ujjwal-akshith-m"},
        {"Name": "Satvik Ahlawat", "Department": "Data Science", "LinkedIn": "https://linkedin.com/in/satvikahlawat/"},
        {"Name": "Rohit Mishra", "Department": "Data Analytics", "LinkedIn": "https://linkedin.com/in/rohit-mishra-a6689031b"},
    ]

# Initialize issues data (will be populated by load_issues_from_google_sheet)
if 'issues_data' not in st.session_state:
    st.session_state.issues_data = pd.DataFrame(columns=[
        "id", "Business Vertical", "Team", "Contact", "Email/Phone",
        "Issue Title", "Description", "Issue Type", "Gov Body",
        "Priority", "Resolution", "File", "Date", "Status", "Response",
        "Updated By", "Last Updated"
    ])

# -------------------------------
# GOOGLE SHEET OPERATIONS
# -------------------------------
@st.cache_resource # Cache the gspread client to avoid re-authenticating on every rerun
def get_gspread_client():
    """Authenticate and return a gspread client."""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        if not os.path.exists(CREDENTIALS_FILE_PATH):
            st.error(f"Authentication Error: Google Sheets credentials file not found at '{CREDENTIALS_FILE_PATH}'. Please ensure it exists and the path is correct.")
            return None
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE_PATH, scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Authentication failed for Google Sheets: {e}. Please check your credentials file and permissions.")
        return None

def load_issues_from_google_sheet():
    """Loads issues from the Google Sheet."""
    client = get_gspread_client()
    if not client:
        return pd.DataFrame(columns=[ # Return empty df on auth failure
            "id", "Business Vertical", "Team", "Contact", "Email/Phone",
            "Issue Title", "Description", "Issue Type", "Gov Body",
            "Priority", "Resolution", "File", "Date", "Status", "Response",
            "Updated By", "Last Updated"
        ])
    try:
        sheet = client.open_by_url(ISSUES_GOOGLE_SHEET_URL).sheet1
        data = sheet.get_all_records()  # Fetch all rows as a list of dicts
        df = pd.DataFrame(data)

        # Ensure 'id' column exists, add it if missing (for new rows added manually to sheet)
        if 'id' not in df.columns:
            df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
            st.warning("No 'id' column found in Google Sheet. Assigning temporary UUIDs for internal use. Please add an 'id' column to your sheet for persistent IDs.")
        return df
    except Exception as e:
        st.error(f"Error loading issues from Google Sheet: {e}. Ensure the sheet is shared with the service account and the URL is correct.")
        return pd.DataFrame(columns=[
            "id", "Business Vertical", "Team", "Contact", "Email/Phone",
            "Issue Title", "Description", "Issue Type", "Gov Body",
            "Priority", "Resolution", "File", "Date", "Status", "Response",
            "Updated By", "Last Updated"
        ])

def save_issues_to_google_sheet(df):
    """Saves the issues DataFrame back to Google Sheet."""
    client = get_gspread_client()
    if not client:
        st.error("Cannot save: Google Sheets client not authenticated.")
        return False
    try:
        sheet = client.open_by_url(ISSUES_GOOGLE_SHEET_URL).sheet1

        # Clear existing data and upload the updated dataframe
        # Note: This clears ALL data in sheet1 and replaces it.
        # For partial updates, you'd need to find the specific row and update it.
        sheet.clear()
        sheet.update([df.columns.values.tolist()] + df.values.tolist())
        st.success("Changes saved to Google Sheet.")
        return True
    except Exception as e:
        st.error(f"Error saving issues to Google Sheet: {e}. Check service account permissions.")
        return False

# Load issues data on app start from Google Sheet
st.session_state.issues_data = load_issues_from_google_sheet()


# -------------------------------
# LOAD LOGO FROM GITHUB URL
# -------------------------------
logo_url = "https://raw.githubusercontent.com/Zishanmallick/Zishan/main/L.1.jpg"

try:
    response = requests.get(logo_url)
    response.raise_for_status()
    reliance_logo = Image.open(BytesIO(response.content))

    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(reliance_logo, width=150)
    with col2:
        st.title("Reliance Intern & Policy Issue Portal")
except Exception as e:
    st.error(f"Error: Failed to load logo from {logo_url}. Error: {e}")
    st.title("Reliance Intern & Policy Issue Portal")


# -------------------------------
# LOGIN SIDEBAR
# -------------------------------
st.sidebar.title("Login")
all_names = ["Admin", "Chairman", "Policy", "Jio Retail Manager", "Jio Platforms Manager", "Jio Financial Manager", "Jio Legal Services"] + [intern["Name"] for intern in st.session_state.intern_data]
selected_user = st.sidebar.selectbox("Select Your Name", all_names)
entered_password = st.sidebar.text_input("Enter Access Code", type="password")

if st.sidebar.button("Login"):
    # Custom authentication based on roles
    if selected_user == "Admin" and entered_password == "admin@jio":
        st.session_state.logged_in = True
        st.session_state.user_name = "Admin"
        st.session_state.is_admin = True
        st.success("Welcome, Admin!")
    elif selected_user == "Chairman" and entered_password == "chairman@jio":
        st.session_state.logged_in = True
        st.session_state.user_name = "Chairman"
        st.success("Welcome, Chairman Office!")
    elif selected_user == "Policy" and entered_password == "policy@jio":
        st.session_state.logged_in = True
        st.session_state.user_name = "Policy"
        st.success("Welcome to the Policy Dashboard!")
    elif selected_user == "Jio Retail Manager" and entered_password == "retail@jio":
        st.session_state.logged_in = True
        st.session_state.user_name = "Jio Retail Manager"
        st.success("Welcome, Jio Retail Manager!")
    elif selected_user == "Jio Platforms Manager" and entered_password == "platforms@jio":
        st.session_state.logged_in = True
        st.session_state.user_name = "Jio Platforms Manager"
        st.success("Welcome, Jio Platforms Manager!")
    elif selected_user == "Jio Financial Manager" and entered_password == "financial@jio":
        st.session_state.logged_in = True
        st.session_state.user_name = "Jio Financial Manager"
        st.success("Welcome, Jio Financial Manager!")
    elif selected_user == "Jio Legal Services" and entered_password == "legal@jio":
        st.session_state.logged_in = True
        st.session_state.user_name = "Jio Legal Services"
        st.success("Welcome, Jio Legal Services!")
    # Intern Login Logic
    elif selected_user not in ["Admin", "Chairman", "Policy", "Jio Retail Manager", "Jio Platforms Manager", "Jio Financial Manager", "Jio Legal Services"] and entered_password == "jio2025":
        st.session_state.logged_in = True
        st.session_state.user_name = selected_user
        st.success(f"Welcome, {selected_user}!")
    else:
        st.error("Incorrect Access Code.")


# -------------------------------
# LOGOUT FUNCTIONALITY
# -------------------------------
if st.session_state.logged_in:
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.session_state.is_admin = False
        st.success("You have been logged out.")
        st.rerun() # Use st.rerun() for full app refresh


# -------------------------------
# MAIN APPLICATION CONTENT
# -------------------------------

# Intern Dashboard (Logged in as an Intern)
if st.session_state.logged_in and st.session_state.user_name not in ["Admin", "Chairman", "Policy", "Jio Retail Manager", "Jio Platforms Manager", "Jio Financial Manager", "Jio Legal Services"]:
    st.header("Your Dashboard – Weekly Tasks & Submissions")
    st.markdown(f"Welcome, **{st.session_state.user_name}**! Here are your tasks and ways to connect.")
    st.divider()

    tab_tasks, tab_blogs, tab_profiles = st.tabs([
        "Tasks", "Blog Board", "Interns"
    ])

    with tab_tasks:
        st.subheader("Announcements")
        announcements = [
            "Intern Townhall on **May 25 at 4:00 PM**.",
            "Task 2 deadline: **May 24, 11:59 PM**.",
            "Intern of the Week: **Zishan Mallick!**"
        ]
        for note in announcements:
            st.info(note)

        st.divider()

        st.subheader("Weekly Tasks")
        tasks = {
            "Week 1": "Intro to Jio Platforms + Submit project preference form",
            "Week 2": "Research Jio's AI Strategy and write 500-word report",
            "Week 3": "Group presentation on Jio Digital Transformation"
        }
        for week, desc in tasks.items():
            st.write(f"**{week}:** {desc}")

        st.subheader("Reading Materials")
        pdfs = {
            "Week 1 – Jio Overview": "materials/JioBrain.pdf",
            "Week 2 – AI Strategy": "materials/Digital Transformation PPT for DFS Meeting_Sept2024.pdf",
            "Week 3 – Digital Transformation": "materials/RIL_4Q_FY25_Analyst_Presentation_25Apr25.pdf"
        }
        for title, path in pdfs.items():
            st.subheader(title)
            try:
                with open(path, "rb") as f:
                    st.download_button("Download", f, file_name=os.path.basename(path))
            except FileNotFoundError:
                st.warning(f"Missing file: {os.path.basename(path)}")

        st.divider()

        st.subheader("Submit Task")
        with st.form("upload_form"):
            week = st.selectbox("Select Week", list(tasks.keys()))
            file = st.file_uploader("Upload PDF/DOC", type=["pdf", "docx"])
            submitted = st.form_submit_button("Submit")
            if submitted and file:
                os.makedirs("uploads", exist_ok=True)
                path = f"uploads/{st.session_state.user_name.replace(' ', '_')}_{week}_{file.name}"
                with open(path, "wb") as f:
                    f.write(file.read())
                st.success("Uploaded and saved successfully!")

        st.divider()

        st.subheader("Intern Chat")
        chat_msg = st.text_input("Message:")
        if st.button("Send") and chat_msg:
            st.session_state.chat.append(f"{st.session_state.user_name}: {chat_msg}")
        for msg in st.session_state.chat[-10:]:
            st.write(msg)


    with tab_blogs:
        st.subheader("Intern Blog Board")
        if os.path.exists("blog_posts.csv"):
            blog_df = pd.read_csv("blog_posts.csv")
            for _, row in blog_df.iterrows():
                st.subheader(row["Title"])
                st.write(row["Content"])
                st.markdown("---")
        else:
            st.info("No blogs yet.")

    with tab_profiles:
        st.subheader("Intern Profiles")
        for intern in st.session_state.intern_data:
            st.subheader(intern["Name"])
            st.write(f"**Department:** {intern['Department']}")
            st.markdown(f"[LinkedIn]({intern['LinkedIn']})", unsafe_allow_html=True)
            st.markdown("---")


# -------------------------------
# POLICY + ADMIN/CHAIRMAN + MANAGERS DASHBOARD
# -------------------------------
elif st.session_state.logged_in and st.session_state.user_name in ["Policy", "Admin", "Chairman", "Jio Retail Manager", "Jio Platforms Manager", "Jio Financial Manager", "Jio Legal Services"]:
    st.header("Policy Issues Tracker")
    st.markdown(f"Welcome, **{st.session_state.user_name}**!")

    # Public Submissions from Google Form (external CSV URL) - unchanged
    csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQXnxefBfU43AgIEdCeCd5QBMgGVSifK9fSmSFuZd_jA_6B0Xem13xSjVqCY31QKsB88sjlOEa5T_gX/pub?output=csv"
    try:
        df_live = pd.read_csv(csv_url)
        st.success("Google Form data loaded successfully!")
        st.subheader("Public Submissions (from Google Form)")
        st.dataframe(df_live, use_container_width=True)
    except Exception as e:
        st.error(f"Google Form data failed to load: {e}")

    st.subheader("Internal Tracker & Review (Live via Google Sheet)")

    # Load issues from the new Google Sheet URL
    st.session_state.issues_data = load_issues_from_google_sheet()

    df = st.session_state.issues_data.copy()
    user_role = st.session_state.user_name

    if user_role == "Jio Retail Manager":
        df = df[df["Business Vertical"].isin(["Retail", "Reliance Retail", "Reliance Digital"])]
    elif user_role == "Jio Platforms Manager":
        df = df[df["Business Vertical"] == "Jio Platforms"]
    elif user_role == "Jio Financial Manager":
        df = df[df["Business Vertical"] == "Jio Financial"]
    elif user_role == "Jio Legal Services":
        df = df[(df["Issue Type"] == "Regulatory") | (df["Gov Body"] == "SEBI")]

    if not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            selected_priority = st.selectbox("Filter by Priority", ["All"] + df["Priority"].dropna().unique().tolist())
        with col2:
            selected_status = st.selectbox("Filter by Status", ["All", "New", "In Review", "Actioned", "Needs Clarification", "Solved"])

        filtered = df.copy()
        if selected_priority != "All":
            filtered = filtered[filtered["Priority"] == selected_priority]
        if selected_status != "All":
            filtered = filtered[filtered["Status"] == selected_status]

        st.dataframe(filtered, use_container_width=True)

        st.subheader("Update Issue Status (Changes are persisted to Google Sheet)")
        issue_selection_options = filtered['Issue Title'].tolist()
        selected_issue_title = st.selectbox("Select Issue to Update", issue_selection_options)

        if selected_issue_title:
            original_df = st.session_state.issues_data.copy()
            selected_issue_row = original_df[original_df['Issue Title'] == selected_issue_title]
            if not selected_issue_row.empty:
                selected_issue_id = selected_issue_row['id'].iloc[0]
                current_issue_status = selected_issue_row['Status'].iloc[0]
                current_issue_response = selected_issue_row['Response'].iloc[0]
            else:
                selected_issue_id = None
                current_issue_status = "New"
                current_issue_response = ""
                st.warning("Could not find selected issue in original data. Defaulting status/response.")


            new_status = st.selectbox("Update Status", ["New", "In Review", "Actioned", "Needs Clarification", "Solved"],
                                      index=["New", "In Review", "Actioned", "Needs Clarification", "Solved"].index(current_issue_status))
            response_text = st.text_area("Add Response", value=current_issue_response)

            if st.button("Update Issue"):
                if selected_issue_id:
                    idx = st.session_state.issues_data[st.session_state.issues_data['id'] == selected_issue_id].index[0]
                    st.session_state.issues_data.at[idx, "Status"] = new_status
                    st.session_state.issues_data.at[idx, "Response"] = response_text
                    st.session_state.issues_data.at[idx, "Updated By"] = st.session_state.user_name
                    st.session_state.issues_data.at[idx, "Last Updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # Save changes to Google Sheet
                    save_issues_to_google_sheet(st.session_state.issues_data)
                    st.success("Issue updated in current session's view and persisted to Google Sheet.")
                    st.rerun()
                else:
                    st.error("Cannot update: Issue ID not found.")
    else:
        st.info("No issues found for your department/role in the tracker.")

    st.download_button("Export Internal Tracker (Current View)", data=df.to_csv(index=False), file_name="issues_tracker.csv")
    st.divider()

    st.subheader("Intern Blog Board")
    if os.path.exists("blog_posts.csv"):
        blog_df = pd.read_csv("blog_posts.csv")
        for i, row in blog_df.iterrows():
            st.subheader(row["Title"])
            st.write(row["Content"])
            if st.session_state.is_admin and st.button(f"Delete Blog {i+1}", key=f"delete_blog_{i}"):
                blog_df = blog_df.drop(i)
                blog_df.to_csv("blog_posts.csv", index=False)
                st.success("Blog deleted!")
                st.rerun()
            st.markdown("---")
    else:
        st.info("No blogs yet.")

    if st.session_state.is_admin:
        st.subheader("Publish Blog")
        blog_title = st.text_input("Title")
        blog_content = st.text_area("Content")
        if st.button("Post Blog"):
            entry = pd.DataFrame([[blog_title, blog_content]], columns=["Title", "Content"])
            if os.path.exists("blog_posts.csv"):
                entry.to_csv("blog_posts.csv", mode="a", header=False, index=False)
            else:
                entry.to_csv("blog_posts.csv", index=False)
            st.success("Blog posted!")
            st.rerun()

        st.subheader("Add New Intern")
        new_name = st.text_input("Intern Name", key="new_intern_name")
        new_dept = st.text_input("Department", key="new_intern_dept")
        new_linkedin = st.text_input("LinkedIn URL", key="new_intern_linkedin")
        if st.button("Add Intern", key="add_intern_button"):
            st.session_state.intern_data.append({
                "Name": new_name,
                "Department": new_dept,
                "LinkedIn": new_linkedin
            })
            st.success(f"{new_name} added to intern list.")
            st.rerun()

# -------------------------------
# NOT LOGGED IN (Main Landing Page with Tabs)
# -------------------------------
else:
    st.header("Welcome to the Reliance Intern & Policy Issue Portal")
    st.markdown("Please log in using the sidebar to access your personalized dashboard.")
    st.divider()

    tab_welcome, tab_interns_public, tab_policy_public = st.tabs([
        "Welcome", "Interns Directory", "Public Policy Data"
    ])

    with tab_welcome:
        st.markdown("""
            This portal serves as a central hub for Reliance interns and for tracking policy-related issues.
            Depending on your login credentials, you will gain access to different features.

            **Interns:** Access your weekly tasks, reading materials, connect with other interns, and submit your work.

            **Policy/Admin/Chairman/Managers:** Monitor and manage policy issues, review public submissions, and oversee intern activities.

            Please use the login section in the sidebar to get started.
        """)

    with tab_interns_public:
        st.subheader("Our Interns (Public View)")
        st.info("This section provides a public directory of our current interns. Full details are available upon login.")
        for intern in st.session_state.intern_data:
            st.markdown(f"**{intern['Name']}** - {intern['Department']}")
            st.markdown("---")

    with tab_policy_public:
        st.subheader("Public Policy Submissions Overview")
        st.info("This tab displays publicly submitted policy data from our Google Form. More detailed tracking and updates are available to authorized personnel upon login.")
        # This is the original public Google Form URL, kept separate from the internal tracker.
        csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQXnxefBfU43AgIEdCeCd5QBMgGVSifK9fSmSFuZd_jA_6B0Xem13xSjVqCY31QKsB88sjlOEa5T_gX/pub?output=csv"
        try:
            df_live = pd.read_csv(csv_url)
            st.dataframe(df_live, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not load public form data at this time. Please try again later. Error: {e}")

# -------------------------------
# FOOTER
# -------------------------------
st.divider()
st.markdown("© 2025 Reliance Jio Internship designed by Zishan Mallick | For academic use only.")
st.markdown("**Disclaimer:** This is a simulated environment for educational purposes. All data is fictional and does not represent real issues or individuals.")
st.markdown("**Note:** Please do not share any sensitive information. This is a public platform.")
