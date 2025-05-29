import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
 
# --- Streamlit Page Configuration (MUST BE FIRST STREAMLIT COMMANDS) ---
# This ensures set_page_config is called only once at the very beginning of the script execution.
st.set_page_config(page_title="Reliance Intern & Policy Issue Portal", layout="wide")
st.title("🚀 Reliance Intern & Policy Issue Portal")
 
# Add the logo here, just below the title
# The width is set to 200px for a reasonable size, adjust as needed.
st.image("https://raw.githubusercontent.com/Zishanmallick/Zishan/main/L.1.jpg", width=200)
 
# --- Configuration ---
# Centralized configuration for Google Sheet IDs and names.
SHEET_CONFIG = {
    "tracker": {"id": "1tq_g6q7tnS2OQjhehSu4lieR3wTOJ-_s0RfItq0XzWI", "name": "Sheet1"},
    "response": {"id": "1pdfnjg9gzRSpecLyw6kXzVmuPCj1ozq_DJGstQHEzdY", "name": "Form Responses 1"},
    "log": {"id": "1K7myr-bi4ry3z_tQyGg25nRJrn9QrGupeP3Tem1z4kQ", "name": "Sheet1"},
    "blog": {"id": "1uyURjMiA8C1A7Yb5ZVAtUurb7ChCIKwKN7XeJhDP0Cg", "name": "Sheet1"},
}
GOOGLE_CREDS_FILE = "reliance-jio-461118-34d43c8520bf.json"
ADMIN_PASSWORD = "admin@jio"
USER_PASSWORD = "jio2025" # General user password
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
 
# --- Column Names Mappings (for robust access) ---
# These dictionaries map a consistent internal key to the actual column name in the Google Sheet.
# .strip() is applied when reading from sheets to handle potential leading/trailing spaces,
# so the keys here should match the stripped column names.
TRACKER_COLUMNS = {
    "id": "id",
    "business_vertical": "Business Vertical",
    "team": "Team",
    "contact": "Contact",
    "email_phone": "Email/Phone",
    "issue_title": "Issue Title",
    "description": "Description",
    "issue_type": "Issue Type",
    "gov_body": "Gov Body",
    "priority": "Priority",
    "resolution": "Resolution",
    "file": "File",
    "date": "Date",
    "status": "Status",
    "response": "Response",
    "updated_by": "Updated By",
    "last_updated": "Last Updated"
}
 
RESPONSE_COLUMNS = {
    "timestamp": "Timestamp",
    "business_vertical": "Business Vertical",
    "department_name": "Department Name",
    "contact_person": "Contact Person Name & Designation",
    "email_phone": "Email ID / Phone Number",
    "issue_title": "Title of Issue",
    "description": "Detailed Description of the Issue",
    "issue_type": "Type of Issues",
    "gov_body": "Relevant Government Body",
    "priority_level": "Priority Level",
    "impact_unresolved": "Impact if Unresolved",
    "proposed_resolution": "Proposed Resolution",
    "file": "Attach Supporting Documents",
    "date_submission": "Date of Submission"
}
 
BLOG_COLUMNS = {
    "author": "author",
    "title": "title",
    "content": "content",
    "timestamp": "time" # Assuming 'time' is the actual column name in the sheet
}
 
LOG_COLUMNS = {
    "issue_id": "Issue ID",
    "field": "Field",
    "old_value": "Old Value",
    "new_value": "New Value",
    "updated_by": "Updated By",
    "timestamp": "Timestamp"
}
 
 
# --- Google Sheets Setup ---
# Initialize the Google Sheets client once and cache it for efficiency.
@st.cache_resource
def init_sheets_client():
    """Initializes the Google Sheets client and caches it."""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDS_FILE, scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Failed to initialize Google Sheets client. Please ensure '{GOOGLE_CREDS_FILE}' is correct and has necessary permissions: {e}")
        st.stop() # Stop the app if client cannot be initialized, as it's a critical dependency
 
client = init_sheets_client()
 
 
def get_worksheet(client, sheet_id, worksheet_name):
    """Retrieves a Google Sheet worksheet."""
    try:
        sheet = client.open_by_key(sheet_id)
        return sheet.worksheet(worksheet_name)
    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"Spreadsheet with ID '{sheet_id}' not found. Please verify the ID in SHEET_CONFIG.")
        return None
    except gspread.exceptions.WorksheetNotFound:
        st.error(f"Worksheet '{worksheet_name}' not found in spreadsheet '{sheet_id}'. Please verify the worksheet name in SHEET_CONFIG.")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred while accessing worksheet: {e}")
        return None
 
 
def get_dataframe_from_sheet(worksheet):
    """Retrieves all records from a worksheet as a Pandas DataFrame, cleaning column names."""
    try:
        data = worksheet.get_all_records()
        if not data: # Handle empty sheet case gracefully
            return pd.DataFrame()
        df = pd.DataFrame(data)
        # Strip whitespace from column names to ensure robust matching
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error reading data from worksheet '{worksheet.title}': {e}")
        return pd.DataFrame()  # Return empty DataFrame to avoid further errors
 
 
def append_row_to_sheet(worksheet, row_data):
    """Appends a row to a Google Sheet worksheet."""
    try:
        worksheet.append_row(row_data)
        return True
    except Exception as e:
        st.error(f"Error appending row to worksheet '{worksheet.title}': {e}")
        return False
 
 
def update_worksheet_row(worksheet, row_index, row_data):
    """Updates a specific row in a Google Sheet worksheet.
    row_index is 1-based (Google Sheets API). row_data is a list of values for the row.
    """
    try:
        # Determine the A1 notation range for the row to update
        # len(row_data) gives the number of columns to update
        range_to_update = f'A{row_index}:{gspread.utils.rowcol_to_a1(row_index, len(row_data))}'
        worksheet.update(range_to_update, [row_data])
        return True
    except Exception as e:
        st.error(f"Error updating row {row_index} in worksheet '{worksheet.title}': {e}")
        return False
 
def update_entire_worksheet(worksheet, df):
    """Updates the entire worksheet with the given DataFrame, including headers."""
    try:
        # Convert DataFrame to a list of lists, including the header
        data_to_write = [df.columns.tolist()] + df.values.tolist()
        worksheet.update(data_to_write)
        return True
    except Exception as e:
        st.error(f"Error updating entire worksheet '{worksheet.title}': {e}")
        return False
 
# --- Streamlit UI Functions ---
def display_tasks():
    """Displays the weekly tasks and submission form."""
    st.header("Weekly Tasks & Submissions")
    st.info("Upload and track your weekly tasks here.")
    st.success(f"🗓️ **Current Task:** {CURRENT_WEEK} - {TASKS[CURRENT_WEEK]}")
 
    for week, desc in TASKS.items():
        st.write(f"**{week}:** {desc}")
 
    st.subheader("Submit Your Work")
    with st.form("task_form"):
        selected_week = st.selectbox("Select Week", list(TASKS.keys()))
        uploaded_file = st.file_uploader("Upload File", type=["pdf", "docx"])
        submitted = st.form_submit_button("Submit")
        if submitted and uploaded_file:
            st.success(f"✅ File uploaded for {selected_week}")
        elif submitted and not uploaded_file:
            st.warning("Please upload a file to submit.")
 
 
def display_blog_board():
    """Displays the blog board with viewing, posting, and editing functionality."""
    st.header("Blog Board")
    st.info("View and share updates and insights. Only Admins & Chairman can post and edit.")
 
    blog_ws = get_worksheet(client, SHEET_CONFIG["blog"]["id"], SHEET_CONFIG["blog"]["name"])
    if blog_ws is None: # If worksheet could not be retrieved, stop here.
        return
 
    blogs_df = get_dataframe_from_sheet(blog_ws)
 
    # Initialize session state for editing if not present
    if 'edit_blog_idx' not in st.session_state:
        st.session_state.edit_blog_idx = None
    if 'edit_blog_title' not in st.session_state:
        st.session_state.edit_blog_title = ""
    if 'edit_blog_content' not in st.session_state:
        st.session_state.edit_blog_content = ""
 
    if not blogs_df.empty:
        # Check if all expected blog columns exist in the DataFrame
        expected_cols = [BLOG_COLUMNS["title"], BLOG_COLUMNS["author"], BLOG_COLUMNS["timestamp"], BLOG_COLUMNS["content"]]
        if not all(col in blogs_df.columns for col in expected_cols):
            st.warning("Blog sheet columns do not match expected format. Please check sheet configuration and actual column headers.")
            return # Exit function if columns are incorrect
 
        for idx, blog in blogs_df.iterrows():
            # Check if this blog post is currently being edited
            is_editing_this_post = (st.session_state.edit_blog_idx == idx)
 
            post_time = blog.get(BLOG_COLUMNS["timestamp"], 'Unknown')
 
            st.markdown(f"### 📝 {blog[BLOG_COLUMNS['title']]}\n**By:** {blog[BLOG_COLUMNS['author']]} &nbsp;&nbsp; ⏱ {post_time}")
            st.markdown(f"> {blog[BLOG_COLUMNS['content']]}")
 
            # Edit button for Admins and Chairman
            if st.session_state.is_admin or st.session_state.user_name == "Chairman":
                col1, col2 = st.columns([1, 5])
                with col1:
                    # Disable edit button if another post is already being edited
                    if st.button("Edit Blog", key=f"edit_blog_{idx}", disabled=st.session_state.edit_blog_idx is not None):
                        st.session_state.edit_blog_idx = idx
                        st.session_state.edit_blog_title = blog[BLOG_COLUMNS['title']]
                        st.session_state.edit_blog_content = blog[BLOG_COLUMNS['content']]
                        st.rerun() # Rerun to show the edit form
            st.markdown("---")
    else:
        st.info("No blog posts available yet.")
 
    # Edit functionality form (only for Admins and Chairman, and if a post is selected for editing)
    if (st.session_state.is_admin or st.session_state.user_name == "Chairman") and st.session_state.edit_blog_idx is not None:
        st.subheader(f"Edit Blog Post (Index: {st.session_state.edit_blog_idx})")
        with st.form("edit_blog_form"):
            edited_title = st.text_input("Title", value=st.session_state.edit_blog_title, key="edited_blog_title")
            edited_content = st.text_area("Content", value=st.session_state.edit_blog_content, key="edited_blog_content")
 
            col1, col2 = st.columns(2)
            with col1:
                submit_edit = st.form_submit_button("Save Changes")
            with col2:
                cancel_edit = st.form_submit_button("Cancel Edit")
 
            if submit_edit:
                if edited_title and edited_content:
                    # Retrieve the original row to preserve other columns (like author, timestamp)
                    # Use .iloc to access by integer position if index is not unique or reset
                    # Assuming blogs_df is still valid from the initial fetch
                    if blogs_df.empty:
                        st.error("Cannot save changes: Original blog data not found.")
                        st.session_state.edit_blog_idx = None
                        st.rerun()
                        return
 
                    original_blog_row = blogs_df.iloc[st.session_state.edit_blog_idx]
 
                    # Construct the updated row data in the exact order of your Google Sheet columns
                    # Based on BLOG_COLUMNS mapping: author, title, content, time
                    updated_blog_values = [
                        original_blog_row[BLOG_COLUMNS["author"]],
                        edited_title,
                        edited_content,
                        original_blog_row[BLOG_COLUMNS["timestamp"]]
                    ]
 
                    # gspread uses 1-based indexing for rows. Add 2 (1 for header, 1 for 0-based index)
                    row_in_sheet = st.session_state.edit_blog_idx + 2
                    if blog_ws and update_worksheet_row(blog_ws, row_in_sheet, updated_blog_values):
                        st.success("Blog post updated successfully!")
                        st.session_state.edit_blog_idx = None # Clear edit state
                        st.session_state.edit_blog_title = ""
                        st.session_state.edit_blog_content = ""
                        st.rerun() # Rerun to refresh the blog list and clear form
                else:
                    st.warning("Please fill in both title and content for the blog post.")
            elif cancel_edit:
                st.session_state.edit_blog_idx = None # Clear edit state
                st.session_state.edit_blog_title = ""
                st.session_state.edit_blog_content = ""
                st.rerun() # Rerun to clear form
 
 
    # Posting functionality (only for Admins and Chairman)
    if st.session_state.is_admin or st.session_state.user_name == "Chairman":
        st.subheader("Post a New Blog")
        st.session_state.temp_blog_title = st.text_input("Title", st.session_state.temp_blog_title, key="new_blog_title_input")
        st.session_state.temp_blog_content = st.text_area("Content", st.session_state.temp_blog_content, key="new_blog_content_input")
        if st.button("Post Blog", key="post_new_blog_button"):
            if st.session_state.temp_blog_title and st.session_state.temp_blog_content:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Order of values must match the column order in your Google Sheet: author, title, content, time
                blog_post_values = [
                    st.session_state.user_name, # author
                    st.session_state.temp_blog_title, # title
                    st.session_state.temp_blog_content, # content
                    now # time
                ]
                if blog_ws:
                    if append_row_to_sheet(blog_ws, blog_post_values):
                        st.success("Blog posted successfully!")
                        st.session_state.temp_blog_title = ""
                        st.session_state.temp_blog_content = ""
                        st.rerun() # Rerun to clear input fields and refresh blog list
            else:
                st.warning("Please fill in both title and content for the blog post.")
 
 
def display_intern_profiles():
    """Displays the intern profiles."""
    st.header("Intern Profiles")
    df_profiles = pd.DataFrame(INTERN_PROFILES)
    st.dataframe(df_profiles, use_container_width=True)
 
 
def update_tracker_with_responses(log_ws):
    """Updates the issue tracker with responses from the response sheet and logs changes."""
    tracker_ws = get_worksheet(client, SHEET_CONFIG["tracker"]["id"], SHEET_CONFIG["tracker"]["name"])
    response_ws = get_worksheet(client, SHEET_CONFIG["response"]["id"], SHEET_CONFIG["response"]["name"])
 
    if log_ws is None or tracker_ws is None or response_ws is None:
        return # Exit if any required worksheet is not found
 
    # Initialize log sheet header if empty
    if not log_ws.get_all_values():
        append_row_to_sheet(log_ws, [
            LOG_COLUMNS["timestamp"],
            LOG_COLUMNS["updated_by"],
            LOG_COLUMNS["field"],
            LOG_COLUMNS["old_value"],
            LOG_COLUMNS["new_value"],
            LOG_COLUMNS["issue_id"]
        ])
 
    tracker_df = get_dataframe_from_sheet(tracker_ws)
    responses_df = get_dataframe_from_sheet(response_ws)
 
    if tracker_df.empty:
        st.info("Tracker sheet is empty. No issues to update from responses.")
        return
    if responses_df.empty:
        st.info("Response sheet is empty. No new responses to process.")
        return
 
    # Define the mapping from response sheet columns to tracker sheet columns
    response_to_tracker_map = {
        RESPONSE_COLUMNS["email_phone"]: TRACKER_COLUMNS["email_phone"],
        RESPONSE_COLUMNS["description"]: TRACKER_COLUMNS["description"],
        RESPONSE_COLUMNS["issue_type"]: TRACKER_COLUMNS["issue_type"],
        RESPONSE_COLUMNS["gov_body"]: TRACKER_COLUMNS["gov_body"],
        RESPONSE_COLUMNS["priority_level"]: TRACKER_COLUMNS["priority"],
        RESPONSE_COLUMNS["proposed_resolution"]: TRACKER_COLUMNS["resolution"],
        RESPONSE_COLUMNS["file"]: TRACKER_COLUMNS["file"],
        RESPONSE_COLUMNS["date_submission"]: TRACKER_COLUMNS["date"]
    }
 
    updated_count = 0
    for i, resp in responses_df.iterrows():
        # Match based on 'Contact Person Name & Designation' and 'Title of Issue'
        contact_person_col = RESPONSE_COLUMNS["contact_person"]
        issue_title_col = RESPONSE_COLUMNS["issue_title"]
        tracker_contact_col = TRACKER_COLUMNS["contact"]
        tracker_issue_title_col = TRACKER_COLUMNS["issue_title"]
 
        # Validate existence of matching columns in response data
        if contact_person_col not in resp or issue_title_col not in resp:
            st.warning(f"Response row {i+2} is missing required matching columns ('{contact_person_col}' or '{issue_title_col}'). Skipping.")
            continue
        # Validate existence of matching columns in tracker dataframe
        if tracker_contact_col not in tracker_df.columns or tracker_issue_title_col not in tracker_df.columns:
            st.error(f"Tracker sheet is missing required matching columns ('{tracker_contact_col}' or '{tracker_issue_title_col}'). Cannot process responses.")
            return
 
        match = tracker_df[
            (tracker_df[tracker_contact_col] == resp[contact_person_col]) &
            (tracker_df[tracker_issue_title_col] == resp[issue_title_col])
        ]
 
        if not match.empty:
            row_idx = match.index[0]
            # Ensure current_issue_id is converted to string to prevent JSON serialization errors
            current_issue_id = str(tracker_df.at[row_idx, TRACKER_COLUMNS["id"]])
 
            changes_made_to_row = False
            for resp_col, tracker_col in response_to_tracker_map.items():
                if tracker_col in tracker_df.columns and resp_col in resp:
                    # Only update if the tracker field is empty or NaN
                    if pd.isna(tracker_df.at[row_idx, tracker_col]) or str(tracker_df.at[row_idx, tracker_col]).strip() == "":
                        old_value = tracker_df.at[row_idx, tracker_col]
                        new_value = resp[resp_col]
                        tracker_df.at[row_idx, tracker_col] = new_value
                        changes_made_to_row = True
 
                        # Log the individual change
                        append_row_to_sheet(log_ws, [
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            st.session_state.user_name,
                            tracker_col, # Corrected: Use tracker_col here
                            str(old_value) if pd.notna(old_value) else "", # Convert NaN to empty string for log
                            str(new_value) if pd.notna(new_value) else "",
                            current_issue_id
                        ])
 
            if changes_made_to_row:
                tracker_df.at[row_idx, TRACKER_COLUMNS["last_updated"]] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                tracker_df.at[row_idx, TRACKER_COLUMNS["updated_by"]] = st.session_state.user_name
                updated_count += 1
 
    if updated_count > 0:
        # Update the entire tracker worksheet with the modified DataFrame
        if update_entire_worksheet(tracker_ws, tracker_df):
            st.success(f"Tracker updated successfully with {updated_count} new responses!")
        else:
            st.error("Failed to write updated tracker data back to the sheet.")
    else:
        st.info("No new responses found to update the tracker.")
 
 
def display_issue_tracker():
    """Displays the issue tracker functionality (admin-only)."""
    st.header("Issue Tracker")
    st.info("Admin-only section for managing issues raised by departments.")
 
    log_ws = get_worksheet(client, SHEET_CONFIG["log"]["id"], SHEET_CONFIG["log"]["name"])
    tracker_ws = get_worksheet(client, SHEET_CONFIG["tracker"]["id"], SHEET_CONFIG["tracker"]["name"])
 
    if log_ws is None or tracker_ws is None:
        return # Exit if any required worksheet is not found
 
    # First, process any new responses from the response sheet
    update_tracker_with_responses(log_ws)
 
    # Then, display the current tracker data and allow for manual updates
    st.subheader("Current Issue Tracker Data")
    tracker_df = get_dataframe_from_sheet(tracker_ws)
 
    if not tracker_df.empty:
        st.dataframe(tracker_df, use_container_width=True)
 
        # Initialize session state for editing an issue
        if 'editing_tracker_issue_id' not in st.session_state:
            st.session_state.editing_tracker_issue_id = None
        if 'editing_tracker_data' not in st.session_state:
            st.session_state.editing_tracker_data = {}
 
        st.subheader("Update Existing Issue")
 
        # Create a list of issue titles for the selectbox
        issue_titles = ["Select an Issue to Edit"] + tracker_df[TRACKER_COLUMNS["issue_title"]].tolist()
        selected_issue_title = st.selectbox(
            "Choose an Issue to Update",
            issue_titles,
            key="select_issue_to_edit"
        )
 
        if selected_issue_title != "Select an Issue to Edit":
            # Find the selected row in the DataFrame
            selected_row = tracker_df[tracker_df[TRACKER_COLUMNS["issue_title"]] == selected_issue_title].iloc[0]
 
            # Pre-fill session state for the form
            st.session_state.editing_tracker_issue_id = selected_row[TRACKER_COLUMNS["id"]]
            st.session_state.editing_tracker_data = selected_row.to_dict()
 
            st.write(f"Editing Issue: **{selected_issue_title}**")
 
            with st.form("edit_tracker_issue_form"):
                # Display non-editable fields
                st.text_input("ID", value=st.session_state.editing_tracker_data.get(TRACKER_COLUMNS["id"], ""), disabled=True)
                st.text_input("Business Vertical", value=st.session_state.editing_tracker_data.get(TRACKER_COLUMNS["business_vertical"], ""), disabled=True)
                st.text_input("Team", value=st.session_state.editing_tracker_data.get(TRACKER_COLUMNS["team"], ""), disabled=True)
                st.text_input("Contact", value=st.session_state.editing_tracker_data.get(TRACKER_COLUMNS["contact"], ""), disabled=True)
 
                # Editable fields
                updated_email_phone = st.text_input("Email/Phone", value=st.session_state.editing_tracker_data.get(TRACKER_COLUMNS["email_phone"], ""), key="edit_email_phone")
                updated_description = st.text_area("Description", value=st.session_state.editing_tracker_data.get(TRACKER_COLUMNS["description"], ""), key="edit_description")
                updated_issue_type = st.text_input("Issue Type", value=st.session_state.editing_tracker_data.get(TRACKER_COLUMNS["issue_type"], ""), key="edit_issue_type")
                updated_gov_body = st.text_input("Gov Body", value=st.session_state.editing_tracker_data.get(TRACKER_COLUMNS["gov_body"], ""), key="edit_gov_body")
 
                # Define status options
                status_options = ["Open", "In Progress", "Resolved", "Closed"]
                current_status_value = st.session_state.editing_tracker_data.get(TRACKER_COLUMNS["status"], "Open")
                # Safely get the index for the selectbox
                try:
                    status_index = status_options.index(current_status_value)
                except ValueError:
                    status_index = 0 # Default to "Open" if current status is not in options
                updated_status = st.selectbox("Status", options=status_options, index=status_index, key="edit_status")
 
                # Define priority options
                priority_options = ["Low", "Medium", "High", "Critical"]
                current_priority_value = st.session_state.editing_tracker_data.get(TRACKER_COLUMNS["priority"], "Low")
                # Safely get the index for the selectbox
                try:
                    priority_index = priority_options.index(current_priority_value)
                except ValueError:
                    priority_index = 0 # Default to "Low" if current priority is not in options
                updated_priority = st.selectbox("Priority", options=priority_options, index=priority_index, key="edit_priority")
 
                updated_resolution = st.text_area("Resolution", value=st.session_state.editing_tracker_data.get(TRACKER_COLUMNS["resolution"], ""), key="edit_resolution")
                updated_file = st.text_input("File", value=st.session_state.editing_tracker_data.get(TRACKER_COLUMNS["file"], ""), key="edit_file")
                updated_date = st.text_input("Date", value=st.session_state.editing_tracker_data.get(TRACKER_COLUMNS["date"], ""), key="edit_date")
                updated_response = st.text_area("Response", value=st.session_state.editing_tracker_data.get(TRACKER_COLUMNS["response"], ""), key="edit_response")
 
                # Adjusted column layout for buttons
                col_save, col_cancel = st.columns([1,1]) # Use equal columns for save and cancel
                with col_save:
                    save_changes = st.form_submit_button("Save Changes")
                with col_cancel:
                    cancel_edit = st.form_submit_button("Cancel")
 
                if save_changes:
                    # Find the original row index in the DataFrame
                    original_row_idx = tracker_df[tracker_df[TRACKER_COLUMNS["id"]] == st.session_state.editing_tracker_issue_id].index[0]
 
                    changes_made = {}
                    # Compare and update fields, logging changes
                    fields_to_update = {
                        TRACKER_COLUMNS["email_phone"]: updated_email_phone,
                        TRACKER_COLUMNS["description"]: updated_description,
                        TRACKER_COLUMNS["issue_type"]: updated_issue_type,
                        TRACKER_COLUMNS["gov_body"]: updated_gov_body,
                        TRACKER_COLUMNS["priority"]: updated_priority,
                        TRACKER_COLUMNS["resolution"]: updated_resolution,
                        TRACKER_COLUMNS["file"]: updated_file,
                        TRACKER_COLUMNS["date"]: updated_date,
                        TRACKER_COLUMNS["status"]: updated_status,
                        TRACKER_COLUMNS["response"]: updated_response
                    }
 
                    for col_name, new_value in fields_to_update.items():
                        current_value = tracker_df.at[original_row_idx, col_name]
                        # Convert to string for comparison to handle potential type differences (e.g., int vs str)
                        if str(current_value).strip() != str(new_value).strip():
                            tracker_df.at[original_row_idx, col_name] = new_value
                            changes_made[col_name] = {"old": current_value, "new": new_value}
 
                            # Log the change
                            append_row_to_sheet(log_ws, [
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                st.session_state.user_name,
                                col_name,
                                str(current_value) if pd.notna(current_value) else "",
                                str(new_value) if pd.notna(new_value) else "",
                                str(st.session_state.editing_tracker_issue_id)
                            ])
 
                    if changes_made:
                        tracker_df.at[original_row_idx, TRACKER_COLUMNS["last_updated"]] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        tracker_df.at[original_row_idx, TRACKER_COLUMNS["updated_by"]] = st.session_state.user_name
 
                        if update_entire_worksheet(tracker_ws, tracker_df):
                            st.success("Issue updated successfully!")
                            st.session_state.editing_tracker_issue_id = None
                            st.session_state.editing_tracker_data = {}
                            st.rerun()
                        else:
                            st.error("Failed to save changes to the tracker sheet.")
                    else:
                        st.info("No changes detected.")
                        st.session_state.editing_tracker_issue_id = None
                        st.session_state.editing_tracker_data = {}
                        st.rerun()
 
                elif cancel_edit:
                    st.session_state.editing_tracker_issue_id = None
                    st.session_state.editing_tracker_data = {}
                    st.rerun()
 
    else:
        st.info("Tracker is currently empty. No issues to display or update.")
 
 
# --- Authentication ---
def login():
    """Handles user login."""
    st.sidebar.header("Login")
    username = st.sidebar.selectbox("Select Your Name", INTERN_NAMES)
    password = st.sidebar.text_input("Password", type="password")
 
    if st.sidebar.button("Login"):
        if password == ADMIN_PASSWORD:
            st.session_state.user_name = username
            st.session_state.logged_in = True
            st.session_state.is_admin = True
            st.success(f"Welcome, Admin {username}!")
            st.rerun() # Rerun to update UI based on login status
        elif password == USER_PASSWORD:
            st.session_state.user_name = username
            st.session_state.logged_in = True
            st.session_state.is_admin = False
            st.success(f"Welcome, {username}!")
            st.rerun() # Rerun to update UI based on login status
        else:
            st.error("Incorrect credentials")
 
 
def logout():
    """Handles user logout."""
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.session_state.is_admin = False
        # Clear blog post related session states on logout
        st.session_state.temp_blog_title = ""
        st.session_state.temp_blog_content = ""
        st.session_state.edit_blog_idx = None
        st.session_state.edit_blog_title = ""
        st.session_state.edit_blog_content = ""
        # Clear tracker related session states on logout
        st.session_state.editing_tracker_issue_id = None
        st.session_state.editing_tracker_data = {}
 
        st.success("Logged out successfully.")
        st.rerun() # Rerun to show login screen
 
 
# --- Main ---
def main():
    """Main function to run the Streamlit app."""
    # --- Session Initialization ---
    # Initialize all necessary session state variables if they don't exist.
    # This ensures a consistent state across reruns.
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False
    if "temp_blog_title" not in st.session_state:
        st.session_state.temp_blog_title = ""
    if "temp_blog_content" not in st.session_state:
        st.session_state.temp_blog_content = ""
    if 'edit_blog_idx' not in st.session_state:
        st.session_state.edit_blog_idx = None
    if 'edit_blog_title' not in st.session_state:
        st.session_state.edit_blog_title = ""
    if 'edit_blog_content' not in st.session_state:
        st.session_state.edit_blog_content = "" # Corrected: Was temp_blog_content
    # New session state for tracker editing
    if 'editing_tracker_issue_id' not in st.session_state:
        st.session_state.editing_tracker_issue_id = None
    if 'editing_tracker_data' not in st.session_state:
        st.session_state.editing_tracker_data = {}
 
 
    # Display login or main content based on login status
    if not st.session_state.logged_in:
        st.write("Please log in to access the portal features.")
        login()
    else:
        st.sidebar.write(f"Logged in as: **{st.session_state.user_name}**")
        logout() # Show logout button if logged in
 
        # --- Tabs for Portal ---
        tabs = ["Tasks", "Intern Profiles"]
        # Blog Board is now visible to all logged-in users (Admins, Chairman, and other Interns)
        tabs.insert(1, "Blog Board")
 
        # Issue Tracker remains exclusive to Admin/Chairman
        if st.session_state.is_admin or st.session_state.user_name == "Chairman":
            tabs.append("Issue Tracker")
 
        selected_tab = st.selectbox("Select a tab", tabs)
 
        # Display content based on selected tab
        if selected_tab == "Tasks":
            display_tasks()
        elif selected_tab == "Blog Board":
            display_blog_board()
        elif selected_tab == "Intern Profiles":
            display_intern_profiles()
        elif selected_tab == "Issue Tracker":
            display_issue_tracker()
 
 
if __name__ == "__main__":
    main()
