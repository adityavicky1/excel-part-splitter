import hashlib
import io
import os
import zipfile
import pandas as pd
from PIL import Image
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


# Initialize Database of Users in Session State (with 20 free default credits)
if "users_db" not in st.session_state:
    st.session_state.users_db = {
        "admin": {"password": make_hash("steel2026"), "credits": 100},
        "avikram": {"password": make_hash("vicky123"), "credits": 20},
        "manager": {"password": make_hash("plant2026"), "credits": 20},
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
                    "Sign In", use_container_width=True, type="primary"
                )

                if submit:
                    if username in st.session_state.users_db and check_hash(
                        password, st.session_state.users_db[username]["password"]
                    ):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

        else:
            st.markdown(
                "<h3 style='text-align: center; color: #333;'>Register New Account</h3>",
                unsafe_allow_html=True,
            )
            with st.form("register_form"):
                new_user = st.text_input("Choose Username")
                new_pass = st.text_input("Choose Password", type="password")
                confirm_pass = st.text_input("Confirm Password", type="password")
                reg_submit = st.form_submit_button(
                    "Register Account", use_container_width=True, type="primary"
                )

                if reg_submit:
                    if not new_user or not new_pass:
                        st.warning("Please fill in all fields.")
                    elif new_user in st.session_state.users_db:
                        st.error("Username already exists. Choose another.")
                    elif new_pass != confirm_pass:
                        st.error("Passwords do not match.")
                    else:
                        # Give new user 20 free credits upon registration
                        st.session_state.users_db[new_user] = {
                            "password": make_hash(new_pass),
                            "credits": 20
                        }
                        st.success(
                            "Account created successfully with 20 Free Credits! Please switch to 'Sign In' above."
                        )

# --- MAIN DASHBOARD (AFTER LOGIN) ---
else:
    current_user = st.session_state.username
    user_credits = st.session_state.users_db[current_user]["credits"]

    st.markdown(
        f"""
            <div class="top-navbar">
                <span>Utilities & Automation Dashboard</span>
                <span>User: {current_user} &nbsp;|&nbsp; Free Credits Left: {user_credits}</span>
            </div>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar Menu
    st.sidebar.markdown(
        '<h2 style="font-size: 20px; color: #111; margin-bottom: 5px;">Plant Utilities</h2>',
        unsafe_allow_html=True,
    )

    selected_page = st.sidebar.radio(
        "Navigation",
        [
            "PDF to Table",
            "OCR Converter",
            "PDF Page Splitter",
            "Image to PDF",
            "Subscription Plans & Billing",
        ],
        label_visibility="collapsed",
    )

    # Display user credits in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Usage & Credits")
    st.sidebar.metric(label="Available Free Checks", value=user_credits)
    if user_credits <= 5:
        st.sidebar.warning("⚠️ Low credits! Top up via billing page.")

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()


    # Helper function to check and deduct credits before running a utility
    def use_credit():
        if st.session_state.users_db[current_user]["credits"] > 0:
            st.session_state.users_db[current_user]["credits"] -= 1
            return True
        return False


    # --- 1. PDF TO TABLE ---
    if selected_page == "PDF to Table":
        st.markdown("<h2>PDF to Table Extractor</h2>", unsafe_allow_html=True)
        st.write("Extract structured table data from PDF reports into an editable Excel spreadsheet.")

        pdf_file = st.file_uploader("Upload PDF Document", type=["pdf"], key="pdf_table_uploader")

        if pdf_file is not None:
            if user_credits <= 0:
                st.error("⚠️ You have 0 credits remaining! Please top up via the 'Subscription Plans & Billing' tab.")
            else:
                if st.button("Extract Table Data (Cost: 1 Credit)", type="primary"):
                    if use_credit():
                        try:
                            reader = PdfReader(pdf_file)
                            extracted_rows = []
                            for idx, page in enumerate(reader.pages):
                                text = page.extract_text() or ""
                                lines = text.splitlines()
                                for line in lines:
                                    if line.strip():
                                        extracted_rows.append({"Page": idx + 1, "Extracted Row Text": line.strip()})

                            df_table = pd.DataFrame(extracted_rows)
                            st.success("Table data extracted successfully! (1 credit deducted)")
                            st.dataframe(df_table, use_container_width=True)

                            out_excel = io.BytesIO()
                            with pd.ExcelWriter(out_excel, engine="openpyxl") as writer:
                                df_table.to_excel(writer, index=False, sheet_name="PDF_Table")
                            out_excel.seek(0)

                            st.download_button(
                                label="📥 Download Extracted Table (Excel)",
                                data=out_excel,
                                file_name="pdf_extracted_table.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error extracting table: {e}")

    # --- 2. OCR CONVERTER ---
    elif selected_page == "OCR Converter":
        st.markdown("<h2>OCR Text Converter</h2>", unsafe_allow_html=True)
        st.write("Upload scanned documents or images to convert them into readable text format.")

        ocr_image = st.file_uploader("Upload Scanned Image / PDF Document", type=["png", "jpg", "jpeg", "pdf"], key="ocr_uploader")

        if ocr_image is not None:
            if user_credits <= 0:
                st.error("⚠️ You have 0 credits remaining! Please top up via the 'Subscription Plans & Billing' tab.")
            else:
                if st.button("Run OCR Analysis (Cost: 1 Credit)", type="primary"):
                    if use_credit():
                        st.success("OCR scanning completed! (1 credit deducted)")
                        st.text_area("Extracted OCR Text Result:", value="[Simulated OCR Output]: Scanned document text successfully recognized and parsed into clean plaintext format.", height=150)
                        st.rerun()

    # --- 3. PDF PAGE SPLITTER ---
    elif selected_page == "PDF Page Splitter":
        st.markdown("<h2>PDF Page Splitter</h2>", unsafe_allow_html=True)
        st.write("Split a multi-page PDF document into individual single-page files packaged inside a ZIP.")

        split_pdf = st.file_uploader("Upload Multi-Page PDF", type=["pdf"], key="pdf_splitter_uploader")

        if split_pdf is not None:
            if user_credits <= 0:
                st.error("⚠️ You have 0 credits remaining! Please top up via the 'Subscription Plans & Billing' tab.")
            else:
                if st.button("Split PDF Pages into ZIP (Cost: 1 Credit)", type="primary"):
                    if use_credit():
                        try:
                            reader = PdfReader(split_pdf)
                            zip_buffer = io.BytesIO()
                            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                                for idx, page in enumerate(reader.pages):
                                    writer = PdfWriter()
                                    writer.add_page(page)
                                    page_io = io.BytesIO()
                                    writer.write(page_io)
                                    page_io.seek(0)
                                    zf.writestr(f"page_{idx+1}.pdf", page_io.read())

                            zip_buffer.seek(0)
                            st.success("PDF split successfully! (1 credit deducted)")
                            st.download_button(
                                label="📥 Download Split Pages (ZIP)",
                                data=zip_buffer,
                                file_name="split_pdf_pages.zip",
                                mime="application/zip",
                                use_container_width=True
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error splitting PDF: {e}")

    # --- 4. IMAGE TO PDF ---
    elif selected_page == "Image to PDF":
        st.markdown("<h2>Image to PDF Converter</h2>", unsafe_allow_html=True)
        st.write("Upload one or multiple images (PNG, JPG) and combine them into a clean PDF document.")

        image_files = st.file_uploader("Select Image Files", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="img_to_pdf_uploader")

        if image_files:
            st.info(f"{len(image_files)} image(s) selected.")
            if user_credits <= 0:
                st.error("⚠️ You have 0 credits remaining! Please top up via the 'Subscription Plans & Billing' tab.")
            else:
                if st.button("Convert Images to PDF (Cost: 1 Credit)", type="primary"):
                    if use_credit():
                        try:
                            image_list = []
                            for img_file in image_files:
                                img = Image.open(img_file).convert("RGB")
                                image_list.append(img)

                            pdf_output = io.BytesIO()
                            if image_list:
                                image_list[0].save(pdf_output, format="PDF", save_all=True, append_images=image_list[1:])
                            pdf_output.seek(0)

                            st.success("Images converted to PDF successfully! (1 credit deducted)")
                            st.download_button(
                                label="📥 Download Converted PDF",
                                data=pdf_output,
                                file_name="converted_images.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error converting images: {e}")

    # --- 5. SUBSCRIPTION PLANS & BILLING (Razorpay Integration) ---
    elif selected_page == "Subscription Plans & Billing":
        st.markdown("<h2>Subscription Plans & Credit Top-Up</h2>", unsafe_allow_html=True)
        st.write("Top up your checks or upgrade your account tier using secure Razorpay payment links.")

        col_p1, col_p2, col_p3 = st.columns(3)

        with col_p1:
            st.markdown(
                """
                <div class="pricing-card">
                    <h3>Starter Top-Up</h3>
                    <h2 style="color: #e62117;">₹199</h2>
                    <p>+50 Additional Credits<br>Standard Utilities Access<br>Email Support</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("<br>", unsafe_allow_html=True)
            # Replace with your actual Razorpay payment link
            st.markdown('<a href="https://rzp.io/l/your-razorpay-link" target="_blank"><button style="background-color:#e62117; color:white; border:none; padding:10px 20px; border-radius:4px; width:100%; font-weight:bold; cursor:pointer;">Pay via Razorpay</button></a>', unsafe_allow_html=True)

        with col_p2:
            st.markdown(
                """
                <div class="pricing-card" style="border: 2px solid #e62117;">
                    <h3>Professional Pack</h3>
                    <h2 style="color: #e62117;">₹499</h2>
                    <p>+200 Additional Credits<br>Priority Processing<br>Advanced OCR & Splitter</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<a href="https://rzp.io/l/your-razorpay-link" target="_blank"><button style="background-color:#e62117; color:white; border:none; padding:10px 20px; border-radius:4px; width:100%; font-weight:bold; cursor:pointer;">Pay via Razorpay</button></a>', unsafe_allow_html=True)

        with col_p3:
            st.markdown(
                """
                <div class="pricing-card">
                    <h3>Enterprise Unlimited</h3>
                    <h2 style="color: #e62117;">₹2,499 / mo</h2>
                    <p>Unlimited Checks & Exports<br>Dedicated Account Manager<br>API Access</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<a href="https://rzp.io/l/your-razorpay-link" target="_blank"><button style="background-color:#e62117; color:white; border:none; padding:10px 20px; border-radius:4px; width:100%; font-weight:bold; cursor:pointer;">Pay via Razorpay</button></a>', unsafe_allow_html=True)
