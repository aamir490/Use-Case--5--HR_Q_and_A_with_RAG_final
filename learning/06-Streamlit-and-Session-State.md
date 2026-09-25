# `06-Streamlit-and-Session-State.md`

## NovaMindAI HR Q&A — Streamlit and Session State

### Main question

> **How does Streamlit work in my HR Q&A project, why do I use `st.session_state`, and what exactly happens when Streamlit reruns the application?**

This file is important because there is an easy misunderstanding:

> **Streamlit Session State is NOT conversation memory and is NOT persistent vector storage.**

In your project, its main purpose is much simpler:

> **Keep the FAISS vector index available across Streamlit reruns for the current user session.**

---

# 1. Where are we in the learning path?

So far:

```text
01 → Project Overview
02 → Current Architecture
03 → End-to-End Flow
04 → Technology Stack
05 → Backend Code
06 → STREAMLIT + SESSION STATE
```

In File 05, we studied:

```text
rag_backend.py
```

Now we're mainly looking at:

```text
rag_frontend.py
```

The frontend imports the backend and stores the vector index in Streamlit session state. That matches the project's current single-application RAG design rather than a separate API/microservice architecture. :chatgpt-content-reference{index="0"}

---

# 2. First understand Streamlit

Streamlit is a Python framework for creating interactive web applications.

In your project:

```text
Employee
    ↓
Web Browser
    ↓
Streamlit Application
    ↓
rag_frontend.py
```

It gives the employee an interface for asking questions about the HR Leave Policy.

Think of Streamlit's role as:

```text
┌─────────────────────────────┐
│       STREAMLIT UI          │
│                             │
│  NovaMindAI — HR Q&A        │
│                             │
│  Ask your question:         │
│  ┌───────────────────────┐  │
│  │ What is privilege     │  │
│  │ leave?                │  │
│  └───────────────────────┘  │
│                             │
│       [ Ask Question ]      │
│                             │
│  Answer: ...                │
└─────────────────────────────┘
```

Streamlit is therefore your:

> **User interaction layer.**

---

# 3. What does `rag_frontend.py` do?

Your frontend has several responsibilities:

```text
rag_frontend.py
       │
       ├── Configure/display UI
       │
       ├── Display logo/sidebar information
       │
       ├── Check session state
       │
       ├── Build FAISS index if needed
       │
       ├── Accept employee question
       │
       ├── Validate question
       │
       ├── Call backend
       │
       └── Display answer
```

Notice something important:

It does **not** implement the entire RAG logic itself.

Instead:

```text
rag_frontend.py
      ↓
UI + application state

rag_backend.py
      ↓
RAG processing
```

---

# 4. Frontend imports backend

Your frontend uses:

```python
import rag_backend as demo
```

This means:

```text
rag_frontend.py
       │
       │ imports
       ▼
rag_backend.py
```

Then the frontend can call backend functions such as:

```python
demo.hr_index()
```

and:

```python
demo.hr_rag_response(...)
```

So there isn't a REST API call between these two files.

They are Python modules in the same application.

That distinction matters.

---

# 5. Frontend → Backend communication

A beginner might imagine:

```text
Streamlit
   ↓
API Gateway
   ↓
REST API
   ↓
Backend server
```

That is **not** the current implementation.

Your flow is closer to:

```text
Streamlit Python Code
        ↓
Python function call
        ↓
rag_backend.py
```

For example:

```python
demo.hr_index()
```

is a normal Python function call.

Likewise:

```python
demo.hr_rag_response(...)
```

is another Python function call.

---

# 6. Now the most important concept: Streamlit reruns

Streamlit has a behavior you need to understand.

When the user interacts with widgets, Streamlit can rerun the application script.

Imagine:

```text
Application starts
      ↓
Python script runs
      ↓
UI displayed

Employee interacts
      ↓
Streamlit reruns script
      ↓
UI updated
```

This creates a problem.

Suppose every rerun did this:

```text
Load PDF
   ↓
Split PDF
   ↓
Call Titan for all chunks
   ↓
Create FAISS
```

again.

That would be unnecessary.

---

# 7. The problem without session state

Imagine you wrote:

```python
index = demo.hr_index()
```

unconditionally at the top level.

Conceptually:

```text
FIRST RUN

hr_index()
   ↓
Load PDF
   ↓
Split
   ↓
Titan embeddings
   ↓
Build FAISS
```

Then an interaction causes another rerun:

```text
RERUN

hr_index()
   ↓
Load PDF AGAIN
   ↓
Split AGAIN
   ↓
Embeddings AGAIN
   ↓
FAISS AGAIN
```

Then another interaction:

```text
RERUN AGAIN

Build everything AGAIN
```

That would repeat expensive work.

---

# 8. Solution — `st.session_state`

Your project uses Streamlit's:

```python
st.session_state
```

Think of session state as a temporary Python-like storage area associated with the current Streamlit session.

Conceptually:

```text
Current Streamlit Session

┌──────────────────────────────┐
│ session_state                │
│                              │
│ vector_index = FAISS object  │
│                              │
└──────────────────────────────┘
```

So the application can ask:

> **“Have I already created the vector index for this session?”**

---

# 9. The key code

Your frontend uses the logic:

```python
if 'vector_index' not in st.session_state:
    st.session_state.vector_index = demo.hr_index()
```

This small block is extremely important.

Let's understand every part.

---

# 10. What does this condition mean?

```python
if 'vector_index' not in st.session_state:
```

means:

> **If the current session does not already contain something called `vector_index`, run the following code.**

Conceptually:

```text
Does vector_index exist?

        │
   ┌────┴────┐
   │         │
  NO        YES
   │         │
   ▼         ▼
Build      Reuse
Index      Index
```

---

# 11. First application session

Imagine the employee opens the application.

Initially:

```text
session_state

{}
```

There is no:

```text
vector_index
```

Therefore:

```python
'vector_index' not in st.session_state
```

is:

```text
TRUE
```

So Streamlit calls:

```python
demo.hr_index()
```

---

# 12. What happens inside `hr_index()`?

From File 05:

```text
demo.hr_index()
      ↓
Load HR Policy PDF
      ↓
Split into chunks
      ↓
Titan embeddings
      ↓
Create FAISS index
      ↓
return db_index
```

The frontend receives that FAISS object.

---

# 13. Store the index

Then:

```python
st.session_state.vector_index = demo.hr_index()
```

means conceptually:

```text
FAISS Index
     ↓
Store in
     ↓
st.session_state
```

Now:

```text
session_state

{
    vector_index: FAISS(...)
}
```

The actual object is held in session state for reuse during that session.

---

# 14. User asks a question

Now suppose the employee types:

> **“What is the privilege leave policy?”**

and clicks the button.

Streamlit handles the interaction and the script reruns.

Now it reaches:

```python
if 'vector_index' not in st.session_state:
```

again.

But this time:

```text
session_state

{
    vector_index: FAISS(...)
}
```

So:

```text
'vector_index' not in session_state
```

is:

```text
FALSE
```

Therefore:

```python
demo.hr_index()
```

does **not** need to run again on that rerun.

---

# 15. The existing index is reused

The frontend later passes:

```python
index=st.session_state.vector_index
```

to:

```python
demo.hr_rag_response(...)
```

So:

```text
Existing FAISS Index
        ↓
session_state.vector_index
        ↓
hr_rag_response()
        ↓
Similarity Search
```

That's the main reason session state matters in this project.

---

# 16. Complete first-run flow

Let's visualize it.

```text
Employee Opens Application
          ↓
Streamlit Starts
          ↓
rag_frontend.py runs
          ↓
Check session_state
          ↓
Does vector_index exist?
          ↓
         NO
          ↓
demo.hr_index()
          ↓
Load PDF
          ↓
Chunk
          ↓
Titan Embeddings
          ↓
Build FAISS
          ↓
Return FAISS Index
          ↓
st.session_state.vector_index
          ↓
Application Ready
```

---

# 17. Subsequent interaction flow

Now:

```text
Employee asks question
          ↓
Streamlit reruns
          ↓
Check session_state
          ↓
Does vector_index exist?
          ↓
         YES
          ↓
Do NOT rebuild it
          ↓
Use existing vector_index
          ↓
hr_rag_response()
          ↓
Retrieve
          ↓
Augment
          ↓
Generate
          ↓
Display answer
```

This is the key difference.

---

# 18. Why does this matter financially?

Remember how `hr_index()` works:

```text
PDF
 ↓
Chunking
 ↓
Titan embedding calls
 ↓
FAISS
```

Titan embeddings involve Amazon Bedrock.

If you unnecessarily rebuild the index repeatedly, you potentially repeat:

```text
Embedding requests
+
processing
+
latency
```

So session reuse helps avoid unnecessary repeated work during the same session.

---

# 19. Session state is NOT persistent storage

This is the biggest interview trap.

Suppose your session contains:

```text
st.session_state.vector_index
```

Does that mean the FAISS index is permanently saved?

**No.**

Think:

```text
Session State

TEMPORARY APPLICATION STATE
```

not:

```text
Permanent Database
```

Your current architecture does not implement something like:

```text
FAISS index
   ↓
Save durable index files
   ↓
S3 / persistent disk
   ↓
Load after restart
```

as the normal application lifecycle.

---

# 20. Session state is NOT conversation memory

Another major misunderstanding:

You have:

```python
st.session_state.vector_index
```

Does that mean Claude remembers:

```text
Question 1
Question 2
Question 3
```

No.

You're storing:

```text
vector_index
```

not:

```text
chat_history
```

The current design is:

```text
Question 1
   ↓
RAG
   ↓
Answer 1


Question 2
   ↓
RAG
   ↓
Answer 2
```

Question 2 is not automatically sent to Claude together with Question 1 and Answer 1.

So there is no implemented multi-turn conversational memory.

---

# 21. Example showing no conversation memory

Imagine:

### Question 1

> “How many privilege leaves are allowed?”

The application retrieves relevant policy context and answers.

Then the employee asks:

### Question 2

> “Can I carry them forward?”

A human knows:

> “them” = privilege leaves.

But your current implementation sends the new question independently:

```text
"Can I carry them forward?"
```

along with whatever chunks FAISS retrieves.

It does not explicitly provide Claude with:

```text
Previous Question:
How many privilege leaves are allowed?

Previous Answer:
...

Current Question:
Can I carry them forward?
```

Therefore conversational references may be weaker or ambiguous.

---

# 22. What would actual conversation memory look like?

Conceptually, you might store:

```python
st.session_state.messages
```

with:

```text
User: What is privilege leave?

Assistant: ...

User: Can I carry it forward?

Assistant: ...
```

Then deliberately provide relevant conversation history to the model.

But your current implementation does not do that.

This is a **future improvement**, not a current feature.

---

# 23. Session state vs vector database vs conversation memory

This distinction is extremely important:

| Concept | Purpose | Current Project |
|---|---|---|
| Session State | Temporary application state | ✅ Yes |
| FAISS | Vector indexing/retrieval | ✅ Yes |
| Persistent vector store | Durable shared vector data | ❌ No |
| Conversation memory | Remember prior dialogue | ❌ No |

Don't mix these concepts.

---

# 24. Streamlit's role in the question flow

Once the index exists:

```text
Employee
   ↓
Streamlit text area
   ↓
input_text
   ↓
Button click
   ↓
Validate input
   ↓
demo.hr_rag_response(...)
```

The important call is:

```python
response_content = demo.hr_rag_response(
    index=st.session_state.vector_index,
    question=input_text
)
```

Notice:

```text
Backend receives

1. Existing index
2. Current question
```

It does **not** receive:

```text
previous chat history
```

---

# 25. Empty input validation

Your frontend checks:

```python
input_text.strip()
```

Why use `.strip()`?

Suppose the employee enters:

```text
"      "
```

Technically, that's a string containing spaces.

But:

```python
"      ".strip()
```

becomes:

```text
""
```

So the frontend can recognize that the user hasn't entered a meaningful question.

Conceptually:

```text
User Input
    ↓
.strip()
    ↓
Empty?
   / \
 YES  NO
 ↓     ↓
Warn  RAG
```

---

# 26. Backend call

For valid input:

```python
response_content = demo.hr_rag_response(
    index=st.session_state.vector_index,
    question=input_text
)
```

Now connect File 06 to File 05.

The frontend provides:

```text
vector_index
+
question
```

The backend performs:

```text
Retrieve
   ↓
Augment
   ↓
Generate
```

and returns:

```text
response_content
```

---

# 27. Displaying the response

The frontend then displays the generated response using Streamlit.

Conceptually:

```text
Claude
 ↓
Backend
 ↓
response_content
 ↓
Streamlit
 ↓
Employee
```

So Streamlit participates at both ends:

```text
Streamlit
   ↓
Collect question

        RAG processing

Streamlit
   ↑
Display answer
```

---

# 28. Frontend and backend relationship

You should now understand this architecture:

```text
┌───────────────────────────────────┐
│          rag_frontend.py          │
│                                   │
│ Streamlit UI                      │
│ Input validation                  │
│ Session state                     │
│ Display answer                    │
└─────────────────┬─────────────────┘
                  │
            Python calls
                  │
                  ▼
┌───────────────────────────────────┐
│           rag_backend.py          │
│                                   │
│ hr_index()                        │
│ hr_llm()                          │
│ hr_rag_response()                 │
└───────────────────────────────────┘
```

No REST API is between them.

---

# 29. What happens if the application/session state is lost?

The current application does not have a durable shared index.

So when the relevant session no longer has:

```text
vector_index
```

the application must go through:

```text
hr_index()
   ↓
Load
   ↓
Split
   ↓
Embed
   ↓
FAISS
```

again.

This is one of the project's important scalability limitations.

---

# 30. What about multiple users?

Imagine:

```text
Employee A
Employee B
Employee C
```

The current design should not be described as:

> “All employees use one permanently stored enterprise FAISS database.”

That is not what this implementation proves.

Instead, the architecture relies on Streamlit session-level state for its index lifecycle.

For a production multi-user system, you'd normally reconsider how the knowledge index is created, persisted, shared and versioned.

We'll study that in:

`14-State-Memory-and-Index-Lifecycle.md`

and:

`22-Production-V2-and-Design-Decisions.md`

---

# 31. Why this design is acceptable for a PoC

Remember: this is a proof of concept.

For a PoC, this design is useful because it's:

```text
Simple
+
Easy to demonstrate
+
Easy to understand
+
Requires little infrastructure
```

You can demonstrate:

```text
PDF
→ embeddings
→ FAISS
→ retrieval
→ Claude
```

without first building:

```text
distributed frontend
+
API layer
+
persistent vector infrastructure
+
authentication
+
multi-user state management
```

The important thing is to recognize where the design stops being suitable as requirements grow.

---

# 32. Streamlit in one sentence

> **“Streamlit provides the employee-facing web interface, manages interaction-driven reruns and holds the FAISS vector index in session state so the application can reuse it during the current session.”**

---

# 33. Session State in one sentence

> **“I use Streamlit session state to temporarily retain the FAISS vector index across reruns within the current session, not as permanent storage or conversational memory.”**

That sentence is worth mastering.

---

# 34. Full mental model

```text
                STREAMLIT SESSION

Application starts
       ↓
rag_frontend.py
       ↓
Check session_state
       ↓
┌───────────────────────────────┐
│ Does vector_index exist?      │
└───────────────┬───────────────┘
                │
          ┌─────┴─────┐
          │           │
         NO          YES
          │           │
          ▼           │
      hr_index()      │
          │           │
      Build FAISS     │
          │           │
          ▼           │
Store in session      │
          │           │
          └─────┬─────┘
                ▼
          Existing Index
                │
                ▼
        Employee Question
                │
                ▼
      hr_rag_response()
                │
                ▼
       FAISS Retrieval
                │
                ▼
      Context + Question
                │
                ▼
             Claude
                │
                ▼
             Answer
                │
                ▼
            Streamlit
```

---

# Interview Questions & Answers — `06-Streamlit-and-Session-State.md`

## Q1. What is Streamlit's role in your project?

### Word-to-word interview answer

> “Streamlit provides the user-facing web interface for my HR Q&A application. It accepts the employee's question, performs basic input validation, maintains the FAISS vector index in session state, calls my Python backend functions and displays the generated answer. Since this is a proof of concept, Streamlit allowed me to build the interface directly in Python without creating a separate frontend and REST API.”

---

## Q2. Why are you using Streamlit Session State?

### Word-to-word interview answer

> “I use Streamlit session state to retain the FAISS vector index across reruns within the current Streamlit session. If `vector_index` doesn't exist, the application calls `hr_index()` and builds it. Once it exists, subsequent interactions can reuse that index instead of rebuilding the complete document embedding pipeline every time.”

---

## Q3. What does this code do?

```python
if 'vector_index' not in st.session_state:
    st.session_state.vector_index = demo.hr_index()
```

### Word-to-word interview answer

> “This code checks whether the current Streamlit session already contains the FAISS vector index. If it doesn't, the application calls `hr_index()`, which loads the HR policy, chunks it, creates Titan embeddings and builds the FAISS index. The returned index is then stored in session state so it can be reused during later reruns in that session.”

---

## Q4. Why would Streamlit rerun your script?

### Word-to-word interview answer

> “Streamlit uses a rerun-based execution model for user interactions. When a user interacts with widgets, the Python script can run again to update the application state and interface. Because of that behavior, I use session state for the vector index so expensive initialization work doesn't have to be repeated on every ordinary interaction.”

---

## Q5. What would happen without session state?

### Word-to-word interview answer

> “If I called `hr_index()` unconditionally during every Streamlit rerun, the application could repeatedly load the policy, split it, call the embedding model and rebuild the FAISS index. That would add unnecessary latency and repeated embedding work. Session state allows me to reuse the existing index within the session.”

---

## Q6. Is Streamlit Session State a database?

### Word-to-word interview answer

> “No. Streamlit session state is application state associated with a user session. In my project I use it to hold the FAISS index temporarily. I don't treat it as durable database storage.”

---

## Q7. Is your FAISS index persistent?

### Word-to-word interview answer

> “Not in the current application design. The FAISS index is created in memory and stored through Streamlit session state for reuse in that session. The application does not implement a durable shared vector-index persistence layer.”

---

## Q8. Does Session State provide conversation memory?

### Word-to-word interview answer

> “No. In my current implementation, session state stores the FAISS vector index, not the conversation history. Each user question is passed independently to the RAG backend. So session state should not be confused with LLM conversation memory.”

---

## Q9. Does Claude remember the previous question?

### Word-to-word interview answer

> “Not through the current implementation. I don't maintain and send a conversation history to Claude. The backend receives the current question and retrieved policy context. Therefore, I would describe the application as single-turn policy Q&A rather than a conversational chatbot with memory.”

---

## Q10. How does the frontend communicate with the backend?

### Word-to-word interview answer

> “The frontend imports `rag_backend.py` as a Python module and calls its functions directly. For example, it calls `demo.hr_index()` to build the vector index and `demo.hr_rag_response()` to process a question. There is no REST API or API Gateway between the Streamlit frontend and backend in the current implementation.”

---

## Q11. What does the frontend pass to `hr_rag_response()`?

### Word-to-word interview answer

> “The frontend passes two main things: the existing FAISS index from `st.session_state.vector_index` and the current user question. The backend then uses that index to retrieve relevant HR policy chunks and generate the answer.”

---

## Q12. Why do you use `input_text.strip()`?

### Word-to-word interview answer

> “I use `strip()` to remove leading and trailing whitespace before checking the input. This prevents an input containing only spaces from being treated as a valid HR question. If the resulting input is empty, the frontend displays a warning instead of calling the RAG backend.”

---

## Q13. What happens when the same employee asks a second question?

### Word-to-word interview answer

> “If the FAISS index is still available in that Streamlit session, the script sees that `vector_index` already exists in session state and reuses it. The second question can therefore go directly through retrieval, augmentation and generation without rebuilding the document index.”

---

## Q14. What happens in a new session?

### Word-to-word interview answer

> “If a new session doesn't contain `vector_index` in session state, the application calls `hr_index()` again. That means it loads the policy, performs chunking and embeddings and builds a new FAISS index. This is acceptable for the current proof of concept but is an important limitation for a larger multi-user production application.”

---

## Q15. Why not just rebuild FAISS every time?

### Word-to-word interview answer

> “Because rebuilding the index repeats work that hasn't changed. The HR policy chunks would need to be processed and embedded again, which adds latency and additional embedding calls. Reusing the index within the session is more efficient.”

---

## Q16. Is your Streamlit frontend a separate microservice?

### Word-to-word interview answer

> “No. I would not describe the current implementation as microservices. The Streamlit frontend imports the backend Python module and calls its functions directly. It's a relatively simple single-application proof-of-concept architecture.”

---

## Q17. How would you add conversation memory?

### Word-to-word interview answer

> “I would explicitly maintain conversation history, for example using appropriate session state for the UI session, and decide which previous messages should be provided to the model. I would also need to manage context size and ensure that retrieved HR policy evidence remains the primary grounding source. That functionality is not implemented in the current project.”

---

## Q18. What is the biggest limitation of the current session-state design?

### Word-to-word interview answer

> “The main limitation is that the vector index lifecycle is tied to session-level application state rather than a durable shared knowledge-index architecture. As the number of users increases, rebuilding the same policy index for new sessions becomes inefficient. For production, I would separate document ingestion and indexing from user query processing and reuse a shared, versioned index.”

---

## Q19. Why is this architecture still reasonable for your project?

### Word-to-word interview answer

> “Because the current project is a proof of concept focused on demonstrating the RAG workflow. Streamlit session state gives me a simple way to avoid rebuilding the index on every interaction without introducing additional infrastructure. For production, I would redesign the state and persistence layer according to concurrency, availability, freshness and scaling requirements.”

---

## Q20. Explain Streamlit and Session State in 30 seconds.

### Word-to-word interview answer

> “Streamlit provides the user interface for my HR Q&A application. Because Streamlit reruns the script during interactions, I store the FAISS vector index in `st.session_state`. On the first session run, if the index doesn't exist, the application builds it using the HR policy and Titan embeddings. On later interactions in the same session, it reuses the existing index. Session state is only temporary application state in this design; it is not persistent vector storage and it does not provide conversation memory.”

---

# Important interview traps

If the interviewer asks:

**“You use Session State, so your chatbot has memory, right?”**

Answer:

> **“No. I store the FAISS index in session state, not chat history.”**

If they ask:

**“So FAISS is permanently stored in Streamlit?”**

Answer:

> **“No. The current implementation uses an in-memory/session-level index, not durable persistent vector storage.”**

If they ask:

**“Does Streamlit call your backend through REST?”**

Answer:

> **“No. `rag_frontend.py` directly imports `rag_backend.py` and calls its Python functions.”**

If they ask:

**“Why don't you rebuild the index for every question?”**

Answer:

> **“Because the document hasn't changed, so rebuilding and re-embedding it would repeat unnecessary work.”**

---

# Five questions to master first

Focus especially on:

**Q1 — What is Streamlit's role?**

**Q2 — Why Session State?**

**Q3 — Explain the `vector_index` condition.**

**Q8 — Does Session State mean conversation memory?**

**Q18 — What is the limitation of this design?**

And keep this one diagram in your head:

```text
                 SESSION START
                      ↓
             vector_index exists?
                /             \
              NO               YES
              ↓                 ↓
         Build Index          Reuse
              \                 /
               └───────┬───────┘
                       ↓
                 User Question
                       ↓
                 FAISS Retrieval
                       ↓
                Claude Generation
                       ↓
                Streamlit Answer
```

The most important sentence from `06-Streamlit-and-Session-State.md` is:

> **“Streamlit session state lets me reuse the FAISS vector index across reruns in the current session; it is not persistent vector storage and it is not conversation memory.”**