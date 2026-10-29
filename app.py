import hashlib
import io
import os
import zipfile
import pandas as pd
from pypdf import PdfReader, PdfWriter
import streamlit as st
from google import genai

st.set_page_config(
    page_title="FABTECH Industrial Supplies & Services",
    page_icon="⚙️",
    layout="wide",
)

# Initialize Gemini Client (reads key securely from Streamlit Secrets or environment variable)
def get_gemini_client():
    try:
        api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
        if api_key:
            return genai.Client(api_key=api_key)
    except Exception:
        pass
    return None

# Helper function to hash passwords securely
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hash(password, hashed_text):
    return make_hash(password) == hashed_text

# Initialize Database of Users in Session State
if "users_db" not in st.session_state:
    st.session_state.users_db = {
        "admin": make_hash("steel2030"),
        "avikram": make_hash("vicky123"),
        "manager": make_hash("plant2030"),
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Custom CSS matching the clean enterprise layout
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
    </style>
    """,
    unsafe_allow_html=True,
)

# --- AUTHENTICATION SCREEN ---
if not st.session_state.logged_in:
    st.markdown(
        """
            <div style="text-align: center; margin-top: 20px;">
                <h1 style="color: #e62117; font-family: sans-serif; font-weight: 900; letter-spacing: 2px;">FABTECH<br><span style="font-size: 18px;">INDUSTRIAL SUPPLIES & SERVICES</span></h1>
           </div>
        """,
        unsafe_allow_html=True,
    )

    _, col2, _ = st.columns([1, 1.2, 1])

    with col2:
        st.markdown("<h3 style='text-align: center; color: #333;'>System Sign In</h3>", unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button(
                "Sign In", use_container_width=True, type="primary"
            )

            if submit:
                if username in st.session_state.users_db and check_hash(
                    password, st.session_state.users_db[username]
                ):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

# --- MAIN DASHBOARD (AFTER LOGIN) ---
else:
    st.markdown(
        f"""
            <div class="top-navbar">
                <span>Utilities & Automation Dashboard</span>
                <span>User: {st.session_state.username}</span>
           </div>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar Menu
    st.sidebar.markdown(
        '<h2 style="font-size: 20px; color: #111; margin-bottom: 5px;">Utilities</h2>',
        unsafe_allow_html=True,
    )

    selected_page = st.sidebar.radio(
        "Navigation",
        [
            "Merge PDF",
            "PDF Drawing Splitter & Renamer",
            "Excel Part Splitter",
            "Excel Sheet Combiner",
            "NC File Sorter & Extractor",
            "Smart File Finder & Extractor",
            "Automated DPR Synthesizer",
            "AI Assistant",  # <--- Added AI Search / Assistant Page
            "Under Construction",
        ],
        label_visibility="collapsed",
    )

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    # --- MERGE PDF PAGE ---
    if selected_page == "Merge PDF":
        st.markdown("<h2>Merge PDF</h2>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Select PDFs",
            type=["pdf"],
            accept_multiple_files=True,
            key="merge_uploader",
        )

        if uploaded_files:
            num_files = len(uploaded_files)
            st.markdown(f"<p style='color: gray;'>{num_files} file(s) selected</p>", unsafe_allow_html=True)

            if st.button("🔄 Sort A-Z"):
                uploaded_files = sorted(uploaded_files, key=lambda x: x.name)

            if st.button("Download Merged PDF", type="primary"):
                try:
                    merger = PdfWriter()
                    for file in uploaded_files:
                        file.seek(0)
                        merger.append(file)

                    output_buffer = io.BytesIO()
                    merger.write(output_buffer)
                    merger.close()
                    output_buffer.seek(0)

                    st.success("PDFs merged successfully!")
                    st.download_button(
                        label="📥 Click here to download your Merged PDF",
                        data=output_buffer,
                        file_name="merged_output.pdf",
                        mime="application/pdf",
                    )
                except Exception as e:
                    st.error(f"Error merging files: {e}")

    # --- PDF DRAWING SPLITTER & RENAMER PAGE ---
    elif selected_page == "PDF Drawing Splitter & Renamer":
        st.markdown("<h2>PDF Drawing Splitter & Renamer</h2>", unsafe_allow_html=True)
        st.write("Upload a multi-page drawing binder PDF to auto-detect drawing numbers and split them.")
        
        drawing_pdf = st.file_uploader("Upload Multi-Page Drawing Binder PDF", type=["pdf"], key="drawing_splitter_uploader")
        
        if drawing_pdf is not None:
            try:
                reader = PdfReader(drawing_pdf, strict=False)
                st.success(f"Successfully loaded PDF binder with **{len(reader.pages)}** pages.")
            except Exception as e:
                st.error(f"Error loading PDF: {e}")

    # --- AI ASSISTANT PAGE ---
    elif selected_page == "AI Assistant":
        st.markdown("<h2>🤖 AI Assistant & Search</h2>", unsafe_allow_html=True)
        st.write("Ask technical questions, generate summaries, or search information using Gemini AI.")

        client = get_gemini_client()

        if not client:
            st.warning("⚠️ Gemini API Key not found. Please add your `GEMINI_API_KEY` to your Streamlit secrets (`.streamlit/secrets.toml`) or environment variables.")
        else:
            # Initialize chat history in session state
            if "ai_messages" not in st.session_state:
                st.session_state.ai_messages = [
                    {"role": "model", "text": "Hello! I am your industrial automation and engineering AI assistant. How can I help you today?"}
                ]

            # Display prior messages
            for message in st.session_state.ai_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["text"])

            # Chat input box at the bottom
            if prompt := st.chat_input("Ask a question about engineering data, standards, or formulas..."):
                st.session_state.ai_messages.append({"role": "user", "text": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("model"):
                    with st.spinner("Thinking..."):
                        try:
                            # Generate response using gemini-2.5-flash
                            response = client.models.generate_content(
                                model="gemini-2.5-flash",
                                contents=prompt,
                            )
                            ai_reply = response.text
                            st.markdown(ai_reply)
                            st.session_state.ai_messages.append({"role": "model", "text": ai_reply})
                        except Exception as e:
                            error_msg = f"Error generating response: {e}"
                            st.error(error_msg)

    # --- OTHER PAGES PLACEHOLDERS ---
    elif selected_page in ["Excel Part Splitter", "Excel Sheet Combiner", "NC File Sorter & Extractor", "Smart File Finder & Extractor", "Automated DPR Synthesizer", "Under Construction"]:
        st.markdown(f"<h2>{selected_page}</h2>", unsafe_allow_html=True)
        st.info(f"Module '{selected_page}' is loaded and ready.")
