import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from grader import grade_documents # Import your code

# Load the API key from .env
load_dotenv()

# Mocking the "State" that LangGraph usually handles
class MockDocument:
    def __init__(self, content):
        self.page_content = content

def test_grader():
    # Scenario: The user asks about CachyOS, but the retriever found garbage.
    question = "How do I update CachyOS?"
    
    bad_docs = [
        MockDocument("The price of gold rose by 2% today."),
        MockDocument("To bake a cake, you need flour and eggs.")
    ]
    
    good_docs = [
        MockDocument("CachyOS is updated using the 'sudo pacman -Syu' command.")
    ]

    print("Testing with IRRELEVANT docs...")
    result_fail = grade_documents({"question": question, "documents": bad_docs})
    print(f"Relevant docs found: {len(result_fail['documents'])}")
    print(f"Trigger Rewrite? {result_fail['relevant']}")

    print("\nTesting with RELEVANT docs...")
    result_pass = grade_documents({"question": question, "documents": good_docs})
    print(f"Relevant docs found: {len(result_pass['documents'])}")
    print(f"Trigger Rewrite? {result_pass['relevant']}")

if __name__ == "__main__":
    test_grader()
