import os
import random
from datetime import datetime

import pandas as pd
import streamlit as st

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(page_title="Test Mode", page_icon="📝", layout="wide")

# --------------------------------------------------
# CSS
# --------------------------------------------------

st.markdown(
    """
<style>

.main-title{
    text-align:center;
    font-size:42px;
    font-weight:bold;
    color:#1E3A8A;
}

.question-box{

    padding:15px;
    margin-bottom:25px;
    border-radius:10px;
    border:1px solid #cccccc;
    background:#f9f9f9;

}

.result-correct{

    background:#E8F8EC;
    border-left:6px solid green;
    padding:12px;
    margin-bottom:15px;
    border-radius:8px;

}

.result-wrong{

    background:#FDECEC;
    border-left:6px solid red;
    padding:12px;
    margin-bottom:15px;
    border-radius:8px;

}

div.stButton > button:first-child{

    background:linear-gradient(90deg,#1e3c72,#2a5298);
    color:white;
    font-size:22px;
    font-weight:bold;
    height:55px;
    border:none;
    border-radius:10px;

}

div.stButton > button:first-child:hover{

    background:linear-gradient(90deg,#2a5298,#1e3c72);

}

</style>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

defaults = {
    "test_started": False,
    "submitted": False,
    "selected_questions": [],
    "start_time": None,
    "end_time": None,
    "score": 0,
    "percentage": 0,
}

for key, value in defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value

# --------------------------------------------------
# LOAD QUESTION BANK
# --------------------------------------------------


@st.cache_data(show_spinner=False)
def load_question_bank(file_path):

    workbook = pd.read_excel(file_path, sheet_name=None, header=None, engine="openpyxl")

    bank = {}

    for sheet, df in workbook.items():

        heading = str(df.iloc[0, 0])

        df = df.iloc[1:, [0, 1]]

        df.columns = ["question", "answer"]

        df = df.dropna(subset=["question", "answer"])

        questions = list(zip(df["question"].astype(str), df["answer"].astype(str)))

        bank[sheet] = {"heading": heading, "questions": questions}

    return bank


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.markdown("<div class='main-title'>📝 Test Mode</div>", unsafe_allow_html=True)

st.divider()

# --------------------------------------------------
# SUBJECT
# --------------------------------------------------

QUESTION_BANK_FOLDER = "question_bank"

files = sorted(
    [f for f in os.listdir(QUESTION_BANK_FOLDER) if f.endswith((".xlsx", ".xls"))]
)

if not files:

    st.error("No Question Bank Found.")

    st.stop()

selected_file = st.selectbox("📂 Select Subject", files)

subject_name = os.path.splitext(selected_file)[0]

file_path = os.path.join(QUESTION_BANK_FOLDER, selected_file)

# --------------------------------------------------
# LOAD BANK
# --------------------------------------------------

with st.spinner("Loading Question Bank..."):

    bank = load_question_bank(file_path)

sheet_names = list(bank.keys())

# --------------------------------------------------
# TOPIC SELECTION
# --------------------------------------------------

st.subheader("📚 Select Topics")

topic_display = {}

for sheet in sheet_names:

    total = len(bank[sheet]["questions"])

    topic_display[f"{sheet} ({total})"] = sheet

selected_display = st.pills(
    "Choose Topics", list(topic_display.keys()), selection_mode="multi"
)

selected_topics = [topic_display[item] for item in selected_display]

# --------------------------------------------------
# QUESTION COUNT
# --------------------------------------------------

topic_counts = {}

if selected_topics:

    st.subheader("Number of Questions")

    cols = st.columns(3)

    for index, sheet in enumerate(selected_topics):

        with cols[index % 3]:

            maximum = len(bank[sheet]["questions"])

            topic_counts[sheet] = st.number_input(
                sheet,
                min_value=1,
                max_value=maximum,
                value=min(5, maximum),
                step=1,
                key=f"count_{sheet}",
            )

# --------------------------------------------------
# START TEST BUTTON
# --------------------------------------------------

if selected_topics:

    start_test = st.button("▶ START TEST", use_container_width=True)

else:

    start_test = False

# --------------------------------------------------
# GENERATE RANDOM QUESTIONS
# --------------------------------------------------

if start_test:

    selected_questions = []

    for sheet in selected_topics:

        questions = bank[sheet]["questions"]

        count = min(topic_counts[sheet], len(questions))

        chosen = random.sample(questions, count)

        for q, a in chosen:

            selected_questions.append(
                {
                    "topic": sheet,
                    "heading": bank[sheet]["heading"],
                    "question": q,
                    "answer": a,
                }
            )

    st.session_state.selected_questions = selected_questions

    st.session_state.test_started = True

    st.session_state.submitted = False

    st.session_state.start_time = datetime.now()

    st.rerun()

# ==========================================================
# TEST PAGE
# ==========================================================

if st.session_state.test_started and not st.session_state.submitted:

    st.divider()

    st.header("📝 Test Paper")

    total_questions = len(st.session_state.selected_questions)

    st.info(f"Subject : {subject_name}    |    " f"Total Questions : {total_questions}")

    st.warning(
        "Answer all the questions. " "Click 'Submit Test' after completing the test."
    )

    st.write("")

    # ------------------------------------------
    # DISPLAY ALL QUESTIONS
    # ------------------------------------------

    current_heading = ""

    for i, item in enumerate(st.session_state.selected_questions, start=1):

        if item["heading"] != current_heading:

            current_heading = item["heading"]

            st.subheader(current_heading)
            st.divider()

        st.write(f"**{i}. {item['question']}**")

        st.text_input("Your Answer", key=f"answer_{i}")

    st.write("")
    st.divider()

    # ------------------------------------------
    # SUBMIT BUTTON
    # ------------------------------------------

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        if st.button("✅ Submit Test", use_container_width=True):

            st.session_state.confirm_submit = True

            st.rerun()

# ==========================================================
# SUBMIT CONFIRMATION
# ==========================================================

if st.session_state.get("confirm_submit", False):

    st.warning(
        "Are you sure you want to submit the test?\n\n"
        "You won't be able to change your answers afterwards."
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button("✔ Yes, Submit", use_container_width=True):

            st.session_state.end_time = datetime.now()

            st.session_state.submitted = True

            st.session_state.confirm_submit = False

            st.rerun()

    with c2:

        if st.button("❌ Continue Test", use_container_width=True):

            st.session_state.confirm_submit = False

            st.rerun()

# ==========================================================
# AUTO EVALUATION
# ==========================================================

if st.session_state.submitted:

    st.divider()

    st.header("📊 Test Result")

    # ------------------------------------------
    # NORMALIZE FUNCTION
    # ------------------------------------------

    def normalize(text):

        text = str(text).strip()

        text = " ".join(text.split())

        text = text.lower()

        return text

    # ------------------------------------------
    # MARKING
    # ------------------------------------------

    total = len(st.session_state.selected_questions)

    correct = 0

    results = []

    for index, item in enumerate(st.session_state.selected_questions, start=1):

        student_answer = st.session_state.get(f"answer_{index}", "")

        correct_answer = item["answer"]

        is_correct = normalize(student_answer) == normalize(correct_answer)

        if is_correct:

            correct += 1

        results.append(
            {
                "question": item["question"],
                "student": student_answer,
                "correct": correct_answer,
                "status": is_correct,
            }
        )

    wrong = total - correct

    percentage = round(correct * 100 / total, 2)

    st.session_state.score = correct

    st.session_state.percentage = percentage

    # ------------------------------------------
    # TIME TAKEN
    # ------------------------------------------

    duration = st.session_state.end_time - st.session_state.start_time

    total_seconds = int(duration.total_seconds())

    minutes = total_seconds // 60

    seconds = total_seconds % 60

    # ------------------------------------------
    # SUMMARY
    # ------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total", total)

    c2.metric("Correct", correct)

    c3.metric("Wrong", wrong)

    c4.metric("Percentage", f"{percentage}%")

    st.success(f"⏱ Time Taken : {minutes} min {seconds} sec")

    st.divider()

    # ------------------------------------------
    # ANSWER SHEET
    # ------------------------------------------

    st.subheader("📖 Answer Sheet")

    for i, item in enumerate(results, start=1):

        if item["status"]:

            box = "result-correct"

            symbol = "✅ Correct"

        else:

            box = "result-wrong"

            symbol = "❌ Wrong"

        st.markdown(
            f"""
            <div class="{box}">

            <h4>Question {i}</h4>

            <b>Question :</b><br>
            {item["question"]}

            <br><br>

            <b>Your Answer :</b><br>
            {item["student"] if item["student"] else "<i>No Answer</i>"}

            <br><br>

            <b>Correct Answer :</b><br>
            {item["correct"]}

            <br><br>

            <b>{symbol}</b>

            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # ------------------------------------------
    # START NEW TEST
    # ------------------------------------------

    if st.button("🔄 Start New Test", use_container_width=True):

        keys = list(st.session_state.keys())

        for key in keys:

            del st.session_state[key]

        st.rerun()

