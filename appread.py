import os
import pandas as pd
import streamlit as st

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Excel Cell Reader",
    page_icon="📄",
    layout="wide"
)


# --------------------------------------------------
# LOAD WORKBOOK
# --------------------------------------------------

@st.cache_data(show_spinner=False)
def load_workbook(file_path):

    return pd.read_excel(
        file_path,
        sheet_name=None,
        header=None,
        engine="openpyxl"
    )

# --------------------------------------------------
# FILE SELECTION
# --------------------------------------------------

QUESTION_BANK_FOLDER = "question_bank"

files = sorted([
    f for f in os.listdir(QUESTION_BANK_FOLDER)
    if f.endswith((".xlsx", ".xls"))
])

if not files:
    st.error("No Excel files found.")
    st.stop()

selected_file = st.selectbox(
    "📂 Select Excel File",
    files
)

file_path = os.path.join(
    QUESTION_BANK_FOLDER,
    selected_file
)

workbook = load_workbook(file_path)

# --------------------------------------------------
# SHEET SELECTION
# --------------------------------------------------

sheet_name = st.selectbox(
    "📑 Select Sheet",
    list(workbook.keys())
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "display_text" not in st.session_state:
    st.session_state.display_text = ""

if "visible_count" not in st.session_state:
    st.session_state.visible_count = 0

if "last_sheet" not in st.session_state:
    st.session_state.last_sheet = sheet_name

# Reset if sheet changes
if st.session_state.last_sheet != sheet_name:

    st.session_state.last_sheet = sheet_name
    st.session_state.visible_count = 0
    st.session_state.display_text = ""
    st.rerun()

# --------------------------------------------------
# BUILD CELL LIST
# --------------------------------------------------

df = workbook[sheet_name]

cells = []

# Start from Excel Row 2
for r in range(1, len(df)):

    for c in range(2):      # A,B,C only

        value = ""

        if c < df.shape[1]:

            cell = df.iat[r, c]

            if pd.notna(cell):
                value = str(cell)

        address = f"{chr(65+c)}{r+1}"

        #cells.append((address, value))
        cells.append((address, value))

# --------------------------------------------------
# DISPLAY WINDOW
# --------------------------------------------------

st.markdown(
    f"""
<div style="
    white-space: pre-wrap;
    word-wrap: break-word;
    border:1px solid #ccc;
    padding:10px;
    height:500px;
    overflow-y:auto;
    background:white;
    color:black;
    font-size:20px;
">
{st.session_state.display_text}
</div>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------
# BUTTONS
# --------------------------------------------------

col1, col2 = st.columns([1,1])

with col1:

    if st.button("Next ➜", use_container_width=True):

        if st.session_state.visible_count < len(cells):

            address, value = cells[
                st.session_state.visible_count
            ]

            st.session_state.display_text += f"{value.strip()}\n\n"

            st.session_state.visible_count += 1

            st.rerun()

with col2:

    if st.button("Clear", use_container_width=True):

        st.session_state.display_text = ""
        st.session_state.visible_count = 0
        st.rerun()

# --------------------------------------------------
# FINISHED
# --------------------------------------------------

if st.session_state.visible_count >= len(cells):

    st.success("✅ Finished reading all cells.")