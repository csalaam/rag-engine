from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

class Grade(BaseModel):
    """Evaluation of document utility for answering a user question."""
    justification: str = Field(
        description="A one-sentence extraction of facts from the document that directly address the query. If none exist, state why."
    )
    binary_score: str = Field(
        description="Strictly 'yes' if actionable facts exist, or 'no' if the document is only tangentially related."
    )

def grade_documents(state):
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    structured_grader = llm.with_structured_output(Grade)

    # No high-entropy phrases like "semantic meaning related to"
    system_prompt = """You are an unyielding data auditor verifying document utility for a production pipeline.
    
    Your sole mandate is to reject noise. A document is only relevant if it contains specific, actionable facts that can directly answer the user's question. 
    If it is only topically related, shares keyword overlap, or lacks explicit utility, it must be marked as irrelevant."""

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

    search_again = "no" if filtered_docs else "yes"
    return {"documents": filtered_docs, "run_re_write": search_again}
