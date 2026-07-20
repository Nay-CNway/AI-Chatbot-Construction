import os
import streamlit as st
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv

load_dotenv()

with st.sidebar:
    st.image("asset/logo.png", width= 150)
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    **Creative Paradise Construction and Decoration Co., Ltd**
    
    **Operating Areas:**
    - Magway Division
    - Yangon Division
    - Nay Pyi Taw Division
    - Mandalay Division 
                
    **Services:**
    - Residential Buildings
    - Commercial Buildings
    - Renovation & Remodeling
    - Design & Planning
    """)

    st.markdown("---")
    st.markdown("### How to use")
    st.markdown("""
    Simply type your question about 
    construction costs in the chat box.
                
    **Example questions:**
    - How much does a 3 storey house cost?
    - What is the cost per square foot?
    - Estimate cost for a 2 storey building
    """)

    st.markdown("---")
    st.caption("Powered by Creative Paradise AI")

st.set_page_config(
    page_title= "Creative Paradise Construction AI",
    page_icon= "🏗️",
    layout= "centered"
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(BASE_DIR,"asset","logo.png")

col1, col2 = st.columns([1,4])
with col1:
    st.image(LOGO_PATH,width= 100)
with col2:
    st.title("Creative Paradise Construction")
    st.subheader("AI Cost Estimation Assistant")

st.markdown("Ask me anything about construction costs in Myanmar! 🏗️")  
st.divider()
@st.cache_resource

def load_chain():
    embeddings = OpenAIEmbeddings()

    vectorstore = Chroma(
        collection_name= "construction_projects",
        embedding_function= embeddings,
        persist_directory= r"C:\Users\naych\AI-Chatbot-Construction\data\chromadb"
    )

    llm = ChatOpenAI(
        model = "gpt-3.5-turbo",
        temperature= 0.2
    )

    prompt = PromptTemplate.from_template("""You are a construction cost estimation assistant for 
Creative Paradise Construction and Decoration Co., Ltd in Myanmar.

Use the following real past project data to answer the question.
Always mention costs in MMK (Myanmar Kyat).
Be helpful, professional and specific.
If you don't know the answer from the provided data, say so honestly.

Past project data:
{context}

Question: {question}

Answer:""")
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    retriever = vectorstore.as_retriever(search_kwargs = {"k": 2})

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain

chain = load_chain()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything about Construction costs ..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Calculating estimate ..."):
            try:
                answer = chain.invoke(prompt)
                st.markdown(answer)
                st.session_state.messages.append({"role":"assistant", "content": answer})
            except Exception as e:
                error_msg = "Sorry, I encountered an error. Please try again later!!"
                st.error(error_msg)
                st.session_state.messages.append({"role":"assistant","content": error_msg})