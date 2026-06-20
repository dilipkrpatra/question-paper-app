import streamlit as st
import pandas as pd
import random
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from docx import Document
from datetime import datetime
import os
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
from datetime import datetime
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle

st.write(st.__version__)

pdfmetrics.registerFont(
    TTFont(
        'Bengali',
        'fonts/NotoSansBengali-Regular.ttf'
    )
)

pdfmetrics.registerFont(
    TTFont(
        'Bengali2',
        'fonts/solaimanlipi_22-02-2012.ttf'
    )
)

# ----------------------------
# SESSION STATE
# ----------------------------
if "generated" not in st.session_state:
    st.session_state.generated = {}
if "qa_text" not in st.session_state:
    st.session_state.qa_text = ""
if "ans_text" not in st.session_state:
    st.session_state.ans_text = ""
if "qa_ans_text" not in st.session_state:
    st.session_state.qa_ans_text = ""

st.title("📘 Test Paper Generator")

# ----------------------------
# UPLOAD EXCEL
# ----------------------------
FOLDER = "question_bank"

files = [f for f in os.listdir(FOLDER) if f.endswith((".xlsx", ".xls"))]

selected_file = st.selectbox("📂 Select Subject", files)

uploaded_file = None
file_path = None

if selected_file:
    file_path = os.path.join(FOLDER, selected_file)
    uploaded_file = file_path

    st.success(f"Selected: {selected_file}")

if uploaded_file:
    xls = pd.ExcelFile(file_path)
    sheets = xls.sheet_names

    st.subheader("Select Topics")

    # Dropdown List
    #selected_sheets = st.multiselect("Choose Sheets", sheets)
    
    selected_sheets = st.pills(
        "Select Topics",
        sheets,
        selection_mode="multi"
    )

    topic_counts = {}
    for sheet in selected_sheets:
        topic_counts[sheet] = st.number_input(
            f"Questions for {sheet}",
            min_value=1,
            value=5,
            step=1
        )


    def create_pdf(header, text):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer)

        styles = getSampleStyleSheet()

        bengali_style = ParagraphStyle(
            "BengaliStyle",
            parent=styles["Normal"],
            fontName="Bengali2",
            fontSize=11,
            leading=16
        )

        # 🎯 Custom header style
        header_style = ParagraphStyle(
            name="Header",
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=12,
            leading=20
        )

        story = []

        # ---------------- HEADER ----------------
        story.append(Paragraph(header, header_style))
        story.append(Spacer(1, 10))

        subject = os.path.splitext(selected_file)[0]
        story.insert(1, Paragraph(f"Subject: {subject}", styles["Normal"]))

        today = datetime.now().strftime("%d-%m-%Y")
        story.insert(2, Paragraph(f"Date: {today}", styles["Normal"]))

        # ---------------- CONTENT ----------------
        for line in text.split("\n"):
            if line.strip():
                story.append(Paragraph(line, bengali_style))
                story.append(Spacer(1, 6))
            else:
                story.append(Spacer(1, 10))

        doc.build(story)
        buffer.seek(0)
        return buffer

    st.markdown("""
    <style>
    
    div.stButton > button:first-child {
        background: linear-gradient(90deg,#1e3c72,#2a5298);
        color:white;
        font-size:22px;
        font-weight:bold;
        border-radius:15px;
        height:60px;
        border:none;
        box-shadow:0 4px 10px rgba(0,0,0,0.25);
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(90deg,#2a5298,#1e3c72);
    }
    
   
    </style>
    """, unsafe_allow_html=True)


    if selected_sheets:

        col1, col2 = st.columns(2)

        with col1:
            auto_generate = st.button(
                "⚡ GENERATE QUESTIONS (AUTO)",
                use_container_width=True
            )

        with col2:
            manual_select = st.button(
                "✏  MANUAL SELECTION..",
                use_container_width=True
            )

        if auto_generate:
        # ----------------------------
        # GENERATE PAPER
        # ----------------------------
            qa_data = {}
            qa_text = ""
            ans_text = ""
            qa_ans_text = ""

            for sheet in selected_sheets:
                df = pd.read_excel(file_path, sheet_name=sheet).dropna()

                qa_pairs = list(zip(df.iloc[:, 0].astype(str), df.iloc[:, 1].astype(str)))

                count = min(topic_counts[sheet], len(qa_pairs))
                selected = random.sample(qa_pairs, count)

                qa_data[sheet] = selected

                qa_text += f"\n{sheet}\n" + "-" * 40 + "\n"
                ans_text += f"\n{sheet}\n" + "-" * 40 + "\n"
                qa_ans_text += f"\n{sheet}\n" + "-" * 40 + "\n"

                for i, (q, a) in enumerate(selected, 1):
                    qa_text += f"{i}. {q}\n"
                    ans_text += f"{i}. {a}\n"
                    qa_ans_text += f"{i}. {q} || {a}\n"

            st.session_state.generated = qa_data
            st.session_state.qa_text = qa_text
            st.session_state.ans_text = ans_text
            st.session_state.qa_ans_text = qa_ans_text

            st.success("Paper Generated!")

        if manual_select:
            st.session_state.manual_mode = True

        # ----------------------------
        # MANUAL SELECTION
        # ----------------------------
        if st.session_state.get("manual_mode", False):

            st.subheader("Manual Question Selection")

            manual_data = {}

            for sheet in selected_sheets:
                df = pd.read_excel(file_path, sheet_name=sheet).dropna()
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
                qa_ans_text = ""

                for sheet, items in manual_data.items():
                    qa_text += f"\n{sheet}\n" + "-" * 40 + "\n"
                    ans_text += f"\n{sheet}\n" + "-" * 40 + "\n"
                    qa_ans_text += f"\n{sheet}\n" + "-" * 40 + "\n"

                    for i, (q, a) in enumerate(items, 1):
                        qa_text += f"{i}. {q}\n"
                        ans_text += f"{i}. {a}\n"
                        qa_ans_text += f"{i}. {q} || {a}\n"

                st.session_state.qa_text = qa_text
                st.session_state.ans_text = ans_text
                st.session_state.qa_ans_text = qa_ans_text

                st.success("Manual selection applied!")

    # ----------------------------
    # PREVIEW
    # ----------------------------
    st.subheader("Question Paper")
#    st.text_area("Questions", st.session_state.qa_text, height=300)

    st.code(
        st.session_state.qa_text,
        language="text"
    )

    st.subheader("Answer Key")
    #st.text_area("Answers", st.session_state.ans_text, height=300)

    st.code(
        st.session_state.ans_text,
        language="text"
    )

    # ----------------------------
    # SAVE FOLDER
    # ----------------------------
    SAVE_FOLDER = "TEST_PAPERS"
    os.makedirs(SAVE_FOLDER, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")


    # CREATE PDF FROM SESSION STATE
    pdf_buffer_qa = create_pdf("QUESTION PAPER", st.session_state.qa_text)
    pdf_buffer_ans = create_pdf("ANSWER SHEET", st.session_state.ans_text)
    pdf_buffer_qa_ans = create_pdf("ANSWER SHEET", st.session_state.qa_ans_text)

    st.download_button(
        label="📤 Download Questions",
        data=pdf_buffer_qa,
        file_name="question_paper.pdf",
        mime="application/pdf"
    )
  
    
    st.download_button(
        label="📤 Download Questions & Answers",
        data=pdf_buffer_qa_ans,
        file_name="answer_paper.pdf",
        mime="application/pdf"
    )





