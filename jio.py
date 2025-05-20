import streamlit as st
import pandas as pd
import os
from PIL import Image
import requests
from io import BytesIO  # Required to open image from bytes

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
        {"Name": "Abuzar Tamannai", "Department": "Marketing", "LinkedIn": "https://linkedin.com/in/abuzar-tamannai-44b503257"},
        {"Name": "Trapti Singh", "Department": "Finance", "LinkedIn": "https://linkedin.com/in/trapti-singh16"},
        {"Name": "Ujjwal Akshith Mondreti", "Department": "Machine Learning", "LinkedIn": "https://linkedin.com/in/ujjwal-akshith-m"},
        {"Name": "Satvik Ahlawat", "Department": "Data Science", "LinkedIn": "https://linkedin.com/in/satvikahlawat/"},
        {"Name": "Rohit Mishra", "Department": "Data Analytics", "LinkedIn": "https://linkedin.com/in/rohit-mishra-a6689031b"},
    ]

# -------------------------------
# LOAD LOGO FROM GITHUB
# -------------------------------
logo_url = "./L.1.jpg"

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
    st.error(f"Error loading logo: {e}")
    st.title("Reliance Intern & Policy Issue Portal")

# -------------------------------
# LOGIN SIDEBAR
# -------------------------------
st.sidebar.title("Login")
all_names = ["Admin", "Chairman", "Policy"] + [intern["Name"] for intern in st.session_state.intern_data]
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
        st.success("Welcome, Chairman Office!")
    elif selected_user == "Policy" and entered_password == "policy@jio":
        st.session_state.logged_in = True
        st.session_state.user_name = "Policy"
        st.success("Welcome to the Policy Dashboard!")
    elif selected_user not in ["Admin", "Chairman", "Policy"] and entered_password == "jio2025":
        st.session_state.logged_in = True
        st.session_state.user_name = selected_user
        st.success(f"Welcome, {selected_user}!")
    else:
        st.error("Incorrect Access Code.")

# -------------------------------
# INTERN DASHBOARD
# -------------------------------
if st.session_state.logged_in and st.session_state.user_name not in ["Admin", "Chairman", "Policy"]:
    st.header("Your Dashboard – Weekly Tasks & Submissions")
    st.markdown(f"Welcome, **{st.session_state.user_name}**! Here are your tasks and ways to connect.")
    st.divider()

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

    st.divider()

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

    st.subheader("Intern Profiles")
    for intern in st.session_state.intern_data:
        st.subheader(intern["Name"])
        st.write(f"**Department:** {intern['Department']}")
        st.markdown(f"[LinkedIn]({intern['LinkedIn']})", unsafe_allow_html=True)
        st.markdown("---")

    st.divider()

    st.subheader("Intern Blog Board")
    if os.path.exists("blog_posts.csv"):
        blog_df = pd.read_csv("blog_posts.csv")
        for _, row in blog_df.iterrows():
            st.subheader(row["Title"])
            st.write(row["Content"])
            st.markdown("---")
    else:
        st.info("No blogs yet.")

    st.divider()

    st.subheader("Submit Task")
    with st.form("upload_form"):
        week = st.selectbox("Select Week", list(tasks.keys()))
        file = st.file_uploader("Upload PDF/DOC", type=["pdf", "docx"])
        submitted = st.form_submit_button("Submit")
        if submitted and file:
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

# -------------------------------
# POLICY + ADMIN/CHAIRMAN DASHBOARD
# -------------------------------
elif st.session_state.logged_in and st.session_state.user_name in ["Policy", "Admin", "Chairman"]:
    st.header("Policy Issues Tracker")

    csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQXnxefBfU43AgIEdCeCd5QBMgGVSifK9fSmSFuZd_jA_6B0Xem13xSjVqCY31QKsB88sjlOEa5T_gX/pub?output=csv"
    try:
        df_live = pd.read_csv(csv_url)
        st.success("Google Form data loaded successfully!")
        st.subheader("Public Submissions (from Google Form)")
        st.dataframe(df_live, use_container_width=True)
    except Exception as e:
        st.error(f"Google Form data failed to load: {e}")

    if st.session_state.user_name in ["Admin", "Chairman"]:
        st.subheader("Internal Tracker & Review")

        if os.path.exists("issues.csv"):
            df = pd.read_csv("issues.csv")
        else:
            df = pd.DataFrame(columns=[
                "Business Vertical", "Team", "Contact", "Email/Phone",
                "Issue Title", "Description", "Issue Type", "Gov Body",
                "Priority", "Resolution", "File", "Date", "Status", "Response"
            ])

        col1, col2 = st.columns(2)
        with col1:
            selected_priority = st.selectbox("Filter by Priority", ["All"] + df["Priority"].dropna().unique().tolist())
        with col2:
            selected_status = st.selectbox("Filter by Status", ["All", "New", "In Review", "Actioned", "Needs Clarification"])

        filtered = df.copy()
        if selected_priority != "All":
            filtered = filtered[filtered["Priority"] == selected_priority]
        if selected_status != "All":
            filtered = filtered[filtered["Status"] == selected_status]

        st.dataframe(filtered, use_container_width=True)

        st.subheader("Update Issue")
        if not df.empty:
            selected_issue = st.selectbox("Select Issue", df["Issue Title"].tolist())
            status = st.selectbox("Update Status", ["New", "In Review", "Actioned", "Needs Clarification"])
            response = st.text_area("Add Response")
            if st.button("Update Issue"):
                idx = df[df["Issue Title"] == selected_issue].index[0]
                df.at[idx, "Status"] = status
                df.at[idx, "Response"] = response
                df.to_csv("issues.csv", index=False)
                st.success("Issue updated and saved")

        st.download_button("Export Internal Tracker", data=df.to_csv(index=False), file_name="issues.csv")
        st.divider()
        st.markdown("© 2025 Reliance Jio Internship designed by Zishan Mallick| For academic use only.")
        st.markdown("**Disclaimer:** This is a simulated environment for educational purposes. All data is fictional and does not represent real issues or individuals.")
        st.markdown("**Note:** Please do not share any sensitive information. This is a public platform.")

        st.subheader("Intern Blog Board")
        if os.path.exists("blog_posts.csv"):
            blog_df = pd.read_csv("blog_posts.csv")
            for i, row in blog_df.iterrows():
                st.subheader(row["Title"])
                st.write(row["Content"])
                if st.session_state.is_admin and st.button(f"Delete Blog {i+1}", key=f"delete_{i}"):
                    blog_df = blog_df.drop(i)
                    blog_df.to_csv("blog_posts.csv", index=False)
                    st.success("Blog deleted!")
                    st.experimental_rerun()
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

            st.subheader("Add New Intern")
            new_name = st.text_input("Intern Name")
            new_dept = st.text_input("Department")
            new_linkedin = st.text_input("LinkedIn URL")
            if st.button("Add Intern"):
                st.session_state.intern_data.append({
                    "Name": new_name,
                    "Department": new_dept,
                    "LinkedIn": new_linkedin
                })
                st.success(f"{new_name} added to intern list.")

        st.divider()

# -------------------------------
# NOT LOGGED IN
# -------------------------------
else:
    st.info("Please log in using your name and access code in the sidebar.")

st.divider()
st.markdown("© 2025 Reliance Jio Internship designed by Zishan Mallick| For academic use only.")
st.markdown("**Disclaimer:** This is a simulated environment for educational purposes. All data is fictional and does not represent real issues or individuals.")
st.markdown("**Note:** Please do not share any sensitive information. This is a public platform.")
