import streamlit as st
import requests
import plotly.graph_objects as go
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# ── Session state defaults ────────────────────────────────────────────────────
for key, default in [
    ("token", None), ("role", None), ("full_name", None),
    ("result", None), ("active_tab", "Home"),
    ("selected_job_id", None), ("selected_job_title", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="HireSense AI", page_icon="🧠", layout="wide")

# ── Custom CSS Inject ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    /* App background & fonts */
    .stApp {
        background-color: #070913;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    /* Custom Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #0b0f19 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Input field styling */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        background-color: #111827 !important;
        color: #f3f4f6 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
    }
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }

    /* Cards */
    .glass-card {
        background: rgba(17, 24, 39, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
    }

    .job-card {
        background: rgba(22, 28, 45, 0.55);
        border: 1px solid rgba(99, 102, 241, 0.15);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        transition: all 0.3s ease;
    }
    
    .job-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.1);
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-pending {
        background-color: rgba(245, 158, 11, 0.12);
        color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .badge-shortlist {
        background-color: rgba(16, 185, 129, 0.12);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .badge-reject {
        background-color: rgba(239, 68, 68, 0.12);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    /* Gradient header banner */
    .hero-banner {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.1) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 30px;
        border-left: 6px solid #6366f1;
    }
    
    /* Text colors */
    .text-glow {
        color: #ffffff;
        text-shadow: 0 0 10px rgba(99, 102, 241, 0.3);
    }
    .text-purple {
        color: #a855f7;
    }
    
    /* Custom buttons styling */
    .stButton>button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
</style>
""", unsafe_allow_html=True)


def auth_header():
    return {"Authorization": f"Bearer {st.session_state['token']}"}


# ── Auth Pages ────────────────────────────────────────────────────────────────
def login_page():
    st.markdown("<h1 style='text-align: center; margin-top: 50px;' class='text-glow'>🧠 HireSense AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #9ca3af;'>Next-gen recruiting & resume ranking platform</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔒 Login", "📝 Register"])

        with tab1:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Log In", use_container_width=True, type="primary"):
                try:
                    resp = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
                    if resp.status_code == 200:
                        data = resp.json()
                        st.session_state["token"] = data["access_token"]
                        st.session_state["role"] = data["role"]
                        st.session_state["full_name"] = data["full_name"]
                        st.session_state["active_tab"] = "Home"
                        st.rerun()
                    else:
                        st.error(resp.json().get("detail", "Login failed"))
                except Exception as e:
                    st.error(f"Connection error: {e}")

        with tab2:
            full_name = st.text_input("Full Name")
            reg_email = st.text_input("Email Address", key="reg_email")
            reg_password = st.text_input("Password (min 8 chars)", type="password", key="reg_pass")
            role = st.selectbox("I want to register as a:", ["candidate", "recruiter"])
            if st.button("Create Account", use_container_width=True):
                try:
                    resp = requests.post(f"{API_URL}/auth/register", json={
                        "full_name": full_name, "email": reg_email,
                        "password": reg_password, "role": role,
                    })
                    if resp.status_code == 201:
                        st.success("Registration successful! Please log in above.")
                    else:
                        st.error(resp.json().get("detail", "Registration failed"))
                except Exception as e:
                    st.error(f"Connection error: {e}")
        st.markdown("</div>", unsafe_allow_html=True)


# ── Navigation & Sidebar ──────────────────────────────────────────────────────
def draw_sidebar():
    st.sidebar.markdown("<h2 style='text-align: center; color: #6366f1; margin-top: 20px; font-weight: 800;'>🧠 HireSense AI</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("<hr style='margin: 10px 0; opacity: 0.15;' />", unsafe_allow_html=True)

    st.sidebar.markdown(f"""
    <div style='text-align: center; padding: 10px;'>
        <div style='font-size: 1.1rem; font-weight: 700; color: #ffffff;'>{st.session_state['full_name']}</div>
        <div class='badge badge-pending' style='margin-top: 4px; padding: 2px 8px; font-size: 0.7rem;'>{st.session_state['role'].upper()}</div>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    # Custom menu buttons
    def make_nav_button(label, key_name):
        if st.sidebar.button(label, use_container_width=True, type="primary" if st.session_state["active_tab"] == key_name else "secondary"):
            st.session_state["active_tab"] = key_name
            st.session_state["result"] = None
            st.rerun()

    make_nav_button("🏠 Home", "Home")

    if st.session_state["role"] == "candidate":
        make_nav_button("💼 Explore Jobs", "Explore Jobs")
        make_nav_button("🔍 Match & Apply", "Analyze Candidate")
        make_nav_button("📋 My Applications", "My Applications")
    else:
        make_nav_button("📋 Post a Job", "Post Job")
        make_nav_button("⚙️ Manage Jobs & Applicants", "Manage Jobs")
        make_nav_button("🧪 Quick Match Sandbox", "Analyze Candidate")

    st.sidebar.markdown("<br><br><hr style='opacity: 0.15;' />", unsafe_allow_html=True)
    if st.sidebar.button("🚪 Log Out", use_container_width=True):
        for key in ["token", "role", "full_name", "result", "active_tab", "selected_job_id", "selected_job_title"]:
            st.session_state[key] = None
        st.rerun()


# ── Pages ─────────────────────────────────────────────────────────────────────

def page_home():
    st.markdown(f"""
    <div class='hero-banner'>
        <h1 style='margin: 0; color: #ffffff;' class='text-glow'>Welcome back, {st.session_state['full_name']}!</h1>
        <p style='margin: 8px 0 0 0; color: #9ca3af; font-size: 1.1rem;'>
            Streamline your recruitment lifecycle with AI-powered resume parsing, semantic Job Description alignment, and GitHub audit analytics.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state["role"] == "recruiter":
        # Recruiter Dashboard Statistics
        try:
            resp = requests.get(f"{API_URL}/recruiter/dashboard", headers=auth_header())
            if resp.status_code == 200:
                stats = resp.json()
                st.subheader("📊 Recruiter Insights")
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.markdown(f"<div class='glass-card' style='text-align: center;'><h3>💼 Jobs Posted</h3><h2 style='color:#6366f1; margin:0;'>{stats['jobs_posted']}</h2></div>", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"<div class='glass-card' style='text-align: center;'><h3>👥 Total Applications</h3><h2 style='color:#a855f7; margin:0;'>{stats['total_applications']}</h2></div>", unsafe_allow_html=True)
                with c3:
                    st.markdown(f"<div class='glass-card' style='text-align: center;'><h3>✅ Shortlisted</h3><h2 style='color:#10b981; margin:0;'>{stats['shortlisted']}</h2></div>", unsafe_allow_html=True)
                with c4:
                    st.markdown(f"<div class='glass-card' style='text-align: center;'><h3>📈 Avg Match Score</h3><h2 style='color:#0ea5e9; margin:0;'>{stats['average_match_score']}%</h2></div>", unsafe_allow_html=True)
            else:
                st.error("Failed to load dashboard metrics.")
        except Exception as e:
            st.error(f"Error loading dashboard metrics: {e}")
    else:
        # Candidate overview
        st.subheader("🚀 Active Pipeline Capabilities")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown("<div class='glass-card' style='text-align: center;'><h4>Resume Parser</h4><p style='color: #10b981; font-weight: 700; margin: 0;'>Active</p><span style='font-size:0.8rem; color:#9ca3af;'>Extracts contact info & skill vectors</span></div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='glass-card' style='text-align: center;'><h4>JD Alignment</h4><p style='color: #10b981; font-weight: 700; margin: 0;'>Active</p><span style='font-size:0.8rem; color:#9ca3af;'>SentenceTransformer semantic similarity</span></div>", unsafe_allow_html=True)
        with c3:
            st.markdown("<div class='glass-card' style='text-align: center;'><h4>GitHub Verification</h4><p style='color: #10b981; font-weight: 700; margin: 0;'>Active</p><span style='font-size:0.8rem; color:#9ca3af;'>Analyzes repositories & languages</span></div>", unsafe_allow_html=True)
        with c4:
            st.markdown("<div class='glass-card' style='text-align: center;'><h4>Dynamic Scoring</h4><p style='color: #10b981; font-weight: 700; margin: 0;'>Active</p><span style='font-size:0.8rem; color:#9ca3af;'>Dynamic weights based on profile</span></div>", unsafe_allow_html=True)


def page_explore_jobs():
    st.markdown("<h2 class='text-glow'>💼 Explore Job Opportunities</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9ca3af;'>Browse openings, review required skills, and match your resume.</p>", unsafe_allow_html=True)

    try:
        resp = requests.get(f"{API_URL}/jobs/", headers=auth_header())
        if resp.status_code == 200:
            jobs = resp.json()
            if not jobs:
                st.info("No job openings currently available.")
                return

            for job in jobs:
                st.markdown(f"""
                <div class='job-card'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <h3 style='margin: 0; color: #ffffff;'>{job['title']}</h3>
                        <span style='color: #a855f7; font-weight: 700; font-size: 1rem;'>🏢 {job['company']}</span>
                    </div>
                    <p style='margin: 12px 0; color: #d1d5db; font-size: 0.95rem;'>{job['description']}</p>
                    <div style='margin-top: 10px;'>
                        <strong>Required Skills: </strong>
                        <span style='color: #818cf8;'>{job['required_skills']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Button to apply
                col1, col2 = st.columns([1, 5])
                with col1:
                    if st.button("Apply & Match", key=f"apply_{job['id']}", type="primary"):
                        st.session_state["selected_job_id"] = job["id"]
                        st.session_state["selected_job_title"] = f"{job['title']} at {job['company']}"
                        st.session_state["active_tab"] = "Analyze Candidate"
                        st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.error("Failed to retrieve jobs.")
    except Exception as e:
        st.error(f"Error fetching jobs: {e}")


def page_my_applications():
    st.markdown("<h2 class='text-glow'>📋 My Applications & Status</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9ca3af;'>Track your match scores and status decisions from recruiters.</p>", unsafe_allow_html=True)

    try:
        resp = requests.get(f"{API_URL}/candidate/applications", headers=auth_header())
        if resp.status_code == 200:
            apps = resp.json()
            if not apps:
                st.info("You haven't matched or applied against any job openings yet.")
                return

            for app in apps:
                status = app["status"]
                badge_class = "badge-pending"
                if status == "shortlist":
                    badge_class = "badge-shortlist"
                elif status == "reject":
                    badge_class = "badge-reject"

                st.markdown(f"""
                <div class='glass-card'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <h3 style='margin:0; color:#ffffff;'>{app['job_title']}</h3>
                        <span class='badge {badge_class}'>{status}</span>
                    </div>
                    <div style='color: #a855f7; font-weight: 600; margin-top: 4px;'>🏢 {app['company']}</div>
                    <hr style='opacity: 0.1; margin: 12px 0;' />
                    <div style='display: flex; gap: 40px;'>
                        <div>
                            <span style='color: #9ca3af;'>Match Score:</span>
                            <strong style='font-size: 1.1rem; color: #10b981;'> {app['match_score']}%</strong>
                        </div>
                        <div>
                            <span style='color: #9ca3af;'>Applied On:</span>
                            <strong> {app['applied_at'][:10] if app['applied_at'] else 'N/A'}</strong>
                        </div>
                    </div>
                    {f"<div style='margin-top: 10px; font-size: 0.9rem; color: #ef4444;'>⚠️ <strong>Detected Skill Gaps:</strong> {app['skill_gaps']}</div>" if app['skill_gaps'] else ""}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("Failed to load applications.")
    except Exception as e:
        st.error(f"Error: {e}")


def page_post_job():
    st.markdown("<h2 class='text-glow'>📋 Post a New Job opening</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9ca3af;'>Publish requirements for automated candidate ranking & matching.</p>", unsafe_allow_html=True)

    with st.form("post_job_form", clear_on_submit=True):
        title = st.text_input("Job Title *", placeholder="e.g. Lead Full-Stack Engineer")
        company = st.text_input("Company *", placeholder="e.g. Acme Corporation")
        description = st.text_area("Job Description *", height=150, placeholder="Describe role, responsibilities, and qualifications...")
        required_skills = st.text_input("Required Skills (comma separated) *", placeholder="e.g. Python, React, AWS, Docker")

        submit = st.form_submit_button("Publish Job", type="primary")

        if submit:
            if not all([title, company, description, required_skills]):
                st.warning("Please fill in all required fields.")
            else:
                try:
                    resp = requests.post(f"{API_URL}/jobs/", json={
                        "title": title, "company": company,
                        "description": description, "required_skills": required_skills,
                    }, headers=auth_header())
                    if resp.status_code == 201:
                        st.success(f"🎉 Job successfully published! Job ID: {resp.json()['job_id']}")
                    else:
                        st.error(resp.json().get("detail", "Failed to publish job."))
                except Exception as e:
                    st.error(f"Connection error: {e}")


def page_manage_jobs():
    st.markdown("<h2 class='text-glow'>⚙️ Manage Jobs & Applicants</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9ca3af;'>View applicant rankings, skill gaps, and send shortlist notifications.</p>", unsafe_allow_html=True)

    try:
        resp = requests.get(f"{API_URL}/recruiter/jobs", headers=auth_header())
        if resp.status_code == 200:
            jobs = resp.json()
            if not jobs:
                st.info("You haven't posted any job openings yet.")
                return

            # Selection dropdown
            job_opts = {f"{j['title']} (ID: {j['id']})": j for j in jobs}
            selected_option = st.selectbox("Select Job Posting to Audit", list(job_opts.keys()))
            selected_job = job_opts[selected_option]

            st.markdown(f"""
            <div class='glass-card' style='border-left: 4px solid #a855f7;'>
                <h3 style='margin: 0; color: #ffffff;'>{selected_job['title']}</h3>
                <p style='color: #d1d5db; margin: 8px 0;'>{selected_job['description']}</p>
                <div><strong>Required skills:</strong> <span style='color: #818cf8;'>{selected_job['required_skills']}</span></div>
            </div>
            """, unsafe_allow_html=True)

            # Get applicants
            app_resp = requests.get(f"{API_URL}/recruiter/jobs/{selected_job['id']}/applications", headers=auth_header())
            if app_resp.status_code == 200:
                applicants = app_resp.json()
                if not applicants:
                    st.warning("No applications received yet for this position.")
                    return

                st.subheader(f"👥 Applicants Sorted by Rank ({len(applicants)})")
                
                for idx, app in enumerate(applicants):
                    status = app["status"]
                    badge_class = "badge-pending"
                    if status == "shortlist":
                        badge_class = "badge-shortlist"
                    elif status == "reject":
                        badge_class = "badge-reject"

                    # Card for applicant
                    with st.expander(f"🏅 {app['candidate_name']} ── Score: {app['match_score']}% ── status: {status.upper()}", expanded=idx == 0):
                        st.markdown(f"""
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div>
                                <strong>Candidate Email:</strong> {app['candidate_email']}<br>
                                <strong>Matched on:</strong> {app['created_at'][:10] if app['created_at'] else 'N/A'}
                            </div>
                            <span class='badge {badge_class}'>{status}</span>
                        </div>
                        """, unsafe_allow_html=True)

                        if app['skill_gaps']:
                            st.markdown(f"<div style='margin-top: 10px; color:#ef4444;'>⚠️ <strong>Missing skills:</strong> {app['skill_gaps']}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div style='margin-top: 10px; color:#10b981;'>✅ <strong>All required skills met!</strong></div>", unsafe_allow_html=True)

                        # Decision block
                        st.markdown("---")
                        st.markdown("##### ⚙️ Update Decision")
                        
                        email_notify = st.checkbox("Send Email Notification automatically", value=True, key=f"notify_check_{app['match_id']}")
                        
                        col1, col2, col3 = st.columns([1, 1, 3])
                        with col1:
                            if st.button("✅ Shortlist", key=f"sl_{app['match_id']}", type="primary"):
                                update_status_api(app['match_id'], "shortlist", app['candidate_name'], app['candidate_email'], app['match_score'], email_notify)
                        with col2:
                            if st.button("❌ Reject", key=f"rj_{app['match_id']}"):
                                update_status_api(app['match_id'], "reject", app['candidate_name'], app['candidate_email'], app['match_score'], email_notify)
            else:
                st.error("Failed to load applicants for this job.")
        else:
            st.error("Failed to retrieve your jobs.")
    except Exception as e:
        st.error(f"Error loading recruiter panel: {e}")


def update_status_api(match_id, status, candidate_name, candidate_email, score, send_mail):
    try:
        resp = requests.post(f"{API_URL}/recruiter/applications/{match_id}/status", params={"status": status}, headers=auth_header())
        if resp.status_code == 200:
            st.success(f"Application updated to: {status.upper()}")
            
            if send_mail:
                # Trigger email notification
                mail_resp = requests.post(f"{API_URL}/notify/email", json={
                    "to_email": candidate_email,
                    "candidate_name": candidate_name,
                    "decision": status,
                    "score": score
                }, headers=auth_header())
                if mail_resp.status_code == 200:
                    st.info("Status notification email sent successfully!")
                else:
                    st.warning("Application saved, but notification email failed to send (check server configurations).")
            
            st.rerun()
        else:
            st.error(resp.json().get("detail", "Failed to update status."))
    except Exception as e:
        st.error(f"Connection error: {e}")


def page_analyze_candidate():
    st.markdown("<h2 class='text-glow'>🔍 Resume Matching & Rank Analytics</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9ca3af;'>Parse resume files, match against standard or specific JDs, and inspect GitHub metrics.</p>", unsafe_allow_html=True)

    job_id = st.session_state.get("selected_job_id")
    job_title = st.session_state.get("selected_job_title")

    # Clear selected job context button if set
    if job_id:
        st.markdown(f"""
        <div class='glass-card' style='border: 1px solid rgba(99, 102, 241, 0.4); background: rgba(99, 102, 241, 0.08); padding: 12px 20px;'>
            <strong>Matching against Job:</strong> {job_title}
        </div>
        """, unsafe_allow_html=True)
        if st.button("Reset to Sandbox (Custom Matching)"):
            st.session_state["selected_job_id"] = None
            st.session_state["selected_job_title"] = ""
            st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX) *", type=["pdf", "docx"])
        github_username = st.text_input("GitHub Username (optional)", placeholder="e.g. octocat")
    with col2:
        if job_id:
            st.text_area("Job Description (Auto-loaded from job posting)", value="Job details pre-loaded. Description is managed by backend.", height=150, disabled=True)
            jd_text = ""  # Will be resolved by the backend using job_id
        else:
            jd_text = st.text_area("Job Description *", height=150, placeholder="Paste the details of the job requirements here...")

    if st.button("Run Profile Analysis 🚀", type="primary", use_container_width=True):
        if not uploaded_file or (not job_id and not jd_text.strip()):
            st.warning("Resume file and Job Description (or Selected Job) are required.")
        else:
            with st.spinner("Analyzing profile & fetching metrics..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    params = {"github_username": github_username}
                    if job_id:
                        params["job_id"] = job_id
                    else:
                        params["jd_text"] = jd_text

                    resp = requests.post(
                        f"{API_URL}/rank/candidate",
                        files=files, params=params,
                        headers=auth_header(),
                        timeout=90
                    )

                    if resp.status_code == 200:
                        st.session_state["result"] = resp.json()
                        st.success("✅ Analysis successfully completed!")
                    elif resp.status_code == 401:
                        st.error("Session expired. Please log in again.")
                    else:
                        st.error(resp.json().get("detail", "Analysis failed."))
                except requests.exceptions.Timeout:
                    st.error("Request timed out. GitHub lookup took too long — try matching without providing a GitHub username.")
                except Exception as e:
                    st.error(f"Error: {e}")

    # Results Render
    result = st.session_state.get("result")
    if result:
        ranking = result["ranking"]
        st.markdown("<hr style='opacity: 0.15;' />", unsafe_allow_html=True)
        st.markdown(f"### 📊 Scorecard for **{result['candidate_name']}**", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div class='glass-card' style='text-align: center; border-bottom: 4px solid #10b981;'><h4>Final Score</h4><h1 style='color: #10b981;'>{ranking['final_score']}%</h1></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='glass-card' style='text-align: center; border-bottom: 4px solid #a855f7;'><h4>Grade</h4><h1 style='color: #a855f7;'>{ranking['grade']}</h1></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='glass-card' style='text-align: center; border-bottom: 4px solid #0ea5e9;'><h4>Recommendation</h4><h3 style='color: #0ea5e9; margin-top:12px;'>{ranking['recommendation']}</h3></div>", unsafe_allow_html=True)

        # Plotly gauge chart
        score_val = ranking["final_score"]
        gauge_color = "#10b981" if score_val >= 70 else ("#f59e0b" if score_val >= 40 else "#ef4444")
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score_val,
            title={"text": "Profile Fit Score", "font": {"color": "#ffffff"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#ffffff"},
                "bar": {"color": gauge_color},
                "bgcolor": "rgba(255,255,255,0.05)",
                "steps": [
                    {"range": [0, 40], "color": "rgba(239, 68, 68, 0.1)"},
                    {"range": [40, 70], "color": "rgba(245, 158, 11, 0.1)"},
                    {"range": [70, 100], "color": "rgba(16, 185, 129, 0.1)"},
                ],
            },
        ))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={"color": "#ffffff"}, height=280)
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🛠️ Extracted Skills")
            if result["skills"]:
                skills_html = "".join([f"<span class='badge badge-pending' style='margin: 4px; font-size: 0.9rem;'>{s}</span>" for s in result["skills"]])
                st.markdown(f"<div style='margin-bottom: 20px;'>{skills_html}</div>", unsafe_allow_html=True)
            else:
                st.info("No known engineering skills detected in resume.")

            st.subheader("🎯 Job Description Match")
            match_pct = result["jd_match"]["match_score"]
            verdict = result["jd_match"]["verdict"]
            st.markdown(f"""
            <div class='glass-card'>
                <h4>Semantic similarity: <span style='color:#10b981;'>{match_pct}%</span></h4>
                <div style='font-size:1.1rem;'>Verdict: <strong>{verdict}</strong></div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.subheader("🐙 GitHub Audit Stats")
            g = result["github"]
            if g.get("username"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Repos", g["repos"])
                with c2:
                    st.metric("Commits", g["commits"])
                with c3:
                    st.metric("Languages", len(g["languages"]))

                if g["top_repos"]:
                    st.markdown("<p style='margin-top: 10px; font-weight:700;'>Recent Active Repos:</p>", unsafe_allow_html=True)
                    for repo in g["top_repos"][:3]:
                        st.markdown(f"""
                        <div class='job-card' style='padding: 8px 12px; margin-bottom: 8px;'>
                            <a href='{repo.get("url","#")}' target='_blank' style='color:#6366f1; font-weight:700;'>{repo['name']}</a> 
                            ── <span style='color:#a855f7;'>{repo['language'] or 'Text'}</span> ⭐ {repo['stars']}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No GitHub username was provided for verification.")

        # Breakdown chart
        breakdown = ranking["breakdown"]
        # filter out zero components
        breakdown_items = {k.replace("_score", "").replace("_", " ").title(): v for k, v in breakdown.items() if v > 0}
        fig2 = go.Figure(go.Bar(
            x=list(breakdown_items.values()),
            y=list(breakdown_items.keys()),
            orientation='h',
            marker_color="#6366f1",
        ))
        fig2.update_layout(
            title="Weight Contribution Breakdown",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#ffffff"},
            xaxis_title="Points Added",
            height=250,
            margin=dict(l=150, r=20, t=40, b=40)
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Recruiter decision box (if run from Sandbox and recruiter role)
        if st.session_state["role"] == "recruiter" and not job_id:
            st.divider()
            st.subheader("📬 Instant Recruiter Action (Sandbox)")
            candidate_email = st.text_input("Candidate Notification Email Address", value=result["candidate_email"])

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Shortlist Candidate", type="primary", use_container_width=True):
                    notify_sandbox_decision(candidate_email, result["candidate_name"], "shortlist", ranking["final_score"])
            with col2:
                if st.button("❌ Reject Candidate", use_container_width=True):
                    notify_sandbox_decision(candidate_email, result["candidate_name"], "reject", ranking["final_score"])


def notify_sandbox_decision(email, name, decision, score):
    if not email:
        st.error("Please enter a valid email address first.")
        return
    try:
        resp = requests.post(f"{API_URL}/notify/email", json={
            "to_email": email,
            "candidate_name": name,
            "decision": decision,
            "score": score
        }, headers=auth_header())
        if resp.status_code == 200:
            st.success(f"Email sent successfully notifying {name} of {decision.upper()} status!")
        else:
            st.error("Failed to send decision email.")
    except Exception as e:
        st.error(f"Error: {e}")


# ── Entry Point ───────────────────────────────────────────────────────────────
if st.session_state["token"]:
    draw_sidebar()
    tab = st.session_state["active_tab"]
    
    if tab == "Home":
        page_home()
    elif tab == "Explore Jobs":
        page_explore_jobs()
    elif tab == "Analyze Candidate":
        page_analyze_candidate()
    elif tab == "My Applications":
        page_my_applications()
    elif tab == "Post Job":
        page_post_job()
    elif tab == "Manage Jobs":
        page_manage_jobs()
else:
    login_page()
