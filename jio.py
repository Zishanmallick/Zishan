import streamlit as st
import datetime
import os
import pandas as pd

# -------------------- CONFIG --------------------
st.set_page_config(page_title="Jio Intern Portal", layout="centered")
st.title("🚀 Reliance Jio Intern Portal")

# -------------------- SESSION SETUP --------------------
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
        {"Name": "satvik Ahlawat", "Department": "Data Science", "LinkedIn": "https://linkedin.com/in/satvikahlawat/"},
        {"Name": "Rohit Mishra", "Department": "Data Analytics", "LinkedIn": "https://linkedin.com/in/rohit-mishra-a6689031b"},

    ]

# -------------------- LOGIN --------------------
st.sidebar.title("🔐 Login")
all_names = ["Admin"] + [intern["Name"] for intern in st.session_state.intern_data]
selected_user = st.sidebar.selectbox("Select Your Name", all_names)
entered_password = st.sidebar.text_input("Enter Access Code", type="password")

if st.sidebar.button("Login"):
    if selected_user == "Admin" and entered_password == "admin@jio":
        st.session_state.logged_in = True
        st.session_state.user_name = "Admin"
        st.session_state.is_admin = True
        st.success("Welcome, Admin! 🔐")
    elif selected_user != "Admin" and entered_password == "jio2025":
        st.session_state.logged_in = True
        st.session_state.user_name = selected_user
        st.session_state.is_admin = False
        st.success(f"Welcome, {selected_user}!")
    else:
        st.error("Incorrect Access Code.")

# -------------------- MAIN DASHBOARD --------------------
if st.session_state.logged_in:
    st.markdown(f"Welcome to the intern portal, **{st.session_state.user_name}**. Here you’ll find weekly tasks, announcements, resources, and tools.")
    st.divider()

    # 📢 Announcements
    st.header("📢 Announcements")
    announcements = [
        "📣 Intern Townhall on **May 25 at 4:00 PM**.",
        "📝 Task 2 deadline: **May 24, 11:59 PM**.",
        "🎖️ Intern of the Week: **Zishan Mallick!**"
    ]
    for note in announcements:
        st.info(note)

    st.divider()

    # 📋 Weekly Tasks
    st.header("📋 Weekly Tasks")
    tasks = {
        "Week 1": "Intro to Jio Platforms + Submit project preference form",
        "Week 2": "Research Jio's AI Strategy and write 500-word report",
        "Week 3": "Group presentation on Jio Digital Transformation"
    }
    for week, desc in tasks.items():
        st.write(f"**{week}:** {desc}")

    st.divider()

    # 📚 PDFs
    st.header("📚 Reading Materials")
    pdfs = {
        "Week 1 – Jio Overview": "materials/JioBrain.pdf",
        "Week 2 – AI Strategy": "materials/Digital Transformation PPT for DFS Meeting_Sept2024.pdf",
        "Week 3 – Digital Transformation": "materials/RIL_4Q_FY25_Analyst_Presentation_25Apr25.pdf"
    }
    for title, path in pdfs.items():
        st.subheader(title)
        try:
            with open(path, "rb") as f:
                st.download_button("📄 Download", f, file_name=os.path.basename(path))
        except FileNotFoundError:
            st.warning(f"Missing file: {os.path.basename(path)}")

    st.divider()

    # 👩‍💻 Intern Profiles
    st.header("👩‍💻 Intern Profiles")
    for intern in st.session_state.intern_data:
        st.subheader(intern["Name"])
        st.write(f"**Department:** {intern['Department']}")
        st.markdown(f"[🔗 LinkedIn]({intern['LinkedIn']})", unsafe_allow_html=True)
        st.markdown("---")

    st.divider()

    # 📤 Upload Task (Save only)
    st.header("📤 Submit Task")
    with st.form("upload_form"):
        week = st.selectbox("Select Week", list(tasks.keys()))
        file = st.file_uploader("Upload PDF/DOC", type=["pdf", "docx"])
        submitted = st.form_submit_button("Submit")
        if submitted and file:
            path = f"uploads/{st.session_state.user_name.replace(' ', '_')}_{week}_{file.name}"
            with open(path, "wb") as f:
                f.write(file.read())
            st.success("✅ Uploaded and saved successfully!")

    st.divider()

    # 💬 Chat Box
    st.header("💬 Intern Chat")
    chat_msg = st.text_input("Message:")
    if st.button("Send") and chat_msg:
        st.session_state.chat.append(f"{st.session_state.user_name}: {chat_msg}")
    for msg in st.session_state.chat[-10:]:
        st.write(msg)

    st.divider()

    # 📰 Blog Board
    st.header("📰 Intern Blog Board")
    if os.path.exists("blog_posts.csv"):
        blog_df = pd.read_csv("blog_posts.csv")
        for i, row in blog_df.iterrows():
            st.subheader(row["Title"])
            st.write(row["Content"])
            if st.session_state.is_admin and st.button(f"🗑️ Delete Blog {i+1}", key=f"delete_{i}"):
                blog_df = blog_df.drop(i)
                blog_df.to_csv("blog_posts.csv", index=False)
                st.success("Blog deleted!")
                st.experimental_rerun()
            st.markdown("---")
    else:
        st.info("No blogs yet.")

    if st.session_state.is_admin:
        st.subheader("✍️ Publish Blog")
        blog_title = st.text_input("Title")
        blog_content = st.text_area("Content")
        if st.button("Post Blog"):
            entry = pd.DataFrame([[blog_title, blog_content]], columns=["Title", "Content"])
            if os.path.exists("blog_posts.csv"):
                entry.to_csv("blog_posts.csv", mode="a", header=False, index=False)
            else:
                entry.to_csv("blog_posts.csv", index=False)
            st.success("✅ Blog posted!")

    st.divider()

    # ➕ Add Intern (Admin Only)
    if st.session_state.is_admin:
        st.subheader("➕ Add New Intern")
        new_name = st.text_input("Intern Name")
        new_dept = st.text_input("Department")
        new_linkedin = st.text_input("LinkedIn URL")
        if st.button("Add Intern"):
            st.session_state.intern_data.append({
                "Name": new_name,
                "Department": new_dept,
                "LinkedIn": new_linkedin
            })
            st.success(f"✅ {new_name} added to intern list.")

    st.divider()
    st.markdown("© 2025 Reliance Jio Internship | For academic use only.") 

else:
    st.info("👈 Please log in using your name and access code in the sidebar.")
