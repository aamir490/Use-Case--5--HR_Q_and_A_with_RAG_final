# `02-Current-Architecture.md`

## NovaMindAI HR Q&A — Current Architecture

In `01-Project-Overview.md`, we understood **what the project does and why it exists**.

Now we answer:

> **“What is the current architecture of my HR Q&A application, and how do all the components connect?”**

The most important rule for this file is:

> **We will explain the architecture that is actually implemented, not the more advanced architecture we might build later.**

The Codex analysis identifies the application as a **single-process Python/Streamlit RAG proof of concept**, with Streamlit as the UI, Python functions as the application/RAG logic, a remote HR PDF as the knowledge source, Titan embeddings, an in-memory FAISS index, and Claude through Bedrock. :chatgpt-content-reference{index="0"}

---

# 1. What does “architecture” mean?

Before studying your architecture, understand the word.

**Software architecture** describes:

- what components exist
- what responsibility each component has
- how the components communicate
- how data moves through the system

For your project, architecture answers:

> “When an employee asks an HR question, which components are involved and what does each component do?”

---

# 2. Current architecture at a glance

![Current architecture](images\current_architecture.png)

Your architecture can be understood like this:

```text
                         NovaMindAI HR Q&A
                     CURRENT IMPLEMENTATION

┌──────────────────────────────────────────────────────────────┐
│                         USER                                 │
│                           │                                  │
│                           ▼                                  │
│                   Streamlit Frontend                         │
│                   rag_frontend.py                            │
│                           │                                  │
│                           ▼                                  │
│                    Python RAG Backend                        │
│                     rag_backend.py                           │
│                                                              │
│    ┌──────────────── DOCUMENT PROCESSING ────────────────┐   │
│    │                                                     │   │
│    │ HR Leave Policy PDF                                 │   │
│    │       ↓                                             │   │
│    │ PyPDFLoader                                         │   │
│    │       ↓                                             │   │
│    │ RecursiveCharacterTextSplitter                      │   │
│    │       ↓                                             │   │
│    │ Text Chunks                                         │   │
│    │       ↓                                             │   │
│    │ Amazon Titan Embeddings ← Amazon Bedrock            │   │
│    │       ↓                                             │   │
│    │ FAISS Vector Index                                  │   │
│    └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│                           │                                  │
│                    USER QUESTION                             │
│                           ↓                                  │
│                 FAISS Similarity Search                      │
│                           ↓                                  │
│                 Top 3 Relevant Chunks                        │
│                           ↓                                  │
│                 Context + User Question                      │
│                           ↓                                  │
│                 Claude Haiku 4.5                             │
│                  Amazon Bedrock                              │
│                           ↓                                  │
│                    Generated Answer                          │
│                           ↓                                  │
│                    Streamlit UI                              │
└──────────────────────────────────────────────────────────────┘
```

The Codex analysis confirms this manual RAG sequence: document loading → splitting → Titan embeddings → FAISS indexing → top-3 similarity retrieval → context construction → Claude generation. :chatgpt-content-reference{index="1"}

---

# 3. The architecture actually has two flows

This is one of the most important things to understand.

Don't think of the project as one giant flow.

Think:

```text
                  HR RAG APPLICATION

             ┌────────────┴────────────┐
             ↓                         ↓
       INDEXING FLOW               QUERY FLOW

PDF → chunks → embeddings       Question
          ↓                        ↓
        FAISS                  Search FAISS
                                  ↓
                            Relevant chunks
                                  ↓
                              Claude
                                  ↓
                               Answer
```

These flows have different purposes.

### Indexing flow

Prepare the HR policy so it can be searched.

### Query flow

Use the prepared index to answer an employee's question.

This distinction will make the entire project much easier to explain.

---

# 4. Component 1 — User / Employee

The first component is simply the person using the application.

For example:

> “How many privilege leave days are allowed?”

The user does not interact directly with:

```text
FAISS
Titan
Claude API
PyPDFLoader
Python functions
```

The user interacts with:

**Streamlit.**

---

# 5. Component 2 — Streamlit frontend

Your frontend file is:

```text
rag_frontend.py
```

Streamlit provides the web interface.

Its responsibility includes:

```text
Display application
        ↓
Accept employee question
        ↓
Validate that question isn't empty
        ↓
Call backend RAG function
        ↓
Receive answer
        ↓
Display answer
```

Conceptually:

```text
Employee
   ↓
Streamlit
   ↓
Python RAG Backend
   ↓
Answer
   ↓
Streamlit
   ↓
Employee
```

### Important distinction

Streamlit does **not** perform the actual semantic search itself.

Streamlit does **not** generate embeddings itself.

Streamlit does **not** generate the final AI answer itself.

It is primarily your **application/UI layer**.

---

# 6. Component 3 — `rag_backend.py`

This is the core RAG implementation.

Your backend contains three particularly important functions:

```text
hr_index()
hr_llm()
hr_rag_response()
```

Think of their responsibilities like this:

```text
hr_index()
    ↓
Prepare searchable HR knowledge

hr_llm()
    ↓
Configure Claude

hr_rag_response()
    ↓
Retrieve relevant HR information
and generate an answer
```

We'll study the code line-by-line in:

**`05-Backend-Code-Walkthrough.md`**

For architecture, you only need to understand their roles.

---

# 7. Component 4 — HR Leave Policy PDF

Your RAG system needs a source of knowledge.

The current backend uses an HR Leave Policy PDF.

Conceptually:

```text
HR Leave Policy
      ↓
RAG knowledge source
```

The important point is:

> **The PDF is the document being prepared for retrieval.**

Your current architecture does not have an implemented document-management platform where HR users upload many documents.

---

# 8. Component 5 — PyPDFLoader

The PDF cannot simply be placed into FAISS directly.

First, the application needs to extract text.

Your project uses:

```python
PyPDFLoader
```

Conceptually:

```text
HR Policy PDF

     ↓

PyPDFLoader

     ↓

Extracted text/pages
```

PyPDFLoader is therefore part of the:

**document ingestion / processing stage.**

---

# 9. Component 6 — RecursiveCharacterTextSplitter

After extracting the PDF text, your application doesn't treat the entire document as one giant piece of text.

It splits it into smaller pieces called:

**chunks**

Your project uses:

```python
RecursiveCharacterTextSplitter
```

with:

```text
chunk_size = 1000
chunk_overlap = 100
```

Conceptually:

```text
Large HR Policy
       ↓
Text Splitter
       ↓
┌──────────┐
│ Chunk 1  │
└──────────┘
┌──────────┐
│ Chunk 2  │
└──────────┘
┌──────────┐
│ Chunk 3  │
└──────────┘
    ...
```

Why?

Because retrieval needs smaller searchable units.

We'll study why `1000` and `100` matter in:

**`09-Chunking-and-Document-Processing.md`**

---

# 10. Component 7 — Amazon Titan Embeddings

Now we have text chunks.

But FAISS searches vectors.

So we need to convert text into numerical representations.

Your architecture uses:

**Amazon Titan Embeddings through Amazon Bedrock.**

Conceptually:

```text
Text Chunk

"Employees are eligible for..."

           ↓

Amazon Titan Embeddings
via Amazon Bedrock

           ↓

Vector

[0.13, -0.28, 0.74, ...]
```

The embedding captures semantic information about the text in numerical form.

The project analysis identifies Titan embeddings as part of the implemented RAG path. :chatgpt-content-reference{index="2"}

---

# 11. Component 8 — FAISS

Once the document chunks become embeddings, they are indexed in:

**FAISS**

FAISS is your vector search component.

Conceptually:

```text
Chunk 1 → Vector 1 ┐
Chunk 2 → Vector 2 ├──→ FAISS
Chunk 3 → Vector 3 ┘
```

Now you have something that can be searched semantically.

This is important:

> **FAISS is not generating the answer.**

FAISS's job is retrieval.

Claude's job is generation.

Remember:

```text
FAISS
  ↓
RETRIEVAL

Claude
  ↓
GENERATION
```

---

# 12. Where is FAISS running?

In your current implementation, FAISS is **inside the Python application process**.

This is different from using a remote service such as:

```text
OpenSearch
Pinecone
Qdrant
another external vector database
```

Conceptually:

```text
Python / Streamlit Process
│
├── Application logic
│
├── LangChain integrations
│
└── FAISS index in memory
```

The FAISS index isn't implemented as an independently deployed vector database service.

That distinction becomes very important when discussing scalability.

---

# 13. Component 9 — Streamlit session state

Your frontend contains an important architectural behavior.

Conceptually:

```python
if 'vector_index' not in st.session_state:
    st.session_state.vector_index = demo.hr_index()
```

This means:

```text
Session begins
      ↓
Does vector_index exist?
      ↓
     NO
      ↓
Build index
      ↓
Store in session_state
```

Later:

```text
User asks another question
      ↓
vector_index already exists
      ↓
Reuse it
```

This avoids rebuilding the index on every Streamlit rerun **within that session**.

But remember:

> **Session state is not a central persistent vector database.**

And:

> **Session state is not conversation memory.**

---

# 14. Now the query flow begins

Suppose the employee asks:

> “How many privilege leave days are allowed?”

Streamlit sends this question to your backend:

```text
Employee Question
        ↓
rag_frontend.py
        ↓
hr_rag_response(
    index=vector_index,
    question=input_text
)
```

Now the RAG query process begins.

---

# 15. Component 10 — Similarity search

The backend performs:

```python
index.similarity_search(question, k=3)
```

Meaning:

```text
Employee Question
       ↓
Embedding/search process
       ↓
Compare against indexed policy chunks
       ↓
Retrieve top 3 relevant chunks
```

`k=3` means:

> Retrieve three matching chunks.

So if the question is about privilege leave, FAISS tries to return chunks semantically related to privilege leave.

---

# 16. Component 11 — Context construction

After retrieving the documents, your application extracts their text.

Conceptually:

```text
Relevant Chunk 1
       +
Relevant Chunk 2
       +
Relevant Chunk 3
       ↓
Retrieved Context
```

Then the backend constructs a prompt containing:

```text
Instruction
+
Retrieved HR Policy Context
+
User Question
```

This is the **augmentation** part of RAG.

---

# 17. Component 12 — Claude Haiku 4.5

The prompt is then sent to:

**Claude Haiku 4.5 through Amazon Bedrock.**

Your project configures Claude with values including:

```text
temperature = 0.1
max_tokens = 3000
```

Conceptually:

```text
Retrieved HR Policy Context
            +
Employee Question
            ↓
     Claude Haiku 4.5
      Amazon Bedrock
            ↓
     Generated Answer
```

Important:

Claude isn't searching FAISS.

Your Python application already performed retrieval.

Claude receives the context your application constructed.

---

# 18. Bedrock has two roles

This architecture point is easy to miss.

Amazon Bedrock is involved in two different places:

```text
                  AMAZON BEDROCK

             ┌──────────┴──────────┐
             ↓                     ↓

      Titan Embeddings      Claude Haiku 4.5
             ↓                     ↓
     Vector creation          Generation
```

So if an interviewer asks:

> “Where are you using Amazon Bedrock?”

don't answer only:

> “For Claude.”

Your project also uses Bedrock for Titan embeddings.

---

# 19. Complete indexing architecture

Now combine everything we've learned.

```text
              INDEXING / PREPARATION FLOW

HR Leave Policy PDF
        │
        ▼
    PyPDFLoader
        │
        ▼
Extracted Documents
        │
        ▼
RecursiveCharacterTextSplitter
        │
        │ chunk_size = 1000
        │ chunk_overlap = 100
        ▼
     Text Chunks
        │
        ▼
Amazon Titan Embeddings
   via Amazon Bedrock
        │
        ▼
     Embeddings
        │
        ▼
      FAISS
        │
        ▼
In-Memory Vector Index
        │
        ▼
Streamlit Session State
```

---

# 20. Complete query architecture

Now the second half:

```text
                    QUERY FLOW

Employee
   │
   ▼
Streamlit
   │
   ▼
Employee Question
   │
   ▼
hr_rag_response()
   │
   ▼
FAISS Similarity Search
   │
   │ k = 3
   ▼
Top 3 Relevant Policy Chunks
   │
   ▼
Build Context
   │
   ▼
Context + Question
   │
   ▼
Claude Haiku 4.5
Amazon Bedrock
   │
   ▼
AIMessage
   │
   ▼
.content
   │
   ▼
Streamlit
   │
   ▼
Employee sees answer
```

That is the architecture you need to be able to explain.

---

# 21. What is NOT in the current architecture?

This is just as important.

Do not accidentally add:

```text
❌ API Gateway
❌ Lambda
❌ Bedrock Knowledge Base
❌ OpenSearch
❌ DynamoDB
❌ S3 vector persistence
❌ ECS
❌ EKS
❌ Kubernetes
❌ Application Load Balancer
❌ LangGraph
❌ AI Agents
❌ SharePoint integration
❌ CI/CD
```

to your explanation of the **current implementation**.

The Codex analysis specifically separates implemented components from documented, future, or absent components. :chatgpt-content-reference{index="3"}

---

# 22. What about EC2?

This requires careful wording.

Your repository contains **EC2 deployment documentation**.

That means you can study:

```text
Streamlit Application
        ↓
EC2 hosting
        ↓
Port 8501
```

as the documented deployment approach.

But the Codex analysis could not verify a currently running live EC2 deployment.

Therefore don't say:

> “The production application is currently deployed on EC2.”

unless you have independently verified that deployment.

Better:

> “The repository includes a documented EC2 deployment approach for hosting the Streamlit application, while the inspected project itself does not provide evidence of a currently running production deployment.”

We will study this properly in `17-Deployment-and-EC2.md`.

---

# 23. What about SharePoint?

Some architecture/documentation material references SharePoint or document-upload ideas.

But the current application code does not implement that ingestion path.

Current:

```text
Fixed remote HR policy PDF
        ↓
PyPDFLoader
```

Not current:

```text
SharePoint
    ↓
Automatic ingestion
    ↓
RAG
```

Codex specifically flagged this architecture/documentation mismatch. :chatgpt-content-reference{index="4"}

---

# 24. Architecture classification

If an interviewer asks:

> “What kind of architecture is this?”

A safe description is:

> **A single-process Streamlit-based RAG proof-of-concept architecture using Amazon Bedrock for embeddings and LLM inference and FAISS for in-memory vector retrieval.**

Don't call it:

```text
Microservices architecture ❌
Serverless architecture ❌
Event-driven architecture ❌
Multi-agent architecture ❌
Distributed RAG platform ❌
```

based on the current implementation.

---

# 25. Architecture responsibility map

This is worth understanding very clearly:

| Component | Responsibility |
|---|---|
| Streamlit | User interface |
| `rag_frontend.py` | UI + session-state coordination |
| `rag_backend.py` | Core RAG logic |
| HR Leave Policy PDF | Knowledge source |
| PyPDFLoader | PDF text extraction |
| RecursiveCharacterTextSplitter | Chunking |
| Amazon Titan | Embeddings |
| Amazon Bedrock | Managed access to Titan/Claude |
| FAISS | Vector indexing + similarity retrieval |
| Claude Haiku 4.5 | Answer generation |
| `st.session_state` | Keeps vector index during Streamlit session |

---

# 26. One architecture sentence

You should eventually be able to say:

> **“My current architecture is a Python and Streamlit RAG application where an HR policy PDF is loaded and chunked, Amazon Titan generates embeddings, FAISS stores and retrieves the relevant vectors, and the top three retrieved policy chunks are combined with the user's question and sent to Claude Haiku 4.5 through Amazon Bedrock to generate the final answer.”**

If you understand that sentence rather than memorize it, you understand the basic architecture.

---
---




# Explanation of the Current Architecture — NovaMindAI HR Q&A RAG


![Current architecture](images\current_architecture.png)


Yes. The easiest way to understand this diagram is to **not try to understand everything at once**.

Your architecture has **two main flows**:

```text
1. DOCUMENT INDEXING FLOW
   "Prepare the HR policy so it can be searched."

2. USER QUERY / RAG FLOW
   "Use that prepared knowledge to answer an employee's question."
```

That distinction is the key to the whole diagram.

---

## 1. First Flow — Document Indexing / Knowledge Preparation

Look at the **top part** of your diagram.

It starts here:

```text
HR Leave Policy PDF
        ↓
PyPDFLoader
        ↓
Extracted Text
        ↓
Text Splitter
        ↓
Text Chunks
        ↓
Titan Embeddings
        ↓
FAISS
```

Let's understand why each step exists.

### Step 1 — HR Leave Policy PDF

This is your application's **knowledge source**.

For example, imagine the PDF contains:

> Employees are entitled to a certain number of privilege leave days...

Your application needs this company-specific information so it can answer HR questions.

At this stage:

```text
HR Leave Policy PDF
        ↓
Contains the knowledge
```

---

## 2. PyPDFLoader

Next comes:

```text
HR Policy PDF
      ↓
PyPDFLoader
```

The PDF is a document file. Your RAG pipeline needs usable text from it.

`PyPDFLoader` loads the PDF and extracts its textual content.

Think:

```text
PDF file
   ↓
PyPDFLoader
   ↓
Python-readable document text
```

So if an interviewer asks:

**“Why do you need PyPDFLoader?”**

You can say:

> “I use PyPDFLoader to load the HR Leave Policy PDF and extract its textual content so that it can be processed by the RAG pipeline.”

---

# 3. RecursiveCharacterTextSplitter

Now you have the document text.

But imagine the entire policy is very large.

Instead of treating the whole document as one huge piece of text, your application splits it into smaller pieces.

```text
Large HR Policy Text
        ↓
RecursiveCharacterTextSplitter
        ↓
Chunk 1
Chunk 2
Chunk 3
Chunk 4
...
```

Your configuration is:

```text
chunk_size = 1000
chunk_overlap = 100
```

For now, understand it simply as:

**Chunk size 1000** → approximately how large each chunk is allowed to be according to the splitter's length measurement.

**Overlap 100** → neighboring chunks retain some overlapping text to reduce the chance of losing useful context at a chunk boundary.

We'll study the exact behavior later in `09-Chunking-and-Document-Processing.md`.

---

# 4. Why do we need chunks?

Suppose your HR policy discusses:

```text
Page/Section A → Sick Leave
Page/Section B → Privilege Leave
Page/Section C → Maternity Leave
Page/Section D → Holiday Policy
```

And the employee asks:

> “What is the privilege leave policy?”

You don't necessarily want to give the entire policy to Claude.

You want to retrieve the **relevant portions**.

So:

```text
Large Document
      ↓
Smaller searchable chunks
```

This is why chunking is important.

---

# 5. Amazon Titan Embeddings

Now we have text chunks.

But FAISS performs vector similarity search.

Therefore the chunks need numerical representations.

Your architecture sends the chunks to:

**Amazon Titan Embeddings through Amazon Bedrock.**

```text
Text Chunk
    ↓
Amazon Bedrock
    ↓
Titan Embeddings
    ↓
Vector
```

For example, conceptually:

```text
"Employees can carry forward privilege leave..."

                ↓

         Titan Embeddings

                ↓

[0.18, -0.42, 0.73, 0.11, ...]
```

Don't worry about the numbers themselves.

The important idea is:

> **Embeddings convert text into numerical vectors that represent semantic meaning, allowing semantically similar text to be found.**

---

# 6. What is Amazon Bedrock doing here?

This diagram shows something very important.

Bedrock is used **twice**.

First:

```text
Text Chunks
     ↓
Amazon Bedrock
     ↓
Titan Embeddings
     ↓
Vectors
```

Later:

```text
Context + Question
       ↓
Amazon Bedrock
       ↓
Claude Haiku 4.5
       ↓
Answer
```

So remember:

> **Bedrock provides access to the embedding model and the generation model in this project.**

---

# 7. FAISS Vector Index

Titan creates embeddings.

Those vectors are then indexed in:

**FAISS**

```text
Chunk 1 → Embedding 1 ┐
Chunk 2 → Embedding 2 ├──→ FAISS
Chunk 3 → Embedding 3 ┘
```

FAISS lets your application search for semantically relevant document chunks.

Very important distinction:

```text
FAISS = Retrieval
Claude = Generation
```

FAISS doesn't write the final HR answer.

Claude doesn't directly search the FAISS database by itself.

Your Python code connects these steps.

---

# 8. Streamlit Session State

The diagram then shows:

```text
FAISS Vector Index
        ↓
Streamlit Session State
```

Your application stores a reference to the generated index in:

```python
st.session_state.vector_index
```

Why?

Because Streamlit reruns your Python script when users interact with the UI.

Without keeping the index in session state, you could unnecessarily recreate it on every interaction.

So conceptually:

```text
First interaction/session initialization

Is vector_index available?
        ↓
       No
        ↓
Build FAISS index
        ↓
Save in session_state
```

Later:

```text
Another question
      ↓
Index already exists
      ↓
Reuse index
```

### Important

This does **not** mean:

```text
Session State = permanent database ❌
Session State = conversation memory ❌
```

It's session-level application state.

---

# Now Flow 2 — User Query / RAG Inference

Now look at the **bottom part** of your diagram.

This is where the employee actually asks something.

The basic flow is:

```text
Employee
   ↓
Streamlit
   ↓
Question
   ↓
Python Backend
   ↓
FAISS
   ↓
Top 3 Chunks
   ↓
Context + Question
   ↓
Claude
   ↓
Answer
   ↓
Streamlit
   ↓
Employee
```

Now let's understand it.

---

# 9. Employee asks a question

Suppose the employee enters:

> “What is the privilege leave policy?”

The employee interacts with:

**Streamlit Web UI — `rag_frontend.py`**

So:

```text
Employee
    ↓
Streamlit
    ↓
"What is the privilege leave policy?"
```

Streamlit itself doesn't answer the question.

It passes the question to your RAG logic.

---

# 10. Python RAG Backend

The diagram shows:

```text
rag_backend.py

hr_index()
hr_llm()
hr_rag_response()
```

Think of them at a high level:

### `hr_index()`

Builds the searchable HR knowledge index.

```text
PDF
→ Chunk
→ Embed
→ FAISS
```

### `hr_llm()`

Configures the Claude model connection.

### `hr_rag_response()`

Handles the main question-answering flow.

```text
Question
→ Retrieve
→ Build Prompt
→ Claude
→ Answer
```

We'll open and understand these functions line-by-line in `05-Backend-Code-Walkthrough.md`.

---

# 11. R — RETRIEVE

Now we reach the first part of **RAG**.

The backend performs:

```python
docs = index.similarity_search(question, k=3)
```

Conceptually:

```text
Question:
"What is the privilege leave policy?"

             ↓

        Search FAISS

             ↓

Compare semantic relevance

             ↓

Top 3 Relevant Chunks
```

`k=3` means:

> **Retrieve the three most relevant matching chunks returned by this similarity search.**

This is:

# RETRIEVAL

---

# 12. A — AUGMENT

Now you have:

```text
Employee Question

+

3 Retrieved HR Policy Chunks
```

Your application combines the retrieved chunk text into context.

Conceptually:

```text
Context:

Chunk 1
+
Chunk 2
+
Chunk 3

Question:
"What is the privilege leave policy?"
```

Then your code constructs a prompt similar to:

```text
Use the following HR policy context to answer the question.

Context:
[Retrieved HR Policy Information]

Question:
[Employee Question]

Answer:
```

This is:

# AUGMENTATION

You're augmenting the LLM's input with retrieved information.

---

# 13. G — GENERATE

Now:

```text
Retrieved Context
       +
Employee Question
       ↓
Claude Haiku 4.5
       ↓
Generated Answer
```

Claude receives the constructed prompt through Amazon Bedrock.

Claude reads:

1. your instruction
2. retrieved HR policy context
3. employee's question

and generates the response.

This is:

# GENERATION

---

# 14. The entire RAG concept is now visible

Your diagram makes RAG very easy to explain:

```text
R — RETRIEVE

Question
   ↓
FAISS
   ↓
Top 3 relevant chunks


A — AUGMENT

Retrieved chunks
       +
User question
       ↓
RAG Prompt


G — GENERATE

RAG Prompt
    ↓
Claude Haiku 4.5
    ↓
Answer
```

So if an interviewer asks:

> **“Where exactly is RAG happening in your project?”**

A strong answer is:

> “RAG happens in three stages. First, I retrieve the top three relevant HR policy chunks from FAISS. Second, I augment the prompt by combining those retrieved chunks with the user's question. Third, I send that prompt to Claude Haiku 4.5 through Amazon Bedrock to generate the final answer.”

---

# 15. Very important — Claude does NOT search the PDF

This is one of the most important architecture concepts.

Don't imagine:

```text
Question
   ↓
Claude
   ↓
Claude searches PDF
   ↓
Answer
```

❌ That's not your architecture.

Your architecture is:

```text
Question
   ↓
Your Python Application
   ↓
FAISS Retrieval
   ↓
Relevant Policy Chunks
   ↓
Your Python Application
   ↓
Construct Prompt
   ↓
Claude
   ↓
Answer
```

So **your application orchestrates the RAG process**.

---

# 16. Where does LangChain fit?

You may notice the architecture title includes LangChain, but there isn't a huge “LangChain server.”

That's because LangChain is not a separate cloud service here.

Your Python application uses LangChain ecosystem components/integrations such as:

```text
Python Application
│
├── PyPDFLoader
│
├── RecursiveCharacterTextSplitter
│
├── BedrockEmbeddings
│
├── FAISS integration
│
└── ChatBedrock
```

So:

> **LangChain helps connect and implement components of the RAG pipeline inside your Python application.**

It isn't another server between Streamlit and AWS.

---

# 17. Where is AWS in this architecture?

This is also important for your AWS Generative AI interviews.

Your application isn't entirely running inside AWS simply because you're using Bedrock.

The clear AWS dependency in this diagram is:

```text
             AMAZON BEDROCK
                   │
        ┌──────────┴──────────┐
        ↓                     ↓
Titan Embeddings       Claude Haiku 4.5
        ↓                     ↓
Embeddings             Generation
```

Meanwhile, FAISS is part of the Python application architecture.

Don't call FAISS an AWS service.

---

# 18. One complete example

Let's walk through an employee question from beginning to end.

### Before the employee asks anything

```text
HR Leave Policy PDF
        ↓
PyPDFLoader
        ↓
Extract text
        ↓
Split into chunks
        ↓
Titan Embeddings
        ↓
Vectors
        ↓
FAISS Index
```

Knowledge is now searchable.

### Employee asks:

> “What is the privilege leave policy?”

Then:

```text
Employee
   ↓
Streamlit
   ↓
"What is the privilege leave policy?"
   ↓
rag_backend.py
   ↓
FAISS similarity search
   ↓
Top 3 relevant policy chunks
   ↓
Combine chunks
   ↓
Add employee question
   ↓
Construct RAG prompt
   ↓
Claude Haiku 4.5
   ↓
Generated answer
   ↓
Streamlit
   ↓
Employee
```

That's your entire project at the architecture level.

---

# 19. How to explain this diagram in an interview

If an interviewer puts this diagram in front of you and says:

> **“Walk me through this architecture.”**

You can say:

> “Sure. I divide the architecture into two main flows: document indexing and user query processing.
>
> In the document indexing flow, the application loads the HR Leave Policy PDF using PyPDFLoader. I then use RecursiveCharacterTextSplitter to split the extracted text into smaller overlapping chunks, with a chunk size of 1000 and overlap of 100.
>
> These chunks are converted into embeddings using Amazon Titan through Amazon Bedrock. The resulting vectors are indexed in FAISS, which is an in-memory vector search component in my current implementation. The FAISS index is kept in Streamlit session state so it can be reused within that session.
>
> The second part is the query flow. An employee enters an HR policy question through the Streamlit interface. My Python backend takes that question and performs a similarity search against FAISS with k equal to three.
>
> FAISS returns the top three relevant policy chunks. I combine those chunks with the user's question to construct the RAG prompt.
>
> That prompt is then sent to Claude Haiku 4.5 through Amazon Bedrock. Claude generates the answer using the retrieved HR policy context, and the result is returned to Streamlit and displayed to the employee.
>
> So, in terms of RAG, FAISS performs retrieval, my application performs augmentation by constructing the context-based prompt, and Claude performs generation.”

That's an excellent architecture explanation **because every part maps back to something visible in your diagram and current implementation**.

---

# One thing I would correct in the generated diagram

There is one label you should be careful with.

The diagram currently says:

> **“Python / Streamlit RAG Application (Local or EC2)”**

For a strict **Current Implementation** diagram, I would prefer:

> **“Python / Streamlit RAG Application”**

because your repository contains EC2 deployment instructions, but that does not by itself prove the currently inspected application is live on EC2.

So when speaking in an interview, don't use the diagram to claim a verified live EC2 deployment unless you have actually deployed and verified it.

---

## Your mental model

Don't memorize the whole diagram.

First memorize this:

```text
INDEXING

PDF
 ↓
Load
 ↓
Chunk
 ↓
Embed
 ↓
FAISS


QUERY

Question
 ↓
FAISS
 ↓
Retrieve Top 3
 ↓
Context + Question
 ↓
Claude
 ↓
Answer
```

And then remember:

> **Titan = Embeddings**  
> **FAISS = Retrieval**  
> **Python = Orchestration + Augmentation**  
> **Claude = Generation**  
> **Streamlit = User Interface**  
> **Bedrock = Managed access to Titan and Claude**

If these six relationships are clear in your mind, you already understand the core architecture rather than just memorizing the picture.

---
---
# Interview Questions & Answers — `02-Current-Architecture.md`

Now we connect what you learned directly to interview speaking.

---

## Q1. Can you explain the architecture of your HR Q&A project?

### Word-to-word interview answer

> “My project uses a relatively simple RAG architecture built with Python and Streamlit.
>
> On the document-processing side, the application loads an HR Leave Policy PDF using PyPDFLoader and splits the extracted text into overlapping chunks using RecursiveCharacterTextSplitter.
>
> Those chunks are converted into embeddings using Amazon Titan through Amazon Bedrock, and the resulting vectors are indexed in FAISS.
>
> On the query side, the employee asks a question through the Streamlit interface. The backend performs a similarity search against FAISS and retrieves the top three relevant policy chunks.
>
> I combine those retrieved chunks with the user's question and send the resulting prompt to Claude Haiku 4.5 through Amazon Bedrock.
>
> Claude generates the answer, and Streamlit displays it back to the user.
>
> The current architecture is a proof of concept and uses an in-memory FAISS index rather than a persistent production vector database.”

---

## Q2. What are the main components in your architecture?

### Word-to-word interview answer

> “The main components are Streamlit for the user interface, Python for the application logic, PyPDFLoader for loading the HR policy, RecursiveCharacterTextSplitter for chunking, Amazon Titan through Bedrock for embeddings, FAISS for vector retrieval, and Claude Haiku 4.5 through Bedrock for answer generation.
>
> Each component has a specific responsibility in the RAG pipeline.”

---

## Q3. Can you explain the indexing flow?

### Word-to-word interview answer

> “The indexing flow starts with the HR Leave Policy PDF.
>
> PyPDFLoader loads and extracts the document text. RecursiveCharacterTextSplitter then divides that text into overlapping chunks using a chunk size of 1000 and overlap of 100.
>
> Amazon Titan through Bedrock creates embeddings for those chunks, and FAISS indexes the resulting vectors.
>
> The FAISS index is then kept in Streamlit session state so it can be reused for questions within that session.”

---

## Q4. Can you explain the query flow?

### Word-to-word interview answer

> “When an employee enters a question in Streamlit, the application passes the question to my RAG backend.
>
> The backend performs a FAISS similarity search with k equal to three, so it retrieves the top three relevant HR policy chunks.
>
> I combine the text from those chunks with the employee's question to construct the prompt.
>
> That prompt is sent to Claude Haiku 4.5 through Amazon Bedrock.
>
> Claude generates the answer, and the result is returned to Streamlit and displayed to the employee.”

---

## Q5. Why do you separate indexing flow and query flow?

### Word-to-word interview answer

> “They solve two different problems.
>
> The indexing flow prepares the HR document for semantic retrieval by loading, chunking, embedding and indexing it.
>
> The query flow happens when the user asks a question. It searches the prepared index, retrieves relevant context and uses Claude to generate the answer.
>
> Understanding these separately also makes troubleshooting easier because an answer problem can come from document preparation, retrieval, or generation.”

---

## Q6. Where does FAISS fit in the architecture?

### Word-to-word interview answer

> “FAISS sits between the embedding stage and the generation stage.
>
> During indexing, it stores or indexes the embeddings created from HR policy chunks.
>
> During a query, it performs similarity search and returns the top three relevant chunks.
>
> FAISS is responsible for retrieval, while Claude is responsible for generation.”

---

## Q7. Where does Amazon Bedrock fit in the architecture?

### Word-to-word interview answer

> “Amazon Bedrock is used in two places.
>
> First, I use Amazon Titan through Bedrock to create embeddings for the HR policy chunks and support semantic retrieval.
>
> Second, I use Claude Haiku 4.5 through Bedrock to generate the final answer from the retrieved context and the user's question.
>
> So Bedrock supports both the embedding side and the generation side of my RAG architecture.”

---

## Q8. Is FAISS running as a separate server?

### Word-to-word interview answer

> “No. In the current implementation, FAISS runs inside the Python application process.
>
> The vector index is created in memory and stored in Streamlit session state.
>
> So it is not deployed as a separate vector database service.
>
> This is suitable for the current proof of concept, but for a larger multi-user production system I would evaluate persistent and centrally managed vector storage.”

---

## Q9. Why are you using Streamlit session state?

### Word-to-word interview answer

> “Streamlit reruns the application when users interact with the UI.
>
> I use session state to keep the FAISS vector index available during the browser session instead of rebuilding it on every interaction.
>
> However, I don't treat session state as durable storage. It is session-level application state, not a persistent vector database.”

---

## Q10. Does session state provide chatbot memory?

### Word-to-word interview answer

> “No. In this project, session state is used to keep the vector index, not conversation history.
>
> The application does not currently implement multi-turn conversation memory.
>
> Each question is processed independently using retrieval from the HR policy.”

---

## Q11. Is your project using Bedrock Knowledge Bases?

### Word-to-word interview answer

> “No. This project uses a custom RAG pipeline rather than Amazon Bedrock Knowledge Bases.
>
> My Python code explicitly handles document loading, chunking, Titan embeddings, FAISS indexing, similarity retrieval, prompt construction and Claude invocation.
>
> Bedrock provides the AI models, but the retrieval pipeline is implemented in my application using LangChain components and FAISS.”

---

## Q12. Is this a microservices architecture?

### Word-to-word interview answer

> “No. I would not describe the current implementation as microservices.
>
> It is a small single-process Python and Streamlit proof of concept.
>
> The frontend and RAG logic are organized into separate Python files, but they are not independently deployed services communicating over a service API.”

---

## Q13. Is this a serverless architecture?

### Word-to-word interview answer

> “No. I would not describe the complete application architecture as serverless.
>
> Amazon Bedrock is a managed AWS service, but the Streamlit application itself is a Python application.
>
> The repository also documents an EC2 deployment approach, so calling the complete project serverless would be inaccurate.”

---

## Q14. Is EC2 part of your current architecture?

### Word-to-word interview answer

> “The repository contains a documented EC2 deployment approach for hosting the Streamlit application.
>
> However, from the inspected project files alone, I cannot claim that a live production EC2 deployment is currently running.
>
> So I separate the implemented application architecture from the documented deployment architecture when I explain the project.”

---

## Q15. Is SharePoint part of the current architecture?

### Word-to-word interview answer

> “No. Some project diagrams or documentation mention SharePoint or document-ingestion ideas, but the current application code does not implement a SharePoint integration.
>
> The current backend loads a fixed HR policy PDF directly.
>
> If I added SharePoint later, I would describe that as a future ingestion improvement rather than current functionality.”

This is one of the documentation/code differences identified by the Codex analysis. :chatgpt-content-reference{index="5"}

---

## Q16. Why did you choose this simple architecture?

### Word-to-word interview answer

> “Because the current goal is to demonstrate and understand the core RAG workflow using a small HR policy document.
>
> Streamlit makes the UI simple, FAISS provides lightweight vector retrieval without requiring a separate database service, and Amazon Bedrock gives me managed access to Titan embeddings and Claude.
>
> For a proof of concept, this keeps the architecture understandable and avoids adding infrastructure that the current requirement doesn't need.”

---

## Q17. What happens when a new user session starts?

### Word-to-word interview answer

> “In the current implementation, if the vector index is not already present in that Streamlit session, the application calls the indexing function.
>
> It loads the HR policy PDF, splits the text, generates embeddings using Titan and creates the FAISS index.
>
> The index is then stored in Streamlit session state and reused within that session.
>
> This works for a proof of concept, but repeated index creation across sessions is one of the areas I would improve for production.”

---

## Q18. What is the biggest architectural limitation?

### Word-to-word interview answer

> “One important limitation is that the knowledge index is session-based rather than a shared persistent production index.
>
> That means document processing and embedding work can be repeated for new sessions.
>
> The application also lacks production capabilities such as authentication, centralized document ingestion, stronger error handling, automated RAG evaluation and observability.
>
> I would address those requirements before scaling the application.”

---

## Q19. How would you troubleshoot this architecture if the answer is wrong?

### Word-to-word interview answer

> “I would troubleshoot it layer by layer rather than immediately blaming the LLM.
>
> First, I would check whether the correct HR policy was loaded and whether the relevant text was extracted properly.
>
> Then I would inspect chunking and verify whether FAISS retrieved the correct top-three chunks for the question.
>
> If retrieval is correct, I would inspect the context and prompt sent to Claude.
>
> Finally, I would examine the generated response.
>
> This helps determine whether the problem is document quality, chunking, embeddings, retrieval, prompt construction or generation.”

---

## Q20. Can you summarize your architecture in one sentence?

### Word-to-word interview answer

> “My project is a Streamlit-based RAG application where an HR policy PDF is loaded and chunked, Amazon Titan creates embeddings, FAISS performs top-three semantic retrieval, and the retrieved policy context together with the user's question is sent to Claude Haiku 4.5 through Amazon Bedrock to generate the final answer.”

---

# Interview trap questions

There are a few questions where an interviewer may intentionally check whether you really understand your project.

### “Which vector database are you using?”

Correct:

> “FAISS.”

Not:

> “OpenSearch.”

### “Are you using Bedrock Knowledge Bases?”

Correct:

> “No. I built the retrieval pipeline using LangChain components, Titan embeddings and FAISS.”

### “Does Claude search the PDF?”

Correct:

> “No. My application retrieves relevant chunks from FAISS first and then provides those chunks to Claude.”

### “Does Streamlit session state give you conversation memory?”

Correct:

> “No. I use it for the FAISS index. Conversation history is not implemented.”

### “Is this microservices?”

Correct:

> “No. It's currently a single-process Python/Streamlit PoC.”

---

# Five architecture questions to master first

Before trying to remember all 20, concentrate on:

**Q1. Explain your architecture.**

**Q3. Explain the indexing flow.**

**Q4. Explain the query flow.**

**Q7. Where is Amazon Bedrock used?**

**Q11. Are you using Bedrock Knowledge Bases?**

If you deeply understand those five, most architecture follow-up questions become much easier.

### Architecture mental model

Keep this in your head:

```text
        PREPARE KNOWLEDGE

PDF
 ↓
Load
 ↓
Chunk
 ↓
Titan Embeddings
 ↓
FAISS


        ANSWER QUESTION

Question
 ↓
FAISS Search
 ↓
Top 3 Chunks
 ↓
Context + Question
 ↓
Claude
 ↓
Answer
```

That is the core of `02-Current-Architecture.md`.