#1. Import OS, Document Loader, Text Splitter, Bedrock Embeddings, Vector DB, VectorStoreIndex, Bedrock-LLM
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_aws import ChatBedrock

#5c. Wrap within a function
def hr_index():
    #2. Define the data source and load data with PDFLoader
    data_load = PyPDFLoader('https://www.upl-ltd.com/images/people/downloads/Leave-Policy-India.pdf')
    documents = data_load.load()

    #3. Split the Text based on Character, Tokens etc.
    data_split = RecursiveCharacterTextSplitter(separators=["\n\n", "\n", " ", ""], chunk_size=1000, chunk_overlap=100)
    chunks = data_split.split_documents(documents)

    #4. Create Embeddings -- Client connection
    data_embeddings = BedrockEmbeddings(
        credentials_profile_name='default',
        model_id='amazon.titan-embed-text-v1')

    #5. Create FAISS Vector DB from chunks and embeddings
    db_index = FAISS.from_documents(chunks, data_embeddings)
    return db_index
#6a. Write a function to connect to Bedrock Foundation Model - Claude 3 Haiku
def hr_llm():
    llm = ChatBedrock(
        credentials_profile_name='default',
        model_id='us.anthropic.claude-haiku-4-5-20251001-v1:0',
        model_kwargs={
            "max_tokens": 3000,
            "temperature": 0.1})
    return llm
#6b. Write a function which searches the user prompt, searches the best match from Vector DB and sends both to LLM.
def hr_rag_response(index, question):
    rag_llm = hr_llm()
    # Retrieve top 3 matching chunks from FAISS
    docs = index.similarity_search(question, k=3)
    context = "\n\n".join([doc.page_content for doc in docs])
    # Build prompt with context and question
    prompt = f"Use the following HR policy context to answer the question.\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer:"
    hr_rag_query = rag_llm.invoke(prompt)
    # ChatBedrock returns an AIMessage object — extract the text
    return hr_rag_query.content
# Index creation --> https://api.python.langchain.com/en/latest/indexes/langchain.indexes.vectorstore.VectorstoreIndexCreator.html