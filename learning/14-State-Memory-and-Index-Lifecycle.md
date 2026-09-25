# `14-State-Memory-and-Index-Lifecycle.md`

## NovaMindAI HR Q&A — State, Memory, and FAISS Index Lifecycle

### Main question

> **What does my application remember, where is the FAISS index kept, what happens during Streamlit reruns and new sessions, and why is session state NOT the same as conversation memory or persistent storage?**

This file connects several things you have already learned:

```text
PDF → Chunking → Titan → FAISS
                         ↓
                  Where does this
                  index live?
                         ↓
               Streamlit Session State
```

The most important code is in `rag_frontend.py`:

```python
if 'vector_index' not in st.session_state:
    st.session_state.vector_index = demo.hr_index()
```

Then when the employee asks a question:

```python
response_content = demo.hr_rag_response(
    index=st.session_state.vector_index,
    question=input_text
)
```

This small piece of code controls a very important part of your application's lifecycle.

---

# 1. First understand three different concepts

Do not mix these:

```text
STATE
MEMORY
PERSISTENCE
```

They sound similar, but they mean different things.

For this project:

```text
Session State
     ≠
Conversation Memory
     ≠
Persistent Vector Storage
```

Understanding this distinction is the main goal of File 14.

---

# 2. What is state?

In simple English:

> **State is information the application keeps so it can continue operating without starting everything from zero during the same interaction/session context.**

Your important state is:

```python
st.session_state.vector_index
```

That contains the FAISS vector-store/index object used by the application.

Think:

```text
Streamlit Session

┌─────────────────────────────┐
│ session_state               │
│                             │
│ vector_index → FAISS object │
└─────────────────────────────┘
```

---

# 3. Why do you need session state?

Remember how Streamlit works.

User interactions can cause the Streamlit script to rerun.

Without state, you could end up doing:

```text
User opens app
     ↓
Build FAISS

User clicks Ask
     ↓
Rerun
     ↓
Build FAISS AGAIN

Another interaction
     ↓
Rerun
     ↓
Build FAISS AGAIN
```

That would be wasteful.

Instead, your application checks:

```python
if 'vector_index' not in st.session_state:
```

Meaning:

> **“Does this session already have a vector index?”**

---

# 4. First-time session behavior

Imagine Employee A opens the application.

Initially:

```text
st.session_state

vector_index = NOT PRESENT
```

The condition becomes true:

```python
if 'vector_index' not in st.session_state:
```

Therefore:

```python
demo.hr_index()
```

runs.

And now you already know exactly what `hr_index()` does:

```text
Remote HR Policy PDF
        ↓
PyPDFLoader
        ↓
Documents
        ↓
RecursiveCharacterTextSplitter
        ↓
Chunks
        ↓
Titan Embeddings
        ↓
FAISS.from_documents()
        ↓
FAISS Index
```

Then:

```python
st.session_state.vector_index = demo.hr_index()
```

stores the resulting object in session state.

---

# 5. First-session lifecycle

So the first-time flow is:

```text
Employee Opens App
        ↓
Streamlit Executes Script
        ↓
Check Session State
        ↓
vector_index exists?
        ↓
       NO
        ↓
hr_index()
        ↓
Load PDF
        ↓
Chunk
        ↓
Titan Embeddings
        ↓
Build FAISS
        ↓
Store FAISS Object
        ↓
st.session_state.vector_index
```

This is the expensive initialization path compared with simply reusing an existing index.

---

# 6. What happens after the index exists?

Now:

```text
st.session_state

vector_index = FAISS INDEX
```

Suppose the employee enters:

> “Can privilege leave be carried forward?”

and clicks the button.

Streamlit may rerun the script.

The application reaches:

```python
if 'vector_index' not in st.session_state:
```

But now:

```text
vector_index EXISTS
```

So:

```python
demo.hr_index()
```

is not called again for that condition.

Instead, the existing index is reused.

---

# 7. Same-session behavior

Conceptually:

```text
FIRST RUN

No index
   ↓
Build Index
   ↓
Store in Session State


LATER RERUN

Index already exists
   ↓
Skip Index Building
   ↓
Reuse Existing Index
```

This is one of the most important reasons `st.session_state` exists in your current design.

---

# 8. Why is this useful?

Remember what building your index requires:

```text
Download/load PDF
       ↓
Extract document
       ↓
Split document
       ↓
Generate embeddings
       ↓
Build FAISS index
```

Repeating this unnecessarily could increase:

```text
Latency
Embedding calls
Compute work
External dependency calls
Potential Bedrock usage/cost
```

Session state avoids repeating that initialization on every normal rerun within the same session.

---

# 9. What exactly is stored in session state?

Your code stores:

```python
st.session_state.vector_index
```

So the important state is:

> **The FAISS vector-store/index object.**

Don't say:

> “I store the PDF in Streamlit memory.”

That's not what this specific code line demonstrates.

Don't say:

> “I store all conversations in session state.”

You don't.

The key current object is:

```text
vector_index
```

---

# 10. Session state is NOT conversation memory

This is probably the biggest interview trap.

Suppose:

### Question 1

> “How many casual leave days do I get?”

Claude answers.

Then employee asks:

### Question 2

> “Can I carry them forward?”

A true conversational-memory system might send:

```text
Previous Question
+
Previous Answer
+
Current Question
+
Retrieved Context
        ↓
Claude
```

But your current project does not implement this.

---

# 11. What does your current Claude call receive?

From File 12:

```text
Retrieved Current Context
          +
Current Employee Question
          ↓
        Claude
```

It does not explicitly receive:

```text
Question 1
Answer 1
Question 2
Answer 2
...
```

Therefore:

> **The application has session state for the vector index, but it does not have implemented conversation memory.**

---

# 12. State vs memory

Let's make it extremely clear.

### State in your project

```text
"Keep this FAISS index available
during the session."
```

### Conversation memory

```text
"Remember what the employee and
assistant previously discussed."
```

These are different.

Your project implements the first.

It does not implement the second.

---

# 13. Example

Employee asks:

> “What is maternity leave?”

Your application does:

```text
Current Question
      ↓
FAISS
      ↓
Current Relevant Chunks
      ↓
Claude
      ↓
Answer
```

Then employee asks:

> “What about after that?”

Your current application does not inherently give Claude the previous turn so it can know what:

> **“that”**

means.

It treats the new input as the current retrieval question.

This can make follow-up questions ambiguous.

---

# 14. Session state is also NOT persistent storage

Another critical distinction.

You have:

```python
st.session_state.vector_index
```

This does not mean:

```text
FAISS Index
    ↓
Permanent Database
```

Your current application does not demonstrate a durable shared vector database/index store.

The project analysis identifies the FAISS index as in-memory rather than persistent. :chatgpt-content-reference{index="0"}

---

# 15. What does persistent mean?

Persistent means data survives beyond temporary application/session memory according to the storage design.

For example, conceptually:

```text
Build Index
    ↓
Save to Durable Storage
    ↓
Application Restarts
    ↓
Load Existing Index
```

Your current flow is instead closer to:

```text
New Session
    ↓
No Session Index
    ↓
hr_index()
    ↓
Build Index
```

There is no implemented durable shared index-loading workflow in the current application.

---

# 16. Current FAISS lifecycle

The core lifecycle is:

```text
NEW SESSION
    ↓
Check session_state
    ↓
Index missing
    ↓
hr_index()
    ↓
PDF → Chunk → Embed → FAISS
    ↓
Store index in session_state
    ↓
Use index for questions
    ↓
Same-session reruns
    ↓
Reuse index
```

The project analysis also distinguishes the current in-memory design from persistent/shared vector storage that is not implemented. :chatgpt-content-reference{index="1"}

---

# 17. What happens with another user/session?

Conceptually, suppose:

```text
Employee A
```

opens the app.

Their session needs:

```text
vector_index
```

Now:

```text
Employee B
```

opens a separate session.

You should **not describe the current architecture as one centrally shared enterprise vector index**.

The current code uses:

```python
st.session_state.vector_index
```

which is session-oriented application state.

Therefore, a new session can require its own initialization path.

---

# 18. Why can this become inefficient?

Imagine many new sessions.

Conceptually:

```text
Session A
   ↓
Load PDF
Chunk
Embed
Build FAISS


Session B
   ↓
Load PDF
Chunk
Embed
Build FAISS


Session C
   ↓
Load PDF
Chunk
Embed
Build FAISS
```

Notice the problem?

The HR policy may not have changed.

But the same preparation work can be repeated.

For a PoC, that's understandable.

For a production system, that's inefficient.

---

# 19. Why repeated embeddings matter

Titan embedding work happens during index creation.

Therefore repeated index creation can mean repeated embedding calls.

Conceptually:

```text
Same HR Policy
     ↓
Embed
     ↓
Index A


Same HR Policy
     ↓
Embed Again
     ↓
Index B
```

This can affect:

```text
Startup latency
Bedrock usage
Cost
Scalability
Reliability
```

We'll study the cost side more deeply in File 20.

---

# 20. What is the better production idea?

A more mature architecture could separate:

```text
INGESTION / INDEXING
```

from:

```text
QUERY SERVING
```

Conceptually:

```text
            INGESTION

Approved HR Policy
       ↓
Load + Validate
       ↓
Chunk
       ↓
Titan Embeddings
       ↓
Persistent / Shared Vector Index
       ↓
Versioned Knowledge


             QUERY

Employee Question
       ↓
Shared Vector Index
       ↓
Relevant Chunks
       ↓
Claude
       ↓
Answer
```

Now many users can query an already prepared knowledge base/index rather than rebuilding the same knowledge for every session.

This is a **future production design**, not the current implementation.

---

# 21. Why separate indexing from querying?

Because they have different jobs.

### Indexing

```text
Document changes
      ↓
Process document
      ↓
Generate embeddings
      ↓
Update index
```

This doesn't necessarily need to happen for every employee question.

### Querying

```text
Employee asks question
      ↓
Search existing index
      ↓
Retrieve evidence
      ↓
Generate answer
```

Separating them can improve efficiency and scalability.

---

# 22. Current project mixes initialization with application session

Your current application does:

```text
Streamlit Session Starts
        ↓
Index missing?
        ↓
Build index
```

So knowledge preparation is tied to application/session initialization.

A production design could instead do:

```text
Controlled Ingestion Pipeline
        ↓
Build/Update Shared Index

             SEPARATE

Application
        ↓
Query Existing Index
```

That's an important architectural improvement.

---

# 23. What happens when the source PDF changes?

This introduces another lifecycle problem.

Current source:

```text
Remote HR Policy URL
```

Suppose its content changes.

Your current application has no dedicated:

```text
Detect New Policy Version
        ↓
Validate
        ↓
Approve
        ↓
Re-chunk
        ↓
Re-embed changed knowledge
        ↓
Version index
        ↓
Deploy updated index
```

pipeline.

A new index build may pick up whatever content the URL currently serves, but that's not the same as controlled policy lifecycle management.

---

# 24. Index lifecycle should follow document lifecycle

For production, think:

```text
Policy v1
   ↓
Chunks v1
   ↓
Embeddings v1
   ↓
Index v1


Policy updated


Policy v2
   ↓
Chunks v2
   ↓
Embeddings v2
   ↓
Index v2
```

This gives you traceability.

For HR policy systems, that's important because employees should receive answers from the correct approved policy version.

Again, this is a future improvement.

---

# 25. What if you change the embedding model?

Suppose your index was created using:

```text
Embedding Model A
```

and later you change to:

```text
Embedding Model B
```

You generally shouldn't blindly assume the existing index representations remain compatible with the new query representation.

Conceptually:

```text
Embedding Model Version
        ↕
Vector Index Version
```

should be managed together.

A production design should know:

```text
Which embedding model created this index?
Which document version?
Which chunking configuration?
```

This is part of index lifecycle management.

---

# 26. What if you change chunk size?

Same principle.

Suppose:

```text
Index v1
chunk_size=1000
overlap=100
```

Then you change to:

```text
Index v2
chunk_size=500
overlap=50
```

Your retrieval units have changed.

Therefore, you'd need to rebuild the index for the new chunk representation.

Think:

```text
Source Version
+
Chunking Version
+
Embedding Model Version
=
Index Version
```

That's a useful production mental model.

---

# 27. What is application memory?

In the broad computer-science sense, an application can keep objects in runtime memory.

Your current FAISS index is an in-memory object used by the application.

But don't confuse:

```text
Computer/Application Memory
```

with:

```text
AI Conversation Memory
```

These are completely different uses of the word **memory**.

---

# 28. Four different things called “memory”

This will prevent a lot of confusion.

### 1. Runtime memory

```text
Python objects exist while application runs.
```

### 2. Streamlit session state

```text
Keeps selected Python values across reruns
for a user's session.
```

### 3. Vector index

```text
Stores/indexes vector representations
for retrieval.
```

### 4. Conversation memory

```text
Preserves previous dialogue context
for future model turns.
```

Your project has:

```text
✓ Runtime state
✓ Streamlit session state
✓ FAISS vector index

✗ Implemented conversation memory
```

---

# 29. FAISS is knowledge retrieval, not conversation memory

Another important distinction.

FAISS contains representations of:

```text
HR POLICY CHUNKS
```

It doesn't automatically contain:

```text
Employee Question 1
Claude Answer 1
Employee Question 2
Claude Answer 2
```

Therefore:

```text
FAISS Index
≠
Chat History
```

---

# 30. Session state is not a database

Do not tell an interviewer:

> “I use Streamlit session state as my database.”

No.

In this project:

> **Streamlit session state is temporary application/session state used to reuse the FAISS index across reruns.**

That's the correct answer.

---

# 31. Why didn't you just rebuild the index for every question?

Because that would be unnecessary.

Bad conceptual design:

```text
Question
   ↓
Download PDF
   ↓
Split
   ↓
Embed all chunks
   ↓
Build FAISS
   ↓
Search
   ↓
Answer


Next Question
   ↓
DO EVERYTHING AGAIN
```

Your current design improves on this within a session:

```text
Build Index Once
       ↓
Store in Session State
       ↓
Question 1 → Search
Question 2 → Search
Question 3 → Search
```

That's an important design decision.

---

# 32. Index creation vs query embedding

Don't mix these.

### During index creation

```text
All policy chunks
      ↓
Titan
      ↓
Document embeddings
      ↓
FAISS
```

### During each question

```text
Current question
      ↓
Embedding representation
      ↓
Search existing FAISS index
```

You do **not** need to re-embed all policy chunks for every question when the existing index is reused.

That's a major efficiency benefit.

---

# 33. Current state architecture

Your current state design is approximately:

```text
┌──────────────────────────────────────┐
│       STREAMLIT USER SESSION         │
│                                      │
│  st.session_state                    │
│          │                           │
│          └── vector_index            │
│                  │                   │
│                  ▼                   │
│              FAISS INDEX             │
│                                      │
│  Employee Question                   │
│          │                           │
│          ▼                           │
│  hr_rag_response()                   │
│          │                           │
│          └── reuse vector_index      │
└──────────────────────────────────────┘

                │
                ▼

          Amazon Bedrock
          ├── Titan
          └── Claude
```

---

# 34. Current architecture does NOT look like this

Don't accidentally describe:

```text
Employee A ─┐
Employee B ─┼──→ Shared Managed Vector DB
Employee C ─┘
```

as the implemented architecture.

That may be a sensible production direction, but it isn't what the current code proves.

---

# 35. No durable FAISS persistence in current application flow

Your current application doesn't show an implemented lifecycle like:

```python
FAISS.save_local(...)
```

followed later by:

```python
FAISS.load_local(...)
```

as its standard application architecture.

Therefore don't claim:

> “I persist the FAISS index to disk and load it after restart.”

Your current design builds it through `hr_index()` when required by session state.

---

# 36. No Redis state

Some production applications use Redis for:

```text
Sessions
Cache
Conversation state
```

Your current project does not.

Don't mix this HR project with your other projects.

---

# 37. No DynamoDB conversation history

Similarly, there's no current flow:

```text
Question
 ↓
DynamoDB
 ↓
Conversation History
 ↓
Claude
```

DynamoDB isn't part of this application's implemented memory architecture.

---

# 38. No Bedrock conversation memory

Amazon Bedrock provides model access in your current application.

That does not mean:

> “Bedrock remembers my users' conversations automatically.”

Your application controls what context is sent to the model.

Current prompt:

```text
Retrieved Policy Context
+
Current Question
```

No previous conversation is explicitly added.

---

# 39. What happens on an ambiguous follow-up?

Imagine:

### Q1

> “How many privilege leave days are allowed?”

Then:

### Q2

> “Can I carry them forward?”

A human knows:

```text
"them"
=
privilege leave days
```

But without conversation history, your RAG system receives Q2 essentially as:

```text
Can I carry them forward?
```

The retriever may lack enough context to interpret “them.”

This is a limitation of stateless question handling.

---

# 40. How could conversation memory be added later?

Conceptually:

```text
Previous Conversation
        +
Current Question
        ↓
Resolve Current Intent
        ↓
Retrieve Relevant Policy
        ↓
Context
        +
Conversation
        +
Current Question
        ↓
Claude
```

But be careful.

For HR systems, you shouldn't blindly send unlimited conversation history.

You'd need to consider:

```text
Privacy
Token usage
Relevance
Data retention
Security
Conversation boundaries
```

So memory should be designed deliberately.

---

# 41. State vs cache

Another useful distinction.

Your current session-state approach has a cache-like effect because it avoids rebuilding the index during the same session.

But don't overstate it as a production caching layer.

You don't currently have:

```text
Redis Cache
Distributed Cache
Shared Application Cache
```

The implementation is specifically:

```python
st.session_state.vector_index
```

---

# 42. What would production V2 look like conceptually?

Not necessarily more services—just better lifecycle separation.

```text
              KNOWLEDGE PIPELINE

Approved Policy
      ↓
Validate
      ↓
Chunk
      ↓
Embed
      ↓
Version
      ↓
Persistent Shared Index


              QUERY PIPELINE

Employee
      ↓
Authentication
      ↓
Question
      ↓
Shared Index
      ↓
Relevant Policy Evidence
      ↓
Claude
      ↓
Answer + Citation
```

Potential conversation state could be added separately if business requirements need it.

This is a **future architecture**, not the current implementation.

---

# 43. Why not immediately add conversation memory?

Because this application is primarily:

> **Policy question answering**

Many questions can be answered independently.

Adding memory creates additional complexity:

```text
Privacy
Security
Token cost
Incorrect historical context
Session management
Data retention
```

So production design should ask:

> **Do users actually need multi-turn contextual conversations?**

rather than adding memory because it's fashionable.

That's good engineering judgment.

---

# 44. Three lifecycle questions you should always ask

For any RAG system:

### Document lifecycle

```text
When does knowledge change?
```

### Index lifecycle

```text
When should embeddings/index be rebuilt?
```

### Conversation lifecycle

```text
Should user dialogue be remembered,
for how long, and where?
```

Your current PoC only handles these minimally.

---

# 45. Current vs future

## CURRENTLY IMPLEMENTED

```text
✓ Streamlit session state
✓ vector_index stored in session state
✓ FAISS in-memory index
✓ Index built when session lacks vector_index
✓ Same-session index reuse
✓ Current question retrieval
✓ Current retrieved context sent to Claude
```

## NOT CURRENTLY IMPLEMENTED

```text
✗ Durable shared vector index
✗ Persistent FAISS lifecycle
✗ Central managed vector database
✗ Conversation history
✗ Long-term chat memory
✗ Redis cache/session store
✗ DynamoDB conversation store
✗ Automated policy versioning
✗ Automated index refresh
✗ Multi-instance shared state
```

This aligns with the project's broader current-vs-not-present analysis, which distinguishes the implemented in-memory PoC from persistent storage, conversation memory, and production ingestion capabilities that are absent. :chatgpt-content-reference{index="2"}

---

# Interview Questions & Answers — `14-State-Memory-and-Index-Lifecycle.md`

## Q1. How do you manage the FAISS index in your Streamlit application?

> “I store the FAISS vector index in Streamlit session state using `st.session_state.vector_index`. When a session starts, I check whether the index already exists. If it doesn't, I call `hr_index()` to load the policy, split it, generate embeddings and build the FAISS index. Once created, I reuse that index across reruns within the same session.”

---

## Q2. Why do you use Streamlit session state?

> “Streamlit reruns the application script during interactions. Without session state, I could unnecessarily rebuild the vector index repeatedly. Session state lets me keep the FAISS object available across reruns within the session.”

---

## Q3. What happens when the application gets a new session?

> “If the new session doesn't contain `vector_index` in session state, the application calls `hr_index()`. That reloads the policy, splits it into chunks, generates Titan embeddings and creates a new in-memory FAISS index.”

---

## Q4. Do you rebuild the FAISS index for every question?

> “No. Once the index has been created and stored in session state, later interactions in that session reuse it. The application still needs to represent the current query for similarity search, but it doesn't intentionally rebuild all policy embeddings for every question within that session.”

---

## Q5. Is Streamlit session state persistent storage?

> “No. I use it as session-level application state. The current project doesn't implement a durable shared vector index that is persisted and reloaded independently of user sessions.”

---

## Q6. Is your FAISS index persistent?

> “Not in the current application architecture. The index is created in memory and kept in Streamlit session state for reuse within the session. I don't currently implement a durable shared FAISS save-and-load lifecycle.”

---

## Q7. Does your application have conversation memory?

> “No. The current application doesn't explicitly maintain previous question-and-answer turns and send them to Claude. Each request uses the current question and the policy context retrieved for that question.”

---

## Q8. What's the difference between session state and conversation memory?

> “Session state is application state that I currently use to keep the FAISS index available across Streamlit reruns. Conversation memory would preserve previous dialogue turns so later questions could use that history. My project implements the first, not the second.”

---

## Q9. Does FAISS store your conversation history?

> “No. FAISS is used to index and retrieve HR policy chunks. It isn't being used to store employee-chat history in my implementation.”

---

## Q10. Does Amazon Bedrock remember previous questions automatically?

> “Not in the way my application is implemented. My backend controls the prompt sent on each request. I send the current retrieved policy context and current question, but I don't explicitly include previous conversation turns.”

---

## Q11. What problem does session state solve?

> “It avoids unnecessary index reconstruction during normal reruns in the same Streamlit session. Since index construction involves loading the document, chunking it, generating embeddings and creating FAISS, reusing the index avoids repeating that work for every interaction.”

---

## Q12. What is a limitation of this design?

> “The index is session-oriented and in memory rather than a durable shared production index. With many new sessions, the same policy-processing and embedding work can be repeated, which can increase startup latency, resource usage and embedding cost.”

---

## Q13. How would you improve index management for production?

> “I would separate document ingestion and indexing from query serving. The approved policy would be processed when needed, and the resulting index would be stored in an appropriate persistent shared architecture. User requests could then query that existing index instead of rebuilding the same knowledge for each new session.”

---

## Q14. What happens when the HR policy changes?

> “The current PoC doesn't implement a controlled automatic policy-versioning and index-refresh pipeline. For production, I would detect or receive an approved new policy version, validate it, process the changed knowledge, regenerate the required embeddings and update or version the index so I know exactly which policy supports the answers.”

---

## Q15. What happens if you change the embedding model?

> “I would treat that as an index lifecycle change. The existing document vectors were created using the previous embedding model, so I would rebuild the index using the new model rather than assuming the old and new representations are directly compatible.”

---

## Q16. What happens if you change the chunking strategy?

> “I would rebuild the index because the retrieval units have changed. For example, changing chunk size or overlap produces different chunks, which need new embeddings and a corresponding updated index.”

---

## Q17. Why don't you add conversation memory immediately?

> “I would add it only if the product requires multi-turn contextual questions. Conversation memory adds privacy, security, retention, token and relevance concerns, especially for an HR application. For a simple policy Q&A system, stateless questions may be sufficient for many use cases.”

---

## Q18. How would conversation memory help this application?

> “It would help with follow-up questions that depend on previous turns. For example, after asking about privilege leave, a user could ask ‘Can I carry them forward?’ and the system could use the previous turn to understand what ‘them’ refers to. That behavior is not implemented in the current version.”

---

## Q19. Is your current architecture suitable for many users?

> “It is suitable as a small proof of concept, but I wouldn't describe the session-level in-memory index design as a production multi-user vector architecture. For larger usage, I would evaluate shared persistent indexing, separate ingestion, concurrency, availability, security and monitoring requirements.”

---

## Q20. Explain your state and index lifecycle in 30 seconds.

> “When a Streamlit session starts, my application checks whether `vector_index` exists in session state. If not, it calls `hr_index()`, which loads the HR policy, chunks it, generates Titan embeddings and creates an in-memory FAISS index. That index is stored in session state and reused across reruns within the session. However, this is not persistent shared storage and it is not conversation memory. For production, I would separate indexing from query serving and use an appropriate persistent shared index.”

---

# Important interview traps

### “You use session state, so your chatbot has memory?”

> **No. Session state currently keeps the FAISS index; previous conversation turns are not being passed to Claude.**

### “Your FAISS index is permanently stored?”

> **No. The current architecture uses an in-memory/session-level FAISS index.**

### “FAISS stores employee conversations?”

> **No. It indexes HR policy knowledge for retrieval.**

### “Bedrock remembers the user's previous questions?”

> **Not in this implementation. The application sends the current context and current question.**

### “You rebuild every document embedding for every question?”

> **No. Once the index exists in the same session, it is reused for subsequent searches.**

### “Your current vector index is shared across every employee?”

> **I would not claim that. The current code stores the index in Streamlit session state and is a PoC design, not a centrally shared production vector architecture.**

---

# Five questions to master first

Focus especially on:

**Q1 — How is the FAISS index managed?**

**Q4 — Do you rebuild it for every question?**

**Q7 — Does the application have conversation memory?**

**Q8 — Session state vs conversation memory?**

**Q13 — How would you improve it for production?**

Keep this mental model:

```text
               FIRST SESSION RUN

No vector_index
       ↓
hr_index()
       ↓
PDF
 ↓
Chunks
 ↓
Titan Embeddings
 ↓
FAISS Index
       ↓
st.session_state.vector_index


              SAME SESSION

Employee Question
       ↓
Reuse Existing FAISS Index
       ↓
Similarity Search
       ↓
Top 3 Chunks
       ↓
Claude
       ↓
Answer


            IMPORTANT DISTINCTION

st.session_state
       ↓
Keeps FAISS object
across session reruns

        ≠

Conversation Memory
       ↓
Previous Q&A history

        ≠

Persistent Storage
       ↓
Durable shared index
```

The most important sentence from `14-State-Memory-and-Index-Lifecycle.md` is:

> **“My application uses Streamlit session state to reuse the in-memory FAISS index across reruns within a session, but this is neither conversation memory nor durable shared vector storage.”**

And for production thinking:

> **“I would separate knowledge ingestion and indexing from query serving, so approved HR policies are embedded when needed and a shared persistent index can be reused by many queries rather than rebuilt for each new session.”**