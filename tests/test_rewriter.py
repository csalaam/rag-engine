import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from rewriter import rewrite_query

# Load keys
load_dotenv()

def test_rewriter():
    print("--- TESTING QUERY REWRITER ---")
    
    # Simulating a "State" dictionary that a LangGraph agent would use
    # Scenario: User asked something vague that failed initial retrieval
    mock_state = {
        "question": "how to make things go faster on cachy",
        "documents": [] # Empty because the grader rejected previous results
    }

    print(f"Original Question: {mock_state['question']}")

    # Invoke your rewriter logic
    result = rewrite_query(mock_state)

    print(f"\nRewritten Question: {result['question']}")
    
    # Validation Logic
    if len(result['question']) > len(mock_state['question']):
        print("\n✅ Success: The query was expanded with better search terms.")
    else:
        print("\n⚠️ Warning: The query was not significantly improved.")

if __name__ == "__main__":
    test_rewriter()
