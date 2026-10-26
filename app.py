import hashlib
import io
import os
import zipfile
import pandas as pd
from pypdf import PdfReader, PdfWriter
import streamlit as st

st.set_page_config(
    page_title="BHARAT Industrial Supplies & Services",
    page_icon="⚙️",
    layout="wide",
)


# Helper function to hash passwords securely
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_hash(password, hashed_text):
    return make_hash(password) == hashed_text


# Initialize Database of Users in Session State
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

# Custom CSS matching the clean, red top-bar enterprise interface layout
st.markdown(
    """
    <style>
    .top-navbar {
        background-color: #e62117;
        color: white;
        padding: 12px 20px;
        font-weight: bold;
        font-size: 18px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
        border-radius: 4px;
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
            <div style="text-align: center; margin-top: 20px;">
                <h1 style="color: #e62117; font-family: sans-serif; font-weight: 900; letter-spacing: 2px;">BHARAT<br><span style="font-size: 18px;">INDUSTRIAL SUPPLIES & SERVICES</span></h1>
            </div>
        """,
        unsafe_allow_html=True,
    )

    _, col2, _ = st.columns([1, 1.2, 1])

    with col2:
        auth_mode = st.radio(
            "Choose Action",
            ["Sign In", "Create New Account"],
            horizontal=True,
            label_visibility="collapsed",
        )

        if auth_mode == "Sign In":
            st.markdown(
                "<h3 style='text-align: center; color: #333;'>System Sign In</h3>",
                unsafe_allow_html=True,
            )
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button(
                    "Sign In", use_container_width=True, type
