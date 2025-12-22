import chromadb # We need the raw client to match the ingestion method
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

DB_PATH = "./chroma_db"
COLLECTION_NAME = "rag_schematic" # This MUST match ingest.py

def test_retrieval():
    print("--- LOADING DATABASE ---")
    
    embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 1. Initialize the Persistent Client (Same as ingest.py)
    client = chromadb.PersistentClient(path=DB_PATH)

    # 2. Connect to the specific Collection we created
    db = Chroma(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_function
    )

    # 3. The Test
    query = "What optimization schedulers does the kernel use?"
    
    print(f"❓ Querying: '{query}'")
    
    # We can check the count to verify data exists before searching
    count = db._collection.count()
    print(f"📊 Documents in DB: {count}")

    results = db.similarity_search(query, k=1)

    if results:
        print("\n✅ DOCUMENT FOUND:")
        print(f"📄 Content: {results[0].page_content}")
    else:
        print("\n❌ No results found. (This should not happen if count > 0)")

if __name__ == "__main__":
    test_retrieval()
