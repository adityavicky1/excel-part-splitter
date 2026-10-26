import io
import os
import zipfile
import hashlib
import pandas as pd
from pypdf import PdfReader, PdfWriter
import streamlit as st

st.set_page_config(page_title="Bhartiya Industrial Supplies & Services", page_icon="⚙️", layout="wide")

# Helper function to hash passwords securely
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hash(password, hashed_text):
    return make_hash(password) == hashed_text

# Initialize Database of Users in Session State (Pre-populated with default users)
if "users_db" not in st.session_state:
    st.session_state.users_db = {
        "admin": make_hash("steel2026"),
        "avikram": make_hash("vicky123"),
        "manager": make_hash("plant2026"),
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Custom CSS for styling cards and layout
st.markdown(
    """
    <style>
    .top-navbar {
        background-color: #e62117;
        color: white;
        padding: 10px 20px;
        font-weight: bold;
        font-size: 18px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        border-radius: 4px;
    }
    .auth-container {
        max-width: 450px;
        margin: 20px auto;
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .pricing-card {
        background: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- AUTHENTICATION & REGISTRATION SCREEN ---
if not st.session_state.logged_in:
    st.markdown(
        """
            <div style="text-align: center; margin-top: 10px;">
                <h1 style="color: #e62117; font-family: sans-serif; font-weight: 900; letter-spacing: 2px;">BHARTIYA<br><span style="font-size: 18px;">INDUSTRIAL SUPPLIES & SERVICES</span></h1>
            </div>
        """,
        unsafe_allow_html=True,
    )

    _, col2, _ = st.columns([1, 1.2, 1])

    with col2:
        auth_mode = st.radio("Choose Action", ["Sign In", "Create New Account"], horizontal=True, label_visibility="collapsed")
        
        if auth_mode == "Sign In":
            st.markdown("<h3 style='text-align: center; color: #333;'>System Sign In</h3>", unsafe_allow_html=True)
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")

                if submit:
                    if username in st.session_state.users_db and check_hash(password, st.session_state.users_db[username]):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
        
        else:
            st.markdown("<h3 style='text-align: center; color: #333;'>Register New Account</h3>", unsafe_allow_html=True)
            with st.form("register_form"):
                new_user = st.text_input("Choose Username")
                new_pass = st.text_input("Choose Password", type="password")
                confirm_pass = st.text_input("Confirm Password", type="password")
                reg_submit = st.form_submit_button("Register Account", use_container_width=True, type="primary")

                if reg_submit:
                    if not new_user or not new_pass:
                        st.warning("Please fill in all fields.")
                    elif new_user in st.session_state.users_db:
                        st.error("Username already exists. Choose another.")
                    elif new_pass != confirm_pass:
                        st.error("Passwords do not match.")
                    else:
                        st.session_state.users_db[new_user] = make_hash(new_pass)
                        st.success("Account created successfully! Please switch to 'Sign In' above.")

# --- MAIN DASHBOARD (AFTER LOGIN) ---
else:
    st.markdown(
        f"""
            <div class="top-navbar">
                <span>BHARTIYA INDUSTRIAL &nbsp;|&nbsp; Plant Utilities Dashboard</span>
                <span>User: {st.session_state.username}</span>
            </div>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar Menu
    st.sidebar.markdown(
        '<h2 style="font-size: 22px; color: #111; margin-bottom: 10px;">Plant Utilities</h2>',
        unsafe_allow_html=True,
    )

    selected_page = st.sidebar.radio(
        "Navigation",
        [
            "Excel Part Splitter",
            "Merge PDF",
            "NC File Sorter & Extractor",
            "Automated DPR Synthesizer",
            "Subscription Plans & Billing",
            "Under Construction",
        ],
        label_visibility="collapsed",
    )

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    # --- SUBSCRIPTION PLANS & PAYMENT PAGE ---
    if selected_page == "Subscription Plans & Billing":
        st.title("💳 Subscription Plans & Payment Gateway")
        st.write("Upgrade your account tier to unlock advanced automation modules, bulk processing limits, and dedicated support.")

        col_p1, col_p2, col_p3 = st.columns(3)

        with col_p1:
            st.markdown(
                """
                <div class="pricing-card">
                    <h3>Basic Tier</h3>
                    <h2 style="color: #e62117;">₹999 / mo</h2>
                    <p>Standard Utilities<br>Single-file processing<br>Email Support</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("<br>", unsafe_allow_html=True)
            # Insert your Razorpay / Stripe / UPI Payment Link here
            st.markdown('<a href="https://rzp.io/l/your-basic-plan-link" target="_blank"><button style="background-color:#e62117; color:white; border:none; padding:10px 20px; border-radius:4px; width:100%; font-weight:bold; cursor:pointer;">Pay for Basic</button></a>', unsafe_allow_html=True)

        with col_p2:
            st.markdown(
                """
                <div class="pricing-card" style="border: 2px solid #e62117;">
                    <h3>Professional</h3>
                    <h2 style="color: #e62117;">₹2,499 / mo</h2>
                    <p>Advanced DPR & NC Sorter<br>Batch Processing (Unlimited)<br>Priority Support</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<a href="https://rzp.io/l/your-pro-plan-link" target="_blank"><button style="background-color:#e62117; color:white; border:none; padding:10px 20px; border-radius:4px; width:100%; font-weight:bold; cursor:pointer;">Pay for Professional</button></a>', unsafe_allow_html=True)

        with col_p3:
            st.markdown(
                """
                <div class="pricing-card">
                    <h3>Enterprise Plant</h3>
                    <h2 style="color: #e62117;">₹6,999 / mo</h2>
                    <p>Custom Multi-Plant Integration<br>Dedicated Account Manager<br>API Access</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<a href="https://rzp.io/l/your-enterprise-link" target="_blank"><button style="background-color:#e62117; color:white; border:none; padding:10px 20px; border-radius:4px; width:100%; font-weight:bold; cursor:pointer;">Contact / Pay Enterprise</button></a>', unsafe_allow_html=True)

    # (Other existing pages like Excel Part Splitter, Merge PDF, NC Sorter, DPR Synthesizer follow here...)
