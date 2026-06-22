from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

class Grade(BaseModel):
    """Binary Score for relevance check or retrieved documents"""
    binary_score: str = Field(description="Relevance score 'yes' or 'no'")

def grade_documents(state):
    
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    structured_grader = llm.with_structured_output(Grade)


    
    system_prompt = """You are a grader assessing relevance of a retrieved document to a user question. If the document contains keywords or semantic meaning related to the question, grade it as relevant.
        Give a binary score 'yes' or 'no'."""

    grader_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
    ])
    
    grader_chain = grader_prompt | structured_grader 

    filtered_docs = []
    for doc in state["documents"]:
        score = grader_chain.invoke({
            "question": state["question"],
            "document": doc.page_content
        })

        if score.binary_score == "yes":
            filtered_docs.append(doc)

    if filtered_docs:
        search_again = "no"  # We have good docs, so NO rewrite needed
    else:
        search_again = "yes" # No good docs found, YES rewrite needed

    return {"documents": filtered_docs, "run_re_write": search_again}
