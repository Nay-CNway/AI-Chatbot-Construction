import os
import chromadb


chroma_client = chromadb.PersistentClient(
    path = r"C:\Users\naych\AI-Chatbot-Construction\data\project_texts"
)

collection = chroma_client.get_or_create_collection(
    name = "construction_projects"
)

text_folders = r"C:\Users\naych\AI-Chatbot-Construction\data\project_texts"

documents = []
ids = []

for filename in os.listdir(text_folders):
    if filename.endswith(".txt"):
        file_path = os.path.join(text_folders, filename)

        with open(file_path, "r", encoding= "utf-8") as f:
            content = f.read()

        documents.append(content)
        ids.append(filename.replace(".txt", ""))
        print(f"✅ Loaded: {filename}")
existing = collection.get()
if existing["ids"]:
    collection.delete(ids = existing["ids"])
    print("🔄 Cleared existing documents")


collection.add(
    documents= documents,
    ids = ids
)

print(f"\n✅ Successfully loaded {len(documents)} projects into ChromaDB!")
print("ChromaDB is ready to search.")

print("\n=== TESTING SEARCH ===\n")

testing_questions = [
    "How much does a 3 storey building cost?",
    "What is the cost per square foot?",
    "Estimate cost for a one storey house"
]

for question in testing_questions:
    print(f"Questions: {question}")
    results = collection.query(
        query_texts= [question],
        n_results= 2
    )

for doc in results["documents"][0]:
    print(f"  → {doc[:200]}")
print()

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv
import os

load_dotenv()

embeddings = OpenAIEmbeddings()

vectorstore = Chroma(
    collection_name= "construction_projects",
    embedding_function= embeddings,
    persist_directory= r"C:\Users\naych\AI-Chatbot-Construction\data\chromadb"
)

llm = ChatOpenAI(
    model= "gpt-3.5-turbo",
    temperature= 0.2
)

prompt = PromptTemplate.from_template(
    """You are a construction cost estimation assistant for 
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

print("\n=== LANGCHAIN RAG TEST ===\n")

questions = [
    "How much would a 3 storey house roughly cost?",
    "What is the cost per square foot for a one storey building?",
    "Give me a rough estimate for a 2 storey house"
]

for question in questions:
    print(f"Q: {question}")
    answer = chain.invoke(question)
    print(f"A: {answer}")
    print()