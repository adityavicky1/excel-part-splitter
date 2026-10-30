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
                            import re
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
            "Upload your `.nc` or `.nc1` files to parse parameters (Grade & Section)"
            " and organize them automatically into folders based on **MM Section** and **Grade**."
        )

        st.markdown("### ⚙️ Parsing Configuration")
        col_cfg1, col_cfg2 = st.columns(2)
        with col_cfg1:
            grade_line_idx = (
                st.number_input(
                    "Grade Line Number (1-based index)",
                    min_value=1,
                    value=5,
                    step=1,
                    help="Specify which line number in the cleaned file contains the Grade.",
                )
                - 1
            )
        with col_cfg2:
            section_line_idx = (
                st.number_input(
                    "MM Section Line Number (1-based index)",
                    min_value=1,
                    value=7,
                    step=1,
                    help="Specify which line number in the cleaned file contains the MM Section.",
                )
                - 1
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
                    lines = (
                        content_bytes.decode("utf-8", errors="ignore")
                        .splitlines()
                    )
                    cleaned_lines = [
                        line.strip() for line in lines if line.strip()
                    ]

                    grade = "Unknown Grade"
                    section = "Unknown Section"
                    meaningful_lines = [
                        l
                        for l in cleaned_lines
                        if l not in ["ST", "AK", "BO", "EN"]
                    ]

                    if len(meaningful_lines) > max(
                        grade_line_idx, section_line_idx
                    ):
                        grade = meaningful_lines[grade_line_idx]
                        section = meaningful_lines[section_line_idx]
                    elif len(cleaned_lines) > max(
                        grade_line_idx, section_line_idx
                    ):
                        grade = cleaned_lines[grade_line_idx]
                        section = cleaned_lines[section_line_idx]

                    parsed_data.append(
                        {
                            "NC name": file.name,
                            "MM Section": section,
                            "Grade": grade,
                        }
                    )
                except Exception as e:
                    parsed_data.append(
                        {
                            "NC name": file.name,
                            "MM Section": "Error",
                            "Grade": str(e),
                        }
                    )

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
                        zip_file.writestr(
                            file_path_in_zip, file_contents_map[filename]
                        )

            zip_buffer.seek(0)

            col1, col2 = st.columns(2)
            with col1:
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                    df_nc.to_excel(
                        writer, index=False, sheet_name="NC_Summary"
                    )
                excel_buffer.seek(0)

                st.download_button(
                    label="📥 Download Summary Excel",
                    data=excel_buffer,
                    file_name="nc_files_summary.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
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

    # --- SMART FILE FINDER & EXTRACTOR PAGE ---
    elif selected_page == "Smart File Finder & Extractor":
        st.markdown(
            "<h2>Smart File Finder & Extractor</h2>", unsafe_allow_html=True
        )
        st.write(
            "Upload your criteria Excel sheet containing the required file names/numbers, "
            "then upload your source files below to automatically filter and extract them into a ZIP."
        )

        criteria_file = st.file_uploader(
            "1. Upload Excel File containing Required File List",
            type=["xlsx", "xls", "csv"],
            key="criteria_uploader",
        )

        selected_column = None
        target_search_values = []

        if criteria_file is not None:
            try:
                if criteria_file.name.endswith(".csv"):
                    criteria_df = pd.read_csv(criteria_file)
                else:
                    criteria_df = pd.read_excel(criteria_file)

                st.success("Criteria spreadsheet loaded successfully!")
                st.dataframe(criteria_df.head(), use_container_width=True)

                col_options = criteria_df.columns.tolist()
                selected_column = st.selectbox(
                    "Select Column containing File Numbers/Names to extract:",
                    col_options,
                )

                if selected_column:
                    target_search_values = (
                        criteria_df[selected_column]
                        .dropna()
                        .astype(str)
                        .str.strip()
                        .tolist()
                    )
                    st.info(
                        f"Loaded **{len(target_search_values)}** target file identifier(s) from the spreadsheet."
                    )
            except Exception as e:
                st.error(f"Error reading criteria spreadsheet: {e}")

        st.markdown("---")

        source_files = st.file_uploader(
            "2. Upload Source Files (Select all files from your folder to match against)",
            accept_multiple_files=True,
            key="source_files_uploader",
        )

        if source_files and target_search_values:
            try:
                found_files_map = {}

                for file in source_files:
                    base_name, _ = os.path.splitext(file.name)
                    for target in target_search_values:
                        if (
                            target.lower() == base_name.lower()
                            or target.lower() in file.name.lower()
                        ):
                            found_files_map[target] = file

                st.markdown("### Matching Results Summary")
                st.write(
                    f"Matched **{len(found_files_map)}** out of **{len(target_search_values)}** requested files."
                )

                if found_files_map:
                    matched_df = pd.DataFrame(
                        [
                            {
                                "Requested Identifier": k,
                                "Matched Filename": v.name,
                            }
                            for k, v in found_files_map.items()
                        ]
                    )
                    st.dataframe(matched_df, use_container_width=True)

                    if st.button(
                        "📦 Package Matched Files into ZIP", type="primary"
                    ):
                        extracted_zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(
                            extracted_zip_buffer, "w", zipfile.ZIP_DEFLATED
                        ) as zf:
                            for tgt, fobj in found_files_map.items():
                                fobj.seek(0)
                                zf.writestr(fobj.name, fobj.read())
                        extracted_zip_buffer.seek(0)

                        st.success(
                            "Requested documents packaged successfully!"
                        )
                        st.download_button(
                            label="📥 Download Extracted Files (ZIP)",
                            data=extracted_zip_buffer,
                            file_name="matched_extracted_files.zip",
                            mime="application/zip",
                            use_container_width=True,
                        )
                else:
                    st.warning(
                        "No matching files found among the uploaded source files for the identifiers provided in your Excel sheet."
                    )
            except Exception as e:
                st.error(f"Error processing files: {e}")
        elif not criteria_file:
            st.info("Please upload your criteria Excel sheet to get started.")
        elif not source_files:
            st.info("Please upload the source files to match against.")

    # --- AUTOMATED DPR SYNTHESIZER PAGE ---
    elif selected_page == "Automated DPR Synthesizer":
        st.markdown(
            "<h2>Automated DPR Synthesizer</h2>", unsafe_allow_html=True
        )
        st.write(
            "Consolidate daily production reports (DPR), track fabrication milestones, "
            "and generate automated executive status summaries."
        )

        dpr_file = st.file_uploader(
            "Upload Daily Production Report (Excel / CSV)",
            type=["xlsx", "xls", "csv"],
            key="dpr_uploader",
        )

        if dpr_file is not None:
            try:
                if dpr_file.name.endswith(".csv"):
                    dpr_df = pd.read_csv(dpr_file)
                else:
                    dpr_df = pd.read_excel(dpr_file)

                st.success("DPR file uploaded successfully!")
                st.dataframe(dpr_df, use_container_width=True)

                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1:
                    st.metric(label="Total Records", value=len(dpr_df))
                with col_m2:
                    if (
                        "Weight" in dpr_df.columns
                        or "Wt" in dpr_df.columns
                    ):
                        wt_col_name = (
                            "Weight" if "Weight" in dpr_df.columns else "Wt"
                        )
                        total_weight_sum = dpr_df[wt_col_name].sum()
                        st.metric(
                            label="Total Tonnage / Weight",
                            value=f"{total_weight_sum:,.2f}",
                        )
                    else:
                        st.metric(
                            label="Columns Detected", value=len(dpr_df.columns)
                        )
                with col_m3:
                    st.metric(label="Status", value="Ready for Export")

                output_dpr = io.BytesIO()
                with pd.ExcelWriter(output_dpr, engine="openpyxl") as writer:
                    dpr_df.to_excel(
                        writer, index=False, sheet_name="DPR_Synthesis"
                    )
                output_dpr.seek(0)

                st.download_button(
                    label="📥 Download Synthesized DPR Report",
                    data=output_dpr,
                    file_name="synthesized_dpr_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"Error processing DPR file: {e}")

    # --- UNDER CONSTRUCTION PAGE ---
    elif selected_page == "Under Construction":
        st.markdown("<h2>Under Construction</h2>", unsafe_allow_html=True)
        st.info("New automation modules are currently being developed.")
