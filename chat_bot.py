import streamlit as st
from pypdf import PdfReader
from groq import Groq

client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)
st.set_page_config(
    page_title="DocPilot",
    page_icon="📚",
    layout="wide"
)
st.title("📚 DocPilot")
st.caption(
    "Upload a PDF, generate summaries, and ask questions using AI."
)
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
    text = text[:50000]         
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
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "user",
                            "content": summary_prompt
                        }
                    ]
                )
                summary = response.choices[0].message.content
                st.subheader("PDF Summary")
                st.write(summary)
                st.download_button(
    "⬇ Download Summary",
    summary,
    file_name="summary.txt"
)
                
            except Exception as e:
                st.error(f"Error: {e}")

    with st.expander("View PDF Content"):
        st.write(text[:5000])

    question = st.chat_input(
    "Ask about the PDF"
)
    

    if question:
        with st.spinner("Thinking..."):
            prompt = f"""
You are a PDF assistant.

Answer only using information from the PDF.

If the answer is not present in the PDF, reply:
"The PDF does not contain this information."

PDF Content:
{text}

Question:
{question}
"""
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                answer = response.choices[0].message.content
                st.session_state.messages.append({"question": question, "answer": answer})
            except Exception as e:
                st.error(f"Error: {e}")

    for msg in st.session_state.messages:
        with st.chat_message("user"):
            st.write(msg["question"])
        with st.chat_message("assistant"):
            st.write(msg["answer"])

    st.divider()
    st.caption("Built by Harshit using Python, Streamlit and Groq")