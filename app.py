import io
import os
import zipfile
import pandas as pd
from pypdf import PdfReader, PdfWriter
import streamlit as st
import fitz   # PyMuPDF
from PIL import Image

st.set_page_config(page_title="FABTECH India", page_icon="⚙️", layout="wide")

USERS = {
    "admin": "steel2026",
    "avikram": "vicky123",
    "manager": "plant2026",
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Custom CSS for styling cards, top navbar, and sidebar
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
    .login-container {
        max-width: 500px;
        margin: 40px auto;
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .login-header {
        background-color: #ffffff;
        padding: 15px;
        text-align: center;
        font-weight: bold;
        font-size: 18px;
        border-bottom: 1px solid #e0e0e0;
        color: #333333;
    }
    .pdf-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.markdown(
        """
            <div style="text-align: center; margin-top: 20px;">
                <h1 style="color: #e62117; font-family: sans-serif; font-weight: 900; letter-spacing: 2px;">FAB TECH<br><span style="font-size: 20px;">INDIA</span></h1>
            </div>
        """,
        unsafe_allow_html=True,
    )

    _, col2, _ = st.columns([1, 1.2, 1])

    with col2:
        st.markdown(
            """
            <div class="login-container">
                <div class="login-header">System Utilities Login</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            st.markdown(
                '<p style="color: #e62117; margin-bottom: 0px;">* Username</p>',
                unsafe_allow_html=True,
            )
            username = st.text_input("UsernameInput", label_visibility="collapsed")

            st.markdown(
                '<p style="color: #e62117; margin-bottom: 0px;">* Password</p>',
                unsafe_allow_html=True,
            )
            password = st.text_input(
                "PasswordInput", type="password", label_visibility="collapsed"
            )

            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button(
                "Login", use_container_width=True, type="primary"
            )

            if submit:
                if username in USERS and USERS[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid username or password")

# --- MAIN DASHBOARD (AFTER LOGIN) ---
else:
    st.markdown(
        f"""
            <div class="top-navbar">
                <span>FAB TECH INDIA &nbsp;|&nbsp; Plant Utilities Dashboard</span>
                <span>User: {st.session_state.username}</span>
            </div>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar Menu
    st.sidebar.markdown(
        '<h2 style="font-size: 22px; color: #111; margin-bottom: 10px;">Plant'
        " Utilities</h2>",
        unsafe_allow_html=True,
    )

    selected_page = st.sidebar.radio(
        "Navigation",
        [
            "Excel Part Splitter",
            "Merge PDF",
            "NC File Sorter & Extractor",
            "Under Construction",
        ],
        label_visibility="collapsed",
    )

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    # --- MERGE PDF PAGE ---
    if selected_page == "Merge PDF":
        st.markdown(
            "<h2 style='text-align: center;'>Merge PDF</h2>", unsafe_allow_html=True
        )

        uploaded_files = st.file_uploader(
            "Select PDFs",
            type=["pdf"],
            accept_multiple_files=True,
            key="merge_uploader",
        )

        if uploaded_files:
            num_files = len(uploaded_files)
            st.markdown(
                f"<p style='text-align: center; color: gray;'>{num_files} file(s)"
                " selected</p>",
                unsafe_allow_html=True,
            )

            if st.button("🔄 Sort A-Z"):
                uploaded_files = sorted(uploaded_files, key=lambda x: x.name)

            st.markdown("<br>", unsafe_allow_html=True)

            cols = st.columns(min(len(uploaded_files), 3))
            for idx, file in enumerate(uploaded_files):
                try:
                    reader = PdfReader(file)
                    page_count = len(reader.pages)
                except Exception:
                    page_count = "?"

                with cols[idx % len(cols)]:
                    st.markdown(
                        f"""
                            <div class="pdf-card">
                                <p style="font-size: 40px; margin: 0;">📄</p>
                                <p style="font-weight: bold; margin: 5px 0 0 0; color: #333;">{file.name}</p>
                                <p style="font-size: 13px; color: gray; margin: 0;">({page_count} pages)</p>
                            </div>
                        """,
                        unsafe_allow_html=True,
                    )

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button(
                "Download Merged PDF", type="primary", use_container_width=True
            ):
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
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"Error merging files: {e}")

    # --- EXCEL PART SPLITTER PAGE ---
    elif selected_page == "Excel Part Splitter":
        st.title("⚙️ Excel Part Splitter Automation")
        st.write(
            "Upload your spreadsheet containing **Mark no**, **Qty**, and **Wt**"
            " columns. All additional columns (e.g., Drawing No, Area, rev No) are"
            " preserved automatically."
        )

        uploaded_file = st.file_uploader(
            "Choose an Excel file", type=["xlsx", "xls"]
        )

        if uploaded_file is not None:
            try:
                df = pd.read_excel(uploaded_file)

                col_mapping = {col.strip().lower(): col for col in df.columns}
                required_cols = {"mark no", "qty", "wt"}

                if not required_cols.issubset(col_mapping.keys()):
                    st.error(
                        "Invalid columns! Your file must at least contain 'Mark no',"
                        " 'Qty', and 'Wt'."
                    )
                else:
                    mark_col = col_mapping["mark no"]
                    qty_col = col_mapping["qty"]
                    wt_col = col_mapping["wt"]

                    output_rows = []
                    for _, row in df.iterrows():
                        mark_no = row[mark_col]
                        total_qty = int(row[qty_col])
                        total_wt = row[wt_col]

                        part_wt = round(total_wt / total_qty, 3) if total_qty > 0 else 0

                        other_columns_data = {
                            col: row[col]
                            for col in df.columns
                            if col not in [mark_col, qty_col, wt_col]
                        }

                        for i in range(1, total_qty + 1):
                            new_row = {
                                "Mark No": mark_no,
                                "Part SlNo": f"{i}/{total_qty}",
                                "Qty": 1,
                                "Wt": part_wt,
                            }
                            new_row.update(other_columns_data)
                            output_rows.append(new_row)

                    output_df = pd.DataFrame(output_rows)
                    st.success("File processed successfully with all columns preserved!")
                    st.dataframe(output_df)

                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine="openpyxl") as writer:
                        output_df.to_excel(writer, index=False, sheet_name="Split_Parts")
                    output.seek(0)

                    st.download_button(
                        label="📥 Download Processed Excel",
                        data=output,
                        file_name="processed_parts_output.xlsx",
                        mime=(
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        ),
                    )
            except Exception as e:
                st.error(f"Error processing file: {e}")

    # --- NC FILE SORTER & EXTRACTOR PAGE ---
    elif selected_page == "NC File Sorter & Extractor":
        st.title("📂 NC File Sorter & Extractor")
        st.write(
            "Upload your `.nc` or `.nc1` files to parse parameters (Grade & Section)"
            " and organize them automatically into folders based on **MM Section** and"
            " **Grade**."
        )

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

                    if len(meaningful_lines) >= 7:
                        grade = meaningful_lines[4]
                        section = meaningful_lines[6]
                    elif len(cleaned_lines) > 7:
                        grade = cleaned_lines[5]
                        section = cleaned_lines[7]

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

     # --- UNDER CONSTRUCTION PAGE ---
    elif selected_page == "Under Construction":
        st.title("🚧 Under Construction Module")
        st.info("This module is currently under development for advanced plant integration.")
        st.write("Additional fabrication tracking metrics and automated scheduling views will appear here shortly.")
