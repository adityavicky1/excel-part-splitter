import hashlib
import io
import os
import re
import zipfile
import pandas as pd
from pypdf import PdfReader, PdfWriter
import streamlit as st

st.set_page_config(
    page_title="FABTECH Industrial Supplies & Services",
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
        "admin": make_hash("steel2030"),
        "avikram": make_hash("vicky123"),
        "manager": make_hash("plant2030"),
        "ductofab": make_hash("plant2026"),
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
            "Loan EMI & Interest Analyzer",
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
            st.markdown(
                f"<p style='color: gray;'>{num_files} file(s) selected</p>",
                unsafe_allow_html=True,
            )

            if st.button("🔄 Sort A-Z"):
                uploaded_files = sorted(uploaded_files, key=lambda x: x.name)

            st.markdown("<br>", unsafe_allow_html=True)

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
        st.markdown(
            "<h2>PDF Drawing Splitter & Renamer</h2>", unsafe_allow_html=True
        )
        st.write(
            "Upload a multi-page drawing binder PDF. The app will extract each page title efficiently "
            "and package them into a download ZIP."
        )

        drawing_pdf = st.file_uploader(
            "Upload Multi-Page Drawing Binder PDF",
            type=["pdf"],
            key="drawing_splitter_uploader",
        )

        if drawing_pdf is not None:
            try:
                # Read bytes once
                pdf_bytes = drawing_pdf.read()
                reader = PdfReader(io.BytesIO(pdf_bytes), strict=False)
                num_pages = len(reader.pages)
                st.success(
                    f"Successfully loaded PDF binder with **{num_pages}** pages."
                )

                if st.button("📦 Split and Package Drawings into ZIP", type="primary"):
                    with st.spinner("Processing pages and generating ZIP..."):
                        zip_output = io.BytesIO()
                        with zipfile.ZipFile(
                            zip_output, "w", zipfile.ZIP_DEFLATED
                        ) as zf:
                            for idx, page in enumerate(reader.pages):
                                page_num = idx + 1
                                try:
                                    text = page.extract_text() or ""
                                except Exception:
                                    text = ""

                                # Fast regex check for drawing name
                                amns_pattern = r"(H\d{3}-[A-Z0-9\-/\._]+)"
                                matches = re.findall(amns_pattern, text)
                                if matches:
                                    detected_no = max(
                                        matches, key=len
                                    ).strip(".-_/")
                                else:
                                    detected_no = f"Drawing_Page_{page_num}"

                                if len(detected_no) > 60:
                                    detected_no = f"Drawing_Page_{page_num}"

                                safe_filename = "".join(
                                    c
                                    for c in detected_no
                                    if c.isalnum()
                                    or c in (" ", ".", "_", "-")
                                ).strip()
                                filename = f"{safe_filename}.pdf"

                                # Write single page directly to zip buffer to save RAM
                                writer = PdfWriter()
                                writer.add_page(page)
                                page_buffer = io.BytesIO()
                                writer.write(page_buffer)
                                zf.writestr(filename, page_buffer.getvalue())

                        zip_output.seek(0)
                        st.success("All drawings successfully split and renamed!")
                        st.download_button(
                            label="📥 Download Separated Drawings (ZIP)",
                            data=zip_output,
                            file_name="amns_separated_drawings.zip",
                            mime="application/zip",
                            use_container_width=True,
                        )
            except Exception as e:
                st.error(f"Error processing PDF binder: {e}")

    # --- EXCEL PART SPLITTER PAGE ---
    elif selected_page == "Excel Part Splitter":
        st.markdown(
            "<h2>Excel Part Splitter Automation</h2>", unsafe_allow_html=True
        )
        st.write(
            "Upload your spreadsheet containing **Mark no**, **Qty**, **Wt**, and **area**"
            " columns. All additional columns are preserved automatically."
        )

        uploaded_file = st.file_uploader(
            "Choose an Excel file",
            type=["xlsx", "xls"],
            key="part_splitter_uploader",
        )

        if uploaded_file is not None:
            try:
                df = pd.read_excel(uploaded_file)
                col_mapping = {col.strip().lower(): col for col in df.columns}
                required_cols = {"mark no", "qty", "wt", "area"}

                if not required_cols.issubset(col_mapping.keys()):
                    st.error(
                        "Invalid columns! Your file must at least contain 'Mark no', 'Qty', 'Wt', and 'area'."
                    )
                else:
                    mark_col = col_mapping["mark no"]
                    qty_col = col_mapping["qty"]
                    wt_col = col_mapping["wt"]
                    area_col = col_mapping["area"]

                    output_rows = []
                    for _, row in df.iterrows():
                        mark_no = row[mark_col]
                        total_qty = int(row[qty_col])
                        total_wt = row[wt_col]
                        total_area = row[area_col]
                        part_wt = (
                            round(total_wt / total_qty, 3)
                            if total_qty > 0
                            else 0
                        )
                        part_area = (
                            round(total_area / total_qty, 3)
                            if total_qty > 0
                            else 0
                        )

                        other_columns_data = {
                            col: row[col]
                            for col in df.columns
                            if col not in [mark_col, qty_col, wt_col, area_col]
                        }

                        for i in range(1, total_qty + 1):
                            new_row = {
                                "Mark No": mark_no,
                                "Part SlNo": f"{i}/{total_qty}",
                                "Qty": 1,
                                "Wt": part_wt,
                                "area": part_area,
                            }
                            new_row.update(other_columns_data)
                            output_rows.append(new_row)

                    output_df = pd.DataFrame(output_rows)
                    st.success(
                        "File processed successfully with all columns preserved!"
                    )
                    st.dataframe(output_df, use_container_width=True)

                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine="openpyxl") as writer:
                        output_df.to_excel(
                            writer, index=False, sheet_name="Split_Parts"
                        )
                    output.seek(0)

                    st.download_button(
                        label="📥 Download Processed Excel",
                        data=output,
                        file_name="processed_parts_output.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
            except Exception as e:
                st.error(f"Error processing file: {e}")

    # --- EXCEL SHEET COMBINER PAGE ---
    elif selected_page == "Excel Sheet Combiner":
        st.markdown("<h2>Excel Sheet Combiner</h2>", unsafe_allow_html=True)
        st.write(
            "Upload multiple Excel or CSV files to consolidate them into a single comprehensive master workbook."
        )

        combiner_files = st.file_uploader(
            "Select Excel or CSV Files to Combine",
            type=["xlsx", "xls", "csv"],
            accept_multiple_files=True,
            key="excel_combiner_uploader",
        )

        if combiner_files:
            st.info(f"{len(combiner_files)} file(s) selected successfully.")
            if st.button("Combine Spreadsheets", type="primary"):
                try:
                    all_dfs = []
                    for f in combiner_files:
                        f.seek(0)
                        if f.name.endswith(".csv"):
                            temp_df = pd.read_csv(f)
                        else:
                            temp_df = pd.read_excel(f)
                        temp_df["Source_File"] = f.name
                        all_dfs.append(temp_df)

                    master_df = pd.concat(all_dfs, ignore_index=True)
                    st.success("Spreadsheets combined successfully!")
                    st.markdown("### Combined Master Preview")
                    st.dataframe(master_df, use_container_width=True)

                    combined_buffer = io.BytesIO()
                    with pd.ExcelWriter(
                        combined_buffer, engine="openpyxl"
                    ) as writer:
                        master_df.to_excel(
                            writer, index=False, sheet_name="Master_Combined"
                        )
                    combined_buffer.seek(0)

                    st.download_button(
                        label="📥 Download Combined Master Excel",
                        data=combined_buffer,
                        file_name="combined_master_output.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"Error combining files: {e}")
        else:
            st.info("Upload two or more spreadsheet files to begin combining.")

    # --- NC FILE SORTER & EXTRACTOR PAGE ---
    elif selected_page == "NC File Sorter & Extractor":
        st.markdown(
            "<h2>NC File Sorter & Extractor</h2>", unsafe_allow_html=True
        )
        st.write(
            "Upload
