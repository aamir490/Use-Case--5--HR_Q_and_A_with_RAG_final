# `05-Backend-Code-Walkthrough.md`

## NovaMindAI HR Q&A — Backend Code Walkthrough

### Main question

> **How does my `rag_backend.py` actually work line by line, and how does the code implement the RAG pipeline?**

Until now, we understood the project from a higher level:

```text
01 → Project Overview
02 → Current Architecture
03 → End-to-End Flow
04 → Technology Stack
05 → ACTUAL BACKEND CODE
```

Now we connect everything you learned to the real implementation.

Your backend is surprisingly small. The important thing is not the number of lines—it is understanding **what responsibility every line has**.

---

# 1. Complete backend code

Your inspected `rag_backend.py` contains this core implementation:

```python
# 1. Imports
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_aws import ChatBedrock


# 2. Build the HR knowledge index
def hr_index():

    data_load = PyPDFLoader(
        'https://www.upl-ltd.com/images/people/downloads/Leave-Policy-India.pdf'
    )

    documents = data_load.load()

    data_split = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=1000,
        chunk_overlap=100
    )

    chunks = data_split.split_documents(documents)

    data_embeddings = BedrockEmbeddings(
        credentials_profile_name='default',
        model_id='amazon.titan-embed-text-v1'
    )

    db_index = FAISS.from_documents(
        chunks,
        data_embeddings
    )

    return db_index


# 3. Configure Claude
def hr_llm():

    llm = ChatBedrock(
        credentials_profile_name='default',
        model_id='us.anthropic.claude-haiku-4-5-20251001-v1:0',
        model_kwargs={
            "max_tokens": 3000,
            "temperature": 0.1
        }
    )

    return llm


# 4. RAG Question Answering
def hr_rag_response(index, question):

    rag_llm = hr_llm()

    docs = index.similarity_search(
        question,
        k=3
    )

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    prompt = f"""Use the following HR policy context to answer the question.

Context:
{context}

Question: {question}

Answer:"""

    hr_rag_query = rag_llm.invoke(prompt)

    return hr_rag_query.content
```

This code implements the manual RAG workflow identified in the project analysis: document loading → splitting → Titan embeddings → FAISS indexing → top-3 retrieval → context construction → Claude invocation. :chatgpt-content-reference{index="0"}

---

# 2. Don't study this as one large block

Divide `rag_backend.py` into **four parts**:

```text
rag_backend.py

1. IMPORTS
   ↓
Bring required libraries into Python

2. hr_index()
   ↓
Prepare searchable HR knowledge

3. hr_llm()
   ↓
Configure Claude

4. hr_rag_response()
   ↓
Retrieve + Augment + Generate
```

And the three functions have very simple meanings:

```text
hr_index()
   = Prepare Knowledge

hr_llm()
   = Prepare LLM

hr_rag_response()
   = Answer Question
```

Keep this mental model.

---

# 3. Part 1 — Imports

The first section imports the libraries required by your application.

```python
import os
```

`os` is Python's operating-system module.

However, in the inspected core backend code, it does not appear to be actively used.

That's actually a useful code-review observation.

Don't tell an interviewer:

> “I use `os` for environment variables.”

unless your actual code does that.

---

# 4. Import `PyPDFLoader`

```python
from langchain_community.document_loaders import PyPDFLoader
```

This imports the component responsible for loading your HR policy PDF.

Think:

```text
PDF
 ↓
PyPDFLoader
 ↓
LangChain Document objects
```

This belongs to the:

**document ingestion stage.**

---

# 5. Import the text splitter

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter
```

This imports the component used to divide the loaded document into smaller chunks.

Think:

```text
Large Document
      ↓
RecursiveCharacterTextSplitter
      ↓
Smaller Chunks
```

This belongs to:

**document processing.**

---

# 6. Import `BedrockEmbeddings`

```python
from langchain_aws import BedrockEmbeddings
```

This is the LangChain AWS integration used to work with an embedding model through Amazon Bedrock.

In your project:

```text
BedrockEmbeddings
       ↓
Amazon Bedrock
       ↓
Amazon Titan
       ↓
Embeddings
```

This belongs to:

**embedding generation.**

---

# 7. Import FAISS

```python
from langchain_community.vectorstores import FAISS
```

This gives your application the FAISS vector-store integration.

Its job:

```text
Embeddings
    ↓
FAISS Index

and later...

Question
    ↓
FAISS Similarity Search
    ↓
Relevant Documents
```

This belongs to:

**vector indexing and retrieval.**

---

# 8. Import `ChatBedrock`

```python
from langchain_aws import ChatBedrock
```

This provides your Python application with the integration used to invoke the configured chat model through Bedrock.

Think:

```text
Python
 ↓
ChatBedrock
 ↓
Amazon Bedrock
 ↓
Claude
```

This belongs to:

**generation/model invocation.**

---

# 9. Import section mapped to RAG

You can already see your application architecture from the imports:

```text
PyPDFLoader
     ↓
LOAD

RecursiveCharacterTextSplitter
     ↓
SPLIT

BedrockEmbeddings
     ↓
EMBED

FAISS
     ↓
INDEX + RETRIEVE

ChatBedrock
     ↓
GENERATE
```

This is a nice way to understand the code instead of memorizing import statements.

---

# 10. Function 1 — `hr_index()`

Now we reach:

```python
def hr_index():
```

This function has one main responsibility:

> **Convert the HR policy into a searchable FAISS vector index.**

Think:

```text
hr_index()

PDF
 ↓
Load
 ↓
Split
 ↓
Embed
 ↓
FAISS
 ↓
Return Index
```

Let's go line by line.

---

# 11. Create the PDF loader

Your code:

```python
data_load = PyPDFLoader(
    'https://www.upl-ltd.com/images/people/downloads/Leave-Policy-India.pdf'
)
```

Here you create a `PyPDFLoader` object.

Notice something important.

The policy source is:

**hardcoded in the backend.**

The user is not doing:

```text
Upload PDF
   ↓
Choose document
```

Instead:

```text
Backend
   ↓
Known fixed URL
   ↓
HR Leave Policy
```

This is important when discussing limitations later.

---

# 12. Actually load the PDF

Next:

```python
documents = data_load.load()
```

This is where loading actually occurs.

Understand the difference:

```python
data_load = PyPDFLoader(...)
```

means:

> Prepare/configure the loader.

Whereas:

```python
documents = data_load.load()
```

means:

> Actually load the document.

After this:

```text
PDF
 ↓
.load()
 ↓
documents
```

`documents` contains document objects that can be passed to your splitter.

---

# 13. Configure the text splitter

Next:

```python
data_split = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", " ", ""],
    chunk_size=1000,
    chunk_overlap=100
)
```

You're creating/configuring a splitter.

Important parameters:

```text
chunk_size = 1000
chunk_overlap = 100
```

And:

```text
separators =

"\n\n" → paragraph boundaries
"\n"   → line boundaries
" "    → spaces
""     → character-level fallback
```

At a high level, the recursive splitter tries these separators in order to find useful boundaries while respecting the configured chunk size.

We'll go much deeper in File 09.

---

# 14. Actually split the documents

Next:

```python
chunks = data_split.split_documents(documents)
```

Again, distinguish configuration from execution.

```text
RecursiveCharacterTextSplitter(...)
       ↓
Configure splitter

split_documents(documents)
       ↓
Actually perform splitting
```

The result is:

```text
documents
   ↓
split_documents()
   ↓
chunks
```

Now the policy has been divided into smaller document chunks.

---

# 15. Configure Titan embeddings

Next:

```python
data_embeddings = BedrockEmbeddings(
    credentials_profile_name='default',
    model_id='amazon.titan-embed-text-v1'
)
```

There are two important parameters.

### AWS credentials profile

```python
credentials_profile_name='default'
```

Your application expects an AWS profile named:

```text
default
```

to be available in the runtime environment.

That profile needs appropriate AWS permissions.

### Embedding model

```python
model_id='amazon.titan-embed-text-v1'
```

This tells the integration which Bedrock embedding model to use.

Conceptually:

```text
Python
 ↓
BedrockEmbeddings
 ↓
AWS credentials/profile
 ↓
Amazon Bedrock
 ↓
Titan Embeddings
```

---

# 16. Does this line create all embeddings immediately?

This distinction is useful.

```python
data_embeddings = BedrockEmbeddings(...)
```

primarily configures the embedding integration.

Then this:

```python
FAISS.from_documents(
    chunks,
    data_embeddings
)
```

uses that embedding integration while creating the index.

So mentally:

```text
Configure Titan embedding client
            ↓
Pass it to FAISS.from_documents()
            ↓
Embed chunks + build index
```

---

# 17. Create the FAISS index

Now:

```python
db_index = FAISS.from_documents(
    chunks,
    data_embeddings
)
```

This is one of the most important lines.

You provide:

```text
chunks
+
embedding model/integration
```

and get:

```text
FAISS vector index
```

Conceptually:

```text
Chunk 1 ──→ Titan ──→ Vector 1 ┐
Chunk 2 ──→ Titan ──→ Vector 2 ├──→ FAISS
Chunk 3 ──→ Titan ──→ Vector 3 ┘
```

So:

```python
db_index
```

is your searchable vector-store object.

---

# 18. Return the index

Finally:

```python
return db_index
```

So the complete function becomes:

```text
hr_index()
   │
   ├── Load PDF
   ├── Split document
   ├── Configure Titan
   ├── Generate/index embeddings with FAISS
   │
   └── Return searchable index
```

That completes Function 1.

---

# 19. Function 2 — `hr_llm()`

Now:

```python
def hr_llm():
```

This function has a different responsibility.

It does **not**:

```text
❌ Load PDF
❌ Create embeddings
❌ Build FAISS
❌ Search documents
```

Its job is:

> **Configure and return the Claude model integration.**

---

# 20. Create `ChatBedrock`

Your code:

```python
llm = ChatBedrock(
    credentials_profile_name='default',
    model_id='us.anthropic.claude-haiku-4-5-20251001-v1:0',
    model_kwargs={
        "max_tokens": 3000,
        "temperature": 0.1
    }
)
```

Let's break it down.

---

# 21. `credentials_profile_name`

Again:

```python
credentials_profile_name='default'
```

Your application uses the local/default AWS credential profile to authenticate the Bedrock request.

This appears in both:

```text
BedrockEmbeddings
and
ChatBedrock
```

because both need AWS access.

---

# 22. `model_id`

The inspected code specifies:

```python
model_id='us.anthropic.claude-haiku-4-5-20251001-v1:0'
```

This identifies the configured Claude model/profile used by the application.

You do not need to memorize every character of the model ID for an interview.

Understand:

> **Claude Haiku 4.5 is the generation model configured in this version of the project.**

---

# 23. `max_tokens`

Your code has:

```python
"max_tokens": 3000
```

This configures the maximum generated output allowance for the request.

It does not mean:

> “Claude always generates 3000 tokens.”

---

# 24. `temperature`

Your code has:

```python
"temperature": 0.1
```

For this HR policy use case, a low value is consistent with wanting relatively controlled responses rather than creative writing.

But remember:

```text
Low temperature
       ≠
Guaranteed factual answer
```

RAG quality still depends on retrieval, context, prompting and model behavior.

---

# 25. Return the LLM

Finally:

```python
return llm
```

So:

```text
hr_llm()
   ↓
Configure ChatBedrock
   ↓
Claude Haiku 4.5
   ↓
Return LLM object
```

That's Function 2.

---

# 26. Function 3 — `hr_rag_response()`

Now we reach the most important function for runtime RAG:

```python
def hr_rag_response(index, question):
```

It accepts two arguments:

```text
index
   ↓
Existing FAISS index

question
   ↓
Employee's HR question
```

For example:

```text
index = FAISS vector index

question =
"What is the privilege leave policy?"
```

This function implements:

```text
RETRIEVE
   ↓
AUGMENT
   ↓
GENERATE
```

Let's see exactly where.

---

# 27. Get the LLM

First:

```python
rag_llm = hr_llm()
```

The function calls:

```text
hr_llm()
```

which returns the configured Claude integration.

So:

```text
hr_rag_response()
       ↓
hr_llm()
       ↓
Claude integration ready
```

---

# 28. RETRIEVE

Now:

```python
docs = index.similarity_search(question, k=3)
```

This is your **retrieval line**.

Let's break it down.

### `index`

Your FAISS vector-store object.

### `.similarity_search()`

Search for semantically relevant documents.

### `question`

Employee's query.

### `k=3`

Return three matching document chunks.

So:

```text
Question
   ↓
FAISS similarity_search
   ↓
Top 3 Relevant Documents
   ↓
docs
```

This is:

# R = RETRIEVE

---

# 29. What is inside `docs`?

Conceptually:

```text
docs = [
    Document(...),
    Document(...),
    Document(...)
]
```

Each returned document has content.

Your code needs the text:

```python
doc.page_content
```

So conceptually:

```text
Document
   │
   ├── page_content
   └── metadata
```

Your current prompt construction uses the `page_content`.

---

# 30. Build the context

Next:

```python
context = "\n\n".join(
    [doc.page_content for doc in docs]
)
```

This line may initially look difficult.

Let's simplify it.

First:

```python
[doc.page_content for doc in docs]
```

means:

> Go through each retrieved document and get its text.

So:

```text
docs

Document 1 → page_content → Text 1
Document 2 → page_content → Text 2
Document 3 → page_content → Text 3
```

Then:

```python
"\n\n".join(...)
```

combines them with blank lines.

Result:

```text
Text from Chunk 1

Text from Chunk 2

Text from Chunk 3
```

That becomes:

```python
context
```

---

# 31. AUGMENT

Now your code constructs:

```python
prompt = f"""Use the following HR policy context to answer the question.

Context:
{context}

Question: {question}

Answer:"""
```

This is extremely important.

Before:

```text
Question only
```

After:

```text
Instruction
+
Retrieved HR Policy Context
+
Employee Question
```

That's:

# A = AUGMENT

Your application is augmenting the model's input with retrieved information.

---

# 32. What would the actual prompt look like?

Suppose the employee asks:

```text
What is the privilege leave policy?
```

And FAISS retrieves three relevant chunks.

Your prompt becomes conceptually:

```text
Use the following HR policy context to answer the question.

Context:

[Relevant HR Policy Chunk 1]

[Relevant HR Policy Chunk 2]

[Relevant HR Policy Chunk 3]

Question:
What is the privilege leave policy?

Answer:
```

That's what Claude receives.

Not:

```text
"What is the privilege leave policy?"
```

alone.

That's the key difference between your RAG application and a basic direct LLM call.

---

# 33. GENERATE

Next:

```python
hr_rag_query = rag_llm.invoke(prompt)
```

This is your generation call.

Conceptually:

```text
RAG Prompt
   ↓
ChatBedrock
   ↓
Amazon Bedrock
   ↓
Claude Haiku 4.5
   ↓
AIMessage
```

This is:

# G = GENERATE

---

# 34. Extract the generated text

Finally:

```python
return hr_rag_query.content
```

`ChatBedrock.invoke()` returns a message object.

Conceptually:

```text
AIMessage
│
├── content
├── metadata
└── other information
```

You want the generated answer text.

So:

```python
hr_rag_query.content
```

extracts that content.

Then:

```text
Backend
   ↓
Answer text
   ↓
Streamlit
   ↓
Employee
```

---

# 35. Now identify RAG directly in your code

This is one of the most important things to learn from File 05.

If an interviewer opens your code and says:

> **“Show me where RAG happens.”**

You should immediately identify:

### R — Retrieval

```python
docs = index.similarity_search(question, k=3)
```

### A — Augmentation

```python
context = "\n\n".join(
    [doc.page_content for doc in docs]
)
```

and:

```python
prompt = f"""Use the following HR policy context to answer the question.

Context:
{context}

Question: {question}

Answer:"""
```

### G — Generation

```python
hr_rag_query = rag_llm.invoke(prompt)
```

That is your RAG pipeline **in actual code**.

---

# 36. Complete backend code mapped to responsibilities

```text
PyPDFLoader(...)
      ↓
KNOWLEDGE SOURCE

.load()
      ↓
LOAD DOCUMENT

RecursiveCharacterTextSplitter(...)
      ↓
CONFIGURE CHUNKING

split_documents(...)
      ↓
CREATE CHUNKS

BedrockEmbeddings(...)
      ↓
CONFIGURE TITAN

FAISS.from_documents(...)
      ↓
EMBED + CREATE VECTOR INDEX

return db_index
      ↓
SEARCHABLE KNOWLEDGE READY


ChatBedrock(...)
      ↓
CONFIGURE CLAUDE


similarity_search(question, k=3)
      ↓
RETRIEVE

doc.page_content
      ↓
EXTRACT RETRIEVED TEXT

join(...)
      ↓
BUILD CONTEXT

context + question
      ↓
AUGMENT

rag_llm.invoke(prompt)
      ↓
GENERATE

.content
      ↓
EXTRACT FINAL ANSWER
```

This is the code walkthrough in one picture.

---

# 37. What is good about this backend?

For a learning/PoC project, it is easy to understand because the RAG stages are explicit.

You can directly see:

```text
Load
↓
Split
↓
Embed
↓
Index
↓
Retrieve
↓
Prompt
↓
Generate
```

The code does not hide the entire RAG process behind one managed knowledge-base call.

That makes it useful for understanding what actually happens inside a RAG pipeline.

---

# 38. What are the current code limitations?

Understanding limitations demonstrates much stronger engineering knowledge than simply explaining happy-path code.

### 1. Hardcoded document source

The PDF URL is directly inside the function.

```text
Code
 ↓
Fixed URL
```

There's no configurable ingestion system.

### 2. Hardcoded AWS profile

```python
credentials_profile_name='default'
```

This is convenient locally but is not how you would ideally design AWS-hosted production authentication.

### 3. Hardcoded model configuration

Model IDs and generation parameters are directly in code.

A production system may externalize configuration.

### 4. In-memory FAISS

The vector index isn't implemented as centrally durable shared storage.

### 5. Limited error handling

The core functions don't show robust exception handling around:

```text
PDF download
Bedrock embedding calls
FAISS creation
Retrieval
Claude invocation
```

### 6. No source citations returned

You retrieve document objects but ultimately return:

```python
hr_rag_query.content
```

The frontend doesn't receive/display the supporting chunks or citations from this function.

### 7. No explicit “I don't know” control

The prompt says:

> Use the following HR policy context to answer the question.

But the current prompt doesn't contain a stronger explicit rule such as:

```text
If the answer is not present in the context,
say that the information is unavailable.
```

That would be worth considering in a production improvement.

---

# 39. Don't claim things the backend doesn't implement

From this code, do not claim:

```text
❌ Bedrock Knowledge Bases
❌ OpenSearch
❌ agents
❌ LangGraph
❌ reranking
❌ hybrid search
❌ metadata filtering
❌ conversation memory
❌ citations
❌ automatic document refresh
❌ authentication
❌ multi-document ingestion portal
```

The project analysis specifically distinguishes the implemented workflow from documented/future features. :chatgpt-content-reference{index="1"}

---

# 40. The three functions you must remember

Don't memorize every line first.

Remember:

```text
┌─────────────────────────────────────┐
│ hr_index()                          │
│                                     │
│ PDF → Split → Titan → FAISS         │
└─────────────────────────────────────┘

                 ↓

┌─────────────────────────────────────┐
│ hr_llm()                            │
│                                     │
│ Configure Claude via Bedrock        │
└─────────────────────────────────────┘

                 ↓

┌─────────────────────────────────────┐
│ hr_rag_response()                   │
│                                     │
│ Retrieve → Augment → Generate       │
└─────────────────────────────────────┘
```

If these three are clear, the backend becomes much easier.

---

# Interview Questions & Answers — `05-Backend-Code-Walkthrough.md`

## Q1. Can you explain your backend code?

### Word-to-word interview answer

> “My backend is implemented in `rag_backend.py`, and I organize it around three main functions: `hr_index()`, `hr_llm()`, and `hr_rag_response()`.
>
> `hr_index()` prepares the HR knowledge. It loads the HR Leave Policy PDF using PyPDFLoader, splits the document into chunks using RecursiveCharacterTextSplitter, configures Amazon Titan embeddings through Bedrock, and creates a FAISS vector index from those chunks.
>
> `hr_llm()` configures Claude Haiku 4.5 through Amazon Bedrock using ChatBedrock.
>
> Finally, `hr_rag_response()` handles the actual RAG request. It retrieves the top three relevant chunks from FAISS, combines their content into context, constructs a prompt containing that context and the user's question, invokes Claude, and returns the generated text.
>
> So the backend explicitly implements the load, split, embed, retrieve, augment and generate stages.”

---

## Q2. What does `hr_index()` do?

### Word-to-word interview answer

> “`hr_index()` builds the searchable HR knowledge index.
>
> It loads the HR Leave Policy PDF, splits the document into chunks, configures Titan embeddings through Amazon Bedrock and passes the chunks and embedding integration to `FAISS.from_documents()`.
>
> FAISS creates the searchable vector index, and the function returns that index to the frontend.”

---

## Q3. What does `hr_llm()` do?

### Word-to-word interview answer

> “`hr_llm()` configures the generation model.
>
> It creates a ChatBedrock object using Claude Haiku 4.5 and configures parameters including a maximum output token setting of 3000 and temperature of 0.1.
>
> It then returns the configured model integration to the RAG response function.”

---

## Q4. What does `hr_rag_response()` do?

### Word-to-word interview answer

> “`hr_rag_response()` implements the runtime RAG workflow.
>
> It receives the FAISS index and the user's question, obtains the configured Claude model, performs a FAISS similarity search with k equal to three, extracts and combines the retrieved document content, constructs a prompt containing the context and question, invokes Claude and returns the generated response content.”

---

## Q5. Show me where retrieval happens in your code.

### Word-to-word interview answer

> “Retrieval happens in this line: `index.similarity_search(question, k=3)`.
>
> The application uses the user's question to search the FAISS index and requests the top three relevant document chunks.
>
> Those returned documents are then used as context for generation.”

---

## Q6. Show me where augmentation happens.

### Word-to-word interview answer

> “Augmentation happens after retrieval.
>
> First, I extract the `page_content` from the retrieved documents and join them into a context string.
>
> Then I construct a prompt containing that retrieved context together with the user's question.
>
> That step augments the model input with information retrieved from the HR policy.”

---

## Q7. Show me where generation happens.

### Word-to-word interview answer

> “Generation happens when I call `rag_llm.invoke(prompt)`.
>
> The constructed prompt is sent through ChatBedrock to the configured Claude model on Amazon Bedrock.
>
> Claude generates the response, and I return the text from the message's `content` property.”

---

## Q8. What does `k=3` mean?

### Word-to-word interview answer

> “`k=3` means the similarity search requests three relevant document chunks from FAISS.
>
> Those three chunks are then combined and used as context for Claude.
>
> Three is simply the current project configuration. I would evaluate the optimal retrieval count using representative questions rather than assuming three is universally best.”

---

## Q9. Why do you use `doc.page_content`?

### Word-to-word interview answer

> “FAISS returns LangChain document objects rather than only raw strings.
>
> The actual textual content of each retrieved document is available through `page_content`.
>
> I extract that text from the retrieved documents and combine it into the context that I provide to Claude.”

---

## Q10. Why do you use `"\n\n".join()`?

### Word-to-word interview answer

> “I retrieve multiple document chunks, so I need to combine their text into one context string.
>
> `join()` combines the retrieved `page_content` values, and the two newline characters separate the chunks with blank lines to keep the context readable.”

---

## Q11. What does `FAISS.from_documents()` do in your code?

### Word-to-word interview answer

> “I pass the document chunks and the Bedrock embedding integration to `FAISS.from_documents()`.
>
> The document chunks are converted into embeddings using the configured Titan embedding model, and FAISS builds the vector index used later for similarity retrieval.”

---

## Q12. Why do you return `.content`?

### Word-to-word interview answer

> “The ChatBedrock invocation returns an AI message object rather than only a plain text string.
>
> The generated answer text is available in the object's `content` field, so my function returns `hr_rag_query.content` to the frontend.”

---

## Q13. Why did you separate `hr_index()` and `hr_rag_response()`?

### Word-to-word interview answer

> “They have different responsibilities.
>
> `hr_index()` prepares the knowledge base for retrieval by loading, chunking, embedding and indexing the HR policy.
>
> `hr_rag_response()` handles an individual user question using an already prepared index.
>
> Separating them also makes it possible to reuse the index instead of rebuilding the document-processing pipeline for every question within the session.”

---

## Q14. Is the PDF path configurable?

### Word-to-word interview answer

> “Not in the current implementation. The HR Leave Policy URL is hardcoded inside `hr_index()`.
>
> That is acceptable for the current proof of concept, but for production I would move document-source configuration outside the code and build a controlled ingestion and versioning process.”

---

## Q15. How does your code authenticate to Bedrock?

### Word-to-word interview answer

> “The current Bedrock integrations specify `credentials_profile_name='default'`.
>
> That means the application expects an AWS default profile with the required permissions.
>
> This is convenient for local development, but on AWS infrastructure I would prefer IAM role-based temporary credentials rather than depending on locally configured long-term credentials.”

---

## Q16. Does your backend use Bedrock Knowledge Bases?

### Word-to-word interview answer

> “No.
>
> The RAG workflow is explicitly implemented in my Python code.
>
> I load and split the document, use Titan embeddings, create the FAISS index, perform similarity retrieval, construct the context and prompt, and then invoke Claude.
>
> Amazon Bedrock Knowledge Bases is not part of this backend.”

---

## Q17. What happens if the PDF fails to load?

### Word-to-word interview answer

> “In the current backend, robust exception handling around the PDF-loading stage is not implemented.
>
> So a PDF-loading failure can interrupt index creation.
>
> For production, I would add structured exception handling, logging, retries where appropriate and a clear user-facing error rather than allowing the request to fail without useful diagnostics.”

---

## Q18. What happens if Bedrock fails?

### Word-to-word interview answer

> “The current code also has limited error handling around Bedrock calls.
>
> A failure could happen because of credentials, IAM permissions, region or model access, network issues, throttling or service errors.
>
> In production I would classify those failures, add logging and metrics, use appropriate retry and timeout strategies, and avoid exposing raw internal errors to users.”

---

## Q19. What would you improve in this backend for production?

### Word-to-word interview answer

> “I would improve several areas.
>
> I would externalize configuration such as the document source and model settings, replace session-specific indexing with a shared and versioned knowledge index where appropriate, use IAM roles for AWS-hosted authentication, add robust exception handling and structured logging, improve the prompt's grounding behavior, preserve source metadata and citations, add RAG evaluation, and introduce observability around retrieval and model calls.
>
> I would make those changes based on actual production requirements rather than adding services unnecessarily.”

---

## Q20. Can you explain your backend in 30 seconds?

### Word-to-word interview answer

> “My backend has three main functions. `hr_index()` loads the HR policy, chunks it, creates Titan embeddings and builds the FAISS index. `hr_llm()` configures Claude Haiku 4.5 through Amazon Bedrock. `hr_rag_response()` retrieves the top three relevant policy chunks from FAISS, combines them with the user's question, constructs the RAG prompt, invokes Claude and returns the generated answer to Streamlit.”

---

# Most important code interview question

An interviewer could show you this:

```python
docs = index.similarity_search(question, k=3)

context = "\n\n".join(
    [doc.page_content for doc in docs]
)

prompt = f"""Use the following HR policy context to answer the question.

Context:
{context}

Question: {question}

Answer:"""

hr_rag_query = rag_llm.invoke(prompt)
```

and ask:

> **“Explain these lines.”**

Your mental response should immediately be:

```text
similarity_search()
        ↓
RETRIEVE

page_content + join()
        ↓
PREPARE CONTEXT

context + question
        ↓
AUGMENT

invoke(prompt)
        ↓
GENERATE
```

## Five questions to master first

Focus on these before trying to memorize all 20:

**Q1. Explain your backend code.**

**Q2. What does `hr_index()` do?**

**Q4. What does `hr_rag_response()` do?**

**Q5–Q7. Show me retrieval, augmentation and generation in your actual code.**

**Q19. What would you improve for production?**

The single most important thing to remember from `05-Backend-Code-Walkthrough.md` is:

```text
hr_index()
    ↓
PDF → LOAD → CHUNK → EMBED → FAISS

hr_llm()
    ↓
CONFIGURE CLAUDE

hr_rag_response()
    ↓
RETRIEVE → AUGMENT → GENERATE
```

If you can open `rag_backend.py` and explain **why every major line exists**, then you are no longer just saying that you built a RAG project—you can actually defend its implementation in an interview.