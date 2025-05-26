import streamlit as st
import pandas as pd
import os
from PIL import Image
import requests
from io import BytesIO  # Required to open image from bytes
import datetime
import json

# --- Firebase Imports (Conceptual for Canvas Environment) ---
# These global variables are provided by the Canvas environment for Firebase integration.
# In a standard Python environment, you'd use `firebase-admin` or `google-cloud-firestore`.
# DO NOT modify these lines. They are placeholders for the Canvas runtime.
__app_id = "default-app-id"
__firebase_config = "{}"
__initial_auth_token = None

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

# Firestore related state variables
if 'db' not in st.session_state:
    st.session_state.db = None
if 'auth' not in st.session_state:
    st.session_state.auth = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'issues_data' not in st.session_state:
    st.session_state.issues_data = pd.DataFrame(columns=[
        "id", "Business Vertical", "Team", "Contact", "Email/Phone",
        "Issue Title", "Description", "Issue Type", "Gov Body",
        "Priority", "Resolution", "File", "Date", "Status", "Response",
        "Updated By", "Last Updated"
    ])
if 'is_auth_ready' not in st.session_state:
    st.session_state.is_auth_ready = False


# -------------------------------
# FIREBASE INITIALIZATION AND AUTHENTICATION (Conceptual for Canvas)
# This function simulates Firebase initialization and authentication.
# In a real Canvas environment, this would involve JavaScript execution
# to interact with the Firebase JS SDK and populate the global variables.
# For local testing, these globals might need to be mocked or set manually.
# -------------------------------
def initialize_firebase():
    """
    Simulates Firebase initialization and authentication.
    In a Canvas environment, `__app_id`, `__firebase_config`, and `__initial_auth_token`
    are provided globally by the runtime.
    """
    try:
        # Access global variables provided by the Canvas environment
        # These are expected to be present at runtime in Canvas.
        app_id = __app_id
        firebase_config = json.loads(__firebase_config)

        # Only initialize if not already initialized
        if not st.session_state.db:
            # Simulate successful initialization and authentication
            # In a true Canvas integration, these would be handled by JS execution
            # and actual Firebase client SDK objects would be set.
            st.session_state.db = "firestore_instance_placeholder"
            st.session_state.auth = "auth_instance_placeholder"

            # Simulate user sign-in based on __initial_auth_token
            if __initial_auth_token:
                # In a real scenario, this would involve `signInWithCustomToken(auth, __initial_auth_token)`
                # and getting the actual user UID.
                st.session_state.user_id = "authenticated_user_id_placeholder" # Replace with actual UID from auth
            else:
                # In a real scenario, this would be `signInAnonymously(auth)`
                st.session_state.user_id = "anonymous_user_" + str(datetime.datetime.now().timestamp()).replace('.', '') # Unique ID for anonymous
            st.session_state.is_auth_ready = True # Mark authentication as ready

            st.success("Firebase initialized and authenticated (conceptual).")

    except Exception as e:
        st.error(f"Failed to initialize Firebase (conceptual): {e}")

# Initialize Firebase on app start (only if not already ready)
if not st.session_state.is_auth_ready:
    initialize_firebase()

# Display current user ID in the sidebar if authenticated
if st.session_state.user_id:
    st.sidebar.write(f"Logged in as: **{st.session_state.user_id}**")


# -------------------------------
# FIRESTORE OPERATIONS (Simulated/Conceptual for Streamlit Python)
# These functions simulate interactions with Firestore.
# In a real Canvas environment, these would be managed by JavaScript
# code interacting with the Firebase JS SDK, and data would be passed
# to/from Streamlit's session state.
# -------------------------------

def fetch_issues_from_firestore():
    """
    Simulates fetching issues from a Firestore database.
    In a real Canvas setup, this would be an `onSnapshot` listener
    updating `st.session_state.issues_data` in real-time.
    """
    if not st.session_state.is_auth_ready:
        return pd.DataFrame() # Return empty if authentication is not ready

    # Mock data for demonstration.
    # In a real Canvas scenario, this data would be populated by a JavaScript
    # `onSnapshot` listener that updates a Streamlit component or session state.
    mock_issues = [
        {"id": "issue1", "Business Vertical": "Retail", "Team": "Sales", "Contact": "John Doe", "Email/Phone": "john@example.com",
         "Issue Title": "POS System Glitch", "Description": "Customers unable to complete transactions.", "Issue Type": "Technical",
         "Gov Body": "N/A", "Priority": "High", "Resolution": "", "File": "", "Date": "2025-05-20", "Status": "New", "Response": "",
         "Updated By": "Admin", "Last Updated": "2025-05-20 10:00:00"},
        {"id": "issue2", "Business Vertical": "Jio Platforms", "Team": "HR", "Contact": "Jane Smith", "Email/Phone": "jane@example.com",
         "Issue Title": "Internship Policy Clarification", "Description": "Need clarity on leave policy for interns.", "Issue Type": "Policy",
         "Gov Body": "Internal", "Priority": "Medium", "Resolution": "Policy document sent.", "File": "policy.pdf", "Date": "2025-05-18", "Status": "Actioned", "Response": "Policy document shared.",
         "Updated By": "Policy", "Last Updated": "2025-05-22 14:30:00"},
        {"id": "issue3", "Business Vertical": "Reliance Retail", "Team": "Logistics", "Contact": "Alice Brown", "Email/Phone": "alice@example.com",
         "Issue Title": "Supply Chain Delay", "Description": "Shipment from vendor X delayed by 3 days.", "Issue Type": "Operational",
         "Gov Body": "N/A", "Priority": "High", "Resolution": "", "File": "", "Date": "2025-05-25", "Status": "New", "Response": "",
         "Updated By": "Admin", "Last Updated": "2025-05-25 09:00:00"},
        {"id": "issue4", "Business Vertical": "Jio Financial", "Team": "Compliance", "Contact": "Bob White", "Email/Phone": "bob@example.com",
         "Issue Title": "Regulatory Filing Query", "Description": "Question regarding new SEBI regulations.", "Issue Type": "Regulatory",
         "Gov Body": "SEBI", "Priority": "Urgent", "Resolution": "Consulted legal team. Response drafted.", "File": "", "Date": "2025-05-24", "Status": "In Review", "Response": "Legal team is reviewing.",
         "Updated By": "Chairman", "Last Updated": "2025-05-25 11:00:00"},
        {"id": "issue5", "Business Vertical": "Reliance Digital", "Team": "Customer Service", "Contact": "Charlie Green", "Email/Phone": "charlie@example.com",
         "Issue Title": "Customer Complaint - Product X", "Description": "Customer unhappy with product X performance.", "Issue Type": "Customer",
         "Gov Body": "N/A", "Priority": "Low", "Resolution": "Customer contacted, replacement offered.", "File": "", "Date": "2025-05-23", "Status": "Solved", "Response": "Case closed.",
         "Updated By": "Policy", "Last Updated": "2025-05-24 16:00:00"},
    ]
    return pd.DataFrame(mock_issues)

def update_issue_in_firestore(issue_id, new_status, response_text, updated_by_user_name):
    """
    Simulates updating an issue in a Firestore database.
    In a real Canvas setup, this would be a JavaScript call to Firestore's `setDoc` or `updateDoc`.
    """
    if not st.session_state.is_auth_ready:
        st.error("Authentication not ready. Cannot update issue.")
        return

    # Simulate updating the mock data in session state for immediate visual feedback.
    # In a real app, this would trigger a Firestore update, and the onSnapshot listener
    # would then update st.session_state.issues_data.
    current_issues_df = st.session_state.issues_data.copy()
    if issue_id in current_issues_df['id'].values:
        idx = current_issues_df[current_issues_df['id'] == issue_id].index[0]
        current_issues_df.at[idx, "Status"] = new_status
        current_issues_df.at[idx, "Response"] = response_text
        current_issues_df.at[idx, "Updated By"] = updated_by_user_name
        current_issues_df.at[idx, "Last Updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.issues_data = current_issues_df # Update session state
        st.success("Issue updated (simulated Firestore update).")
    else:
        st.warning("Issue not found in current data.")


# -------------------------------
# LOAD LOGO FROM GITHUB URL
# This section loads the Reliance logo from a raw GitHub URL.
# Ensure the URL points to the raw image file (e.g., starts with raw.githubusercontent.com).
# -------------------------------
logo_url = "https://raw.githubusercontent.com/Zishanmallick/Zishan/main/L.1.jpg"

try:
    response = requests.get(logo_url)
    response.raise_for_status()  # Raise an exception for bad status codes (e.g., 404)
    reliance_logo = Image.open(BytesIO(response.content))

    col1, col2 = st.columns([1, 4]) # Use columns for better layout of logo and title
    with col1:
        st.image(reliance_logo, width=150) # Adjust width as needed
    with col2:
        st.title("Reliance Intern & Policy Issue Portal")
except Exception as e:
    st.error(f"Error: Failed to load logo from {logo_url}. Please ensure the URL is correct and points to the raw image file. Error: {e}")
    st.title("Reliance Intern & Policy Issue Portal")


# -------------------------------
# LOGIN SIDEBAR
# This section handles user login authentication.
# -------------------------------
st.sidebar.title("Login")
# Add new manager roles to the selectbox options, including Jio Legal Services
all_names = ["Admin", "Chairman", "Policy", "Jio Retail Manager", "Jio Platforms Manager", "Jio Financial Manager", "Jio Legal Services"] + [intern["Name"] for intern in st.session_state.intern_data]
selected_user = st.sidebar.selectbox("Select Your Name", all_names)
entered_password = st.sidebar.text_input("Enter Access Code", type="password")

if st.sidebar.button("Login"):
    # Authentication logic
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
    # New Manager Login Logic
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
    # New Jio Legal Services Login Logic
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
    st.experimental_rerun() # Rerun to update UI after login

# -------------------------------
# MAIN APPLICATION CONTENT
# This section conditionally renders content based on login status.
# -------------------------------

# Intern Dashboard (Logged in as an Intern)
if st.session_state.logged_in and st.session_state.user_name not in ["Admin", "Chairman", "Policy", "Jio Retail Manager", "Jio Platforms Manager", "Jio Financial Manager", "Jio Legal Services"]:
    st.header("Your Dashboard – Weekly Tasks & Submissions")
    st.markdown(f"Welcome, **{st.session_state.user_name}**! Here are your tasks and ways to connect.")
    st.divider()

    # Define Tabs for Intern Dashboard to reduce vertical scrolling
    tab_tasks, tab_blogs, tab_profiles = st.tabs([
        "Tasks", "Blog Board", "Interns"
    ])

    with tab_tasks: # Weekly Tasks & Announcements Tab
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
            st.experimental_rerun()
        for msg in st.session_state.chat[-10:]:
            st.write(msg)


    with tab_blogs: # Intern Blog Board Tab
        st.subheader("Intern Blog Board")
        if os.path.exists("blog_posts.csv"):
            blog_df = pd.read_csv("blog_posts.csv")
            for _, row in blog_df.iterrows():
                st.subheader(row["Title"])
                st.write(row["Content"])
                st.markdown("---")
        else:
            st.info("No blogs yet.")

    with tab_profiles: # Intern Profiles Tab
        st.subheader("Intern Profiles")
        for intern in st.session_state.intern_data:
            st.subheader(intern["Name"])
            st.write(f"**Department:** {intern['Department']}")
            st.markdown(f"[LinkedIn]({intern['LinkedIn']})", unsafe_allow_html=True)
            st.markdown("---")


# -------------------------------
# POLICY + ADMIN/CHAIRMAN + MANAGERS DASHBOARD
# This section is for authorized personnel to track policy issues.
# -------------------------------
elif st.session_state.logged_in and st.session_state.user_name in ["Policy", "Admin", "Chairman", "Jio Retail Manager", "Jio Platforms Manager", "Jio Financial Manager", "Jio Legal Services"]:
    st.header("Policy Issues Tracker")
    st.markdown(f"Welcome, **{st.session_state.user_name}**!")


    # Display Public Submissions from Google Form (external CSV URL)
    csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQXnxefBfU43AgIEdCeCd5QBMgGVSifK9fSmSFuZd_jA_6B0Xem13xSjVqCY31QKsB88sjlOEa5T_gX/pub?output=csv"
    try:
        df_live = pd.read_csv(csv_url)
        st.success("Google Form data loaded successfully!")
        st.subheader("Public Submissions (from Google Form)")
        st.dataframe(df_live, use_container_width=True)
    except Exception as e:
        st.error(f"Google Form data failed to load: {e}")

    # Internal Tracker & Review (Live via Firestore Concept)
    st.subheader("Internal Tracker & Review (Live via Firestore Concept)")

    # Fetch issues from conceptual Firestore (or update from onSnapshot in real Canvas)
    if st.session_state.is_auth_ready:
        st.session_state.issues_data = fetch_issues_from_firestore()
    else:
        st.info("Waiting for Firebase authentication to be ready to load issues...")

    # Apply filtering based on user role
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
    # Admin, Chairman, Policy see all issues (no filter applied here)

    if not df.empty:
        # Filters for issues
        col1, col2 = st.columns(2)
        with col1:
            selected_priority = st.selectbox("Filter by Priority", ["All"] + df["Priority"].dropna().unique().tolist())
        with col2:
            selected_status = st.selectbox("Filter by Status", ["All", "New", "In Review", "Actioned", "Needs Clarification", "Solved"])

        # Apply filters
        filtered = df.copy()
        if selected_priority != "All":
            filtered = filtered[filtered["Priority"] == selected_priority]
        if selected_status != "All":
            filtered = filtered[filtered["Status"] == selected_status]

        st.dataframe(filtered, use_container_width=True)

        st.subheader("Update Issue Status")
        issue_selection_options = filtered['Issue Title'].tolist() # Only show filterable issues in selectbox
        selected_issue_title = st.selectbox("Select Issue to Update", issue_selection_options)

        if selected_issue_title:
            # Find the ID and current details of the selected issue from the *original* (unfiltered) df
            # to ensure we get the correct issue ID regardless of current filters.
            original_df = st.session_state.issues_data.copy()
            selected_issue_id = original_df[original_df['Issue Title'] == selected_issue_title]['id'].iloc[0]
            current_issue_status = original_df[original_df['id'] == selected_issue_id]['Status'].iloc[0]
            current_issue_response = original_df[original_df['id'] == selected_issue_id]['Response'].iloc[0]

            new_status = st.selectbox("Update Status", ["New", "In Review", "Actioned", "Needs Clarification", "Solved"],
                                      index=["New", "In Review", "Actioned", "Needs Clarification", "Solved"].index(current_issue_status))
            response_text = st.text_area("Add Response", value=current_issue_response)

            if st.button("Update Issue"):
                update_issue_in_firestore(selected_issue_id, new_status, response_text, st.session_state.user_name)
                st.session_state.issues_data = fetch_issues_from_firestore() # Re-fetch to refresh display
                st.experimental_rerun()
    else:
        st.info("No issues found for your department/role in the tracker.")

    # Export button for current view of issues
    st.download_button("Export Internal Tracker (Current View)", data=df.to_csv(index=False), file_name="issues_tracker.csv")
    st.divider()

    # Blog Board (Admin Only - Add/Delete Functionality)
    st.subheader("Intern Blog Board")
    if os.path.exists("blog_posts.csv"):
        blog_df = pd.read_csv("blog_posts.csv")
        for i, row in blog_df.iterrows():
            st.subheader(row["Title"])
            st.write(row["Content"])
            # Admin can delete blogs
            if st.session_state.is_admin and st.button(f"Delete Blog {i+1}", key=f"delete_blog_{i}"):
                blog_df = blog_df.drop(i)
                blog_df.to_csv("blog_posts.csv", index=False)
                st.success("Blog deleted!")
                st.experimental_rerun() # Rerun to update blog list
            st.markdown("---")
    else:
        st.info("No blogs yet.")

    # Admin specific functionalities
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
            st.experimental_rerun()

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
            st.experimental_rerun()

# -------------------------------
# NOT LOGGED IN (Main Landing Page with Tabs)
# This section is displayed when no user is logged in, offering public views.
# -------------------------------
else:
    st.header("Welcome to the Reliance Intern & Policy Issue Portal")
    st.markdown("Please log in using the sidebar to access your personalized dashboard.")
    st.divider()

    # Define Tabs for the Main Landing Page (when not logged in)
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
        # Display intern names and departments publicly
        for intern in st.session_state.intern_data:
            st.markdown(f"**{intern['Name']}** - {intern['Department']}")
            st.markdown("---") # Simple visual separator

    with tab_policy_public:
        st.subheader("Public Policy Submissions Overview")
        st.info("This tab displays publicly submitted policy data from our Google Form. More detailed tracking and updates are available to authorized personnel upon login.")
        # Load and display public Google Form data
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
