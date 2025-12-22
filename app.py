import streamlit as st
import os
import shutil
from dotenv import load_dotenv

# Import your existing logic
from ingest import load_documents, split_text, save_to_chroma
from main import app as graph_app 

# Load environment
load_dotenv()

# --- PAGE CONFIGURATION ---
# Generic Title for any client
st.set_page_config(page_title="AI Knowledge Base", layout="wide")

st.title("🤖 Agentic RAG: Document Assistant")
st.markdown("Upload your documents (PDF, Markdown, Text) and ask questions. The agent analyzes your data to provide accurate, cited answers.")

# --- SIDEBAR: DOCUMENT INGESTION ---
with st.sidebar:
    st.header("📂 Data Ingestion")
    st.info("Supported formats: .pdf, .txt, .md")
    
    uploaded_files = st.file_uploader(
        "Upload your Knowledge Base", 
        accept_multiple_files=True, 
        type=["pdf", "txt", "md"]
    )
    
    if st.button("Build Knowledge Base"):
        if uploaded_files:
            with st.spinner("Processing documents... this may take a moment."):
                # 1. Clear/Create data folder
                if os.path.exists("./data"):
                    shutil.rmtree("./data")
                os.makedirs("./data")
                
                # 2. Save uploaded files
                for uploaded_file in uploaded_files:
                    with open(os.path.join("./data", uploaded_file.name), "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                # 3. Trigger Ingestion
                docs = load_documents()
                chunks = split_text(docs)
                save_to_chroma(chunks)
                
                st.success(f"✅ Success! Indexed {len(chunks)} document chunks.")
        else:
            st.warning("Please upload files before building.")

# --- MAIN CHAT INTERFACE ---

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle Input
if prompt := st.chat_input("Ask a question regarding your documents..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        inputs = {"question": prompt}
        
        # Status container to show the "Thinking" process
        status_text = st.status("Agent is working...", expanded=True)
        
        try:
            for output in graph_app.stream(inputs):
                for key, value in output.items():
                    if key == "retrieve":
                        status_text.write("🔍 Searching documents...")
                    elif key == "grade_documents":
                        status_text.write("⚖️ Verifying relevance...")
                    elif key == "rewrite_query":
                        status_text.write("🔄 Query unclear. Rewriting for better search...")
                    elif key == "generate":
                        status_text.write("💡 Synthesizing answer...")
                        if "generation" in value:
                            full_response = value["generation"]
            
            status_text.update(label="Response Ready", state="complete", expanded=False)
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            status_text.update(label="System Error", state="error")
            st.error(f"An error occurred: {str(e)}")
