# `03-End-to-End-Application-Flow.md`

## NovaMindAI HR Q&A — End-to-End Application Flow

### Main question

> **What exactly happens from the moment my HR Q&A application starts until the employee receives an answer?**

In `02-Current-Architecture.md`, we learned **what components exist**.

Now we focus on **runtime flow**: what happens first, what happens next, and why.

The project analysis describes the implemented sequence as PDF loading → chunking → Titan embeddings → FAISS indexing → user question → top-3 retrieval → context construction → Claude invocation → Streamlit answer. :chatgpt-content-reference{index="0"}

---

# 1. Architecture vs application flow

These sound similar, but they are different.

**Architecture** asks:

> What components are in my system?

For example:

```text
Streamlit
Python
PyPDFLoader
Text Splitter
Titan
FAISS
Claude
```

**Application flow** asks:

> In what order are those components used when my application runs?

That's what we're learning now.

---

# 2. The complete flow in one picture

![complete flow in one picture](images\end-to-end-flow.png)


Your application can be understood in **three phases**:

```text
PHASE 1 — APPLICATION INITIALIZATION
        ↓
Prepare searchable HR knowledge

PHASE 2 — USER QUESTION + RETRIEVAL
        ↓
Find relevant policy information

PHASE 3 — GENERATION + RESPONSE
        ↓
Generate and display the answer
```

More specifically:

```text
Application Starts
       ↓
Streamlit loads
       ↓
Check session_state for vector_index
       ↓
Does vector_index exist?
       │
       ├── NO
       │    ↓
       │   hr_index()
       │    ↓
       │   Load HR Policy PDF
       │    ↓
       │   Extract document text
       │    ↓
       │   Split into chunks
       │    ↓
       │   Titan embeddings
       │    ↓
       │   Build FAISS index
       │    ↓
       │   Save index in session_state
       │
       └── YES
            ↓
          Reuse index
             ↓
        User enters question
             ↓
        User clicks button
             ↓
        Validate input
             ↓
       hr_rag_response()
             ↓
       FAISS similarity search
             ↓
        Top 3 chunks
             ↓
       Combine chunk content
             ↓
        Construct prompt
             ↓
          hr_llm()
             ↓
       Claude Haiku 4.5
             ↓
       Generated AIMessage
             ↓
        Extract .content
             ↓
       Return to Streamlit
             ↓
        Display answer
```

That's your end-to-end application flow.

---

# 3. Phase 1 — Application starts

The user starts the Streamlit application.

Conceptually:

```text
streamlit run rag_frontend.py
```

Streamlit loads:

```text
rag_frontend.py
```

Your frontend also imports your backend:

```python
import rag_backend as demo
```

So think:

```text
Streamlit starts
      ↓
rag_frontend.py
      ↓
imports
      ↓
rag_backend.py
```

The frontend can now call backend functions such as:

```text
demo.hr_index()

demo.hr_rag_response(...)
```

---

# 4. Streamlit builds the UI

The application creates the user-facing interface.

This includes things such as:

```text
NovaMindAI — HR Q&A

HR policy question box

[Ask / Submit]

Answer area
```

At this stage, the employee hasn't necessarily asked anything.

But something important still needs to happen:

> **The HR policy must become searchable.**

---

# 5. Check whether the vector index already exists

Your frontend checks approximately:

```python
if 'vector_index' not in st.session_state:
    st.session_state.vector_index = demo.hr_index()
```

This is very important.

It asks:

```text
Do I already have the FAISS index
for this Streamlit session?
```

There are two possibilities.

### Case A — Index doesn't exist

```text
vector_index missing
       ↓
Call hr_index()
```

The application must prepare the HR knowledge.

### Case B — Index already exists

```text
vector_index exists
       ↓
Reuse existing index
```

It doesn't need to rebuild it for every UI interaction in that session.

---

# 6. `hr_index()` begins

This function is responsible for preparing the searchable knowledge.

Think:

```text
hr_index()

"Prepare my HR policy
so I can search it."
```

The sequence is:

```text
hr_index()
    ↓
Load PDF
    ↓
Split document
    ↓
Create embeddings
    ↓
Create FAISS index
    ↓
Return index
```

---

# 7. Load the HR Leave Policy

Your code uses `PyPDFLoader` with a fixed remote PDF URL.

Conceptually:

```text
Remote HR Leave Policy PDF
            ↓
       PyPDFLoader
            ↓
     Load document
```

The important distinction is that the current code is not waiting for an employee to upload a PDF.

It uses a predetermined policy source.

---

# 8. Extract document content

`PyPDFLoader` loads the document into objects that your Python/LangChain pipeline can process.

Conceptually:

```text
PDF
 ↓
PyPDFLoader
 ↓
Documents / page content
```

At this point, the document still needs to be prepared for retrieval.

---

# 9. Split the document

Your application creates:

```python
RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", " ", ""],
    chunk_size=1000,
    chunk_overlap=100
)
```

Then:

```text
Loaded Documents
       ↓
Text Splitter
       ↓
Chunks
```

Why?

Because you want retrieval to operate on useful portions of the policy rather than treating the entire policy as one search unit.

We'll examine the splitting algorithm much more carefully in File 09.

---

# 10. Create embeddings

Now the application has:

```text
Chunk 1
Chunk 2
Chunk 3
...
```

It configures:

```text
Amazon Titan Embeddings
```

through Amazon Bedrock.

The model configured in the inspected code is:

```text
amazon.titan-embed-text-v1
```

Conceptually:

```text
Chunk 1
   ↓
Titan
   ↓
Vector 1

Chunk 2
   ↓
Titan
   ↓
Vector 2
```

This converts textual information into vector representations that can be used for semantic retrieval.

---

# 11. Create the FAISS index

Your code then performs conceptually:

```python
FAISS.from_documents(chunks, data_embeddings)
```

This stage combines the chunks with the embedding model to build the searchable vector index.

Think:

```text
Text Chunks
     +
Titan Embeddings
     ↓
FAISS.from_documents(...)
     ↓
Searchable FAISS Index
```

Now your HR policy has become searchable using semantic similarity.

---

# 12. Return the index

`hr_index()` returns:

```text
db_index
```

So:

```text
hr_index()
    ↓
FAISS Index
    ↓
return
```

The frontend receives it.

---

# 13. Save it in Streamlit session state

The frontend stores the returned object as:

```text
st.session_state.vector_index
```

Conceptually:

```text
FAISS Index
     ↓
Streamlit Session State
     ↓
vector_index
```

This means the same session can reuse it.

### Important

This is **not permanent persistence**.

If you imagine:

```text
Employee asks Q1
Employee asks Q2
Employee asks Q3
```

the index can be reused within the session.

But the current design is not a shared durable production vector store.

---

# 14. Phase 1 is complete

At this point:

```text
PDF
 ↓
Loaded
 ↓
Chunked
 ↓
Embedded
 ↓
Indexed
 ↓
Ready for search
```

Now the system can answer questions.

This is an important mental checkpoint:

> **Before useful retrieval can happen, the knowledge must first be prepared and indexed.**

---

# 15. Phase 2 — Employee enters a question

Suppose the employee types:

> **“What is the privilege leave policy?”**

Streamlit stores that text as user input.

Conceptually:

```text
Employee
    ↓
Streamlit Text Area
    ↓
input_text
```

---

# 16. Employee clicks the button

The application checks whether the input contains meaningful text.

Conceptually:

```text
User clicks Ask
      ↓
Is input empty?
```

If empty:

```text
YES
 ↓
Show warning
```

If not empty:

```text
NO
 ↓
Continue to RAG
```

This is a small detail, but it demonstrates that the frontend performs basic input validation.

---

# 17. Streamlit calls `hr_rag_response()`

The frontend calls the backend approximately like this:

```python
response_content = demo.hr_rag_response(
    index=st.session_state.vector_index,
    question=input_text
)
```

Notice the two things being passed:

```text
1. Existing FAISS index
2. User question
```

So:

```text
FAISS Index
      +
Question
      ↓
hr_rag_response()
```

This function handles the core runtime RAG operation.

---

# 18. Configure Claude

Inside the RAG response path, your backend calls:

```text
hr_llm()
```

That function configures `ChatBedrock` for Claude.

The inspected implementation uses:

```text
Claude Haiku 4.5
temperature = 0.1
max_tokens = 3000
```

Conceptually:

```text
hr_llm()
   ↓
Configure Claude connection
   ↓
Return LLM object
```

We'll study why temperature is low later.

---

# 19. Retrieve relevant chunks

Now comes one of the most important lines in the whole project:

```python
docs = index.similarity_search(question, k=3)
```

Suppose:

```text
Question:

"What is the privilege leave policy?"
```

FAISS searches the indexed policy knowledge.

Conceptually:

```text
Question
   ↓
Semantic Search
   ↓
FAISS
   ↓
Most relevant chunk #1
Most relevant chunk #2
Most relevant chunk #3
```

Because:

```text
k = 3
```

the code asks for three results.

This is the:

# R — RETRIEVE

part of RAG.

---

# 20. A very important detail about the question

There's an important detail you should understand rather than memorize.

You don't manually write:

```python
question_embedding = titan(question)
```

in `hr_rag_response()`.

Instead, your FAISS/LangChain integration uses the embedding configuration associated with the vector store to support the similarity search.

So at a conceptual level:

```text
Question
   ↓
Embedding/search integration
   ↓
Compare against indexed vectors
   ↓
Relevant chunks
```

Later, in the Titan and FAISS files, we'll go much deeper into this.

---

# 21. Extract text from retrieved documents

FAISS returns relevant document objects.

Your application then does:

```python
context = "\n\n".join(
    [doc.page_content for doc in docs]
)
```

So if FAISS returns:

```text
Document 1
Document 2
Document 3
```

your application extracts:

```text
Document 1.page_content
Document 2.page_content
Document 3.page_content
```

and combines them.

Conceptually:

```text
Chunk 1 text
      +
Chunk 2 text
      +
Chunk 3 text
      ↓
Retrieved Context
```

---

# 22. Augment the question with context

Now the application has:

```text
User Question

+

Retrieved HR Policy Context
```

It builds a prompt conceptually like:

```text
Use the following HR policy context
to answer the question.

Context:
[Retrieved Chunk 1]

[Retrieved Chunk 2]

[Retrieved Chunk 3]

Question:
What is the privilege leave policy?

Answer:
```

This is the:

# A — AUGMENT

part of RAG.

---

# 23. Why is this step important?

Without augmentation:

```text
Question
   ↓
Claude
```

Claude has only the question.

With augmentation:

```text
Relevant HR Policy Information
             +
Employee Question
             ↓
Claude
```

Now the model has project-specific context from the policy.

That's the central idea behind your application.

---

# 24. Phase 3 — Send the prompt to Claude

Your backend then performs conceptually:

```python
rag_llm.invoke(prompt)
```

So:

```text
Constructed Prompt
       ↓
ChatBedrock
       ↓
Amazon Bedrock
       ↓
Claude Haiku 4.5
```

Claude receives the prompt and generates a response.

This is the:

# G — GENERATE

part of RAG.

---

# 25. Claude returns an AIMessage

This is another code-level detail worth understanding.

`ChatBedrock.invoke()` does not simply return a raw Python text string in this implementation.

It returns a message object.

Conceptually:

```text
Claude
  ↓
AIMessage
  │
  └── content
```

Your backend therefore returns:

```python
hr_rag_query.content
```

So:

```text
AIMessage
   ↓
.content
   ↓
Final text answer
```

---

# 26. Backend returns the answer

Now:

```text
hr_rag_response()
       ↓
return answer text
       ↓
rag_frontend.py
```

The frontend receives the generated content.

---

# 27. Streamlit displays the answer

Finally:

```text
Generated answer
      ↓
Streamlit
      ↓
st.success(...)
      ↓
Employee sees answer
```

The end-to-end request is complete.

---

# 28. Complete example from start to finish

Suppose the application has just started.

### Stage 1 — Prepare knowledge

```text
Streamlit starts
      ↓
No vector_index in session
      ↓
hr_index()
      ↓
Download/load HR policy PDF
      ↓
Extract document content
      ↓
Split into chunks
      ↓
Titan creates embeddings
      ↓
FAISS index created
      ↓
Store index in session_state
```

### Stage 2 — Employee asks

```text
Employee:
"What is the privilege leave policy?"
          ↓
Streamlit
          ↓
hr_rag_response()
```

### Stage 3 — Retrieve

```text
Question
    ↓
FAISS similarity_search(k=3)
    ↓
Top 3 relevant chunks
```

### Stage 4 — Augment

```text
Chunk 1
+
Chunk 2
+
Chunk 3
+
Employee Question
       ↓
RAG Prompt
```

### Stage 5 — Generate

```text
RAG Prompt
    ↓
Claude Haiku 4.5
via Amazon Bedrock
    ↓
AIMessage
    ↓
.content
```

### Stage 6 — Display

```text
Answer text
    ↓
Streamlit
    ↓
Employee
```

That is the complete application lifecycle for a question.

---

# 29. What happens with the second question?

This is an excellent interview concept.

Suppose the same Streamlit session asks another question.

Does the application necessarily do this again?

```text
PDF
→ split
→ embed everything
→ create FAISS
```

Not on every UI interaction if `vector_index` remains in that session state.

Instead:

```text
Second question
      ↓
Streamlit reruns
      ↓
vector_index exists?
      ↓
YES
      ↓
Reuse index
      ↓
Retrieve
      ↓
Generate
```

So the expensive preparation is avoided on ordinary subsequent interactions in the same session.

---

# 30. What happens with a new session?

This exposes a limitation.

Conceptually:

```text
New Streamlit Session
       ↓
No vector_index
       ↓
hr_index()
       ↓
Load PDF again
       ↓
Chunk again
       ↓
Create embeddings again
       ↓
Build FAISS again
```

That's acceptable for a small PoC.

But imagine:

```text
1 user
10 users
100 users
10,000 users
```

Repeated indexing becomes a design concern.

That's why later, when we study production V2, we'll consider a **shared/versioned persistent knowledge index** instead of rebuilding it independently for sessions.

---

# 31. Where exactly is RAG?

If the interviewer asks:

> “Show me exactly where RAG happens.”

You can answer:

```text
                 RAG

R — RETRIEVAL
Question
   ↓
FAISS similarity search
   ↓
Top 3 relevant chunks


A — AUGMENTATION
Retrieved chunks
       +
Question
       ↓
Construct prompt


G — GENERATION
Prompt
   ↓
Claude Haiku 4.5
   ↓
Answer
```

That's your RAG implementation.

---

# 32. What Claude does NOT do

Claude does **not**:

```text
❌ Download the PDF
❌ Split the PDF
❌ Build FAISS
❌ Search FAISS itself
❌ Decide which vector database to query
```

Your application performs those operations.

Claude receives:

```text
Retrieved Context
+
Question
```

and performs:

```text
Generation
```

This distinction is important in technical interviews.

---

# 33. What FAISS does NOT do

Similarly, FAISS does not:

```text
❌ Generate HR answers
❌ Understand business rules independently
❌ Call Claude
❌ Build the final natural-language response
```

FAISS's core role here is:

> **Retrieve semantically relevant policy chunks.**

---

# 34. What Streamlit does NOT do

Streamlit isn't your LLM.

It isn't your embedding model.

It isn't your vector database.

Its main responsibility is the application interface and session-level coordination.

Think:

```text
Streamlit = UI / interaction layer

Python backend = RAG orchestration

Titan = embeddings

FAISS = retrieval

Claude = generation
```

This mental map is extremely important.

---

# 35. The five functions/actions you should mentally follow

When looking at the code, think:

```text
START APPLICATION
       ↓
CHECK SESSION STATE
       ↓
hr_index()
       ↓
USER ASKS QUESTION
       ↓
hr_rag_response()
       ↓
hr_llm()
       ↓
FAISS SEARCH + PROMPT + CLAUDE
       ↓
DISPLAY ANSWER
```

Later we'll study exactly which line performs each operation.

---

# 36. End-to-end flow in one sentence

Eventually, you should be able to say:

> **“When the Streamlit application starts, it creates a FAISS index for the HR policy if one is not already available in the current session by loading the PDF, chunking the text and generating Titan embeddings; when the employee asks a question, the backend retrieves the top three relevant chunks from FAISS, combines them with the question, sends that prompt to Claude Haiku 4.5 through Amazon Bedrock, extracts the generated content and displays the answer in Streamlit.”**

That's your entire runtime flow in one sentence.

---

# Interview Questions & Answers — `03-End-to-End-Application-Flow.md`

## Q1. Can you explain the complete end-to-end flow of your application?

### Word-to-word interview answer

> “Sure. I divide the application flow into knowledge preparation and question answering.
>
> When the Streamlit application starts, it checks whether the FAISS vector index is already available in the current session.
>
> If it is not available, the frontend calls my `hr_index()` function. This function loads the HR Leave Policy PDF using PyPDFLoader, splits the document into overlapping chunks using RecursiveCharacterTextSplitter, creates embeddings using Amazon Titan through Bedrock and builds a FAISS vector index.
>
> The index is then stored in Streamlit session state.
>
> When an employee enters a question, Streamlit passes the existing index and the question to my `hr_rag_response()` function.
>
> The backend performs a FAISS similarity search with k equal to three and retrieves the top three relevant policy chunks.
>
> I combine those chunks into context, add the employee's question and construct the RAG prompt.
>
> The prompt is sent to Claude Haiku 4.5 through Amazon Bedrock. Claude generates the answer, the backend extracts the content from the returned message, and Streamlit displays the final answer to the employee.”

---

## Q2. What happens when the application starts for the first time?

### Word-to-word interview answer

> “When the Streamlit application starts, it checks whether `vector_index` exists in Streamlit session state.
>
> If the index doesn't exist, the application calls `hr_index()`.
>
> That function loads the HR policy, splits it into chunks, creates embeddings using Amazon Titan and builds the FAISS index.
>
> The returned index is stored in session state so it can be reused within that session.”

---

## Q3. Why do you check Streamlit session state?

### Word-to-word interview answer

> “I use session state so that the application can reuse the FAISS index during the current Streamlit session.
>
> Streamlit reruns the script when the user interacts with the application, so without session state I could unnecessarily rebuild the index on ordinary interactions.
>
> However, session state is not persistent vector storage. It is only session-level application state.”

---

## Q4. What does `hr_index()` do?

### Word-to-word interview answer

> “The `hr_index()` function prepares the HR knowledge for retrieval.
>
> It loads the HR Leave Policy using PyPDFLoader, splits the document using RecursiveCharacterTextSplitter, configures Amazon Titan embeddings through Bedrock and creates a FAISS index from the resulting document chunks.
>
> It then returns that FAISS index to the frontend.”

---

## Q5. What happens when the user submits a question?

### Word-to-word interview answer

> “The frontend first validates that the question is not empty.
>
> It then passes the user's question together with the FAISS index from session state to `hr_rag_response()`.
>
> That function performs similarity retrieval, constructs the context-based prompt, invokes Claude through Bedrock and returns the generated answer to Streamlit.”

---

## Q6. How does retrieval happen?

### Word-to-word interview answer

> “Retrieval happens using FAISS similarity search.
>
> My backend calls `similarity_search` with the user's question and k equal to three.
>
> The vector-store integration uses semantic embeddings to compare the query with the indexed HR policy chunks and returns the top three relevant document chunks.
>
> Those retrieved chunks become the context for the LLM.”

---

## Q7. Why do you retrieve three chunks?

### Word-to-word interview answer

> “In the current proof of concept, I configured k equal to three, so the application retrieves three relevant chunks.
>
> This is a project configuration choice rather than a universal best value.
>
> In a production system, I would evaluate different retrieval settings using representative HR questions and measure retrieval and answer quality rather than assuming three is always optimal.”

---

## Q8. What happens after FAISS returns the documents?

### Word-to-word interview answer

> “After FAISS returns the top three document chunks, my code extracts the `page_content` from each document and joins those pieces together into one context string.
>
> I then combine that retrieved context with the employee's question to construct the prompt that will be sent to Claude.”

---

## Q9. What exactly do you send to Claude?

### Word-to-word interview answer

> “I send a prompt containing an instruction, the HR policy context retrieved from FAISS and the employee's question.
>
> So Claude is not receiving only the question. It receives the relevant policy context along with the question, which is the augmentation part of the RAG process.”

---

## Q10. Does Claude retrieve the documents?

### Word-to-word interview answer

> “No. Claude does not perform retrieval in this implementation.
>
> My Python application performs the FAISS similarity search first.
>
> After retrieving the relevant chunks, the application constructs the prompt and then sends that prompt to Claude.
>
> So FAISS handles retrieval and Claude handles generation.”

---

## Q11. What does `hr_llm()` do?

### Word-to-word interview answer

> “The `hr_llm()` function configures the Claude model connection using `ChatBedrock`.
>
> In the current implementation, it configures Claude Haiku 4.5 with model parameters such as a temperature of 0.1 and maximum output tokens of 3000.
>
> It returns the configured LLM object, which is then used by the RAG response function.”

---

## Q12. What does `hr_rag_response()` do?

### Word-to-word interview answer

> “`hr_rag_response()` handles the main runtime RAG flow.
>
> It receives the FAISS index and the employee's question, configures the LLM, retrieves the top three relevant chunks from FAISS, joins their content into context, constructs the RAG prompt, invokes Claude and returns the generated text.”

---

## Q13. What does Claude return to your application?

### Word-to-word interview answer

> “In my implementation, `ChatBedrock.invoke()` returns an AI message object.
>
> The generated text is available through its `content` property.
>
> Therefore, my backend returns `hr_rag_query.content` to the frontend.”

---

## Q14. What happens when the same user asks another question?

### Word-to-word interview answer

> “If the FAISS index is still available in that Streamlit session, the application reuses it.
>
> It doesn't need to rebuild the document index for every question.
>
> The new question goes through retrieval, prompt construction and Claude generation using the existing session index.”

---

## Q15. What happens for a new Streamlit session?

### Word-to-word interview answer

> “In the current design, a new session that doesn't have `vector_index` in session state will call `hr_index()` again.
>
> That means the application may reload the policy, split it, generate embeddings and rebuild the FAISS index for that new session.
>
> This is acceptable for the proof of concept, but it is one of the areas I would redesign for a multi-user production system.”

---

## Q16. Where exactly does RAG happen?

### Word-to-word interview answer

> “RAG happens in three stages.
>
> Retrieval happens when FAISS searches for the top three relevant HR policy chunks.
>
> Augmentation happens when my Python application combines those retrieved chunks with the user's question to build the prompt.
>
> Generation happens when Claude Haiku 4.5 receives that prompt through Amazon Bedrock and generates the final answer.
>
> So the flow is retrieve, augment and generate.”

---

## Q17. What happens if the employee submits an empty question?

### Word-to-word interview answer

> “The Streamlit frontend checks the input before calling the RAG backend.
>
> If the question is empty after removing whitespace, the application displays a warning instead of sending an unnecessary request through the RAG pipeline.”

---

## Q18. Does the application remember previous questions?

### Word-to-word interview answer

> “No. The current implementation does not maintain conversation history.
>
> Streamlit session state stores the vector index, but that should not be confused with chat memory.
>
> Each HR question is processed independently against the policy index.”

---

## Q19. Where could this end-to-end flow fail?

### Word-to-word interview answer

> “There are several possible failure points.
>
> The remote PDF could fail to load, document parsing could fail, the Bedrock embedding request could fail because of credentials, permissions, region or model access, FAISS indexing or retrieval could fail, and the Claude invocation could also fail.
>
> The current implementation has limited error handling, so productionizing the application would require better exception handling, logging and observability across these stages.”

---

## Q20. How would you explain this flow in 30 seconds?

### Word-to-word interview answer

> “When the application starts, it loads and chunks the HR policy, generates Titan embeddings through Bedrock and builds an in-memory FAISS index. When an employee asks a question, FAISS retrieves the top three relevant policy chunks. My Python code combines those chunks with the question and sends the resulting prompt to Claude Haiku 4.5 through Bedrock. Claude generates the answer, and Streamlit displays it to the employee.”

---

# Important interview trap

An interviewer may ask:

> **“When a user asks a question, do you create all the document embeddings again?”**

Don't simply answer:

> “Yes.”

For an existing index in the same Streamlit session, the question path is:

```text
Question
   ↓
Reuse existing FAISS index
   ↓
Retrieve
   ↓
Augment
   ↓
Generate
```

The document-index creation path happens when the session doesn't already have the index.

---

# Five questions to master first

For this file, focus first on:

**Q1. Explain the complete end-to-end flow.**

**Q2. What happens when the application starts?**

**Q5. What happens when a user asks a question?**

**Q16. Where exactly does RAG happen?**

**Q15. What happens with a new session?**

Your simplest mental model should now be:

```text
APPLICATION START
      ↓
Check Index
      ↓
If missing:
PDF → Chunk → Embed → FAISS
      ↓
USER QUESTION
      ↓
FAISS → Top 3
      ↓
Context + Question
      ↓
Claude
      ↓
Answer
      ↓
Streamlit
```

That is the complete **end-to-end application flow** of your current HR Q&A RAG proof of concept.



---
---
---
---

![complete flow in one picture](images\end-to-end-flow.png)

# How to Explain the End-to-End Application Flow in an Interview

Yes. Now that you understand the diagram, the goal is to explain it **naturally**, not read every box.

Use this structure:

> **Initialization → Indexing → User Question → Retrieve → Augment → Generate → Display**

## Word-to-word interview answer

> “Sure. I’ll explain the application flow in two main parts: first, how the HR policy knowledge is prepared, and second, what happens when an employee asks a question.
>
> When the Streamlit application starts, it first checks whether the FAISS vector index is already available in the current Streamlit session.
>
> If the index is not available, the application calls my `hr_index()` function. Inside this function, I load the HR Leave Policy PDF using `PyPDFLoader`.
>
> After loading the document, I use `RecursiveCharacterTextSplitter` to divide the policy into smaller overlapping chunks. In my current implementation, the chunk size is 1000 and the chunk overlap is 100.
>
> Next, I use Amazon Titan Embeddings through Amazon Bedrock to convert those text chunks into vector embeddings.
>
> These embeddings are then used to create an in-memory FAISS vector index. I store that index in Streamlit session state so that it can be reused for additional questions within the same session instead of rebuilding it on every interaction.
>
> Once the index is ready, the application can handle employee questions.
>
> For example, suppose an employee asks, ‘What is the privilege leave policy?’ through the Streamlit interface.
>
> Streamlit validates the input and passes the question, along with the existing FAISS index, to my `hr_rag_response()` function.
>
> This is where the actual RAG flow happens.
>
> First is **retrieval**. The application performs a FAISS similarity search with `k=3`, which retrieves the top three relevant chunks from the HR policy.
>
> Second is **augmentation**. My Python code takes those three retrieved chunks, combines their content, and adds the employee’s question to construct a RAG prompt.
>
> Third is **generation**. I send that prompt to Claude Haiku 4.5 through Amazon Bedrock. Claude uses the retrieved HR policy context together with the user’s question to generate the final answer.
>
> `ChatBedrock` returns an AI message, so my backend extracts the generated text from its `content` property and returns it to the Streamlit frontend.
>
> Finally, Streamlit displays the generated HR policy answer to the employee.
>
> So, in simple terms, the complete flow is: **load the policy, split it, create embeddings, build the FAISS index, retrieve relevant chunks for a question, augment the prompt with those chunks, generate the answer with Claude, and display it through Streamlit.**”

## What to point at on your diagram

While explaining the diagram, move through it in this order:

```text
START
  │
  ▼
HR Leave Policy PDF
  │
  ▼
PyPDFLoader
  │
  ▼
Text Splitter
  │
  ▼
Text Chunks
  │
  ▼
Titan Embeddings
  │
  ▼
FAISS Index
  │
  ▼
Streamlit Session State

──────────── QUESTION FLOW ────────────

Employee Question
  │
  ▼
Streamlit
  │
  ▼
Python RAG Backend
  │
  ▼
RETRIEVE
FAISS → Top 3 Chunks
  │
  ▼
AUGMENT
Context + Question
  │
  ▼
GENERATE
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

The **three words you should emphasize** when you reach the bottom half are:

> **Retrieve → Augment → Generate**

That demonstrates you understand what makes the application RAG rather than simply an LLM chatbot.

### Shorter 45-second version

If the interviewer says, **“Give me the flow quickly,”** say:

> “When the application starts, it loads the HR Leave Policy PDF, splits the document into chunks and creates embeddings using Amazon Titan through Bedrock. Those embeddings are indexed in an in-memory FAISS vector store and the index is kept in Streamlit session state.
>
> When an employee asks a question, my backend performs a FAISS similarity search and retrieves the top three relevant policy chunks. I combine those chunks with the employee’s question to construct the RAG prompt and send it to Claude Haiku 4.5 through Amazon Bedrock.
>
> Claude generates the answer using that retrieved context, and the response is returned to Streamlit and displayed to the employee.
>
> So the RAG part is simply **retrieve with FAISS, augment with policy context, and generate with Claude.**”

For interviews, learn the **flow and reasoning**, then practice saying it in your own words rather than trying to reproduce every sentence exactly.