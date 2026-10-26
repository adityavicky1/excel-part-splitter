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
                        password, st.session_state.users_db[username]
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
                        st.session_state.users_db[new_user] = make_hash(new_pass)
                        st.success(
                            "Account created successfully! Please switch to 'Sign In' above."
                        )

# --- MAIN DASHBOARD (AFTER LOGIN) ---
else:
    st.markdown(
        f"""
            <div class="top-navbar">
                <span>BHARAT INDUSTRIAL &nbsp;|&nbsp; Plant Utilities Dashboard</span>
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

    # Display total user tracking in sidebar (Admin Analytics)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 System Analytics")
    st.sidebar.metric(label="Total Registered Users", value=len(st.session_state.users_db))

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    # --- EXCEL PART SPLITTER PAGE ---
    if selected_page == "Excel Part Splitter":
        st.title("📊 Excel Part Splitter")
        st.write(
            "Upload your master Bill of Materials (BOM) Excel sheet to split parts"
            " by section."
        )
        uploaded_file = st.file_uploader(
            "Upload Excel Master Sheet", type=["xlsx", "xls"]
        )
        if uploaded_file is not None:
            df = pd.read_excel(uploaded_file)
            st.success("File uploaded successfully!")
            st.dataframe(df.head())

    # --- MERGE PDF PAGE ---
    elif selected_page == "Merge PDF":
        st.title("📄 Merge PDF Utility")
        st.write("Combine multiple structural drawing PDFs into a single file.")
        pdf_files = st.file_uploader(
            "Upload PDF files", type=["pdf"], accept_multiple_files=True
        )
        if pdf_files:
            st.info(f"{len(pdf_files)} PDF files uploaded.")

    # --- NC FILE SORTER & EXTRACTOR PAGE ---
    elif selected_page == "NC File Sorter & Extractor":
        st.title("📂 NC File Sorter & Extractor")
        st.write(
            "Upload your `.nc` or `.nc1` files to parse parameters (Grade & Section)"
            " and organize them automatically into folders based on **MM Section** and **Grade**."
        )

        # --- Configuration Inputs for Indexing ---
        st.markdown("### ⚙️ Parsing Configuration")
        col_cfg1, col_cfg2 = st.columns(2)
        with col_cfg1:
            grade_line_idx = st.number_input(
                "Grade Line Number (1-based index)", min_value=1, value=5, step=1,
                help="Specify which line number in the cleaned file contains the Grade."
            ) - 1
        with col_cfg2:
            section_line_idx = st.number_input(
                "MM Section Line Number (1-based index)", min_value=1, value=7, step=1,
                help="Specify which line number in the cleaned file contains the MM Section."
            ) - 1

        nc_files = st.file_uploader(
            "Select NC Files",
            type=["nc", "nc1"],
            accept_multiple_files=True,
            key="nc_uploader",
        )

        if nc_files:
            st.info(f"{len(nc_files)} NC file(s) uploaded successfully.")

            parsed_data = []
            file_contents_map = {}

            for file in nc_files:
                try:
                    file.seek(0)
                    content_bytes = file.read()
                    file_contents_map[file.name] = content_bytes
                    lines = content_bytes.decode("utf-8", errors="ignore").splitlines()

                    cleaned_lines = [line.strip() for line in lines if line.strip()]

                    grade = "Unknown Grade"
                    section = "Unknown Section"

                    meaningful_lines = []
                    for l in cleaned_lines:
                        if l in ["ST", "AK", "BO", "EN"]:
                            continue
                        meaningful_lines.append(l)

                    if len(meaningful_lines) > max(grade_line_idx, section_line_idx):
                        grade = meaningful_lines[grade_line_idx]
                        section = meaningful_lines[section_line_idx]
                    elif len(cleaned_lines) > max(grade_line_idx, section_line_idx):
                        grade = cleaned_lines[grade_line_idx]
                        section = cleaned_lines[section_line_idx]

                    parsed_data.append({
                        "NC name": file.name,
                        "MM Section": section,
                        "Grade": grade,
                    })
                except Exception as e:
                    parsed_data.append({
                        "NC name": file.name,
                        "MM Section": "Error",
                        "Grade": str(e),
                    })

            df_nc = pd.DataFrame(parsed_data)

            st.markdown("### Extracted Attributes Preview")
            st.dataframe(df_nc, use_container_width=True)

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(
                zip_buffer, "w", zipfile.ZIP_DEFLATED
            ) as zip_file:
                for item in parsed_data:
                    filename = item["NC name"]
                    sec = item["MM Section"]
                    grd = item["Grade"]
                    folder_name = f"{sec}_{grd}"
                    file_path_in_zip = f"{folder_name}/{filename}"
                    if filename in file_contents_map:
                        zip_file.writestr(file_path_in_zip, file_contents_map[filename])

            zip_buffer.seek(0)

            col1, col2 = st.columns(2)
            with col1:
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                    df_nc.to_excel(writer, index=False, sheet_name="NC_Summary")
                excel_buffer.seek(0)

                st.download_button(
                    label="📥 Download Summary Excel",
                    data=excel_buffer,
                    file_name="nc_files_summary.xlsx",
                    mime=(
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    ),
                    use_container_width=True,
                )

            with col2:
                st.download_button(
                    label="📦 Download Sorted Folders (ZIP)",
                    data=zip_buffer,
                    file_name="sorted_nc_folders.zip",
                    mime="application/zip",
                    use_container_width=True,
                )

    # --- AUTOMATED DPR SYNTHESIZER PAGE ---
    elif selected_page == "Automated DPR Synthesizer":
        st.title("📊 Automated DPR Synthesizer")
        st.write(
            "Consolidate daily production reports (DPR), track fabrication milestones, "
            "and generate automated executive status summaries and metrics."
        )

        dpr_file = st.file_uploader(
            "Upload Daily Production Report (Excel / CSV)",
            type=["xlsx", "xls", "csv"],
            key="dpr_uploader"
        )

        if dpr_file is not None:
            try:
                if dpr_file.name.endswith('.csv'):
                    dpr_df = pd.read_csv(dpr_file)
                else:
                    dpr_df = pd.read_excel(dpr_file)

                st.success("DPR file uploaded successfully!")
                st.markdown("### 📋 Uploaded Data Preview")
                st.dataframe(dpr_df, use_container_width=True)

                st.markdown("### 📈 Synthesis & Metrics")
                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1:
                    st.metric(label="Total Records / Entries", value=len(dpr_df))
                with col_m2:
                    if 'Weight' in dpr_df.columns or 'Wt' in dpr_df.columns:
                        wt_col_name = 'Weight' if 'Weight' in dpr_df.columns else 'Wt'
                        total_weight_sum = dpr_df[wt_col_name].sum()
                        st.metric(label="Total Tonnage / Weight", value=f"{total_weight_sum:,.2f}")
                    else:
                        st.metric(label="Columns Detected", value=len(dpr_df.columns))
                with col_m3:
                    st.metric(label="Status", value="Ready for Export")

                # Export synthesized summary
                output_dpr = io.BytesIO()
                with pd.ExcelWriter(output_dpr, engine="openpyxl") as writer:
                    dpr_df.to_excel(writer, index=False, sheet_name="DPR_Synthesis")
                output_dpr.seek(0)

                st.download_button(
                    label="📥 Download Synthesized DPR Report",
                    data=output_dpr,
                    file_name="synthesized_dpr_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error processing DPR file: {e}")
        else:
            st.info("Upload a daily production spreadsheet to begin synthesis.")

    # --- SUBSCRIPTION PLANS & BILLING PAGE ---
    elif selected_page == "Subscription Plans & Billing":
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

    # --- UNDER CONSTRUCTION PAGE ---
    elif selected_page == "Under Construction":
        st.title("🚧 Under Construction")
        st.write("New automation modules are currently being developed.")
