# `04-Technology-Stack.md`

## NovaMindAI HR Q&A — Technology Stack

### Main question

> **What technologies did I actually use in this project, what does each technology do, and why is it needed?**

By now you understand:

```text
01 → What the project is
02 → Architecture
03 → End-to-end flow
04 → Technologies behind that flow
```

The important goal is **not** to memorize a list of tools.

You should be able to explain:

> **“I used X for this specific responsibility, and it connects to Y in this way.”**

Based on the inspected project, the core stack is Python, Streamlit, LangChain integrations, PyPDFLoader, RecursiveCharacterTextSplitter, Amazon Bedrock/Titan embeddings, FAISS, and ChatBedrock/Claude. The analysis also warns that not every package appearing in project requirements is part of the active application flow. :chatgpt-content-reference{index="0"}

---

# 1. Technology stack at a glance

Your actual application stack can be organized into layers:

| Layer | Technology | Purpose |
|---|---|---|
| Programming | Python | Main application language |
| UI | Streamlit | Employee-facing web interface |
| AI integration | LangChain ecosystem | Connect RAG components |
| Document loading | PyPDFLoader | Load HR policy PDF |
| Text processing | RecursiveCharacterTextSplitter | Split policy into chunks |
| AWS AI platform | Amazon Bedrock | Access embedding + generation models |
| Embeddings | Amazon Titan Embeddings | Convert text into vectors |
| Vector retrieval | FAISS | Semantic similarity search |
| LLM | Claude Haiku 4.5 | Generate final HR answer |
| State | Streamlit Session State | Reuse FAISS index within session |

The easiest mental model is:

```text
Python
  │
  ├── Streamlit ─────────────→ UI
  │
  ├── LangChain components
  │       │
  │       ├── PyPDFLoader ───→ Load PDF
  │       │
  │       ├── TextSplitter ──→ Chunk text
  │       │
  │       ├── BedrockEmbeddings
  │       │         ↓
  │       │       Titan ─────→ Embeddings
  │       │
  │       ├── FAISS ─────────→ Retrieval
  │       │
  │       └── ChatBedrock
  │                 ↓
  │               Claude ────→ Generation
  │
  └── Session State ─────────→ Keep index in session
```

---

# 2. Python

Your main programming language is:

**Python**

Both major application files are Python:

```text
rag_frontend.py
rag_backend.py
```

Python coordinates the entire application.

It is responsible for things such as:

```text
Load libraries
     ↓
Load document
     ↓
Split text
     ↓
Configure embeddings
     ↓
Build FAISS
     ↓
Retrieve chunks
     ↓
Construct prompt
     ↓
Invoke Claude
     ↓
Return answer
```

So don't describe Python as just:

> “I used Python for coding.”

A better understanding is:

> **Python is the main application and orchestration language connecting the UI, document-processing pipeline, vector retrieval, and Bedrock models.**

---

# 3. Streamlit

Your user interface is built using:

**Streamlit**

The frontend file is:

```text
rag_frontend.py
```

Its responsibilities include:

```text
Display application UI
        ↓
Accept HR question
        ↓
Validate input
        ↓
Maintain vector_index in session state
        ↓
Call backend
        ↓
Display generated answer
```

For example:

```text
Employee
   ↓
Streamlit Web UI
   ↓
Question
   ↓
Python Backend
   ↓
Answer
   ↓
Streamlit
```

### Why Streamlit fits this project

For a small AI proof of concept, Streamlit allows you to create a usable interface directly in Python.

You don't need a separate:

```text
React frontend
+
REST API
+
backend service
```

just to demonstrate the RAG workflow.

### Important interview distinction

Streamlit is **not**:

```text
❌ LLM
❌ vector database
❌ AWS service
❌ embedding model
```

It is your:

> **UI/application framework.**

---

# 4. Streamlit Session State

Streamlit also provides:

```python
st.session_state
```

Your project uses it to hold:

```text
vector_index
```

Conceptually:

```text
First run

No vector index
     ↓
Build FAISS
     ↓
st.session_state.vector_index


Later interaction
     ↓
Index exists
     ↓
Reuse it
```

This is useful because Streamlit reruns the application during interactions.

But remember:

```text
Session State
      ≠
Persistent Database

Session State
      ≠
Conversation Memory
```

We'll study this deeply in File 06 and File 14.

---

# 5. LangChain

This is one technology that interviewers may question carefully.

Your project uses several components from the LangChain ecosystem.

But LangChain is **not your AI model**.

It is also not an external server in this architecture.

Think of it as providing useful integrations and abstractions around the RAG components.

Your code imports components such as:

```python
from langchain_community.document_loaders import PyPDFLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_aws import BedrockEmbeddings

from langchain_community.vectorstores import FAISS

from langchain_aws import ChatBedrock
```

So LangChain helps connect:

```text
Document
   ↓
Loader
   ↓
Splitter
   ↓
Embedding integration
   ↓
Vector store integration
   ↓
LLM integration
```

### Very important

Don't say:

> “LangChain performs RAG automatically.”

Your code explicitly controls the workflow.

For example, you explicitly perform:

```python
docs = index.similarity_search(question, k=3)
```

You explicitly join the retrieved documents.

You explicitly construct the prompt.

You explicitly invoke Claude.

So a more accurate explanation is:

> **“I use LangChain components and integrations to simplify document loading, text splitting, vector-store integration and Bedrock model integration, while my Python code explicitly orchestrates the RAG flow.”**

---

# 6. PyPDFLoader

Your project uses:

```text
PyPDFLoader
```

from the LangChain community package.

Its job is simple:

> **Load the HR Leave Policy PDF and expose its content as document objects that the rest of the RAG pipeline can process.**

Conceptually:

```text
HR Leave Policy PDF
        ↓
PyPDFLoader
        ↓
Loaded Documents
```

Without this stage, your text splitter doesn't have the loaded document content to process.

---

# 7. RecursiveCharacterTextSplitter

Next:

```text
RecursiveCharacterTextSplitter
```

Its job is:

> **Split the loaded HR policy into smaller overlapping chunks.**

Your current configuration is:

```python
chunk_size=1000
chunk_overlap=100
```

and separators:

```python
["\n\n", "\n", " ", ""]
```

Conceptually:

```text
Large HR Policy
      ↓
RecursiveCharacterTextSplitter
      ↓
Chunk 1
Chunk 2
Chunk 3
...
```

Why do we need this?

Because retrieval works better when the system can search smaller pieces of information rather than treating the entire policy as one giant unit.

We will study this properly in:

`09-Chunking-and-Document-Processing.md`

---

# 8. Amazon Bedrock

Now we reach the main AWS AI service in the project:

**Amazon Bedrock**

Bedrock is the managed AWS service your application uses to access foundation-model capabilities.

In this project, it is involved in **two different tasks**:

```text
                   Amazon Bedrock

              ┌──────────┴──────────┐
              ↓                     ↓

      Titan Embeddings       Claude Haiku 4.5

              ↓                     ↓

       Create vectors        Generate answer
```

This distinction is extremely important.

If an interviewer asks:

> “How are you using Bedrock?”

don't answer only:

> “For Claude.”

Instead:

> **“I use Bedrock for both Titan embeddings and Claude generation.”**

---

# 9. Amazon Titan Embeddings

Your embedding configuration uses:

```text
amazon.titan-embed-text-v1
```

through:

```python
BedrockEmbeddings
```

Titan's responsibility is:

```text
TEXT
 ↓
VECTOR
```

Example conceptually:

```text
"Employees can carry forward privilege leave..."

                    ↓

             Titan Embeddings

                    ↓

       [0.21, -0.37, 0.82, ...]
```

Why?

Because FAISS performs vector similarity search.

So the relationship is:

```text
Text Chunks
     ↓
Titan
     ↓
Embeddings
     ↓
FAISS
```

### Titan does NOT generate the final HR answer

This distinction matters.

```text
Titan
   ↓
Embeddings

Claude
   ↓
Natural-language generation
```

---

# 10. FAISS

Your vector retrieval technology is:

**FAISS**

FAISS is used to create and search the vector index.

During indexing:

```text
HR Chunks
    ↓
Titan Embeddings
    ↓
Vectors
    ↓
FAISS Index
```

During a question:

```text
Employee Question
       ↓
FAISS Similarity Search
       ↓
Top 3 Relevant Chunks
```

Your code uses:

```python
index.similarity_search(question, k=3)
```

So in your project:

> **FAISS is responsible for semantic retrieval.**

It is not responsible for generation.

---

# 11. Is FAISS an AWS service?

**No.**

This is an interview trap you should be ready for.

Your architecture uses:

```text
Amazon Bedrock → AWS managed service

FAISS → vector-search library/index used by your Python application
```

Do not say:

> “FAISS is my AWS vector database.”

That would be inaccurate.

For this implementation, think:

> **FAISS is an in-memory vector index used inside the application.**

---

# 12. ChatBedrock

Your backend uses:

```python
ChatBedrock
```

This is the integration your Python application uses to interact with the configured Bedrock chat model.

Conceptually:

```text
Python Application
       ↓
ChatBedrock
       ↓
Amazon Bedrock
       ↓
Claude
```

So:

```text
ChatBedrock ≠ Claude
```

Instead:

> **ChatBedrock is the application-side integration/wrapper used to invoke Claude through Amazon Bedrock.**

---

# 13. Claude Haiku 4.5

Claude is your **generation model**.

Its role occurs after retrieval.

The flow is:

```text
FAISS
 ↓
Top 3 Policy Chunks
 ↓
Combine Context
 ↓
Context + Question
 ↓
Claude Haiku 4.5
 ↓
Generated HR Answer
```

The inspected code configures:

```text
temperature = 0.1
max_tokens = 3000
```

Claude's responsibility is therefore:

> **Generate the final natural-language response from the prompt containing retrieved HR policy context and the employee's question.**

Claude is **not** directly searching the PDF.

---

# 14. Why temperature = 0.1?

At a high level, temperature influences generation variability.

For an HR policy Q&A application, you generally want the answer to be more controlled and grounded rather than highly creative.

Your project uses:

```text
temperature = 0.1
```

So a project-specific explanation is:

> **“I configured a low temperature because this is policy question answering, where I want relatively controlled responses rather than creative output.”**

Be careful not to claim:

> “0.1 completely prevents hallucinations.”

It doesn't.

Retrieval quality, prompting, model behavior and evaluation still matter.

---

# 15. `max_tokens = 3000`

Your model configuration also includes:

```text
max_tokens = 3000
```

This controls the configured maximum generated output length for the model request.

It does **not** mean:

> “Claude will always generate 3000 tokens.”

It sets a maximum output allowance.

---

# 16. AWS credentials/profile

The current implementation also contains:

```python
credentials_profile_name='default'
```

for the Bedrock integrations.

That means the application expects an AWS credential profile named:

```text
default
```

Conceptually:

```text
Python Application
       ↓
AWS SDK / integration
       ↓
default AWS profile
       ↓
AWS credentials
       ↓
Amazon Bedrock
```

We'll go deeper into this in:

`15-AWS-Bedrock-IAM-and-Region.md`

For now understand:

> **The local application needs AWS credentials and permissions to invoke the required Bedrock models.**

---

# 17. How all technologies work together

Now put the entire stack together:

```text
                       PYTHON
                         │
                         ▼
                    STREAMLIT
                         │
                  Employee Question
                         │
                         ▼
                  Python RAG Logic
                         │
       ┌─────────────────┴──────────────────┐
       │                                    │
 DOCUMENT PREPARATION                  QUERY PROCESSING
       │                                    │
       ▼                                    ▼
 PyPDFLoader                           User Question
       │                                    │
       ▼                                    │
Text Splitter                               │
       │                                    │
       ▼                                    │
Text Chunks                                 │
       │                                    │
       ▼                                    │
BedrockEmbeddings                           │
       │                                    │
       ▼                                    │
Amazon Titan                               │
       │                                    │
       ▼                                    │
Embeddings                                  │
       │                                    │
       ▼                                    │
FAISS ◄─────────────────────────────────────┘
       │
       ▼
Top 3 Relevant Chunks
       │
       ▼
Context + Question
       │
       ▼
ChatBedrock
       │
       ▼
Amazon Bedrock
       │
       ▼
Claude Haiku 4.5
       │
       ▼
Generated Answer
       │
       ▼
Streamlit
       │
       ▼
Employee
```

---

# 18. What is NOT part of the current core technology stack?

This is important because your repository/documentation may mention additional technologies.

Based on the inspected current implementation, do **not** present these as core implemented components:

```text
❌ Amazon Bedrock Knowledge Bases
❌ Amazon OpenSearch
❌ AWS Lambda
❌ API Gateway
❌ DynamoDB
❌ LangGraph
❌ AI Agents
❌ Redis
❌ Kubernetes
❌ ECS
❌ EKS
❌ SharePoint integration
```

The Codex analysis distinguishes the actual implemented application from documented or proposed components. :chatgpt-content-reference{index="1"}

---

# 19. Requirements file does NOT automatically equal technology stack

This is an important engineering lesson.

Suppose `requirements.txt` contains 15 packages.

That does **not** automatically mean:

> “I used all 15 technologies in my application.”

There can be:

```text
requirements.txt
│
├── Actually imported/used packages ✓
├── Development dependencies
├── Leftover dependencies
└── Unused packages
```

Your project analysis specifically identified dependencies that appear unnecessary to the active application path. :chatgpt-content-reference{index="2"}

In an interview, explain technologies based on **actual implementation**, not simply every dependency name.

---

# 20. Technology → Responsibility mapping

This is the part I want you to understand especially well.

```text
Python
   ↓
Application/orchestration language

Streamlit
   ↓
User interface

PyPDFLoader
   ↓
Document loading

RecursiveCharacterTextSplitter
   ↓
Chunking

Amazon Titan
   ↓
Embeddings

FAISS
   ↓
Vector indexing + retrieval

LangChain integrations
   ↓
Connect/support RAG components

ChatBedrock
   ↓
Bedrock chat-model integration

Claude Haiku 4.5
   ↓
Answer generation

Amazon Bedrock
   ↓
Managed access to Titan + Claude

Streamlit Session State
   ↓
Session-level FAISS index reuse
```

If you understand this mapping, you understand the technology stack.

---

# 21. Why this stack makes sense for a PoC

Your project is a small RAG proof of concept.

So the stack is relatively lightweight:

```text
Streamlit
+
Python
+
LangChain integrations
+
FAISS
+
Amazon Bedrock
```

You did not need to add many distributed infrastructure components simply to demonstrate:

```text
Document
→ Chunk
→ Embed
→ Retrieve
→ Augment
→ Generate
```

That's an important engineering principle:

> **Architecture should match the problem and current requirements. More services do not automatically mean a better system.**

---

# 22. Technology stack in one sentence

You should eventually be able to say:

> **“I built the application in Python with Streamlit for the UI, used LangChain components for document loading, text splitting and AI integrations, Amazon Titan through Bedrock for embeddings, FAISS for semantic vector retrieval, and Claude Haiku 4.5 through Amazon Bedrock for final answer generation.”**

---

# Interview Questions & Answers — `04-Technology-Stack.md`

## Q1. What technologies did you use in this project?

### Word-to-word interview answer

> “The application is primarily built in Python.
>
> I use Streamlit for the user interface and LangChain ecosystem components for document loading, text splitting, FAISS integration and Amazon Bedrock integration.
>
> PyPDFLoader loads the HR policy PDF, RecursiveCharacterTextSplitter splits it into smaller chunks, Amazon Titan through Bedrock generates embeddings, and FAISS provides semantic vector retrieval.
>
> For answer generation, I use Claude Haiku 4.5 through Amazon Bedrock using the ChatBedrock integration.
>
> I also use Streamlit session state to reuse the FAISS index within the current session.”

---

## Q2. Why did you choose Python?

### Word-to-word interview answer

> “I used Python because the complete RAG ecosystem I needed is well supported in Python, including Streamlit, LangChain integrations, FAISS and AWS SDK-based model integrations.
>
> It also allowed me to keep the proof of concept relatively simple because the UI, RAG orchestration and model integration could all be implemented in the same language.”

---

## Q3. Why did you choose Streamlit?

### Word-to-word interview answer

> “I chose Streamlit because this project is a proof of concept and I wanted a simple web interface for demonstrating the RAG workflow.
>
> Streamlit allowed me to create the user interface directly in Python without introducing a separate frontend framework and API layer.
>
> For a larger production application, I would evaluate whether a separate frontend and backend architecture is more appropriate.”

---

## Q4. Why are you using LangChain?

### Word-to-word interview answer

> “I use LangChain because it provides useful components and integrations for the different stages of my RAG pipeline.
>
> In this project I use its ecosystem for PDF loading, recursive text splitting, Bedrock embeddings, FAISS integration and ChatBedrock.
>
> However, my Python code still explicitly controls the RAG flow. I perform the similarity search, combine the retrieved chunks, construct the prompt and invoke the model myself.”

---

## Q5. Is LangChain your LLM?

### Word-to-word interview answer

> “No. LangChain is not the language model.
>
> I use LangChain components and integrations to connect different parts of the RAG application.
>
> The generation model in my project is Claude Haiku 4.5, accessed through Amazon Bedrock.”

---

## Q6. What is PyPDFLoader used for?

### Word-to-word interview answer

> “PyPDFLoader is responsible for loading the HR Leave Policy PDF and converting its contents into document objects that can be processed by the rest of my RAG pipeline.
>
> Those documents are then passed to the text splitter before embedding and indexing.”

---

## Q7. Why do you use RecursiveCharacterTextSplitter?

### Word-to-word interview answer

> “I use RecursiveCharacterTextSplitter to divide the HR policy into smaller overlapping chunks.
>
> Retrieval operates on these chunks instead of treating the complete policy as one large search unit.
>
> In my current configuration, the chunk size is 1000 and the chunk overlap is 100.
>
> We would need evaluation to determine whether those settings are optimal for the document and question set.”

---

## Q8. What is Amazon Titan used for?

### Word-to-word interview answer

> “Amazon Titan is used for embeddings in my project.
>
> It converts HR policy text into vector representations that capture semantic information.
>
> Those vectors are indexed in FAISS so that when an employee asks a question, the application can retrieve semantically relevant policy chunks.”

---

## Q9. What is FAISS used for?

### Word-to-word interview answer

> “FAISS is used for vector indexing and semantic similarity retrieval.
>
> During knowledge preparation, the policy chunks are embedded and indexed in FAISS.
>
> During question answering, the application performs a similarity search against that index and retrieves the top three relevant policy chunks.
>
> Those chunks become context for Claude.”

---

## Q10. Is FAISS an AWS service?

### Word-to-word interview answer

> “No. FAISS is not an AWS service.
>
> In my current project it is used as an in-memory vector index within the Python application.
>
> Amazon Bedrock is the AWS managed service I use for the embedding and generation models.”

---

## Q11. What is Claude's role?

### Word-to-word interview answer

> “Claude is the generation model.
>
> After FAISS retrieves the relevant HR policy chunks, my Python application combines those chunks with the user's question and constructs a prompt.
>
> Claude Haiku 4.5 receives that prompt through Amazon Bedrock and generates the final natural-language answer.”

---

## Q12. What is Amazon Bedrock's role?

### Word-to-word interview answer

> “Amazon Bedrock provides managed access to the AI models used in my application.
>
> I use Amazon Titan through Bedrock for generating embeddings and Claude Haiku 4.5 through Bedrock for generating the final HR policy answer.
>
> So Bedrock participates in both the retrieval preparation side and the generation side of my RAG pipeline.”

---

## Q13. What's the difference between Titan and Claude in your project?

### Word-to-word interview answer

> “They have different responsibilities.
>
> Titan is my embedding model. It converts text into vectors that support semantic retrieval.
>
> Claude is my generation model. It receives the retrieved HR policy context together with the user's question and generates the final answer.
>
> So Titan supports retrieval, while Claude performs generation.”

---

## Q14. What's the difference between FAISS and Claude?

### Word-to-word interview answer

> “FAISS and Claude solve completely different problems.
>
> FAISS performs retrieval. It searches the vector index and returns relevant HR policy chunks.
>
> Claude performs generation. It uses those retrieved chunks as context to produce the natural-language answer.
>
> In simple terms, FAISS finds the information and Claude explains the answer using that information.”

---

## Q15. What is ChatBedrock?

### Word-to-word interview answer

> “ChatBedrock is the LangChain AWS integration I use in my Python application to interact with the configured chat model through Amazon Bedrock.
>
> It is not the model itself.
>
> In my application, Claude Haiku 4.5 is the model, while ChatBedrock provides the application-side integration used to invoke it.”

---

## Q16. Why did you configure temperature to 0.1?

### Word-to-word interview answer

> “Because this is an HR policy question-answering application, I prefer relatively controlled responses rather than highly creative generation.
>
> Therefore, the current model configuration uses a low temperature of 0.1.
>
> However, a low temperature alone does not guarantee factual answers. Retrieval quality, prompting and evaluation are also important.”

---

## Q17. Why are you using FAISS instead of OpenSearch?

### Word-to-word interview answer

> “For this proof of concept, the knowledge source is small and my goal was to implement and understand the core RAG workflow without adding unnecessary infrastructure.
>
> FAISS provides lightweight vector similarity retrieval directly in the Python application.
>
> For a production system, I would evaluate the storage technology based on requirements such as persistence, data volume, concurrent users, filtering, availability, operational management and cost rather than automatically choosing the same solution.”

---

## Q18. Why aren't you using Bedrock Knowledge Bases?

### Word-to-word interview answer

> “This project was designed as a custom RAG implementation.
>
> I explicitly handle document loading, chunking, embeddings, FAISS indexing, retrieval, context construction and model invocation.
>
> That gives me direct visibility into each stage of the RAG pipeline.
>
> Bedrock Knowledge Bases could be evaluated as an alternative managed approach, but it is not part of the current implementation.”

---

## Q19. How does your application authenticate to AWS?

### Word-to-word interview answer

> “In the current implementation, the Bedrock integrations specify the AWS credentials profile named `default`.
>
> That means the application expects the local AWS environment to have that profile configured with credentials and permissions required to access the Bedrock models.
>
> For an AWS-hosted production deployment, I would prefer IAM role-based credentials rather than relying on locally configured long-term credentials.”

---

## Q20. If you had to summarize your technology choices, how would you explain them?

### Word-to-word interview answer

> “I kept the technology stack appropriate for a RAG proof of concept.
>
> Python is the main application language, Streamlit provides the UI, LangChain components simplify document processing and AI integrations, Titan creates embeddings, FAISS performs semantic retrieval, and Claude generates the final answer.
>
> Amazon Bedrock provides managed access to Titan and Claude.
>
> This stack allows me to demonstrate the complete RAG lifecycle without introducing infrastructure that the current proof-of-concept requirements don't need.”

---

# Important interview trap questions

### “Is LangChain the LLM?”

> **No. Claude is the LLM. LangChain provides application components and integrations.**

### “Is FAISS an AWS database?”

> **No. FAISS is an in-memory vector-search/indexing technology used by the Python application.**

### “Does Titan generate your answer?”

> **No. Titan generates embeddings. Claude generates the answer.**

### “Does Claude search FAISS?”

> **No. My application searches FAISS and passes the retrieved context to Claude.**

### “Does Bedrock store your vectors?”

> **Not in this implementation. FAISS is the vector index.**

### “Are all packages in `requirements.txt` part of your architecture?”

> **No. The technology stack should be based on what the application actually imports and uses, not every dependency listed in the requirements file.**

---

# Five questions to master first

For `04-Technology-Stack.md`, focus on these first:

**1. What technologies did you use?**

**2. Why did you use LangChain?**

**3. What's the difference between Titan, FAISS and Claude?**

**4. What role does Amazon Bedrock play?**

**5. Why did you choose this stack for a PoC?**

And remember this simple map:

```text
Python      → Application logic
Streamlit   → UI
LangChain   → Components / integrations
PyPDFLoader → Load document
Splitter    → Create chunks
Titan       → Create embeddings
FAISS       → Retrieve information
Claude      → Generate answer
Bedrock     → Access Titan + Claude
```

If you can explain **why each technology exists**, rather than just listing its name, you understand the technology stack.