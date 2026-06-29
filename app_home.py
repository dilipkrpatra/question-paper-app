import streamlit as st

st.set_page_config(
    page_title="Study Suite",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Study Suite Home")

st.markdown("Choose an application below:")

col1, col2 = st.columns(2)

with col1:
    st.markdown("## 📄 Learn Yourself")
    st.markdown("Read and Learn with flashcards.")

    if st.button("Open Reader", use_container_width=True):
        st.switch_page("pages/read.py")


with col2:
    st.markdown("## 📘 Question Paper Generator")
    st.markdown("Generate random question papers from Question bank.")

    if st.button("Open Generator", use_container_width=True):
        st.switch_page("pages/setqa.py")