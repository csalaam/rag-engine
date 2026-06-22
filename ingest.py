import os
import shutil
import chromadb
from langchain_community.document_loaders import DirectoryLoader, TextLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma 

# *** CLIENT PARAMETERS ***
DATA_PATH = "./data"
DB_PATH = "./chroma_db"
CHUNK_SIZE = 800 # Character per chunk
CHUNK_OVERLAP = 80 # Overlap to preserve context between chunks

def load_documents():
    """
    Polymorphic Loader: Scans the DATA_PATH for .md and .txt files.
    Extendable to .pdf or .docx easily.
    """

    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
        print(f"📁 Created {DATA_PATH}. Please add your files there.")
        return []

    print(f"🔍 Scanning {DATA_PATH}...")

    # For now, enforce Markdown/Text for clean testing
    loader = DirectoryLoader(DATA_PATH, glob="**/*.md", loader_cls=UnstructuredMarkdownLoader)
    documents = loader.load()

    # Add a fallback for .txt files
    txt_loader = DirectoryLoader(DATA_PATH, glob="**/*.txt", loader_cls=TextLoader)
    documents.extend(txt_loader.load())

    return documents

def split_text(documents):
    """
    'Smart Chunking' Logic
    RecursiveCharacterTextSplitter respects sentence structure
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"🧩 Split {len(documents)} documents into {len(chunks)} chunks.")
    return chunks

def save_to_chroma(chunks):
    """
    Embeds and indexes the chunks into a local ChromaDB.
    """

    # Clear out old DB if it exists (for fresh testing)
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)

    # Standard, high-performance local embedding model
    # 'all-MiniLM-L6-v2' is the industry standard for speed/accuracy
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print("💾 Creating Persistent Client...")
    
    # FORCE the use of a PersistentClient
    client = chromadb.PersistentClient(path=DB_PATH)
    
    # Create the collection via LangChain using the client
    db = Chroma(
        client=client,
        embedding_function=embeddings,
        collection_name="rag_schematic"
    )
    
    db.add_documents(documents=chunks)

    print(f"✅ Saved {len(chunks)} chunks to {DB_PATH}.")

def generate_data_store():
    print(f"📍 Current Working Directory: {os.getcwd()}")
    print(f"📍 Target Database Path: {os.path.abspath(DB_PATH)}")

    documents = load_documents()
    if documents:
        chunks = split_text(documents)
        save_to_chroma(chunks)

        # Verify file creation immediately
        if os.path.exists(DB_PATH):
            print(f"✅ CONFIRMED: Directory {DB_PATH} exists.")
            print(f"   Contents: {os.listdir(DB_PATH)}")
        else:
            print(f"❌ CRITICAL ERROR: The script finished, but {DB_PATH} was NOT created.")
    else:
        print("⚠️ No documents found.")

if __name__ == "__main__":
    generate_data_store()
