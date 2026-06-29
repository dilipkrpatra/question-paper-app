import os
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import html


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

if "started" not in st.session_state:
    st.session_state.started = False

# Reset if sheet changes
if st.session_state.last_sheet != sheet_name:

    st.session_state.last_sheet = sheet_name
    st.session_state.visible_count = 0
    st.session_state.display_text = ""
    st.session_state.started = False
    st.rerun()



# --------------------------------------------------
# BUILD CELL LIST
# --------------------------------------------------

df = workbook[sheet_name]

cells = []

# Start from Excel Row 2
for r in range(1, len(df)):

    for c in range(2):      # A,B, only

        value = ""

        if c < df.shape[1]:

            cell = df.iat[r, c]

            if pd.notna(cell):
                value = str(cell)

        address = f"{chr(65+c)}{r+1}"

        cells.append((address, value, c))

# --------------------------------------------------
# START BUTTON
# --------------------------------------------------

if not st.session_state.started:

    if st.button("▶ Start Reading", use_container_width=True):

        st.session_state.started = True

        # Show the first cell immediately
        if len(cells) > 0:

            address, value, column = cells[0]

            text = html.escape(value.strip())

            if text:

                if column == 0:
                    html_text = f"""
<div style="
    background:white;
    border-left:6px solid #222;
    padding:12px;
    margin-bottom:8px;
    border-radius:6px;
    font-size:22px;
    font-weight:bold;
    color:#111;
    box-shadow:0 1px 3px rgba(0,0,0,.15);
">
{text}
</div>
"""
                else:
                    html_text = f"""
<div style="
    background:#eef7ff;
    border-left:6px solid #1e88e5;
    padding:10px 12px;
    margin-left:35px;
    margin-bottom:18px;
    border-radius:6px;
    font-size:20px;
    color:#004a99;
    box-shadow:0 1px 3px rgba(0,0,0,.10);
">
{text}
</div>
"""

                st.session_state.display_text = html_text

            st.session_state.visible_count = 1

        st.rerun()


# --------------------------------------------------
# DISPLAY WINDOW
# --------------------------------------------------

if st.session_state.started:
        components.html(
            f"""
            <div id="textbox"
                 style="
                    height:500px;
                    overflow-y:auto;
                    background:#f5f5f5;
                    padding:15px;
                    border:1px solid #cccccc;
                    border-radius:8px;
                    font-family:Arial;
                ">

                {st.session_state.display_text}

            </div>

            <script>
                var box = document.getElementById("textbox");
                box.scrollTop = box.scrollHeight;
            </script>
            """,
            height=530,
        )

# --------------------------------------------------
# BUTTONS
# --------------------------------------------------

if st.session_state.started:
    col1, col2 = st.columns([1,1])

    with col1:

        if st.button("Next ➜", use_container_width=True):

            if st.session_state.visible_count < len(cells):

                address, value, column = cells[
                    st.session_state.visible_count
                ]

                text = html.escape(value.strip())

                if text:

                    if column == 0:
                        html_text = f"""
                <div style="
                    background:white;
                    border-left:6px solid #222;
                    padding:12px;
                    margin-bottom:8px;
                    border-radius:6px;
                    font-size:22px;
                    font-weight:bold;
                    color:#111;
                    box-shadow:0 1px 3px rgba(0,0,0,.15);
                ">
                {text}
                </div>
                """

                    else:
                        html_text = f"""
                <div style="
                    background:#eef7ff;
                    border-left:6px solid #1e88e5;
                    padding:10px 12px;
                    margin-left:35px;
                    margin-bottom:18px;
                    border-radius:6px;
                    font-size:20px;
                    color:#004a99;
                    box-shadow:0 1px 3px rgba(0,0,0,.10);
                ">
                {text}
                </div>
                """

                    st.session_state.display_text += html_text

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

