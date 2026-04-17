import streamlit as st
import pandas as pd
import sqlite3
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import datetime
import base64

# --- 1. DATABASE ARCHITECTURE ---
def init_db():
    conn = sqlite3.connect('innovate_final.db')
    c = conn.cursor()
    # Table for User Profiles (added dp for profile pictures)
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, role TEXT, 
                  email TEXT, phone TEXT, dept TEXT, bio TEXT, dp BLOB)''')
    # Table for Applications and Chat logs
    c.execute('''CREATE TABLE IF NOT EXISTS applications 
                 (id INTEGER PRIMARY KEY, student TEXT, professor TEXT, status TEXT, 
                  message TEXT, resume_data BLOB, chat_log TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- 2. THEME & SESSION MANAGEMENT ---
if 'user' not in st.session_state: st.session_state.user = None
if 'role' not in st.session_state: st.session_state.role = None

st.set_page_config(page_title="InnovateConnect Pro", layout="wide", page_icon="💬")

# Custom CSS for Dark Modern Theme
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: white; }
    .card { background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 12px; margin-bottom: 15px; }
    .profile-pic { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 2px solid #58a6ff; }
    .sidebar-pic { width: 100px; height: 100px; border-radius: 50%; object-fit: cover; display: block; margin: auto; border: 3px solid #238636; margin-bottom: 10px; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HELPER UTILITIES ---
def get_img_tag(bytes_data, css_class="profile-pic"):
    if bytes_data:
        base64_img = base64.b64encode(bytes_data).decode('utf-8')
        return f'<img src="data:image/png;base64,{base64_img}" class="{css_class}">'
    return f'<img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" class="{css_class}">'

def display_pdf(bytes_data):
    base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- 4. AUTHENTICATION (Fixed with Unique Keys) ---
def auth_page():
    st.title("🛡️ InnovateConnect AI")
    st.markdown("#### *National-Level Research Matchmaking Suite*")
    t1, t2 = st.tabs(["Login Portal", "New Registration"])
    
    with t1:
        u = st.text_input("Username", key="login_user")
        p = st.text_input("Password", type='password', key="login_pass")
        if st.button("Access Dashboard", key="login_btn"):
            conn = sqlite3.connect('innovate_final.db')
            res = conn.execute("SELECT role FROM users WHERE username=? AND password=?", (u, p)).fetchone()
            conn.close()
            if res:
                st.session_state.user, st.session_state.role = u, res[0]
                st.rerun()
            else: st.error("Incorrect credentials. Please try again.")
            
    with t2:
        reg_u = st.text_input("Choose Username", key="reg_user")
        reg_p = st.text_input("Choose Password", type='password', key="reg_pass")
        reg_e = st.text_input("Email ID", key="reg_email")
        reg_ph = st.text_input("Contact Number", key="reg_phone")
        reg_d = st.selectbox("Department", ["CSE", "IT", "ECE", "MECH", "BIOTECH"], key="reg_dept")
        reg_r = st.selectbox("Role", ["Student", "Professor"], key="reg_role")
        reg_b = st.text_area("Research Summary / Skillset", key="reg_bio")
        reg_dp = st.file_uploader("Upload Profile Picture (DP)", type=['png', 'jpg', 'jpeg'], key="reg_dp")
        
        if st.button("Create Account", key="reg_btn"):
            dp_bytes = reg_dp.read() if reg_dp else None
            try:
                conn = sqlite3.connect('innovate_final.db')
                conn.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?,?)", (reg_u, reg_p, reg_r, reg_e, reg_ph, reg_d, reg_b, dp_bytes))
                conn.commit()
                conn.close()
                st.success("Registration Successful! Please switch to Login Portal.")
            except sqlite3.IntegrityError:
                st.error("This username is already taken. Please try another.")

# --- 5. STUDENT DASHBOARD ---
def student_dashboard():
    conn = sqlite3.connect('innovate_final.db')
    my_data = conn.execute("SELECT bio, dp FROM users WHERE username=?", (st.session_state.user,)).fetchone()
    
    st.sidebar.markdown(get_img_tag(my_data[1], "sidebar-pic"), unsafe_allow_html=True)
    st.sidebar.markdown(f"<h3 style='text-align:center;'>{st.session_state.user}</h3>", unsafe_allow_html=True)
    
    menu = st.sidebar.radio("Navigation", ["🔍 Discover Mentors", "💬 Messaging Center"])
    if st.sidebar.button("Logout"): 
        st.session_state.user = None
        st.rerun()

    if menu == "🔍 Discover Mentors":
        st.title("AI-Driven Mentor Matching")
        profs = pd.read_sql_query("SELECT * FROM users WHERE role='Professor'", conn)
        applied_list = pd.read_sql_query("SELECT professor FROM applications WHERE student=?", conn, params=(st.session_state.user,))['professor'].tolist()

        if not profs.empty:
            all_text = profs['bio'].tolist() + [my_data[0]]
            tfidf = TfidfVectorizer().fit_transform(all_text)
            scores = cosine_similarity(tfidf[-1], tfidf[:-1])[0]
            
            for idx, row in profs.iterrows():
                with st.container():
                    c1, c2 = st.columns([1, 5])
                    c1.markdown(get_img_tag(row['dp']), unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"### Dr. {row['username']} ({round(scores[idx]*100,1)}% Match)")
                        st.write(f"**Dept:** {row['dept']} | **Focus:** {row['bio']}")
                    
                    if row['username'] in applied_list:
                        st.success("✅ Application Submitted")
                    else:
                        with st.expander("Apply for Collaboration"):
                            msg = st.text_area("Research Interest Statement", key=f"stmt_{idx}")
                            cv = st.file_uploader("Upload CV (PDF)", type="pdf", key=f"cv_{idx}")
                            if st.button("Submit Proposal", key=f"sub_{idx}"):
                                if cv:
                                    conn.execute("INSERT INTO applications (student, professor, status, message, resume_data, chat_log, timestamp) VALUES (?,?,'Pending',?,?,?,?)",
                                                 (st.session_state.user, row['username'], msg, cv.read(), "", datetime.datetime.now().strftime("%Y-%m-%d")))
                                    conn.commit()
                                    st.rerun()
                                else: st.warning("Please attach your CV to apply.")

    elif menu == "💬 Messaging Center":
        st.title("Inbox")
        apps = pd.read_sql_query("SELECT * FROM applications WHERE student=?", conn, params=(st.session_state.user,))
        if apps.empty: st.info("No messages or applications yet.")
        for idx, row in apps.iterrows():
            with st.expander(f"Update from Dr. {row['professor']} ({row['status']})"):
                st.write(f"**Faculty Remarks:** {row['chat_log'] if row['chat_log'] else 'Review in progress...'}")
    conn.close()

# --- 6. PROFESSOR DASHBOARD ---
def professor_dashboard():
    conn = sqlite3.connect('innovate_final.db')
    my_dp = conn.execute("SELECT dp FROM users WHERE username=?", (st.session_state.user,)).fetchone()[0]
    st.sidebar.markdown(get_img_tag(my_dp, "sidebar-pic"), unsafe_allow_html=True)
    st.sidebar.title(f"Dr. {st.session_state.user}")
    if st.sidebar.button("Logout"): 
        st.session_state.user = None
        st.rerun()

    st.title("Faculty Intake Dashboard")
    apps = pd.read_sql_query("SELECT * FROM applications WHERE professor=?", conn, params=(st.session_state.user,))
    
    if apps.empty:
        st.info("No pending applications.")
    else:
        for idx, row in apps.iterrows():
            student_profile = conn.execute("SELECT * FROM users WHERE username=?", (row['student'],)).fetchone()
            with st.expander(f"New Application: {row['student']} - Status: {row['status']}"):
                col_info, col_pdf = st.columns(2)
                with col_info:
                    st.markdown(get_img_tag(student_profile[7]), unsafe_allow_html=True)
                    st.write(f"**Student:** {student_profile[0]}")
                    st.write(f"**Email:** {student_profile[3]} | **Phone:** {student_profile[4]}")
                    st.write(f"**Skills:** {student_profile[6]}")
                    st.markdown("---")
                    res_msg = st.text_input("Reply to Student", key=f"resp_{idx}")
                    ca, cr = st.columns(2)
                    if ca.button("✅ Accept", key=f"acc_{idx}"):
                        conn.execute("UPDATE applications SET status='Accepted', chat_log=? WHERE id=?", (res_msg, row['id']))
                        conn.commit()
                        st.rerun()
                    if cr.button("❌ Reject", key=f"rej_{idx}"):
                        conn.execute("UPDATE applications SET status='Rejected', chat_log=? WHERE id=?", (res_msg, row['id']))
                        conn.commit()
                        st.rerun()
                with col_pdf:
                    st.write("### CV/Resume Preview")
                    if row['resume_data']: display_pdf(row['resume_data'])
    conn.close()

# --- 7. MAIN ENGINE ---
if st.session_state.user is None:
    auth_page()
elif st.session_state.role == "Student":
    student_dashboard()
else:
    professor_dashboard()