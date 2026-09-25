# `01-Project-Overview.md`

## HR Q&A RAG Project — Project Overview

For this first file, forget FAISS internals, embeddings mathematics, EC2, IAM, and production improvements for now.

We first need to answer one basic question:

> **What exactly did I build, and why?**

---

## 1. What is this project?

Your project is called **NovaMindAI — HR Q&A**.

It is a **Retrieval-Augmented Generation (RAG) proof-of-concept application** that answers questions using an HR Leave Policy document.

In very simple words:

```text
Employee has an HR question
        ↓
Employee asks NovaMindAI
        ↓
System searches the HR policy
        ↓
Finds relevant information
        ↓
Claude generates an answer using that information
        ↓
Employee sees the answer
```

Your Codex analysis describes the project as a small, single-process Python/Streamlit application rather than a large enterprise HR platform. :chatgpt-content-reference{index="0"}

### Simple definition

> **NovaMindAI is an HR policy question-answering application that uses RAG to retrieve relevant information from an HR Leave Policy and uses Claude through Amazon Bedrock to generate an answer.**

That's the first definition I want you to understand.

---

# 2. What problem are you trying to solve?

Imagine a company has a long HR Leave Policy.

An employee wants to know:

> “How many privilege leave days am I allowed?”

Without your application, the employee may need to:

```text
Find HR policy
      ↓
Open PDF
      ↓
Search manually
      ↓
Read different sections
      ↓
Find relevant policy
      ↓
Understand the answer
```

Your project tries to simplify this.

Instead:

```text
Employee
   ↓
"How many privilege leave days are allowed?"
   ↓
NovaMindAI
   ↓
HR Policy retrieval
   ↓
Generated answer
```

So the business problem is essentially:

> **Employees may spend time manually searching HR policy documents to find answers to common policy questions.**

Your PoC explores whether RAG can provide a more natural question-answering interface over such a document.

---

# 3. Why can't we just ask Claude directly?

This is one of the most important ideas in the whole project.

Suppose you ask Claude:

> “According to my company's Leave Policy, how many privilege leave days am I allowed?”

How would Claude automatically know the contents of your specific HR policy?

It may not.

The policy is external knowledge.

That's why your project uses **RAG**.

Instead of:

```text
Question
   ↓
Claude
   ↓
Answer
```

your project does approximately:

```text
Question
   ↓
Search HR Policy
   ↓
Retrieve relevant policy text
   ↓
Question + Policy Context
   ↓
Claude
   ↓
Answer
```

This is the core reason RAG exists in this project.

---

# 4. What does RAG mean here?

RAG means:

**Retrieval-Augmented Generation**

Don't memorize only the full form. Understand the three words.

### Retrieval

Find relevant information from the HR policy.

Example:

```text
Question:
"How many privilege leave days can I take?"

              ↓

Retrieve relevant HR policy chunks
```

### Augmentation

Take that retrieved information and add it to the prompt given to Claude.

Conceptually:

```text
Relevant HR Policy Context
          +
Employee Question
          ↓
        Prompt
```

### Generation

Claude reads the question and retrieved context and generates the final answer.

So:

```text
RETRIEVE
Find relevant HR policy text
        ↓
AUGMENT
Combine context + question
        ↓
GENERATE
Claude produces answer
```

Later, in `07-RAG-Fundamentals-in-This-Project.md`, we'll study this much more deeply.

For now, understand **why RAG exists**.

---

# 5. What have you actually implemented?

This is extremely important for interviews.

Your application actually implements this pipeline:

```text
HR Leave Policy PDF
        ↓
PyPDFLoader
        ↓
Extract text
        ↓
RecursiveCharacterTextSplitter
        ↓
Text Chunks
        ↓
Amazon Titan Embeddings
        ↓
FAISS Vector Index
        ↓

Employee Question
        ↓
FAISS Similarity Search
        ↓
Top 3 Relevant Chunks
        ↓
Context + Question
        ↓
Claude Haiku 4.5
via Amazon Bedrock
        ↓
Generated Answer
        ↓
Streamlit UI
```

The Codex analysis confirms that the application has a real retrieval-and-generation path rather than simply sending the user's question directly to Claude. :chatgpt-content-reference{index="1"}

That makes this a genuine small RAG implementation.

---

# 6. What is the role of Streamlit?

Streamlit gives the user the interface.

The employee doesn't need to interact with Python code directly.

They see something conceptually like:

```text
┌─────────────────────────────────────────┐
│             NovaMindAI                  │
│                                         │
│ HR Policy Q&A                           │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ How many privilege leave days...?  │ │
│ └─────────────────────────────────────┘ │
│                                         │
│             [ Ask NovaMindAI ]          │
│                                         │
│ Answer: ...                             │
└─────────────────────────────────────────┘
```

The user enters the question.

Streamlit sends that question into your Python RAG logic.

Then Streamlit displays the returned answer.

So remember:

> **Streamlit is the application interface. It is not the AI model and it is not the vector database.**

---

# 7. Where does the knowledge come from?

This point is important.

The knowledge source used by the backend is an HR Leave Policy PDF.

Your backend uses:

```python
PyPDFLoader(...)
```

to load the policy.

So the knowledge doesn't originate from:

```text
❌ MySQL
❌ DynamoDB
❌ Amazon Bedrock Knowledge Base
❌ OpenSearch
❌ SharePoint integration
```

The current application flow is based on the **HR policy PDF loaded by the backend**.

Your Codex analysis specifically identifies SharePoint/upload flows shown elsewhere as documentation or conceptual material rather than implemented application behavior. :chatgpt-content-reference{index="2"}

This distinction will protect you in interviews.

---

# 8. What is Amazon Bedrock doing?

Amazon Bedrock is involved in **two important AI operations** in your current implementation.

### Operation 1 — Embeddings

Your project uses:

```text
Amazon Titan Embeddings
```

to convert document chunks into numerical representations.

Very simplified:

```text
"Employees are entitled to privilege leave..."

                   ↓

             Titan Embeddings

                   ↓

[0.12, -0.42, 0.81, ...]
```

These representations allow the application to perform semantic retrieval.

### Operation 2 — Generation

Your project uses:

```text
Claude Haiku 4.5
```

through Bedrock to generate the final answer from:

```text
Retrieved HR Context + Employee Question
```

So a useful mental model is:

```text
Amazon Bedrock
│
├── Titan
│    └── Embeddings
│
└── Claude Haiku 4.5
     └── Answer generation
```

---

# 9. What is FAISS doing?

FAISS is the project's **vector search layer**.

After the HR policy is split into chunks and converted into embeddings, those vectors are indexed using FAISS.

When the employee asks:

> “What is the leave policy?”

your code performs:

```python
similarity_search(question, k=3)
```

So it retrieves:

> **the top 3 matching chunks**

from the FAISS index.

Then those chunks become context for Claude.

For now:

> **FAISS helps the application find HR policy chunks that are semantically relevant to the employee's question.**

We'll study exactly how this works in `11-FAISS-Vector-Search.md`.

---

# 10. What is LangChain doing?

This is another important interview distinction.

You are **not** using LangChain because “LangChain is the AI.”

It isn't.

LangChain provides integrations/components that connect the pieces of your RAG pipeline.

Your project uses LangChain-related components for things such as:

```text
PDF loading
     ↓
Text splitting
     ↓
Bedrock embeddings integration
     ↓
FAISS integration
     ↓
Bedrock Claude integration
```

So:

```text
LangChain ≠ LLM
LangChain ≠ Vector Database
LangChain ≠ AWS

LangChain = integration/orchestration components
            used by your Python application
```

We'll study this properly later.

---

# 11. Is this project using Amazon Bedrock Knowledge Bases?

**No.**

This distinction is especially important because your previous eLearning project did.

### Previous eLearning project

You had approximately:

```text
Lambda
   ↓
Bedrock RetrieveAndGenerate
   ↓
Bedrock Knowledge Base
   ↓
Managed retrieval + generation
```

Bedrock managed much of the RAG workflow.

### This HR project

You implement more of that workflow yourself:

```text
PyPDFLoader
     ↓
Text Splitter
     ↓
Titan Embeddings
     ↓
FAISS
     ↓
Similarity Search
     ↓
Build Prompt
     ↓
Claude
```

This difference is valuable for your learning.

You now have examples of **two different approaches to RAG**.

---

# 12. Is this an Agentic AI project?

No.

There is no evidence in the current implementation of:

```text
❌ AI agents
❌ LangGraph
❌ tool calling
❌ autonomous planning
❌ multi-agent orchestration
❌ action groups
```

This is a:

> **RAG-based Generative AI application.**

That's completely fine.

Don't add “Agentic AI” while explaining this project simply because your other projects use agents.

---

# 13. Is this a microservices architecture?

No.

The current application is much simpler.

Conceptually:

```text
Browser
   ↓
Streamlit Application
   ↓
Python RAG Logic
   ├── PDF processing
   ├── Titan embeddings
   ├── FAISS
   └── Claude
```

The Codex analysis describes it as a single-process Python/Streamlit application. :chatgpt-content-reference{index="3"}

So don't say:

> “I developed a microservices architecture.”

That would not describe the current implementation.

---

# 14. Does the application have conversation memory?

Not in the sense of a multi-turn chatbot memory system.

The current implementation doesn't maintain conversation history such as:

```text
User: What is privilege leave?

AI: ...

User: Can I carry it forward?
     ↑
AI remembers previous conversation
```

Your Streamlit application stores the **vector index** in `st.session_state`, but that is different from storing chat history.

This is a crucial distinction:

```text
Vector Index
    ≠
Conversation Memory
```

We'll study this in detail later.

---

# 15. Is the FAISS index permanent?

No.

The current implementation creates the FAISS index in memory.

Conceptually:

```text
New Streamlit session
        ↓
Load PDF
        ↓
Split PDF
        ↓
Call Titan embeddings
        ↓
Create FAISS index
        ↓
Store index in st.session_state
```

The index isn't implemented as a centrally persistent production knowledge index.

This has consequences for:

- startup time
- repeated embedding calls
- cost
- scalability
- multiple users

We'll cover those later rather than mixing them into the overview.

---

# 16. Is this project production-ready?

No.

A good description is:

> **It is a proof-of-concept HR policy RAG application.**

That does **not** mean the project is bad.

A PoC answers:

> “Can this idea work?”

Production asks much more:

```text
Can it authenticate users?
Can it handle failures?
Can it scale?
Can we monitor it?
Can we evaluate answer quality?
Can HR update policies safely?
Can we trace sources?
Can we control permissions?
Can we reproduce deployment?
Can we protect sensitive data?
```

Those concerns are not fully implemented in the current application.

---

# 17. What is the most important design decision?

One major design decision is using a **custom RAG pipeline** rather than a managed Bedrock Knowledge Base.

You explicitly have:

```text
PyPDFLoader
↓
RecursiveCharacterTextSplitter
↓
BedrockEmbeddings
↓
FAISS
↓
similarity_search()
↓
Custom Prompt
↓
ChatBedrock
```

That gives you visibility into individual RAG stages.

This makes the project particularly useful for learning because you can explain **what happens between the document and the LLM**.

---

# 18. Current implementation vs future ideas

Keep this distinction in your mind throughout this project.

### CURRENTLY IMPLEMENTED

```text
✓ Python
✓ Streamlit
✓ HR Leave Policy PDF
✓ PyPDFLoader
✓ RecursiveCharacterTextSplitter
✓ Titan embeddings through Bedrock
✓ FAISS
✓ Top-3 similarity retrieval
✓ Custom context + question prompt
✓ Claude Haiku 4.5 through Bedrock
✓ Streamlit session-state index
```

### NOT CURRENTLY IMPLEMENTED

```text
✗ Bedrock Knowledge Bases
✗ OpenSearch
✗ SharePoint integration
✗ User document uploads
✗ Authentication
✗ Role-based authorization
✗ Conversation history
✗ Persistent production vector index
✗ LangGraph
✗ Agents
✗ Docker deployment
✗ Kubernetes
✗ Infrastructure as Code
✗ CI/CD pipeline
✗ Automated RAG evaluation
```

The Codex analysis specifically warns against presenting unimplemented or merely documented components as current functionality. :chatgpt-content-reference{index="4"}

---

# 19. Your complete project in one diagram

Memorize the **logic**, not necessarily these exact words:

```text
                    NOVAMINDAI — HR Q&A

                   HR Leave Policy PDF
                           │
                           ▼
                      PyPDFLoader
                           │
                           ▼
              RecursiveCharacterTextSplitter
                           │
                           ▼
                       Text Chunks
                           │
                           ▼
                Amazon Titan Embeddings
                           │
                           ▼
                     FAISS Index
                           │
                           │
Employee                  │
   │                      │
   ▼                      │
Streamlit                 │
   │                      │
   ▼                      │
Question ─────────────────┘
   │
   ▼
FAISS Similarity Search
   │
   ▼
Top 3 Relevant Chunks
   │
   ▼
Context + Question
   │
   ▼
Claude Haiku 4.5
Amazon Bedrock
   │
   ▼
Generated HR Answer
   │
   ▼
Streamlit
   │
   ▼
Employee
```

---

# 20. Interview answer — “Tell me about this project.”

Don't memorize this yet. First understand it.

Once you understand the project, this becomes natural:

> “NovaMindAI is an HR policy question-answering proof of concept that I built using Retrieval-Augmented Generation.
>
> The problem I wanted to solve was that employees may need to manually search through HR policy documents to find answers to common questions.
>
> In my application, I load an HR Leave Policy PDF using PyPDFLoader and split the extracted text into overlapping chunks using LangChain's RecursiveCharacterTextSplitter.
>
> I then create embeddings for those chunks using Amazon Titan through Amazon Bedrock and index them in FAISS.
>
> When a user asks a question through the Streamlit interface, the application performs a similarity search against FAISS and retrieves the top three relevant chunks.
>
> I combine those retrieved chunks with the user's question to create a prompt and send it to Claude Haiku 4.5 through Amazon Bedrock.
>
> Claude generates the answer using that retrieved HR policy context, and the result is displayed back to the user through Streamlit.
>
> The current application is a proof of concept rather than a production-ready HR platform. For example, the vector index is session-based, there is no authentication or conversation history, and production security, evaluation, persistence, and observability would still need to be added.”

---

# 21. Five things you must understand before moving forward

Don't memorize 20 sections.

For **File 01**, I want only these five ideas clear:

**1. Problem**

Employees may need to manually search HR policy documents.

**2. Solution**

Ask questions naturally and retrieve relevant HR policy information before generating an answer.

**3. RAG**

```text
Retrieve relevant policy
        ↓
Add it as context
        ↓
Generate answer
```

**4. Actual project flow**

```text
PDF
→ Chunking
→ Titan Embeddings
→ FAISS
→ Top-3 Retrieval
→ Context + Question
→ Claude
→ Answer
```

**5. Project maturity**

```text
Proof of Concept
≠
Production-ready HR system
```

---

## Knowledge Check — Answer in your own words

Don't look for perfect interview English yet. I want to check your **understanding**.

### Question 1

**What problem does your HR Q&A project solve?**

### Question 2

**Why do you need RAG instead of sending the employee's question directly to Claude?**

Answer just these **two questions in your own words**. I’ll check your understanding and correct anything unclear before we move to `02-Current-Architecture.md`.


---
---
---

Exactly. You want **both the interview questions AND complete word-to-word answers** added inside `01-Project-Overview.md`.

Below is the section I recommend adding at the end of your existing `01-Project-Overview.md`. The answers are grounded in the actual project analysis: this is a Streamlit/Python RAG PoC using a fixed HR Leave Policy PDF, Titan embeddings, FAISS top-3 retrieval, and Claude Haiku 4.5 through Bedrock. :chatgpt-content-reference{index="0"} :chatgpt-content-reference{index="1"}

# Interview Questions & Answers — `01-Project-Overview.md`

## Q1. Can you explain your HR Q&A project?

### Word-to-word interview answer

> “My project is NovaMindAI HR Q&A. It is a proof-of-concept Generative AI application built using Retrieval-Augmented Generation, or RAG.
>
> The main problem I wanted to solve was that employees may need to manually search through HR policy documents whenever they have questions about company policies.
>
> In my project, I load an HR Leave Policy PDF, split the document into smaller chunks, create embeddings using Amazon Titan through Amazon Bedrock, and index those embeddings in FAISS.
>
> When a user asks a question through the Streamlit interface, the application performs a similarity search and retrieves the top three relevant chunks from FAISS. I then combine those chunks with the user's question and send the prompt to Claude Haiku 4.5 through Amazon Bedrock.
>
> Claude generates the answer using the retrieved policy information as context, and the final answer is displayed to the user through Streamlit.
>
> The current application is a proof of concept rather than a complete production HR platform.”

---

## Q2. What problem does your project solve?

### Word-to-word interview answer

> “The project addresses the problem of manually searching HR policy documents.
>
> For example, if an employee wants to know about a leave rule, they may need to open the policy document, search through different sections, and find the relevant information manually.
>
> My application provides a natural-language question-answering interface. The employee can ask a question, and the RAG pipeline retrieves relevant information from the HR Leave Policy and gives that information to Claude to generate the answer.”

---

## Q3. Why did you use RAG in this project?

### Word-to-word interview answer

> “I used RAG because the answers should be based on the HR policy document rather than only on the general knowledge of the language model.
>
> With RAG, I first retrieve relevant information from the HR Leave Policy. Then I provide that retrieved context along with the user's question to Claude.
>
> This helps ground the generated answer in the policy document. It can reduce unsupported answers, although RAG does not completely eliminate hallucinations.”

---

## Q4. Can you explain the project flow at a high level?

### Word-to-word interview answer

> “There are two main parts in my project: preparing the HR document for retrieval and answering user questions.
>
> First, the application loads the HR Leave Policy PDF using PyPDFLoader. It splits the extracted text into smaller overlapping chunks using RecursiveCharacterTextSplitter.
>
> Amazon Titan through Bedrock creates embeddings for those chunks, and the vectors are indexed in FAISS.
>
> When the user asks a question through Streamlit, the application searches FAISS and retrieves the top three relevant chunks.
>
> Those chunks are combined with the user's question and sent to Claude Haiku 4.5 through Amazon Bedrock. Claude generates the answer, and Streamlit displays it to the user.”

That is the core flow implemented by the project. :chatgpt-content-reference{index="2"}

---

## Q5. Why don't you send the user's question directly to Claude?

### Word-to-word interview answer

> “Because Claude does not automatically know the contents of the specific HR Leave Policy used by my application.
>
> If I send only the question, the model may answer using its general knowledge rather than the actual policy.
>
> Therefore, I first retrieve relevant information from the policy using FAISS. Then I send both the retrieved context and the user's question to Claude.
>
> This is the main reason I use RAG.”

---

## Q6. What technologies did you use?

### Word-to-word interview answer

> “The main application is written in Python.
>
> I use Streamlit for the user interface and LangChain integrations for document loading, text splitting, Bedrock embeddings, FAISS integration, and Claude integration.
>
> PyPDFLoader loads the HR Leave Policy PDF, RecursiveCharacterTextSplitter creates chunks, Amazon Titan creates embeddings through Bedrock, FAISS provides vector similarity search, and Claude Haiku 4.5 through Amazon Bedrock generates the final answer.”

The actual project uses these components; the analysis also warns that several other packages in `requirements.txt` are not part of the active application path. :chatgpt-content-reference{index="3"}

---

## Q7. What role does Amazon Bedrock play?

### Word-to-word interview answer

> “Amazon Bedrock is used for two main AI operations in my project.
>
> First, I use Amazon Titan through Bedrock to generate embeddings for the HR policy chunks.
>
> Second, I use Claude Haiku 4.5 through Bedrock as the generation model.
>
> So Titan supports the retrieval side by creating embeddings, while Claude handles the generation side by producing the final answer from the retrieved context.”

---

## Q8. What role does FAISS play?

### Word-to-word interview answer

> “FAISS is the vector search component in my project.
>
> After the HR policy is divided into chunks and converted into embeddings, those vectors are indexed in FAISS.
>
> When a user asks a question, the application performs a similarity search against the FAISS index and retrieves the top three relevant document chunks.
>
> Those chunks are then provided as context to Claude.”

---

## Q9. What role does Streamlit play?

### Word-to-word interview answer

> “Streamlit provides the user interface for the application.
>
> The user enters an HR policy question in the Streamlit application and submits it. Streamlit then calls my backend RAG function and displays the generated response.
>
> I also use Streamlit session state to keep the FAISS vector index available across Streamlit reruns within that browser session.”

---

## Q10. What is the knowledge source for your application?

### Word-to-word interview answer

> “The knowledge source in the current implementation is an HR Leave Policy PDF.
>
> The backend loads that document using PyPDFLoader, extracts the text, splits it into chunks, generates embeddings, and creates the FAISS index.
>
> So the RAG knowledge used for retrieval comes from that policy document rather than from a traditional application database.”

---

## Q11. Are you using Amazon Bedrock Knowledge Bases?

### Word-to-word interview answer

> “No. This project does not use Amazon Bedrock Knowledge Bases.
>
> I implemented the RAG pipeline using LangChain components, Amazon Titan embeddings, and FAISS.
>
> My code explicitly loads the PDF, splits the text, creates embeddings, builds the FAISS index, retrieves the top three chunks, constructs the prompt, and invokes Claude.
>
> Bedrock is used for the embedding and generation models, but FAISS is the vector search layer.”

---

## Q12. Is this an Agentic AI application?

### Word-to-word interview answer

> “No. I would describe this as a RAG-based Generative AI application, not an Agentic AI application.
>
> There are no agents, tool-calling workflows, autonomous planning, LangGraph graphs, or multi-agent orchestration in the current implementation.
>
> The application follows a predefined RAG flow: retrieve relevant policy information and then use Claude to generate an answer.”

---

## Q13. Is this a microservices application?

### Word-to-word interview answer

> “No. The current project is not a microservices architecture.
>
> It is a relatively small Python and Streamlit proof of concept. The frontend and RAG logic are separated into Python files, but that does not make them independent microservices.
>
> I prefer to describe the architecture according to what is actually implemented rather than calling it microservices.”

---

## Q14. Does your application have conversation memory?

### Word-to-word interview answer

> “No. The current implementation does not maintain multi-turn conversation history.
>
> Streamlit session state is used to keep the FAISS vector index available within the session, but that should not be confused with chatbot memory.
>
> The application currently treats each user question independently.”

---

## Q15. Where is your vector database stored?

### Word-to-word interview answer

> “The current FAISS index is created in memory.
>
> When a new Streamlit session initializes the knowledge base, the application loads the PDF, splits it, creates embeddings and builds the FAISS index.
>
> The index is then stored in Streamlit session state for that session.
>
> It is not implemented as a centrally persistent production vector database.”

---

## Q16. Why did you choose FAISS?

### Word-to-word interview answer

> “For this proof of concept, the knowledge source is small, so I didn't need to introduce an external managed vector database.
>
> FAISS allowed me to implement vector similarity search directly inside the Python application and understand the complete RAG workflow.
>
> For a production system with larger data, multiple users, persistence requirements and operational requirements, I would evaluate whether FAISS is still appropriate or whether a managed persistent vector solution would be better.”

---

## Q17. Is the application production-ready?

### Word-to-word interview answer

> “No. I describe the current version as a proof of concept.
>
> It demonstrates the core RAG workflow successfully, but several production concerns are not implemented.
>
> For example, there is no application authentication or role-based authorization, the FAISS index is not centrally persistent, there is no conversation history, automated RAG evaluation is missing, and observability and deployment automation would need improvement.
>
> So I would not describe the current implementation as a production-ready HR platform.”

---

## Q18. What are the main limitations of your current project?

### Word-to-word interview answer

> “The main limitations are around persistence, security, reliability and evaluation.
>
> The application currently depends on a fixed remote HR policy PDF, the FAISS index is created in memory for the Streamlit session, there is no user authentication or authorization, there is no conversation memory, and there is limited error handling.
>
> There is also no automated RAG evaluation framework to continuously measure retrieval and answer quality.
>
> These are areas I would address before considering the application production-ready.”

---

## Q19. How is this project different from a normal chatbot?

### Word-to-word interview answer

> “The main difference is that this application uses retrieval before generation.
>
> A basic chatbot might send the user's question directly to an LLM.
>
> In my project, the question is first used to search the HR policy through FAISS. The application retrieves the top three relevant chunks and provides those chunks to Claude along with the question.
>
> Therefore, the response is intended to be grounded in retrieved HR policy context rather than relying only on the model's general knowledge.”

---

## Q20. What did you learn from building this project?

### Word-to-word interview answer

> “The biggest thing I learned was how the individual stages of a RAG pipeline work together.
>
> Instead of using a completely managed knowledge-base service, this project allowed me to work directly with document loading, chunking, embeddings, vector indexing, similarity search, prompt construction and LLM inference.
>
> I also learned that building a working RAG demo is only one part of the problem. For production, I also need to think about document quality and freshness, security, persistent storage, evaluation, error handling, scalability, monitoring and deployment.
>
> That distinction between a working proof of concept and a production system was an important learning outcome for me.”

---

# ⭐ Most Important 5 Questions to Practice First

Don't try to memorize all 20 immediately.

Start with these:

**Q1 — Can you explain your project?**

**Q2 — What problem does it solve?**

**Q3 — Why did you use RAG?**

**Q4 — Explain the end-to-end flow.**

**Q17 — Is it production-ready?**

Once you can answer those naturally, the other questions become much easier.

And from now on, I'll follow this same pattern in every learning file:

**Learn the topic → understand your actual implementation → project-specific examples → interview questions → complete word-to-word spoken answers.**