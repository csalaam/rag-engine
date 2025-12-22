from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def generate(state):
    print("---GENERATING FINAL ANSWER---")
    question = state["question"]
    documents = state["documents"]

    # Llama 3.3-70B for the final answer because it's articulate and fast
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

    # The Prompt: "Ground" the answer in the provided documents
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an assistant for question-answering tasks. "
                  "Use the following pieces of retrieved context to answer the question. "
                  "If you don't know the answer, say that you don't know. "
                  "Use three sentences maximum and keep the answer concise."),
        ("human", "Question: {question} \n\n Context: {documents}")
    ])

    # Chain: Prompt -> Model -> String Output
    # We format documents into a single string for the prompt
    doc_txt = "\n\n".join([doc.page_content for doc in documents])

    generator_chain = prompt | llm | StrOutputParser()

    generation = generator_chain.invoke({"documents": doc_txt, "question": question})

    return {"generation": generation}
