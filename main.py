import chromadb
from typing import List, TypedDict
from langchain_core.documents import Document
from langgraph.graph import END, StateGraph

from grader import grade_documents
from rewriter import rewrite_query
from generate import generate
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from dotenv import load_dotenv

# ---CONFIGURATION ---

load_dotenv()

DB_PATH = "./chroma_db"
COLLECTION_NAME = "rag_schematic"

# 1. Define the State (The "Memory" of the Agent)
class GraphState(TypedDict):
    question: str
    generation: str
    documents: List[Document]
    run_re_write: str # "yes" or "no"

# 2. Define the RETRIEVER Node (Wraps database logic)
def retrieve(state):
    print("---RETRIEVING---")
    question = state["question"]

    # Connect to the existing DB
    client = chromadb.PersistentClient(path=DB_PATH)
    embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma(client=client, collection_name=COLLECTION_NAME, embedding_function=embedding_function)

    # Retrieve top 3 chunks
    documents = db.similarity_search(question, k=3)
    return {"documents": documents, "question": question}

# 3. Define the DECISION Logic (The "Conditional Edge")
def decide_to_generate(state):
    print("---DECIDING---")
    # If the Grader set this flag to "yes", we rewrite.
    if state["run_re_write"] == "yes":
        print("DECISION: DOCS NOT RELEVANT -> REWRITE QUERY")
        return "rewrite_query"
    else:
        print("DECISION: DOCS RELEVANT -> GENERATE")
        return "generate"

# 4. Build the Graph
workflow = StateGraph(GraphState)

# Add Nodes
workflow.add_node("retrieve", retrieve)
workflow.add_node("grade_documents", grade_documents)
workflow.add_node("rewrite_query", rewrite_query)
workflow.add_node("generate", generate)

# Add Edges (Logic Flow)
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "grade_documents")

# The Conditional Edge: After grading, do we Generate or Rewrite?
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "rewrite_query": "rewrite_query",
        "generate": "generate",
    },
)

# If rewrite, go back to retrieve
workflow.add_edge("rewrite_query", "retrieve")
workflow.add_edge("generate", END)

app = workflow.compile()

# RUN AGENT
if __name__ == "__main__":
    user_input = "How does CachyOS improve network speeds?"
    inputs = {"question": user_input}
    
    print(f"🚀 Starting Agent with Question: '{user_input}'")
    
    final_generation = ""

    # Run the graph ONLY once via stream
    for output in app.stream(inputs):
        for key, value in output.items():
            print(f"  Finished Node: {key}")
            # Capture the generation if this node produced it
            if "generation" in value:
                final_generation = value["generation"]
            
    print("\n--- FINAL RESULT ---")
    print(final_generation)
