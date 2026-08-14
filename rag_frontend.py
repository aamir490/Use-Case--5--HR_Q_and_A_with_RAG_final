# streamlit run rag_frontend.py

import streamlit as st
import rag_backend as demo

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NovaMindAI — HR Q&A",
    page_icon="🤖",
    layout="wide"
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("mylogo2.png", use_container_width=True)
    st.markdown("---")
    st.markdown("### 👨‍💻 Developer")
    st.markdown("**Aamir**")
    st.markdown(
        "[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://www.linkedin.com/in/aamir-imran)",
        unsafe_allow_html=True
    )
    st.markdown("---")
    st.markdown("### 🤖 About NovaMindAI")
    st.markdown(
        "NovaMindAI is an HR Q&A assistant powered by "
        "**Retrieval-Augmented Generation (RAG)** using "
        "**Amazon Bedrock** and **FAISS**."
    )
    st.markdown("---")
    st.markdown("### ⚙️ Tech Stack")
    st.markdown("""
- 🐍 Python 3.12  
- ☁️ AWS Bedrock (Claude Haiku)  
- 🔷 Amazon Titan Embeddings  
- 🗂️ FAISS Vector Store  
- 🔗 LangChain  
- 📄 PyPDF  
- 🖥️ Streamlit  
""")
    st.markdown("---")
    st.caption("© 2025 NovaMindAI · Built by Aamir")

# ── Main Header ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style='text-align: center; padding: 10px 0 5px 0;'>
        <h1 style='color: #1E90FF; font-size: 2.8rem; margin-bottom: 0;'>🤖 NovaMindAI</h1>
        <p style='color: #aaaaaa; font-size: 1.1rem; margin-top: 4px;'>
            HR Policy Q&amp;A — Powered by Amazon Bedrock &amp; RAG
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

# ── Index Initialization ──────────────────────────────────────────────────────
if 'vector_index' not in st.session_state:
    with st.spinner("⚙️ Loading HR knowledge base... please wait."):
        st.session_state.vector_index = demo.hr_index()

# ── Input Area ────────────────────────────────────────────────────────────────
st.markdown("#### 💬 Ask a question about the HR Leave Policy")
input_text = st.text_area(
    label="Your Question",
    placeholder="e.g. How many privilege leave days are allowed per year?",
    height=100,
    label_visibility="collapsed"
)

go_button = st.button("� Ask NovaMindAI", type="primary", use_container_width=True)

# ── Response ──────────────────────────────────────────────────────────────────
if go_button:
    if not input_text.strip():
        st.warning("Please enter a question before clicking Ask.")
    else:
        with st.spinner("🧠 Searching HR policy and generating answer..."):
            response_content = demo.hr_rag_response(
                index=st.session_state.vector_index,
                question=input_text
            )
        st.markdown("#### 📋 Answer")
        st.success(response_content)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#555555; font-size:0.85rem;'>"
    "NovaMindAI · HR Q&A PoC · Built with ❤️ by "
    "<a href='https://www.linkedin.com/in/aamir-imran' target='_blank'>Aamir</a>"
    " · Powered by Amazon Bedrock</p>",
    unsafe_allow_html=True
)
