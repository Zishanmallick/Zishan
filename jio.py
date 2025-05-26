import streamlit as st
import pandas as pd
import os
from PIL import Image
import requests
from io import BytesIO
import datetime
import json
import uuid

# --- Configuration for Google Sheet ---
ISSUES_GOOGLE_SHEET_URL = "https://docs.google.com/sheets/d/e/2PACX-1vQ7KUWovEfXSgd7OO61zgdsWcNP1i_LaOlXCe_t7PiJVXhTS_mfyQcrpiNYWCQBs7PgFzhX_QASeVPG/pub?output=csv"
PUBLIC_SUBMISSIONS_GOOGLE_FORM_URL = "https://docs.google.com/sheets/d/e/2PACX-1vQXnxefBfU43AgIEdCeCd5QBMgGVSifK9fSmSFuZd_jA_6B0Xem13xSjVqCY31QKsB88sjlOEa5T_gX/pub?output=csv"


# --- File Paths ---
BLOG_POSTS_FILE = "blog_posts.csv"
ANNOUNCEMENTS_FILE = "announcements.json" # To persist admin announcements
WEEKLY_TASKS_FILE = "weekly_tasks.json" # To persist admin weekly tasks
UPLOAD_DIR = "uploads"

# Ensure directories exist
os.makedirs("materials", exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -------------------------------
# PAGE CONFIGURATION
# -------------------------------
st.set_page_config(page_title="Reliance Intern + Policy Issue Tracker", layout="wide")

# -------------------------------
# SESSION SETUP
# -------------------------------
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

if 'issues_data' not in st.session_state:
    st.session_state.issues_data = pd.DataFrame(columns=[
        "id", "Business Vertical", "Team", "Contact", "Email/Phone",
        "Issue Title", "Description", "Issue Type", "Gov Body",
        "Priority", "Resolution", "File", "Date", "Status", "Response",
        "Updated By", "Last Updated"
    ])

# Initialize blog posts DataFrame
if BLOG_POSTS_FILE not in st.session_state:
    if os.path.exists(BLOG_POSTS_FILE):
        st.session_state.blog_posts = pd.read_csv(BLOG_POSTS_FILE)
    else:
        st.session_state.blog_posts = pd.DataFrame(columns=["Title", "Content", "Author", "Date"])

# Initialize announcements
if "announcements" not in st.session_state:
    if os.path.exists(ANNOUNCEMENTS_FILE):
        with open(ANNOUNCEMENTS_FILE, 'r') as f:
            st.session_state.announcements = json.load(f)
    else:
        st.session_state.announcements = [
            "Intern Townhall on **May 25 at 4:00 PM**.",
            "Task 2 deadline: **May 24, 11:59 PM**.",
            "Intern of the Week: **Zishan Mallick!**"
        ]

# Initialize weekly tasks
if "weekly_tasks" not in st.session_state:
    if os.path.exists(WEEKLY_TASKS_FILE):
        with open(WEEKLY_TASKS_FILE, 'r') as f:
            st.session_state.weekly_tasks = json.load(f)
    else:
        st.session_state.weekly_tasks = {
            "Week 1": "Intro to Jio Platforms + Submit project preference form",
            "Week 2": "Research Jio's AI Strategy and write 500-word report",
            "Week 3": "Group presentation on Jio Digital Transformation"
        }

# -------------------------------
# SPREADSHEET (GOOGLE SHEET) OPERATIONS
# -------------------------------

def load_issues_from_google_sheet():
    """
    Loads issues from the specified Google Sheet URL.
    """
    try:
        df = pd.read_csv(ISSUES_GOOGLE_SHEET_URL)
        if 'id' not in df.columns:
            df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
            st.warning("No 'id' column found in Google Sheet. Assigning temporary UUIDs for internal use.")
        return df
    except Exception as e:
        st.error(f"Error loading issues from Google Sheet: {e}. Please ensure the sheet is published to web as CSV and the URL is correct.")
        return pd.DataFrame(columns=[
            "id", "Business Vertical", "Team", "Contact", "Email/Phone",
            "Issue Title", "Description", "Issue Type", "Gov Body",
            "Priority", "Resolution", "File", "Date", "Status", "Response",
            "Updated By", "Last Updated"
        ])

def save_issues_to_google_sheet_simulated(df):
    """
    Simulates saving the current issues DataFrame.
    """
    st.warning("Saving changes to the Google Sheet is not directly supported in this demo. Changes are only reflected in this session.")
    st.info("To persist changes, you would need to implement Google Sheets API integration with proper authentication.")
    return True

def save_blog_posts():
    st.session_state.blog_posts.to_csv(BLOG_POSTS_FILE, index=False)

def save_announcements():
    with open(ANNOUNCEMENTS_FILE, 'w') as f:
        json.dump(st.session_state.announcements, f)

def save_weekly_tasks():
    with open(WEEKLY_TASKS_FILE, 'w') as f:
        json.dump(st.session_state.weekly_tasks, f)

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
    st.error(f"Error: Failed to load logo from {logo_url}. Please ensure the URL is correct and points to the raw image file. Error: {e}")
    st.title("Reliance Intern & Policy Issue Portal")


# -------------------------------
# LOGIN SIDEBAR
# -------------------------------
st.sidebar.title("Login")
all_names = ["Admin", "Chairman", "Policy", "Jio Retail Manager", "Jio Platforms Manager", "Jio Financial Manager", "Jio Legal Services"] + [intern["Name"] for intern in st.session_state.intern_data]
selected_user = st.sidebar.selectbox("Select Your Name", all_names)
entered_password = st.sidebar.text_input("Enter Access Code", type="password")

if st.sidebar.button("Login"):
    if selected_user == "Admin" and entered_password == "admin@jio":
        st.session_state.logged_in = True
        st.session_state.user_name = "Admin"
        st.session_state.is_admin = True
        st.success("Welcome, Admin!")
    elif selected_user == "Chairman" and entered_password == "chairman@jio":
        st.session_state.logged_in = True
        st.session_state.user_name = "Chairman"
        st.session_state.is_admin = False # Chairman is not an admin, but has broad view
        st.success("Welcome, Chairman Office!")
    elif selected_user == "Policy" and entered_password == "policy@jio":
        st.session_state.logged_in = True
        st.session_state.user_name = "Policy"
        st.session_state.is_admin = False
        st.success("Welcome to the Policy Dashboard!")
    elif selected_user == "Jio Retail Manager" and entered_password == "retail@jio":
        st.session_state.logged_in = True
        st.session_state.user_name = "Jio Retail Manager"
        st.session_state.is_admin = False
        st.success("Welcome, Jio Retail Manager!")
    elif selected_user == "Jio Platforms Manager" and entered_password == "platforms@jio":
        st.session_state.logged_in = True
        st.session_state.user_name = "Jio Platforms Manager"
        st.session_state.is_admin = False
        st.success("Welcome, Jio Platforms Manager!")
    elif selected_user == "Jio Financial Manager" and entered_password == "financial@jio":
        st.session_state.logged_in = True
        st.session_state.user_name = "Jio Financial Manager"
        st.session_state.is_admin = False
        st.success("Welcome, Jio Financial Manager!")
    elif selected_user == "Jio Legal Services" and entered_password == "legal@jio":
        st.session_state.logged_in = True
        st.session_state.user_name = "Jio Legal Services"
        st.session_state.is_admin = False
        st.success("Welcome, Jio Legal Services!")
    elif selected_user not in ["Admin", "Chairman", "Policy", "Jio Retail Manager", "Jio Platforms Manager", "Jio Financial Manager", "Jio Legal Services"] and entered_password == "jio2025":
        st.session_state.logged_in = True
        st.session_state.user_name = selected_user
        st.session_state.is_admin = False # Interns are not admins
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
        st.experimental_rerun()


# -------------------------------
# SHARED INTERN FUNCTIONS (for both Interns and Admin/Chairman viewing)
# -------------------------------
def display_intern_blog_board():
    st.subheader("Intern Blog Board")
    if not st.session_state.blog_posts.empty:
        # Sort by date for better display
        st.session_state.blog_posts['Date'] = pd.to_datetime(st.session_state.blog_posts['Date'], errors='coerce')
        blog_df_sorted = st.session_state.blog_posts.sort_values(by="Date", ascending=False).fillna('') # Fill NaN dates for sorting
        for _, row in blog_df_sorted.iterrows():
            st.markdown(f"### {row['Title']}")
            st.write(f"**Author:** {row['Author']} | **Date:** {row['Date'].strftime('%Y-%m-%d') if pd.notnull(row['Date']) else 'N/A'}")
            st.write(row["Content"])
            st.markdown("---")
    else:
        st.info("No blogs yet.")

def display_intern_profiles():
    st.subheader("Intern Profiles")
    for intern in st.session_state.intern_data:
        st.subheader(intern["Name"])
        st.write(f"**Department:** {intern['Department']}")
        st.markdown(f"[LinkedIn]({intern['LinkedIn']})", unsafe_allow_html=True)
        st.markdown("---")

def display_intern_announcements():
    st.subheader("Announcements")
    if st.session_state.announcements:
        for note in st.session_state.announcements:
            st.info(note)
    else:
        st.info("No announcements yet.")

def display_weekly_tasks():
    st.subheader("Weekly Tasks")
    if st.session_state.weekly_tasks:
        for week, desc in st.session_state.weekly_tasks.items():
            st.write(f"**{week}:** {desc}")
    else:
        st.info("No weekly tasks defined yet.")

def display_reading_materials():
    st.subheader("Reading Materials")
    pdfs = {
        "Week 1 – Jio Overview": "materials/JioBrain.pdf",
        "Week 2 – AI Strategy": "materials/Digital Transformation PPT for DFS Meeting_Sept2024.pdf",
        "Week 3 – Digital Transformation": "materials/RIL_4Q_FY25_Analyst_Presentation_25Apr25.pdf"
    }
    for title, path in pdfs.items():
        st.subheader(title)
        try:
            # Check if the file actually exists for download
            if os.path.exists(path):
                with open(path, "rb") as f:
                    st.download_button("Download", f, file_name=os.path.basename(path), key=f"download_{title}")
            else:
                st.warning(f"File not found: {os.path.basename(path)}")
        except Exception as e:
            st.error(f"Error accessing file {os.path.basename(path)}: {e}")

# -------------------------------
# MAIN APPLICATION CONTENT
# -------------------------------

if st.session_state.logged_in:
    # Intern Dashboard (for actual interns)
    if st.session_state.user_name not in ["Admin", "Chairman", "Policy", "Jio Retail Manager", "Jio Platforms Manager", "Jio Financial Manager", "Jio Legal Services"]:
        st.header("Your Dashboard – Weekly Tasks & Submissions")
        st.markdown(f"Welcome, **{st.session_state.user_name}**! Here are your tasks and ways to connect.")
        st.divider()

        tab_tasks, tab_blogs, tab_profiles = st.tabs([
            "Tasks", "Blog Board", "Interns"
        ])

        with tab_tasks:
            display_intern_announcements()
            st.divider()
            display_weekly_tasks()
            display_reading_materials()

            st.divider()
            st.subheader("Submit Task")
            with st.form("upload_form"):
                week_options = list(st.session_state.weekly_tasks.keys())
                if week_options:
                    week = st.selectbox("Select Week", week_options)
                else:
                    st.warning("No weekly tasks defined by admin yet.")
                    week = "N/A" # Default if no tasks
                file = st.file_uploader("Upload PDF/DOC", type=["pdf", "docx"])
                submitted = st.form_submit_button("Submit")
                if submitted and file:
                    if week != "N/A":
                        path = os.path.join(UPLOAD_DIR, f"{st.session_state.user_name.replace(' ', '_')}_{week}_{file.name}")
                        with open(path, "wb") as f:
                            f.write(file.read())
                        st.success("Uploaded and saved successfully!")
                    else:
                        st.error("Cannot submit task as no weeks are defined.")
                elif submitted and not file:
                    st.error("Please upload a file.")

            st.divider()
            st.subheader("Intern Chat")
            chat_msg = st.text_input("Message:", key="intern_chat_input")
            if st.button("Send", key="intern_send_button") and chat_msg:
                st.session_state.chat.append(f"[{datetime.datetime.now().strftime('%H:%M')}] {st.session_state.user_name}: {chat_msg}")
                # Clear the input after sending
                st.session_state.chat_input = ""
                st.experimental_rerun() # To clear the input field
            for msg in st.session_state.chat[-10:]:
                st.write(msg)

        with tab_blogs:
            st.subheader("Create a New Blog Post")
            with st.form("new_blog_post_form"):
                blog_title = st.text_input("Blog Title")
                blog_content = st.text_area("Your Blog Content")
                blog_submitted = st.form_submit_button("Publish Blog")
                if blog_submitted:
                    if blog_title and blog_content:
                        new_blog = {
                            "Title": blog_title,
                            "Content": blog_content,
                            "Author": st.session_state.user_name,
                            "Date": datetime.datetime.now().strftime("%Y-%m-%d")
                        }
                        st.session_state.blog_posts = pd.concat([st.session_state.blog_posts, pd.DataFrame([new_blog])], ignore_index=True)
                        save_blog_posts()
                        st.success("Blog post published successfully!")
                        st.experimental_rerun()
                    else:
                        st.error("Please provide both title and content for the blog.")
            st.divider()
            display_intern_blog_board() # Show existing blogs

        with tab_profiles:
            display_intern_profiles()


    # Admin/Chairman/Manager Dashboard
    else:
        role_tabs = ["Policy Issues Tracker"]
        if st.session_state.user_name in ["Admin", "Chairman"]:
            role_tabs.append("Intern Management")

        current_tab = st.tabs(role_tabs)

        with current_tab[0]: # Policy Issues Tracker is always the first tab
            st.header("Policy Issues Tracker")
            st.markdown(f"Welcome, **{st.session_state.user_name}**!")

            st.subheader("Public Submissions (from Google Form)")
            try:
                df_live = pd.read_csv(PUBLIC_SUBMISSIONS_GOOGLE_FORM_URL)
                st.dataframe(df_live, use_container_width=True)
            except Exception as e:
                st.error(f"Google Form data failed to load: {e}")

            st.subheader("Internal Tracker & Review (Live via Google Sheet)")
            st.session_state.issues_data = load_issues_from_google_sheet()
            df = st.session_state.issues_data

            if not df.empty:
                st.dataframe(df, use_container_width=True)

                st.subheader("Update an Issue")
                with st.form("update_issue_form"):
                    issue_id_to_update = st.selectbox("Select Issue ID to Update", df['id'].unique(), key="issue_id_select")
                    issue_to_update = df[df['id'] == issue_id_to_update].iloc[0]

                    new_status = st.selectbox("New Status", ["Open", "In Progress", "Resolved", "Closed"], index=["Open", "In Progress", "Resolved", "Closed"].index(issue_to_update['Status']) if 'Status' in issue_to_update and issue_to_update['Status'] in ["Open", "In Progress", "Resolved", "Closed"] else 0, key="new_status_select")
                    response = st.text_area("Response/Notes", value=issue_to_update['Response'] if 'Response' in issue_to_update else "", key="response_text_area")

                    update_submitted = st.form_submit_button("Update Issue", key="update_issue_button")
                    if update_submitted:
                        idx = df[df['id'] == issue_id_to_update].index[0]
                        st.session_state.issues_data.loc[idx, 'Status'] = new_status
                        st.session_state.issues_data.loc[idx, 'Response'] = response
                        st.session_state.issues_data.loc[idx, 'Updated By'] = st.session_state.user_name
                        st.session_state.issues_data.loc[idx, 'Last Updated'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        if save_issues_to_google_sheet_simulated(st.session_state.issues_data):
                            st.success(f"Issue {issue_id_to_update} updated successfully!")
                            st.experimental_rerun()
                        else:
                            st.error("Failed to update issue (simulated save failed).")
            else:
                st.info("No internal issues to display yet.")

        # Admin/Chairman specific "Intern Management" tab
        if st.session_state.user_name in ["Admin", "Chairman"]:
            with current_tab[1]: # Intern Management is the second tab
                st.header("Intern Management Dashboard")
                st.markdown(f"Welcome, **{st.session_state.user_name}**! Manage intern activities here.")

                intern_management_tabs = st.tabs(["Announcements", "Weekly Tasks", "Blog Review", "Submitted Tasks", "Intern Profiles", "Intern Chat Log"])

                with intern_management_tabs[0]: # Announcements
                    st.subheader("Manage Announcements")
                    display_intern_announcements() # Show current announcements
                    st.divider()
                    with st.form("add_announcement_form"):
                        new_announcement = st.text_area("Add New Announcement")
                        add_announcement_btn = st.form_submit_button("Add Announcement")
                        if add_announcement_btn and new_announcement:
                            st.session_state.announcements.insert(0, new_announcement) # Add to top
                            save_announcements()
                            st.success("Announcement added!")
                            st.experimental_rerun()
                    
                    st.subheader("Remove Announcements")
                    if st.session_state.announcements:
                        announcement_to_remove = st.selectbox("Select announcement to remove", st.session_state.announcements, key="remove_announcement_select")
                        if st.button("Remove Selected Announcement", key="remove_announcement_button"):
                            st.session_state.announcements.remove(announcement_to_remove)
                            save_announcements()
                            st.success("Announcement removed!")
                            st.experimental_rerun()
                    else:
                        st.info("No announcements to remove.")

                with intern_management_tabs[1]: # Weekly Tasks
                    st.subheader("Manage Weekly Tasks")
                    display_weekly_tasks() # Show current tasks
                    st.divider()
                    with st.form("add_weekly_task_form"):
                        new_week = st.text_input("Week (e.g., 'Week 4')", key="new_week_input")
                        new_task_desc = st.text_area("Task Description", key="new_task_desc_input")
                        add_task_btn = st.form_submit_button("Add Weekly Task")
                        if add_task_btn and new_week and new_task_desc:
                            st.session_state.weekly_tasks[new_week] = new_task_desc
                            save_weekly_tasks()
                            st.success(f"Task for {new_week} added!")
                            st.experimental_rerun()

                    st.subheader("Update or Remove Weekly Tasks")
                    if st.session_state.weekly_tasks:
                        task_week_to_manage = st.selectbox("Select Week to Update/Remove", list(st.session_state.weekly_tasks.keys()), key="manage_task_week_select")
                        current_desc = st.session_state.weekly_tasks.get(task_week_to_manage, "")
                        
                        updated_task_desc = st.text_area("Update Task Description", value=current_desc, key="update_task_desc_input")
                        
                        col_update, col_remove = st.columns(2)
                        with col_update:
                            if st.button("Update Task", key="update_task_button"):
                                st.session_state.weekly_tasks[task_week_to_manage] = updated_task_desc
                                save_weekly_tasks()
                                st.success(f"Task for {task_week_to_manage} updated!")
                                st.experimental_rerun()
                        with col_remove:
                            if st.button("Remove Task", key="remove_task_button"):
                                del st.session_state.weekly_tasks[task_week_to_manage]
                                save_weekly_tasks()
                                st.success(f"Task for {task_week_to_manage} removed!")
                                st.experimental_rerun()
                    else:
                        st.info("No weekly tasks to manage.")


                with intern_management_tabs[2]: # Blog Review
                    st.subheader("Intern Blog Posts")
                    display_intern_blog_board() # Show all blogs

                    # You could add approval/rejection logic here if needed
                    # For now, it's just a view.
                    # Example:
                    # if not st.session_state.blog_posts.empty:
                    #     blog_to_review = st.selectbox("Select blog to review", st.session_state.blog_posts['Title'].tolist())
                    #     if st.button("Approve Blog"):
                    #         # Logic to mark as approved or move to a public section
                    #         st.success(f"Blog '{blog_to_review}' approved (simulated).")

                with intern_management_tabs[3]: # Submitted Tasks
                    st.subheader("View Submitted Intern Tasks")
                    
                    if os.path.exists(UPLOAD_DIR) and os.listdir(UPLOAD_DIR):
                        all_submitted_files = os.listdir(UPLOAD_DIR)
                        
                        # Filter by intern for easier viewing
                        intern_names_with_uploads = sorted(list(set([f.split('_')[0] for f in all_submitted_files])))
                        selected_intern_for_tasks = st.selectbox("Filter by Intern", ["All Interns"] + intern_names_with_uploads, key="filter_tasks_by_intern")

                        st.markdown("---")
                        if selected_intern_for_tasks == "All Interns":
                            files_to_display = all_submitted_files
                        else:
                            files_to_display = [f for f in all_submitted_files if f.startswith(selected_intern_for_tasks)]

                        if files_to_display:
                            st.write("Click to download submitted files:")
                            for uploaded_file in files_to_display:
                                file_path = os.path.join(UPLOAD_DIR, uploaded_file)
                                try:
                                    with open(file_path, "rb") as f:
                                        st.download_button(
                                            label=f"Download {uploaded_file}",
                                            data=f,
                                            file_name=uploaded_file,
                                            key=f"download_{uploaded_file}"
                                        )
                                except Exception as e:
                                    st.error(f"Could not read {uploaded_file}: {e}")
                        else:
                            st.info("No tasks submitted yet for the selected intern, or no tasks at all.")
                    else:
                        st.info("No intern tasks have been submitted yet.")

                with intern_management_tabs[4]: # Intern Profiles
                    display_intern_profiles()

                with intern_management_tabs[5]: # Intern Chat Log
                    st.subheader("Intern Chat Log (Read-Only)")
                    if st.session_state.chat:
                        for msg in st.session_state.chat:
                            st.write(msg)
                    else:
                        st.info("No chat messages yet.")

# -------------------------------
# NOT LOGGED IN
# -------------------------------
else:
    st.info("Please log in using the sidebar to access the portal.")
