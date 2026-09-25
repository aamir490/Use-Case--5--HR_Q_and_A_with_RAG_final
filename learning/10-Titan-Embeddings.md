# `10-Titan-Embeddings.md`

## NovaMindAI HR Q&A — Amazon Titan Embeddings

### Main question

> **What are embeddings, why does my RAG project need them, what does Amazon Titan do, and how do embeddings help FAISS find relevant HR policy chunks?**

This is one of the most important RAG concepts.

Your pipeline has now reached:

```text
08 → Load the PDF
        ↓
09 → Split into chunks
        ↓
10 → TITAN EMBEDDINGS
        ↓
11 → FAISS Vector Search
```

Your project configures:

```python
data_embeddings = BedrockEmbeddings(
    credentials_profile_name='default',
    model_id='amazon.titan-embed-text-v1'
)

db_index = FAISS.from_documents(
    chunks,
    data_embeddings
)
```

The project analysis confirms that the application uses Amazon Titan through Bedrock to create embeddings and then builds the FAISS vector index. :chatgpt-content-reference{index="0"}

---

# 1. First understand the problem embeddings solve

Suppose the HR policy says:

> **“Unused privilege leave may be carried forward to the following year.”**

But the employee asks:

> **“Can I move my unused PL to next year?”**

Look carefully.

The words are different:

```text
Policy:
"privilege leave"
"carried forward"
"following year"

Question:
"PL"
"move"
"next year"
```

But the **meaning is similar**.

A useful RAG system should be able to connect semantically related text even when the wording is not identical.

This is where embeddings help.

---

# 2. What is an embedding?

In simple English:

> **An embedding is a numerical representation of text that captures useful semantic information about that text.**

For example:

```text
"Privilege leave can be carried forward"

                ↓
          Embedding Model
                ↓
        Numerical Vector
```

Conceptually, imagine:

```text
[0.18, -0.42, 0.73, 0.09, ...]
```

The actual vector is much larger than this toy example.

The important idea is:

```text
TEXT
 ↓
EMBEDDING MODEL
 ↓
VECTOR
```

---

# 3. What is a vector?

A vector is basically an ordered list of numbers.

Simple example:

```text
[0.2, 0.7, -0.1]
```

In machine learning, vectors can represent things such as:

```text
Text
Images
Audio
Products
Users
```

In your project, vectors represent:

> **HR policy text chunks and query meaning for retrieval.**

---

# 4. Don't get scared by the mathematics

For your interview, you don't need to manually calculate embeddings.

The important concept is:

```text
Text
 ↓
Embedding Model
 ↓
Numbers representing semantic information
```

Then a vector search system can compare those numerical representations.

---

# 5. Why can't FAISS just search the PDF directly?

Your application wants **semantic retrieval**.

FAISS works with vector representations.

So you need:

```text
HR Policy Text
      ↓
Embedding Model
      ↓
Vectors
      ↓
FAISS
```

Titan provides that embedding capability in your current project.

---

# 6. What is Amazon Titan's role?

Your project uses:

```python
model_id='amazon.titan-embed-text-v1'
```

through:

```python
BedrockEmbeddings(...)
```

So conceptually:

```text
Python Application
       ↓
LangChain BedrockEmbeddings
       ↓
Amazon Bedrock
       ↓
Amazon Titan Embedding Model
       ↓
Vector Representation
```

Titan's job here is:

> **Convert text into embeddings.**

Titan does **not** generate the final HR answer.

---

# 7. Titan vs Claude

This distinction must be crystal clear.

## Titan

```text
Text
 ↓
Titan
 ↓
Vector
```

Used for:

**semantic representation / retrieval**

## Claude

```text
Context + Question
       ↓
Claude
       ↓
Natural-language answer
```

Used for:

**generation**

Therefore:

> **Titan creates representations. Claude creates answers.**

---

# 8. Where do embeddings happen in your pipeline?

Your complete indexing flow:

```text
HR Policy PDF
      ↓
PyPDFLoader
      ↓
Documents
      ↓
Text Splitter
      ↓
Chunks
      ↓
Amazon Titan Embeddings
      ↓
Vectors
      ↓
FAISS
```

Notice the order:

```text
Chunk first
↓
Embed second
```

You're not conceptually creating one embedding for the complete PDF.

You're creating searchable representations of the chunks used by the vector store.

---

# 9. Simple example

Suppose your HR policy produces three chunks.

### Chunk 1

```text
Privilege leave may be carried forward...
```

### Chunk 2

```text
Employees can apply for sick leave...
```

### Chunk 3

```text
Maternity leave is available...
```

Titan converts these into vector representations:

```text
Chunk 1
 ↓
Titan
 ↓
Vector A

Chunk 2
 ↓
Titan
 ↓
Vector B

Chunk 3
 ↓
Titan
 ↓
Vector C
```

FAISS then indexes those vectors.

---

# 10. What happens when an employee asks a question?

Suppose:

> **“Can I carry my unused PL into next year?”**

The retrieval system needs to compare the query semantically with the indexed document chunks.

Conceptually:

```text
Question
   ↓
Embedding representation
   ↓
Query Vector

          COMPARE

Query Vector
    ↕
Vector A — Privilege Leave
Vector B — Sick Leave
Vector C — Maternity Leave
```

The privilege-leave vector should ideally be more semantically relevant.

Then FAISS can retrieve that associated chunk.

---

# 11. The core idea: similar meaning → nearby vectors

Imagine a very simplified 2D space:

```text
             Sick Leave
                 ●


Privilege Leave ●  ● Carry Forward Leave


                              ● Maternity Leave
```

Concepts with related meaning can have vector representations that are closer under the similarity/distance behavior used by the retrieval system.

So a query about:

```text
"unused PL next year"
```

may be close to:

```text
"privilege leave carry forward"
```

even though they don't use exactly the same words.

That's the power of semantic retrieval.

---

# 12. Keyword search vs semantic search

Imagine:

### Policy

> “Privilege leave can be carried forward.”

### Employee

> “Can unused PL move to next year?”

A strict keyword system might depend heavily on exact shared terms.

Semantic retrieval tries to recognize related meaning.

Conceptually:

```text
KEYWORD SEARCH
"What words match?"


SEMANTIC SEARCH
"What text has related meaning?"
```

Your embedding + FAISS approach is designed for the second type.

---

# 13. Does Titan understand HR policy like a human?

Be careful with wording.

Don't say:

> “Titan understands the HR policy exactly like a human.”

A better explanation is:

> **“Titan maps text into numerical representations that encode semantic relationships useful for similarity retrieval.”**

That's technically safer and more professional.

---

# 14. What does `BedrockEmbeddings` do?

Your code uses:

```python
from langchain_aws import BedrockEmbeddings
```

and:

```python
data_embeddings = BedrockEmbeddings(
    credentials_profile_name='default',
    model_id='amazon.titan-embed-text-v1'
)
```

`BedrockEmbeddings` is the LangChain AWS integration your application uses to access the configured embedding model through Amazon Bedrock.

Think:

```text
Your Python Code
      ↓
BedrockEmbeddings
      ↓
Amazon Bedrock
      ↓
Titan Embedding Model
```

Don't say:

> “BedrockEmbeddings is Titan.”

It isn't.

Think:

```text
BedrockEmbeddings
      =
Integration/client layer

Titan
      =
Embedding model
```

---

# 15. What does `credentials_profile_name='default'` mean?

Your code specifies:

```python
credentials_profile_name='default'
```

This tells the integration to use the AWS profile named:

```text
default
```

in the current development configuration.

Conceptually:

```text
Python Application
      ↓
AWS default profile
      ↓
AWS authentication/authorization
      ↓
Amazon Bedrock
      ↓
Titan
```

We'll study IAM and AWS access more deeply in:

`15-AWS-Bedrock-IAM-and-Region.md`.

---

# 16. Important: configuring Titan vs calling Titan

This line:

```python
data_embeddings = BedrockEmbeddings(...)
```

configures the embedding integration.

It does not mean:

> “At this exact line, all document chunks have already been embedded.”

Then:

```python
db_index = FAISS.from_documents(
    chunks,
    data_embeddings
)
```

uses the embedding integration while creating the vector store.

So mentally:

```text
BedrockEmbeddings(...)
       ↓
Configure embedding capability

FAISS.from_documents(...)
       ↓
Use embeddings on documents
       ↓
Build vector index
```

This distinction is useful when explaining the code.

---

# 17. What is stored in FAISS?

At a simplified conceptual level:

```text
FAISS

Vector A ↔ Chunk A
Vector B ↔ Chunk B
Vector C ↔ Chunk C
...
```

Why maintain the relationship?

Because after FAISS determines:

```text
Vector B is relevant
```

your application needs the associated document content:

```text
Chunk B
```

Then later:

```python
doc.page_content
```

is used to construct Claude's context.

---

# 18. Why not send vectors to Claude?

This is another important distinction.

Claude does not receive something like:

```text
[0.21, -0.72, 0.14, ...]
```

as the policy context in your current RAG flow.

Vectors are used for:

```text
SEARCH / RETRIEVAL
```

After retrieval:

```text
FAISS
 ↓
Relevant Document
 ↓
page_content
 ↓
Readable Text
 ↓
Claude
```

So:

> **Vectors help find the text. Claude receives the retrieved text.**

---

# 19. Embeddings happen at two conceptual stages

This is an important RAG concept.

## Document-side embeddings

During indexing:

```text
Policy Chunk
    ↓
Titan
    ↓
Chunk Vector
    ↓
FAISS
```

This happens while the vector index is being built.

## Query-side embedding

At retrieval time:

```text
Employee Question
       ↓
Embedding process
       ↓
Query representation
       ↓
Compare against indexed vectors
```

The project analysis explicitly describes question-time retrieval as including question embedding followed by FAISS top-3 retrieval. :chatgpt-content-reference{index="1"}

---

# 20. Why should documents and queries use compatible embeddings?

Imagine you represent policy chunks using one completely unrelated representation system and questions using another.

Then comparisons may not be meaningful.

Conceptually you need:

```text
Document Text
     ↓
Embedding Space
     ↓
Document Vectors


Question
     ↓
Compatible Embedding Space
     ↓
Query Vector
```

Then vector similarity has useful meaning.

In your project, the FAISS vector-store integration is built using the configured Titan embedding integration, which is then associated with retrieval.

---

# 21. Does FAISS create the semantic embeddings?

The roles are different.

Think:

```text
Titan
  ↓
Creates embeddings

FAISS
  ↓
Indexes/searches vector representations
```

Memory trick:

> **Titan converts. FAISS compares/searches.**

---

# 22. Does Bedrock store the FAISS index?

No.

Your architecture is:

```text
Amazon Bedrock
   └── Titan Embeddings

Your Python Application
   └── FAISS Index
```

The project analysis identifies FAISS as an in-memory vector index in the current application. :chatgpt-content-reference{index="2"}

So don't say:

> “My vectors are stored in Amazon Bedrock.”

That isn't what this project implements.

---

# 23. Is FAISS Amazon OpenSearch?

No.

Your current architecture uses:

```text
FAISS
```

not:

```text
Amazon OpenSearch Service
```

FAISS runs as part of the application's Python-side vector retrieval setup.

This is appropriate for a small PoC.

---

# 24. What about embedding dimensions?

You may see documentation or interview notes claiming an exact embedding dimension.

Be careful.

For **this learning file**, the project evidence confirms the model ID:

```text
amazon.titan-embed-text-v1
```

but you don't need an exact vector dimension to explain the project correctly.

Unless you verify the exact model/version documentation, don't make the interview answer depend on memorizing a dimension.

A safe answer is:

> **“Titan converts each chunk into a fixed-size numerical vector that FAISS can index and compare.”**

That's enough for understanding your implementation.

---

# 25. What makes an embedding “good”?

For retrieval, useful embeddings should place semantically related text appropriately for similarity search.

For example:

```text
A:
"Privilege leave carry-forward policy"

B:
"Can unused PL move into next year?"

C:
"What is maternity leave duration?"
```

Ideally:

```text
Similarity(A, B)
    >
Similarity(A, C)
```

because A and B discuss related concepts.

That's the behavior we want from semantic embeddings.

---

# 26. Embeddings are not exact truth

An embedding model doesn't create a perfect map of meaning.

It can make mistakes.

For example:

```text
Question
   ↓
Embedding
   ↓
Similarity Search
   ↓
Wrong Chunk
```

Then:

```text
Wrong Chunk
   ↓
Claude
   ↓
Potentially Wrong Answer
```

Therefore:

> **Embedding quality affects retrieval quality, which affects RAG answer quality.**

---

# 27. The complete dependency chain

This is worth remembering:

```text
Policy Data Quality
       ↓
Chunking Quality
       ↓
Embedding Quality
       ↓
Vector Search Quality
       ↓
Retrieved Context Quality
       ↓
Claude Generation Quality
       ↓
Final Answer
```

RAG is a chain.

A failure early in the chain can affect everything downstream.

---

# 28. Embeddings are not the same as tokens

Another common confusion.

### Tokens

Tokens are units used when models process text.

### Embeddings

Embeddings are numerical vector representations.

So:

```text
TOKEN
≠
EMBEDDING
```

You don't say:

> “Titan stores the HR document as tokens in FAISS.”

A better statement:

> **“Titan generates vector embeddings from the document chunks, and FAISS indexes those representations for retrieval.”**

---

# 29. Embeddings are not the same as chunks

Also:

```text
CHUNK
=
Piece of original text
```

while:

```text
EMBEDDING
=
Numerical representation of that text
```

So:

```text
Chunk

"Unused privilege leave can..."

           ↓ Titan

Embedding

[0.18, -0.41, ...]
```

FAISS needs the representation for similarity search while maintaining access to the associated document.

---

# 30. Embeddings are not model training

Generating embeddings does not mean:

```text
Titan learns your HR policy permanently
```

or:

```text
Claude is retrained
```

Instead:

```text
Policy Chunk
     ↓
Titan
     ↓
Vector
     ↓
FAISS
```

The external knowledge remains part of your RAG system.

---

# 31. What happens when a new session builds the index?

Connect this to File 06.

When:

```python
'vector_index' not in st.session_state
```

your application calls:

```python
demo.hr_index()
```

That eventually performs:

```text
PDF
 ↓
Chunks
 ↓
Titan Embedding Work
 ↓
FAISS Index
```

So rebuilding the index can repeat embedding work.

That's one reason the session-state design avoids rebuilding it on every ordinary interaction within the same session.

It also explains a scalability limitation of the current design.

---

# 32. Why embeddings have a cost implication

Titan is accessed through Amazon Bedrock.

Therefore, repeatedly rebuilding the same document index can mean repeating model inference work for embeddings.

Conceptually:

```text
Session A
 ↓
Embed document

Session B
 ↓
Potentially embed document again

Session C
 ↓
Potentially embed document again
```

For a small PoC, this may be acceptable.

For production, you'd usually consider:

```text
Document changes
       ↓
Embed/update index
       ↓
Persist/share index
       ↓
Many queries reuse it
```

rather than repeatedly processing an unchanged document.

We'll study this in File 20.

---

# 33. What if the HR policy changes?

Suppose:

```text
Old Policy Chunk
      ↓
Old Embedding
      ↓
FAISS
```

Then the policy is updated.

The vector index needs to represent the updated knowledge.

Conceptually:

```text
New Policy
    ↓
New/changed chunks
    ↓
New embeddings
    ↓
Updated index
```

The current project does not implement a dedicated automated versioned update pipeline.

That's a production improvement.

---

# 34. Why Titan instead of using Claude for embeddings?

Different models serve different purposes.

In your architecture:

```text
Titan Embedding Model
      ↓
Designed/used for embedding representation

Claude
      ↓
Used for natural-language generation
```

So you use specialized capabilities:

```text
Titan → Retrieval representation

Claude → Answer generation
```

---

# 35. Why Amazon Bedrock?

In this project's architecture, Bedrock gives your application managed access to the configured foundation-model capabilities.

You use it for two different tasks:

```text
Amazon Bedrock
      │
      ├── Titan
      │     ↓
      │  Embeddings
      │
      └── Claude
            ↓
         Generation
```

This is an important interview point:

> **Bedrock is used twice in the RAG pipeline, for different purposes.**

---

# 36. Embedding model vs LLM

Remember this table:

| Question | Titan Embeddings | Claude |
|---|---|---|
| Converts text to vectors? | ✅ | Not its role here |
| Helps semantic retrieval? | ✅ | Not directly |
| Generates final HR answer? | ❌ | ✅ |
| Used through Bedrock? | ✅ | ✅ |
| Used with FAISS? | ✅ | Indirectly after retrieval |

---

# 37. Embedding model vs vector store

Another critical comparison:

| Component | Titan | FAISS |
|---|---|---|
| Model? | Yes, embedding model | No |
| Creates vectors? | Yes | No, it indexes/searches them |
| Stores/indexes searchable representations? | No | Yes |
| Performs retrieval? | Not by itself | Yes |
| Generates answers? | No | No |

Then:

```text
Claude
=
Generation
```

So your three core RAG technologies are:

```text
Titan → REPRESENT
FAISS → RETRIEVE
Claude → GENERATE
```

---

# 38. Current vs not implemented

### CURRENT

```text
✓ BedrockEmbeddings
✓ Amazon Titan embedding model
✓ Embedding HR policy chunks
✓ FAISS vector index
✓ Query-time semantic retrieval
```

### NOT CURRENT

```text
✗ Bedrock Knowledge Bases
✗ OpenSearch vector storage
✗ Dedicated embedding microservice
✗ Embedding cache service
✗ Automated embedding refresh pipeline
✗ Hybrid retrieval
✗ Reranking
```

Don't add these to your project story unless you're specifically discussing future improvements.

---

# 39. How would you evaluate embeddings?

You don't evaluate an embedding model just by saying:

> “The vectors look good.”

Vectors themselves aren't very human-readable.

Instead, evaluate what they enable.

For example:

```text
Question:
"Can I move unused PL to next year?"

Expected:
Privilege leave carry-forward section

Actual Top 3 Retrieval:
1. ?
2. ?
3. ?
```

Then check:

```text
Did the correct policy section appear?
At what rank?
How consistently?
```

This is retrieval evaluation.

We'll cover it deeply in:

`19-Testing-and-RAG-Evaluation.md`.

---

# 40. Complete embedding flow

Keep this picture in your head:

```text
              INDEXING TIME

HR Policy
    ↓
Chunks
    ↓
┌────────────────────────┐
│ Amazon Titan           │
│ Embedding Model        │
│ via Amazon Bedrock     │
└───────────┬────────────┘
            ↓
     Chunk Embeddings
            ↓
          FAISS


              QUERY TIME

Employee Question
        ↓
Embedding Representation
        ↓
      Query Vector
        ↓
       FAISS
        ↓
Compare with Indexed Vectors
        ↓
Top 3 Relevant Chunks
        ↓
Context + Question
        ↓
Claude Haiku 4.5
        ↓
Answer
```

The inspected application flow confirms that question-time processing includes query embedding and FAISS top-three retrieval before context construction and Claude invocation. :chatgpt-content-reference{index="3"}

---

# Interview Questions & Answers — `10-Titan-Embeddings.md`

## Q1. What are embeddings?

> “Embeddings are numerical vector representations of data such as text. In my RAG project, I use embeddings to represent HR policy chunks in a form that supports semantic similarity search. This allows the retriever to find relevant policy content even when the employee's wording is different from the wording in the policy.”

---

## Q2. Why do you need embeddings in your RAG project?

> “I need embeddings because my retrieval is semantic rather than relying only on exact keyword matching. Titan converts the policy chunks into vector representations, and FAISS indexes those vectors so the application can retrieve chunks that are semantically related to the employee's question.”

---

## Q3. Which embedding model do you use?

> “The current backend configures Amazon Titan using the model ID `amazon.titan-embed-text-v1` through the LangChain `BedrockEmbeddings` integration.”

---

## Q4. What is Titan's role in your project?

> “Titan is the embedding model. It converts HR policy text into numerical vector representations that can be indexed and searched using FAISS. Titan does not generate the final HR answer; Claude handles generation.”

---

## Q5. What is `BedrockEmbeddings`?

> “`BedrockEmbeddings` is the LangChain AWS integration I use to access the configured embedding model through Amazon Bedrock. In my project, it is configured with the default AWS profile and the Titan embedding model ID.”

---

## Q6. Does `BedrockEmbeddings()` immediately embed all documents?

> “That line primarily configures the embedding integration. I then pass that embedding object together with the document chunks to `FAISS.from_documents()`, which uses the embedding capability while creating the vector index.”

---

## Q7. What happens to a policy chunk?

> “A policy chunk is passed through the Titan embedding capability and represented as a numerical vector. FAISS indexes that representation while maintaining the relationship to the source document content, so relevant text can later be returned during retrieval.”

---

## Q8. How does semantic search work in your project?

> “The policy chunks are represented using embeddings and indexed in FAISS. When an employee asks a question, the query is represented in the compatible embedding space and FAISS compares it with the indexed representations to retrieve the most relevant policy chunks.”

---

## Q9. What's the difference between keyword search and semantic search?

> “Keyword search primarily depends on matching words or terms, while semantic retrieval tries to identify text with related meaning. For example, a user might ask about moving unused PL to next year while the policy uses the phrase carry forward privilege leave. Embeddings help retrieval connect those semantically related expressions.”

---

## Q10. What's the difference between Titan and FAISS?

> “Titan creates the vector embeddings. FAISS indexes and searches those vector representations. So Titan provides the semantic representation, while FAISS provides vector retrieval.”

---

## Q11. What's the difference between Titan and Claude?

> “Titan is used for embeddings, while Claude is used for generation. Titan converts text into vector representations for retrieval. After FAISS retrieves relevant chunks, Claude receives those chunks together with the employee's question and generates the final answer.”

---

## Q12. Does Claude search FAISS?

> “No. My Python application performs the FAISS similarity search first. It retrieves the relevant policy chunks, builds the context and then sends that context with the user's question to Claude.”

---

## Q13. Does Claude receive the embedding vectors?

> “Not as the policy context in my current RAG flow. Embeddings are used to identify relevant documents. After retrieval, I extract the actual text using `page_content` and include that readable text in the prompt sent to Claude.”

---

## Q14. Are embeddings the same as tokens?

> “No. Tokens are units used when models process text, while embeddings are numerical vector representations. In my project, Titan produces embeddings for semantic retrieval; I don't describe those vectors as tokens.”

---

## Q15. Are embeddings the same as fine-tuning?

> “No. Creating embeddings does not train Claude or permanently teach Titan my HR policy. The policy remains external knowledge. I generate vector representations of its chunks so they can be retrieved at runtime.”

---

## Q16. Where are your vectors stored?

> “The current project uses FAISS as an in-memory vector index in the application. I don't store the vector index in Amazon Bedrock or OpenSearch in this implementation.”

---

## Q17. Why use the same compatible embedding approach for documents and queries?

> “Similarity comparison only makes sense when document and query representations are compatible. The policy chunks and employee questions need to be represented in the same embedding space so FAISS can meaningfully compare them.”

---

## Q18. Can embeddings produce bad retrieval results?

> “Yes. Embeddings are not perfect. Retrieval quality can also be affected by document quality, chunking and the nature of the query. If the wrong chunks are retrieved, Claude receives poor context, so embedding and retrieval quality need to be evaluated using representative questions.”

---

## Q19. How would you evaluate your embedding and retrieval quality?

> “I would create a set of representative HR questions with known relevant policy sections. Then I would run retrieval and check whether those expected sections appear in the top results and at what rank. I would compare configurations or embedding approaches using retrieval metrics and final answer quality rather than assuming the model is good simply because it produces vectors.”

---

## Q20. Explain Titan embeddings in 30 seconds.

> “In my project, I use Amazon Titan through Bedrock to create embeddings for the HR policy chunks. An embedding is a numerical representation that supports semantic similarity. FAISS indexes those representations. When an employee asks a question, the retrieval process compares the query representation with the indexed vectors and returns the top relevant policy chunks. Those chunks are then sent as text context to Claude for final answer generation.”

---

# Important interview traps

### “Titan generates your HR answers?”

> **No. Titan generates embeddings. Claude generates the final answer.**

### “FAISS creates your embeddings?”

> **No. Titan provides the embeddings; FAISS indexes and searches vector representations.**

### “You store your vectors in Bedrock?”

> **No. The current application uses an in-memory FAISS index. Bedrock provides model access.**

### “Claude receives vectors and translates them into an answer?”

> **No. Vectors are used for retrieval. Claude receives the retrieved policy text as context.**

### “Embedding means you trained Titan on your HR document?”

> **No. Embedding generation creates vector representations; it is not model training or fine-tuning.**

---

# Five questions to master first

Focus on:

**Q1 — What are embeddings?**

**Q2 — Why are embeddings needed?**

**Q4 — What does Titan do?**

**Q10 — Titan vs FAISS?**

**Q11 — Titan vs Claude?**

Keep this simple mental model:

```text
             HR POLICY CHUNK
                    ↓
                  TITAN
                    ↓
                 VECTOR
                    ↓
                  FAISS
                    ↓
              VECTOR SEARCH
                    ↓
           RELEVANT HR CHUNK
                    ↓
                  CLAUDE
                    ↓
                  ANSWER
```

And remember this sentence:

> **“Titan represents meaning as vectors, FAISS uses those vectors to find relevant policy chunks, and Claude uses the retrieved text to generate the final answer.”**

If you can clearly explain **Titan → Vector → FAISS → Retrieved Text → Claude**, you understand the role of embeddings in your project.