import io
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Excel Part Splitter", page_icon="📊", layout="centered"
)
# --- 1. INSERT THE MULTI-USER DICTIONARY HERE (Right after config) ---
USERS = {
    "admin": "steel2026",
    "aditya": "vicky123",
    "manager": "plant2026",
    "supervisor": "fab789",
}
# Session state for login
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False

# Login Screen
if not st.session_state.logged_in:
  st.subheader("🔒 System Login")
  username = st.text_input("Username")
  password = st.text_input("Password", type="password")

 if st.button("Login"):
    # Check if username exists in dictionary and password matches
    if username in USERS and USERS[username] == password:
      st.session_state.logged_in = True
      st.session_state.username = username
      st.rerun()
    else:
      st.error("Invalid username or password")
else:
  # Dashboard Screen
  st.title("⚙️ Excel Part Splitter Automation")
  if st.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

  st.markdown(
      "Upload an Excel file containing columns: **Mark no**, **Qty**, and"
      " **Wt**."
  )

  uploaded_file = st.file_uploader(
      "Choose an Excel file", type=["xlsx", "xls"]
  )

  if uploaded_file is not None:
    try:
      df = pd.read_excel(uploaded_file)
      # Normalize column names
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

        # Download button
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
