import io
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="AM/NS India - Utilities", page_icon="⚙️", layout="wide"
)

USERS = {
    "admin": "steel2026",
    "avikram": "vicky123",
    "manager": "plant2026",
}

if "logged_in" not in st.session_state:
  st.session_state.logged_in = False

# Custom CSS for top navbar, custom sidebar styling, and clean active states
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
    /* Style Streamlit radio buttons in sidebar to match clean list look */
    [data-testid="stSidebar"] .row-widget.stRadio div[role="radiogroup"] {
        gap: 0px;
    }
    [data-testid="stSidebar"] .row-widget.stRadio label {
        padding: 10px 15px;
        border-radius: 4px;
        margin-bottom: 2px;
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
            <h1 style="color: #e62117; font-family: sans-serif; font-weight: 900; letter-spacing: 2px;">AM/NS<br><span style="font-size: 20px;">INDIA</span></h1>
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
  # Top Header Bar matching your layout
  st.markdown(
      f"""
        <div class="top-navbar">
            <span>AM/NS INDIA &nbsp;|&nbsp; Plant Utilities Dashboard</span>
            <span>User: {st.session_state.username}</span>
        </div>
    """,
      unsafe_allow_html=True,
  )

  # Sidebar Menu styled with section header like your reference image
  st.sidebar.markdown(
      '<h2 style="font-size: 22px; color: #111; margin-bottom: 10px;">PDF'
      " Application</h2>",
      unsafe_allow_html=True,
  )

  selected_page = st.sidebar.radio(
      "Navigation",
      [
          "Excel Part Splitter"
          "Merge PDF",
          "Rearrange PDF",
          "Image to PDF",
          "Resize PDF",
          "Remove PDF Pages",
          "PDF to Text - Machine generated",
          "PDF to Text - Scanned",
          "Annotate/Redact PDF",
          "Compress - Machine generated",
          "Compress - Scanned",
          "Rotate PDF",
          "Bookmark PDF",
          "Apply OCR",
      ],
      label_visibility="collapsed",
  )

  st.sidebar.markdown("---")
  if st.sidebar.button("Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

  # --- PAGE: EXCEL PART SPLITTER ---
  if selected_page == "Excel Part Splitter":
    st.title("⚙️ Excel Part Splitter Automation")
    st.write(
        "Upload your layout spreadsheet containing **Mark no**, **Qty**, and"
        " **Wt** columns to generate individual part serial numbers."
    )

    uploaded_file = st.file_uploader(
        "Choose an Excel file", type=["xlsx", "xls"]
    )

    if uploaded_file is not None:
      try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip().str.lower()

        if not {"mark no", "qty", "wt"}.issubset(df.columns):
          st.error(
              "Invalid columns! Expected 'Mark no', 'Qty', and 'Wt' in your"
              " file."
          )
        else:
          output_rows = []
          for _, row in df.iterrows():
            mark_no = row["mark no"]
            total_qty = int(row["qty"])
            total_wt = row["wt"]
            part_wt = round(total_wt / total_qty, 3) if total_qty > 0 else 0

            for i in range(1, total_qty + 1):
              output_rows.append({
                  "Mark No": mark_no,
                  "Part SlNo": f"{i}/{total_qty}",
                  "Qty": 1,
                  "Wt": part_wt,
              })

          output_df = pd.DataFrame(output_rows)
          st.success("File processed successfully!")
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

  # --- OTHER PAGES (PLACEHOLDERS) ---
  else:
    st.title(f"📄 {selected_page}")
    st.write(f"Workspace for **{selected_page}** utility form.")
    st.file_uploader("Upload document for processing", type=["pdf"])
    st.button(f"Process {selected_page}", type="primary")
