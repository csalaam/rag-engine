import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from langchain_core.documents import Document
from generate import generate

# Load Groq AI Key
load_dotenv()

def test_generation():
    print("--- STARTING GENERATOR UNIT TEST ---")

    # 1. Mock the Data
    # This simulates what the Retriever + Grader would pass to this node.
    mock_question = "What makes the CachyOS kernel special?"

    mock_documents = [
        Document(page_content="CachyOS utilizes a custom kernel optimized with LTO (Link Time Optimization)."),
        Document(page_content="The kernel also uses BORE (Burst-Oriented Response Enhancer) schedulers for better desktop responsiveness.")
    ]

    # Create Mock State
    state = {
        "question": mock_question,
        "documents": mock_documents
    }

    # 3. Run Generator Node

    try:
        result = generate(state)
        print("\n🤖 FINAL OUTPUT:")
        print(result["generation"])

        # Validation
        if "LTO" in result["generation"] and "BORE" in result["generation"]:
            print("\n✅ SUCCESS: The answer utilized the context provided.")
        else:
            print("\n⚠️ WARNING: The answer might be hallucinated or generic.")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    test_generation()
