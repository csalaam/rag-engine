from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
def rewrite_query(state):
    """
    If the Grader found no good docs, use an LLM to optimize the question for a better second search.
    """

    print("---REWRITING QUERY---")
    question = state["question"]

    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

    re_write_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert at optimizing search queries for vector databases. "
         "The original question failed to find relevant results."
         "Rewrite the question to be more effective for semantic search."),
        ("human", f"Original question: {question}")
    ])

    rewriter_chain = re_write_prompt | llm | StrOutputParser()

    better_question = rewriter_chain.invoke({})

    return {"question": better_question}
