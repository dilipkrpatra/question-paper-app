import streamlit as st
import pandas as pd
import random
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from docx import Document
from datetime import datetime
import os

# ----------------------------
# SESSION STATE
# ----------------------------
if "generated" not in st.session_state:
    st.session_state.generated = {}
if "qa_text" not in st.session_state:
    st.session_state.qa_text = ""
if "ans_text" not in st.session_state:
    st.session_state.ans_text = ""

st.title("📘 Question Paper Generator (Mobile Ready)")

# ----------------------------
# UPLOAD EXCEL
# ----------------------------
uploaded_file = st.file_uploader("Upload Excel Question Bank", type=["xlsx", "xls"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheets = xls.sheet_names

    st.subheader("Select Topics")

    selected_sheets = st.multiselect("Choose Sheets", sheets)

    topic_counts = {}
    for sheet in selected_sheets:
        topic_counts[sheet] = st.number_input(
            f"Questions for {sheet}",
            min_value=1,
            value=5,
            step=1
        )

    # ----------------------------
    # GENERATE PAPER
    # ----------------------------
    if st.button("Generate Test Paper"):

        qa_data = {}
        qa_text = ""
        ans_text = ""

        for sheet in selected_sheets:
            df = pd.read_excel(uploaded_file, sheet_name=sheet).dropna()

            qa_pairs = list(zip(df.iloc[:, 0].astype(str), df.iloc[:, 1].astype(str)))

            count = min(topic_counts[sheet], len(qa_pairs))
            selected = random.sample(qa_pairs, count)

            qa_data[sheet] = selected

            qa_text += f"\n{sheet}\n" + "-" * 40 + "\n"
            ans_text += f"\n{sheet}\n" + "-" * 40 + "\n"

            for i, (q, a) in enumerate(selected, 1):
                qa_text += f"{i}. {q}\n"
                ans_text += f"{i}. {a}\n"

        st.session_state.generated = qa_data
        st.session_state.qa_text = qa_text
        st.session_state.ans_text = ans_text

        st.success("Paper Generated!")

    # ----------------------------
    # MANUAL SELECTION
    # ----------------------------
    if st.session_state.generated:

        st.subheader("Manual Selection (Optional)")

        manual_data = {}

        for sheet in selected_sheets:
            df = pd.read_excel(uploaded_file, sheet_name=sheet).dropna()
            qa_pairs = list(zip(df.iloc[:, 0].astype(str), df.iloc[:, 1].astype(str)))

            options = [f"{q} || {a}" for q, a in qa_pairs]

            selected = st.multiselect(f"{sheet}", options)

            if selected:
                manual_data[sheet] = [
                    tuple(item.split(" || ")) for item in selected
                ]

        if st.button("Apply Manual Selection"):
            st.session_state.generated = manual_data

            qa_text = ""
            ans_text = ""

            for sheet, items in manual_data.items():
                qa_text += f"\n{sheet}\n" + "-" * 40 + "\n"
                ans_text += f"\n{sheet}\n" + "-" * 40 + "\n"

                for i, (q, a) in enumerate(items, 1):
                    qa_text += f"{i}. {q}\n"
                    ans_text += f"{i}. {a}\n"

            st.session_state.qa_text = qa_text
            st.session_state.ans_text = ans_text

            st.success("Manual selection applied!")

    # ----------------------------
    # PREVIEW
    # ----------------------------
    st.subheader("Question Paper")
    st.text_area("Questions", st.session_state.qa_text, height=300)

    st.subheader("Answer Key")
    st.text_area("Answers", st.session_state.ans_text, height=300)

    # ----------------------------
    # SAVE FOLDER
    # ----------------------------
    SAVE_FOLDER = "TEST_PAPERS"
    os.makedirs(SAVE_FOLDER, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ----------------------------
    # SAVE PDF
    # ----------------------------
    if st.button("Download PDF (Q + A)"):

        file_path = os.path.join(SAVE_FOLDER, f"paper_{timestamp}.pdf")

        doc = SimpleDocTemplate(file_path)
        styles = getSampleStyleSheet()
        story = []

        for line in st.session_state.qa_text.split("\n"):
            story.append(Paragraph(line, styles["Normal"]))

        story.append(PageBreak())

        for line in st.session_state.ans_text.split("\n"):
            story.append(Paragraph(line, styles["Normal"]))

        doc.build(story)

        st.success("PDF saved!")
        with open(file_path, "rb") as f:
            st.download_button("Download PDF", f, file_name="question_paper.pdf")

    # ----------------------------
    # SAVE WORD
    # ----------------------------
    if st.button("Download Word"):

        file_path = os.path.join(SAVE_FOLDER, f"paper_{timestamp}.docx")

        doc = Document()

        doc.add_heading("QUESTION PAPER", 0)
        for line in st.session_state.qa_text.split("\n"):
            doc.add_paragraph(line)

        doc.add_page_break()

        doc.add_heading("ANSWER KEY", 0)
        for line in st.session_state.ans_text.split("\n"):
            doc.add_paragraph(line)

        doc.save(file_path)

        st.success("Word file saved!")
        with open(file_path, "rb") as f:
            st.download_button("Download Word", f, file_name="question_paper.docx")