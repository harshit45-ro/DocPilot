import streamlit as st
from pypdf import PdfReader
import google.generativeai as genai

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

model = genai.GenerativeModel("gemini-2.5-flash")
st.set_page_config(
    page_title="DocPilot",
    page_icon="📚",
    layout="wide"
)
st.write("VERSION 2")
st.title("📚 DocPilot")
st.caption("AI PDF Assistant")
st.sidebar.title("DocPilot")
st.sidebar.write("AI PDF Assistant")
if st.sidebar.button("🗑 Clear Chat"):
    st.session_state.messages = []
    st.rerun()
if "messages" not in st.session_state:
    st.session_state.messages = []

uploaded_file = st.file_uploader(
    "Upload a PDF",
    type="pdf"
)

if uploaded_file:
    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text
    st.success(
    f"Loaded {uploaded_file.name}"
)
    st.sidebar.write(f"📄 Pages: {len(reader.pages)}")
    st.sidebar.write(f"🔤 Characters: {len(text)}")
    if st.button("📋 Summarize PDF"):
        with st.spinner("Generating summary..."):
            summary_prompt = f"""
Summarize this PDF in simple language.

PDF Content:
{text}
"""
            try:
                summary = model.generate_content(
                    summary_prompt
                )

                st.subheader("PDF Summary")
                st.write(summary.text)
                st.download_button(
                    "⬇ Download Summary",
                    summary.text,
                    file_name="summary.txt"
                )
            except Exception as e:
                st.error(f"Error: {e}")

    with st.expander("View PDF Content"):
        st.write(text[:5000])

    question = st.text_input(
        "Ask a question about the PDF"
    )

    if question:
        with st.spinner("Thinking..."):
            prompt = f"""
            Answer the question using the PDF content.

            PDF Content:
            {text}

            Question:
            {question}
            """
            try:
                response = model.generate_content(prompt)
                answer = response.text
                st.session_state.messages.append({"question": question, "answer": answer})
            except Exception as e:
                st.error(f"Error: {e}")

    for msg in st.session_state.messages:
        with st.chat_message("user"):
            st.write(msg["question"])
        with st.chat_message("assistant"):
            st.write(msg["answer"])

    st.divider()
    st.caption("Built by Harshit using Python, Streamlit and Gemini")