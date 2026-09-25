# `11-FAISS-Vector-Search.md`

## NovaMindAI HR Q&A — FAISS Vector Search

### Main question

> **What is FAISS, why does my project need it, what is stored in the FAISS index, and how does `similarity_search(question, k=3)` retrieve relevant HR policy chunks?**

We have now reached the **retrieval engine** of your RAG pipeline:

```text
08 → PDF Loading
       ↓
09 → Chunking
       ↓
10 → Titan Embeddings
       ↓
11 → FAISS VECTOR SEARCH
       ↓
12 → Prompt + Claude
```

Your actual backend does two important things with FAISS:

```python
db_index = FAISS.from_documents(chunks, data_embeddings)
```

and later:

```python
docs = index.similarity_search(question, k=3)
```

The first builds the searchable index. The second searches it. The project analysis confirms that the current implementation builds an in-memory FAISS index and retrieves up to three matching chunks for each question. :chatgpt-content-reference{index="0"}

---

# 1. First understand the problem FAISS solves

After File 10, we have something conceptually like:

```text
Chunk 1
"Privilege leave can be carried forward..."
       ↓
Titan
       ↓
Vector 1


Chunk 2
"Sick leave may be..."
       ↓
Titan
       ↓
Vector 2


Chunk 3
"Maternity leave..."
       ↓
Titan
       ↓
Vector 3
```

Now an employee asks:

> **“Can I move my unused PL to next year?”**

We need to answer:

> **Which HR policy chunks are most relevant to this question?**

That's where FAISS enters.

---

# 2. What is FAISS?

FAISS stands for:

> **Facebook AI Similarity Search**

For this project, the important definition is:

> **FAISS is the vector similarity-search technology used to index the HR policy embeddings and retrieve policy chunks relevant to an employee's question.**

Don't overcomplicate it.

Think:

```text
Vectors
   ↓
FAISS
   ↓
Search
   ↓
Relevant Vectors/Chunks
```

---

# 3. Simple real-world analogy

Imagine a librarian.

The library contains:

```text
Shelf A → Privilege Leave
Shelf B → Sick Leave
Shelf C → Maternity Leave
Shelf D → Carry Forward Rules
```

You ask:

> “Can unused PL move to next year?”

The librarian doesn't write the answer.

The librarian finds:

```text
Privilege Leave
+
Carry Forward Rules
```

and gives those sections to someone who can explain them.

In your project:

```text
FAISS
=
Librarian

Claude
=
Answer writer
```

That's a useful mental model.

---

# 4. FAISS is NOT the LLM

FAISS does not generate:

> “According to your company policy, you can...”

FAISS's job ends earlier:

```text
Employee Question
       ↓
FAISS
       ↓
Relevant Policy Chunks
```

Then:

```text
Relevant Chunks
       +
Question
       ↓
Claude
       ↓
Natural-Language Answer
```

So remember:

> **FAISS retrieves. Claude generates.**

---

# 5. How is the FAISS index created?

Your code:

```python
db_index = FAISS.from_documents(
    chunks,
    data_embeddings
)
```

You already have:

```text
chunks
```

from File 09 and:

```text
data_embeddings
```

from File 10.

So conceptually:

```text
HR Policy
   ↓
Chunks
   ↓
Titan Embeddings
   ↓
Vectors
   ↓
FAISS Index
```

---

# 6. Understanding `FAISS.from_documents()`

Let's break it down:

```python
FAISS.from_documents(
    chunks,
    data_embeddings
)
```

It receives:

### Input 1

```python
chunks
```

The HR policy chunk documents.

### Input 2

```python
data_embeddings
```

The configured embedding integration.

Then it creates the searchable vector-store/index representation.

Conceptually:

```text
Chunk 1 → Titan → Vector 1
Chunk 2 → Titan → Vector 2
Chunk 3 → Titan → Vector 3

               ↓

             FAISS
```

---

# 7. What does the index conceptually contain?

Think of it like:

```text
FAISS VECTOR INDEX

Vector A ↔ Policy Chunk A
Vector B ↔ Policy Chunk B
Vector C ↔ Policy Chunk C
Vector D ↔ Policy Chunk D
...
```

The vector helps with similarity search.

The associated document lets the application recover the readable policy text afterward.

That's why retrieval can ultimately return document objects.

---

# 8. Where is FAISS running?

This is important for your interview.

In your current implementation, FAISS is part of the Python application.

Conceptually:

```text
┌─────────────────────────────┐
│ Python / Streamlit App      │
│                             │
│ PyPDFLoader                 │
│ Splitter                    │
│                             │
│ FAISS Index                 │
│                             │
│ RAG Backend                 │
└─────────────────────────────┘

          │
          ▼

   Amazon Bedrock
   ├── Titan
   └── Claude
```

FAISS is **not an AWS managed service** in this project.

The project analysis specifically identifies the current vector index as in-memory FAISS. :chatgpt-content-reference{index="1"}

---

# 9. Is FAISS Amazon OpenSearch?

No.

These are different technologies.

Your current project uses:

```text
FAISS
```

It does **not** currently use:

```text
Amazon OpenSearch Service
```

So don't say:

> “I stored my embeddings in OpenSearch.”

That's not your implementation.

---

# 10. Is FAISS Amazon Bedrock Knowledge Bases?

Again:

**No.**

Your architecture explicitly handles:

```text
PDF
 ↓
Chunk
 ↓
Titan
 ↓
FAISS
 ↓
Retrieve
 ↓
Claude
```

You're not delegating retrieval to Bedrock Knowledge Bases.

That's an important difference from your previous Bedrock Knowledge Base project.

---

# 11. What happens when an employee asks a question?

Suppose:

> **“Can unused privilege leave be carried forward?”**

Your backend calls:

```python
docs = index.similarity_search(
    question,
    k=3
)
```

This is the most important FAISS retrieval line in your application.

---

# 12. What is `similarity_search()`?

In simple English:

> **Search the vector index for documents whose vector representations are most similar/relevant to the query representation.**

Conceptually:

```text
Employee Question
       ↓
Query Embedding
       ↓
Search FAISS
       ↓
Compare against indexed vectors
       ↓
Find nearest/relevant vectors
       ↓
Return associated documents
```

The project analysis describes this question-time stage as query embedding followed by FAISS top-three retrieval. :chatgpt-content-reference{index="2"}

---

# 13. Where does the question embedding come from?

You don't manually write:

```python
query_vector = titan(question)
```

in `hr_rag_response()`.

Instead, your FAISS vector-store object was created with the embedding integration.

So when:

```python
index.similarity_search(question, k=3)
```

is performed, the vector-store integration can use the configured embedding function for query representation before searching.

Conceptually:

```text
question
   ↓
Titan embedding capability
   ↓
query vector
   ↓
FAISS search
```

---

# 14. What does `k=3` mean?

Your code says:

```python
k=3
```

This means:

> **Return up to the top three relevant document chunks according to the similarity search.**

Conceptually:

```text
Question
   ↓
FAISS

Candidate chunks:

Chunk A → highly relevant
Chunk B → relevant
Chunk C → relevant
Chunk D → less relevant
Chunk E → less relevant

        ↓ k=3

Return:

Chunk A
Chunk B
Chunk C
```

---

# 15. Is `k=3` a magic number?

No.

This is extremely important.

Don't tell an interviewer:

> “3 is the perfect number for RAG.”

Instead:

> **“The current PoC uses `k=3` as its retrieval configuration. In production, I would evaluate different values using representative HR questions.”**

Just like:

```text
chunk_size=1000
overlap=100
```

`k=3` is a tunable design choice.

---

# 16. What happens if `k` is too small?

Imagine:

```python
k=1
```

The answer requires information from two separate policy chunks:

```text
Chunk 1:
Eligibility conditions

Chunk 2:
Carry-forward limit
```

If you retrieve only one:

```text
Question
   ↓
Top 1
   ↓
Incomplete Context
   ↓
Claude
```

Claude may not have enough information.

So:

> **Too small a `k` can miss useful supporting context.**

---

# 17. What happens if `k` is too large?

Now imagine:

```python
k=20
```

The application could retrieve:

```text
Privilege Leave
Sick Leave
Maternity Leave
Holiday Rules
Travel Policy
...
```

even though the question only concerns privilege leave.

Then Claude receives:

```text
Relevant information
+
Less relevant information
+
More context
```

Possible consequences:

```text
More noise
More prompt content
Potential confusion
More token usage
```

Therefore:

> **More retrieved chunks are not automatically better.**

---

# 18. Retrieval has a precision/context trade-off

Think:

```text
Small k
 ↓
Focused context
but risk of missing evidence


Large k
 ↓
More evidence
but risk of noise
```

The right value should be evaluated.

---

# 19. What exactly comes back from FAISS?

Your code:

```python
docs = index.similarity_search(question, k=3)
```

returns document objects.

Conceptually:

```text
docs = [
    Document(...),
    Document(...),
    Document(...)
]
```

These documents contain things such as:

```text
page_content
metadata
```

Your next line extracts:

```python
doc.page_content
```

from each retrieved document.

---

# 20. Why return documents instead of only vectors?

Because Claude needs readable text.

Remember:

```text
Vector
 ↓
Useful for retrieval

Text
 ↓
Useful as Claude context
```

So the retrieval system uses vectors to find the right documents, then gives the application access to their original text.

---

# 21. What happens after FAISS retrieval?

Your code:

```python
context = "\n\n".join(
    [doc.page_content for doc in docs]
)
```

So:

```text
FAISS

   ↓

Document 1
Document 2
Document 3

   ↓

Extract page_content

   ↓

Text 1
+
Text 2
+
Text 3

   ↓

CONTEXT
```

Then:

```text
Context
+
Employee Question
   ↓
Claude
```

So FAISS sits between:

```text
Embeddings
```

and:

```text
Prompt construction
```

---

# 22. Complete retrieval flow

Let's connect Files 09, 10 and 11.

### Indexing

```text
HR Policy
    ↓
Chunking
    ↓
Chunk 1
Chunk 2
Chunk 3
...
    ↓
Titan Embeddings
    ↓
Vector 1
Vector 2
Vector 3
...
    ↓
FAISS Index
```

### Retrieval

```text
Employee Question
       ↓
Query Embedding
       ↓
FAISS Similarity Search
       ↓
Top 3 Relevant Vectors/Documents
       ↓
Relevant Policy Chunks
```

### Generation

```text
Relevant Chunks
       +
Employee Question
       ↓
Claude
       ↓
Answer
```

---

# 23. How does vector similarity work?

You don't need deep mathematics yet.

Imagine vectors as points in space.

For illustration:

```text
                 ● Sick Leave


        ● Privilege Leave
          ● Carry Forward


                           ● Maternity
```

Now the question:

> “Can I move unused PL to next year?”

gets represented as another point:

```text
          × Question
        ● Privilege Leave
          ● Carry Forward
```

The retrieval system identifies nearby/relevant vectors.

The actual embedding space has far more dimensions than this drawing, but the intuition is useful.

---

# 24. What does “nearest” mean?

The general idea is:

```text
Query Vector
     ↓
Compare with document vectors
     ↓
Find vectors with strongest similarity/
smallest relevant distance
```

Different indexes/configurations can use different similarity or distance measures.

For your interview, you don't need to invent a metric that your project code doesn't explicitly configure.

Say:

> **“FAISS performs vector similarity search through the LangChain vector-store integration.”**

That's enough unless the interviewer asks you to inspect the exact configuration.

---

# 25. Don't claim cosine similarity without verifying it

This is a subtle but important interview lesson.

You may know that cosine similarity is common in embedding systems.

But your code says:

```python
FAISS.from_documents(...)
```

It doesn't explicitly show:

```python
metric="cosine"
```

in the code we've inspected.

So don't confidently say:

> “My project uses cosine similarity.”

unless you've verified the underlying configuration.

A safer answer:

> **“I use the LangChain FAISS vector-store integration for similarity search. I haven't explicitly configured a custom similarity metric in this project.”**

That's better than bluffing.

---

# 26. Is FAISS a database?

This needs nuance.

People often casually call FAISS a “vector database.”

For this project, a more precise description is:

> **FAISS is a vector similarity-search/indexing library used as the project's vector store through LangChain.**

It does not give you all the features of a production managed database platform by itself.

Your current implementation uses it in memory.

So in interviews, say:

> **“I use an in-memory FAISS vector index/vector store for the PoC.”**

That's precise.

---

# 27. Is your FAISS index persistent?

No.

Connect to File 06:

```text
New Streamlit Session
        ↓
No vector_index
        ↓
hr_index()
        ↓
Build FAISS
        ↓
st.session_state.vector_index
```

Your current application does not implement:

```text
Build FAISS
    ↓
Persist shared index
    ↓
Restart app
    ↓
Load same durable index
```

as the standard application lifecycle.

So:

> **Current FAISS index = in-memory/session-level application state.**

---

# 28. What happens after application/session loss?

If the relevant index state is gone:

```text
FAISS Index Lost
       ↓
hr_index()
       ↓
Load PDF again
       ↓
Chunk again
       ↓
Embed again
       ↓
Build FAISS again
```

This is acceptable for a learning PoC.

It becomes inefficient as usage grows.

---

# 29. Why is FAISS a reasonable choice for this PoC?

Because your current problem is small:

```text
One policy document
+
Simple Streamlit application
+
Learning/demo workload
```

FAISS lets you demonstrate:

```text
Embedding
   ↓
Vector indexing
   ↓
Semantic retrieval
```

without first provisioning a managed vector database.

That keeps the architecture easy to understand.

---

# 30. Why might FAISS become a limitation?

Imagine:

```text
10,000 employees
+
Many application instances
+
Thousands of policies
+
Frequent updates
+
High availability requirements
```

Now you need to think about:

```text
Shared index
Persistence
Concurrency
Availability
Document updates
Scaling
Access control
Backups
Operational management
```

Your current session-level in-memory FAISS design doesn't demonstrate those production capabilities.

That doesn't mean FAISS itself is “bad.”

It means:

> **Your current way of using FAISS is intentionally simple.**

---

# 31. Could FAISS itself be persisted?

Technically, FAISS/LangChain workflows can support saving/loading indexes in various ways.

But that's not the point of this file.

Your **current project does not implement durable shared persistence**.

So don't answer:

> “Yes, my application saves FAISS permanently.”

because it doesn't.

If asked what you'd improve:

> **“I would separate indexing from query serving and introduce an appropriate shared persistent vector architecture based on production requirements.”**

---

# 32. FAISS does not know HR rules

This sounds obvious, but it's important.

FAISS isn't reasoning:

> “This employee qualifies for 20 days of leave.”

FAISS is doing something closer to:

> **“These chunks appear most relevant to this query in the vector space.”**

Then Claude reasons/generates using those chunks.

So:

```text
FAISS
=
Retrieval

Claude
=
Generation
```

---

# 33. FAISS does not check whether the answer is correct

Suppose FAISS retrieves:

```text
Chunk A
Chunk B
Chunk C
```

FAISS doesn't ask:

> “Will Claude produce a factually correct answer from these?”

It only performs retrieval.

That's why RAG evaluation needs at least two levels:

```text
RETRIEVAL QUALITY
        ↓
Did we retrieve the right chunks?


ANSWER QUALITY
        ↓
Did Claude use them correctly?
```

We'll study this in File 19.

---

# 34. Retrieval failure vs generation failure

This is a very strong interview concept.

Suppose the answer is wrong.

### Scenario A — Retrieval failure

```text
Question
 ↓
FAISS
 ↓
Wrong Chunks
 ↓
Claude
 ↓
Wrong Answer
```

Root problem:

> **Retriever didn't provide the right evidence.**

### Scenario B — Generation failure

```text
Question
 ↓
FAISS
 ↓
Correct Chunks
 ↓
Claude
 ↓
Wrong Answer
```

Root problem:

> **Evidence was correct, but generation failed to use it properly.**

These are different failure modes.

---

# 35. How would you troubleshoot a wrong answer?

Don't immediately blame Claude.

Use this sequence:

```text
Wrong Answer
    ↓
What chunks did FAISS retrieve?
    ↓
Were they relevant?
   / \
 NO   YES
 ↓     ↓
Investigate       Investigate
retrieval         prompt/model
```

If retrieval is wrong, investigate:

```text
Source document
Chunking
Embeddings
Query wording
k value
Retrieval configuration
```

If retrieval is correct, investigate:

```text
Prompt
Grounding instruction
Context quality
Model response
```

This is excellent RAG troubleshooting logic.

---

# 36. What if top 1 is wrong but top 2 is correct?

Suppose:

```text
Top 1 → Sick Leave
Top 2 → Privilege Leave ← correct
Top 3 → Holiday Rules
```

Since:

```python
k=3
```

the correct information is still included in the context.

But you now have noisy context too.

This illustrates why both:

```text
Recall
```

and:

```text
Ranking quality
```

matter.

You want the right evidence to appear and preferably rank highly.

---

# 37. Retrieval evaluation example

Suppose you create 100 HR questions.

For each one, you know the correct policy section.

Then run:

```text
Question
   ↓
FAISS Top 3
```

Ask:

> **Did the expected supporting chunk appear among the top 3?**

This is the type of evaluation that helps you decide whether:

```text
chunk_size=1000
overlap=100
k=3
Titan embeddings
```

are working well together.

You shouldn't optimize these values independently without testing the overall retrieval behavior.

---

# 38. What about metadata filtering?

Imagine later you have:

```text
India Leave Policy
US Leave Policy
UK Leave Policy
```

An employee in India asks a question.

A mature retrieval architecture might use metadata such as:

```text
country = India
policy_status = active
department = HR
```

to constrain retrieval.

But your current project does not implement such filtering.

Current flow:

```text
Question
 ↓
FAISS similarity_search(k=3)
 ↓
Top chunks
```

Don't claim metadata filtering.

---

# 39. What about reranking?

A more advanced RAG pipeline might do:

```text
Question
 ↓
Vector Search
 ↓
Top 20 candidates
 ↓
Reranker
 ↓
Best 3
 ↓
Claude
```

Your current project does:

```text
Question
 ↓
FAISS
 ↓
Top 3
 ↓
Claude
```

There is no implemented reranking stage.

---

# 40. What about hybrid search?

A hybrid system might combine:

```text
Vector Search
      +
Keyword Search
      ↓
Combined Retrieval
```

Your project does not implement this.

It uses the FAISS vector similarity-search path.

Again:

> **Know what your project does, not everything RAG can theoretically do.**

---

# 41. FAISS vs Titan vs Claude

This should now be automatic:

```text
TITAN
  ↓
"What does this text mean numerically?"
  ↓
Embedding


FAISS
  ↓
"Which indexed text is most relevant?"
  ↓
Retrieval


CLAUDE
  ↓
"How should I answer using this context?"
  ↓
Generation
```

A simple memory line:

> **Titan represents. FAISS retrieves. Claude generates.**

---

# 42. FAISS vs Session State

Another distinction:

```text
FAISS
=
Vector index/search capability
```

while:

```text
st.session_state
=
Where the application temporarily keeps
the FAISS object across Streamlit reruns
```

So session state is not performing vector search.

FAISS is.

---

# 43. FAISS vs embeddings

Also:

```text
Embedding
=
Numerical representation
```

while:

```text
FAISS
=
System/library used to index/search
those representations
```

Don't say:

> “FAISS converts my HR policy into embeddings.”

Titan does that.

---

# 44. Current implementation

### Currently implemented

```text
✓ FAISS.from_documents()
✓ Titan embedding integration
✓ In-memory vector index
✓ similarity_search()
✓ k=3
✓ Return document chunks
✓ Extract page_content
```

### Not currently implemented

```text
✗ Managed vector database
✗ OpenSearch
✗ Bedrock Knowledge Bases
✗ Durable shared vector persistence
✗ Metadata filtering
✗ Hybrid search
✗ Reranking
✗ Retrieval confidence threshold
✗ Automated retrieval evaluation
```

These distinctions matter because the project is a focused RAG PoC rather than a production search platform.

---

# 45. Complete project flow up to File 11

You now understand a large part of the RAG system:

```text
HR Leave Policy PDF
        ↓
      FILE 08
    PyPDFLoader
        ↓
      Documents
        ↓
      FILE 09
      Chunking
        ↓
       Chunks
        ↓
      FILE 10
 Titan Embeddings
        ↓
      Vectors
        ↓
      FILE 11
       FAISS
        ↓
   Vector Index


Employee Question
        ↓
 Query Embedding
        ↓
FAISS Similarity Search
        ↓
      k = 3
        ↓
Top 3 Relevant Chunks
        ↓
      FILE 12
Prompt Construction
        ↓
Claude Haiku 4.5
        ↓
      Answer
```

---

# Interview Questions & Answers — `11-FAISS-Vector-Search.md`

## Q1. What is FAISS?

> “FAISS stands for Facebook AI Similarity Search. In my project, I use it as an in-memory vector index through LangChain. It indexes the embeddings generated from the HR policy chunks and allows me to retrieve chunks that are semantically relevant to an employee's question.”

---

## Q2. Why do you use FAISS?

> “I need a way to efficiently search the vector representations generated from my HR policy chunks. Titan provides the embeddings, and FAISS indexes and searches those vectors. For this proof of concept, FAISS gives me a lightweight way to demonstrate semantic retrieval without introducing a managed vector database.”

---

## Q3. How do you create the FAISS index?

> “After loading and splitting the HR policy, I configure Titan embeddings through `BedrockEmbeddings`. I then call `FAISS.from_documents(chunks, data_embeddings)`. This uses the embedding capability to represent the chunks and creates the searchable FAISS vector index.”

---

## Q4. How do you search FAISS?

> “In my `hr_rag_response()` function, I call `index.similarity_search(question, k=3)`. The vector-store integration represents the question using the configured embedding capability and searches the FAISS index for the top three relevant document chunks.”

---

## Q5. What does `k=3` mean?

> “It means my current retrieval configuration asks for the top three relevant document chunks. Those chunks are then combined into the context that I provide to Claude.”

---

## Q6. Why did you choose `k=3`?

> “It is the current proof-of-concept configuration. It provides several relevant chunks without sending a very large amount of context to the model. I don't claim that three is universally optimal; for production, I would evaluate different values against representative HR questions.”

---

## Q7. What happens if `k` is too small?

> “The retriever may miss supporting information needed to answer the question, especially when the answer spans multiple chunks. That can result in incomplete context for Claude.”

---

## Q8. What happens if `k` is too large?

> “The context can contain more irrelevant or redundant information. That can increase prompt size and noise and may make generation less focused. So I would tune `k` through retrieval and answer-quality evaluation.”

---

## Q9. What's the difference between Titan and FAISS?

> “Titan is the embedding model and converts text into numerical vector representations. FAISS indexes and searches those representations. So Titan creates the semantic representation, while FAISS performs retrieval.”

---

## Q10. What's the difference between FAISS and Claude?

> “FAISS retrieves relevant HR policy chunks. Claude generates the final natural-language answer from the retrieved context and employee question. FAISS does not generate answers, and Claude does not directly search my FAISS index.”

---

## Q11. Is FAISS an AWS service?

> “No. FAISS is not an AWS managed service. In my current project, it runs as part of the Python application. Amazon Bedrock is used for Titan embeddings and Claude generation.”

---

## Q12. Are you using Amazon OpenSearch?

> “No. The current project uses FAISS for vector retrieval. Amazon OpenSearch is not part of the implemented architecture.”

---

## Q13. Are you using Bedrock Knowledge Bases?

> “No. I implemented the RAG pipeline explicitly. My application loads and chunks the document, creates Titan embeddings, builds the FAISS index, performs similarity search and then sends the retrieved context to Claude.”

---

## Q14. Where is your FAISS index stored?

> “In the current implementation, the FAISS index is in memory and the Streamlit application keeps the index object in session state for reuse during that session. I don't currently have a durable shared vector-store architecture.”

---

## Q15. What does FAISS return?

> “The LangChain FAISS similarity search returns document objects associated with the relevant indexed vectors. I then extract their `page_content`, combine the retrieved text and use it as context for Claude.”

---

## Q16. Does FAISS use cosine similarity in your project?

> “I use the LangChain FAISS similarity-search integration and I haven't explicitly configured a custom similarity metric in the project code I've implemented. So I wouldn't claim a specific metric without verifying the underlying configuration.”

---

## Q17. How would you troubleshoot a wrong RAG answer?

> “I would first inspect the chunks returned by FAISS. If the correct policy evidence isn't retrieved, I would investigate the source data, chunking, embeddings and retrieval configuration. If the correct evidence is retrieved but the final answer is still wrong, I would investigate the prompt and model-generation stage. This helps separate retrieval failures from generation failures.”

---

## Q18. How would you evaluate FAISS retrieval quality?

> “I would build representative HR questions with known supporting policy sections. For each question, I would inspect whether the expected evidence appears in the top retrieved results and at what rank. I could then compare chunking settings, retrieval depth and embedding approaches using retrieval metrics and final answer quality.”

---

## Q19. Why might you replace the current FAISS architecture for production?

> “The current implementation uses a session-level in-memory index, which is appropriate for a small proof of concept but doesn't provide the shared persistence and operational characteristics I may need for a multi-user production system. I would choose a production vector architecture based on scale, availability, update frequency, filtering, security and operational requirements rather than replacing FAISS just for the sake of adding services.”

---

## Q20. Explain your FAISS flow in 30 seconds.

> “After splitting the HR policy, I use Titan embeddings and `FAISS.from_documents()` to create an in-memory vector index. When an employee asks a question, I call `similarity_search(question, k=3)`. The query is represented using the configured embedding capability, and FAISS retrieves the top three relevant policy chunks. I combine those chunks into context and send that context with the employee's question to Claude for generation.”

---

# Important interview traps

### “FAISS generates embeddings?”

> **No. Titan provides the embeddings; FAISS indexes and searches the vector representations.**

### “FAISS generates your final answer?”

> **No. FAISS retrieves policy chunks; Claude generates the answer.**

### “FAISS is an AWS managed vector database?”

> **No. In this project it runs as an in-memory vector index inside the Python application.**

### “You're using OpenSearch behind FAISS?”

> **No. OpenSearch is not part of the current implementation.**

### “Your project definitely uses cosine similarity?”

> **I haven't explicitly configured a custom similarity metric in the inspected project code, so I wouldn't claim that without verifying the underlying FAISS/LangChain configuration.**

### “Why is top 3 perfect?”

> **It isn't necessarily perfect. `k=3` is the current PoC configuration and should be validated through retrieval evaluation.**

---

# Five questions to master first

Focus especially on:

**Q1 — What is FAISS?**

**Q4 — How does `similarity_search()` work?**

**Q5 — What does `k=3` mean?**

**Q9/Q10 — Titan vs FAISS vs Claude?**

**Q17 — How do you troubleshoot a wrong RAG answer?**

Keep this mental model:

```text
                  INDEXING

Policy Chunk
     ↓
   Titan
     ↓
   Vector
     ↓
   FAISS
     ↓
Vector Index


                  RETRIEVAL

Employee Question
       ↓
Query Embedding
       ↓
     FAISS
       ↓
similarity_search(k=3)
       ↓
Top 3 Policy Chunks
       ↓
page_content
       ↓
Context


                  GENERATION

Context + Question
       ↓
      Claude
       ↓
      Answer
```

The most important sentence from `11-FAISS-Vector-Search.md` is:

> **“Titan converts my HR policy chunks into vector representations, FAISS indexes and searches those representations to retrieve the top three relevant chunks, and Claude uses the retrieved text to generate the final answer.”**