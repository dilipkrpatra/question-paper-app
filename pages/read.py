import os
import html

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(page_title="Learn Yourself", page_icon="📄", layout="wide")


# --------------------------------------------------
# LOAD WORKBOOK
# --------------------------------------------------


@st.cache_data(show_spinner=False)
def load_workbook(file_path):

    return pd.read_excel(file_path, sheet_name=None, header=None, engine="openpyxl")


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

defaults = {
    "display_text": "",
    "visible_count": 0,
    "started": False,
    "last_file": "",
    "last_sheet": "",
}

for key, value in defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value


# --------------------------------------------------
# HELPER : CREATE HTML CARD
# --------------------------------------------------


def create_card(text, column):

    text = html.escape(text.strip())

    if not text:
        return ""

    # ---------------- Question ----------------

    if column == 0:

        return f"""
<div style="
background:white;
border-left:4px solid #222;
padding:10px;
margin-bottom:4px;
border-radius:4px;
font-size:16px;
font-weight:bold;
color:#111;
box-shadow:0 1px 3px rgba(0,0,0,.15);
">
{text}
</div>
"""

    # ---------------- Answer ----------------

    return f"""
<div style="
background:#eef7ff;
border-left:4px solid #1e88e5;
padding:8px 10px;
margin-left:35px;
margin-bottom:10px;
border-radius:4px;
font-size:16px;
font-weight:bold;
color:#004a99;
box-shadow:0 1px 3px rgba(0,0,0,.10);
">
{text}
</div>
"""


# --------------------------------------------------
# HELPER : ADD NEXT CELL
# --------------------------------------------------


def add_next_cell(cells):

    if st.session_state.visible_count >= len(cells):
        return

    _, value, column = cells[st.session_state.visible_count]

    card = create_card(value, column)

    if card:

        st.session_state.display_text += card

    st.session_state.visible_count += 1


# =====================================================
# SUBJECT SELECTION
# =====================================================

st.title("📄 Learn Yourself")

QUESTION_BANK_FOLDER = "question_bank"

files = sorted(
    [f for f in os.listdir(QUESTION_BANK_FOLDER) if f.endswith((".xlsx", ".xls"))]
)

if not files:
    st.error("No Excel files found in 'question_bank' folder.")
    st.stop()

selected_file = st.selectbox("📂 Select Subject", files)

file_path = os.path.join(QUESTION_BANK_FOLDER, selected_file)

subject_name = os.path.splitext(selected_file)[0]


# =====================================================
# LOAD WORKBOOK
# =====================================================

with st.spinner("Loading Workbook..."):

    workbook = load_workbook(file_path)


# =====================================================
# TOPIC SELECTION
# =====================================================

st.subheader("📚 Select Topic")

topic_display = {}

for sheet, df in workbook.items():

    # Count non-empty questions in Column A
    total = 0

    if df.shape[1] > 0:

        total = df.iloc[1:, 0].notna().sum()

    topic_display[f"{sheet} ({total})"] = sheet


selected_display = st.pills(
    "Choose Topic", list(topic_display.keys()), selection_mode="single"
)

if not selected_display:
    st.stop()

sheet_name = topic_display[selected_display]

# =====================================================
# RESET IF SUBJECT / TOPIC CHANGES
# =====================================================

if (
    st.session_state.last_file != selected_file
    or st.session_state.last_sheet != sheet_name
):

    st.session_state.last_file = selected_file
    st.session_state.last_sheet = sheet_name

    st.session_state.display_text = ""
    st.session_state.visible_count = 0
    st.session_state.started = False


# =====================================================
# BUILD CELL LIST
# =====================================================

df = workbook[sheet_name]

cells = []

# Skip heading row (Excel Row 1)
# for r in range(1, len(df)):
# Start reading from heading
for r in range(0, len(df)):

    for c in range(2):

        value = ""

        if c < df.shape[1]:

            cell = df.iat[r, c]

            if pd.notna(cell):

                value = str(cell).strip()

        cells.append((f"{chr(65+c)}{r+1}", value, c))

# =====================================================
# START READING
# =====================================================

if not st.session_state.started:

    if st.button("▶ Start Reading", use_container_width=True):

        st.session_state.started = True

        # Show the first item immediately
        add_next_cell(cells)

        st.rerun()


# =====================================================
# DISPLAY WINDOW
# =====================================================

if st.session_state.started:

    components.html(
        f"""
<div id="textbox"
style="
height:520px;
overflow-y:auto;
background:#f5f5f5;
padding:15px;
border:1px solid #cccccc;
border-radius:8px;
font-family:Arial;
line-height:1.5;
">

{st.session_state.display_text}

</div>

<script>

var box=document.getElementById("textbox");
box.scrollTop=box.scrollHeight;

</script>

""",
        height=540,
    )


# =====================================================
# CONTROL BUTTONS
# =====================================================

if st.session_state.started:

    col1, col2, col3 = st.columns(3)

    # ---------------- NEXT ----------------

    with col1:

        next_disabled = st.session_state.visible_count >= len(cells)

        if st.button("Next ➜", use_container_width=True, disabled=next_disabled):

            add_next_cell(cells)
            st.rerun()

    # ---------------- SHOW ALL ----------------

    with col2:

        show_all_disabled = st.session_state.visible_count >= len(cells)

        if st.button(
            "📖 Show All", use_container_width=True, disabled=show_all_disabled
        ):

            while st.session_state.visible_count < len(cells):

                add_next_cell(cells)

            st.rerun()

    # ---------------- CLEAR ----------------

    with col3:

        if st.button("Clear", use_container_width=True):

            st.session_state.display_text = ""
            st.session_state.visible_count = 0
            st.session_state.started = False

            st.rerun()


# =====================================================
# PROGRESS
# =====================================================

if st.session_state.started:

    st.progress(st.session_state.visible_count / max(len(cells), 1))

    st.caption(f"Items Read : {st.session_state.visible_count} / {len(cells)}")


# =====================================================
# FINISHED
# =====================================================

if st.session_state.started and st.session_state.visible_count >= len(cells):

    st.success("✅ Finished reading all cells.")

