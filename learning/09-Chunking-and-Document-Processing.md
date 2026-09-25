# `09-Chunking-and-Document-Processing.md`

## NovaMindAI HR Q&A — Chunking and Document Processing

### Main question

> **Why do I split the HR policy into chunks, how does `RecursiveCharacterTextSplitter` work, and why did I use `chunk_size=1000` and `chunk_overlap=100`?**

This file connects directly to what we learned in File 08:

```text
08
PDF
 ↓
PyPDFLoader
 ↓
Documents

09
Documents
 ↓
Text Splitter
 ↓
Chunks

10
Chunks
 ↓
Titan Embeddings
```

Your actual backend configures:

```python
data_split = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", " ", ""],
    chunk_size=1000,
    chunk_overlap=100
)

chunks = data_split.split_documents(documents)
```

So now we need to understand **why those lines exist**, not just what they do.

---

# 1. First understand the problem

Suppose your HR policy is one long document:

```text
HR LEAVE POLICY

Section 1: Purpose
...

Section 2: Privilege Leave
...

Section 3: Casual Leave
...

Section 4: Sick Leave
...

Section 5: Maternity Leave
...

Section 6: Carry Forward Rules
...
```

Now an employee asks:

> **“Can I carry forward my privilege leave?”**

Do we want to treat the entire policy as one giant searchable piece?

Usually, no.

Instead, we divide it into smaller pieces:

```text
Complete HR Policy
       ↓
   CHUNKING
       ↓
┌─────────────┐
│  Chunk 1    │
├─────────────┤
│  Chunk 2    │
├─────────────┤
│  Chunk 3    │
├─────────────┤
│  Chunk 4    │
├─────────────┤
│    ...      │
└─────────────┘
```

Those smaller pieces become the units that are embedded and retrieved.

---

# 2. What is chunking?

In simple English:

> **Chunking means dividing a large document into smaller pieces of text before creating embeddings and indexing them for retrieval.**

Your flow becomes:

```text
Large PDF
   ↓
Extract text
   ↓
Split into chunks
   ↓
Embed each chunk
   ↓
Store/index vectors
   ↓
Retrieve relevant chunks
```

So chunking happens **before embeddings**.

---

# 3. Why not embed the entire PDF as one chunk?

Imagine your entire leave policy becomes one vector:

```text
Entire Leave Policy
        ↓
     Titan
        ↓
   One Vector
```

Then an employee asks:

> “What is the sick leave rule?”

Your retrieval system has very little granularity.

The entire document is either retrieved or not.

Instead:

```text
Privilege Leave Section → Vector A
Sick Leave Section      → Vector B
Maternity Section       → Vector C
Carry Forward Section   → Vector D
```

Now:

```text
"What is the sick leave rule?"
              ↓
            FAISS
              ↓
     Relevant Sick Leave Chunk
```

That gives retrieval a much more useful unit to work with.

---

# 4. Why not make chunks extremely small?

Now imagine the opposite extreme.

Suppose:

```text
Chunk 1 = "Employees"
Chunk 2 = "are"
Chunk 3 = "eligible"
Chunk 4 = "for"
Chunk 5 = "privilege"
Chunk 6 = "leave"
```

Retrieval would lose important context.

For example:

```text
"Employees may carry forward unused
privilege leave subject to..."
```

contains a complete idea.

But splitting it too aggressively might create:

```text
Chunk 1:
Employees may carry forward

Chunk 2:
unused privilege leave

Chunk 3:
subject to the following...
```

Each chunk contains only part of the meaning.

So:

> **Chunks that are too small can lose context.**

---

# 5. Why not make chunks extremely large?

Now imagine:

```text
Chunk 1:

Privilege Leave
+
Sick Leave
+
Maternity Leave
+
Holiday Rules
+
Carry Forward Rules
+
Other Policies
```

If FAISS retrieves that chunk for one specific question, Claude receives lots of irrelevant information.

Therefore:

> **Chunks that are too large can reduce retrieval precision and add unnecessary context.**

This gives us the basic trade-off:

```text
VERY SMALL CHUNKS
      ↓
Less context

VERY LARGE CHUNKS
      ↓
More irrelevant information

GOOD CHUNK SIZE
      ↓
Enough meaning
+
Useful retrieval granularity
```

---

# 6. Your project's splitter

Your actual project uses:

```python
RecursiveCharacterTextSplitter
```

with:

```python
chunk_size=1000
chunk_overlap=100
```

and:

```python
separators=["\n\n", "\n", " ", ""]
```

Then:

```python
chunks = data_split.split_documents(documents)
```

So:

```text
Loaded Documents
       ↓
RecursiveCharacterTextSplitter
       ↓
Chunks
```

---

# 7. What does `RecursiveCharacterTextSplitter` mean?

Let's break down the name:

```text
Recursive
+
Character
+
Text
+
Splitter
```

The important idea is that it tries to split text using a hierarchy of separators.

Your project explicitly provides:

```python
["\n\n", "\n", " ", ""]
```

Conceptually, it prefers larger natural boundaries first.

It tries:

```text
1. "\n\n"
   ↓
Paragraph boundary

2. "\n"
   ↓
Line boundary

3. " "
   ↓
Word/space boundary

4. ""
   ↓
Character-level fallback
```

The goal is to keep meaningful text together where possible while respecting the configured chunk size.

---

# 8. Why is it called “recursive”?

Imagine the text is too large to fit into the configured chunk size.

The splitter first tries a higher-level separator.

For example:

```text
Paragraph A

Paragraph B

Paragraph C
```

It first tries:

```python
"\n\n"
```

If the resulting text pieces are still too large, it moves to another separator:

```python
"\n"
```

Then:

```python
" "
```

and finally:

```python
""
```

as a fallback.

You don't need to memorize its internal algorithm line by line.

For an interview, understand:

> **“It attempts to preserve larger natural text boundaries first and falls back to smaller separators when needed.”**

---

# 9. Your separators

Let's understand your exact configuration.

## First separator

```python
"\n\n"
```

Two newline characters commonly represent a paragraph break.

Conceptually:

```text
Paragraph 1

Paragraph 2
```

This is a useful place to split because paragraphs often represent logical groups of information.

---

# 10. Second separator

```python
"\n"
```

One newline can represent a line break.

If paragraph-level splitting isn't sufficient, the splitter can try line boundaries.

---

# 11. Third separator

```python
" "
```

This is a space.

If larger boundaries aren't sufficient, the splitter can split around word boundaries.

---

# 12. Final separator

```python
""
```

An empty separator allows smaller character-level splitting as a fallback.

The overall idea is:

```text
Prefer:

Paragraph
   ↓
Line
   ↓
Word boundary
   ↓
Character fallback
```

rather than immediately chopping text arbitrarily.

---

# 13. What does `chunk_size=1000` mean?

Your project configures:

```python
chunk_size=1000
```

A critical detail:

> **In this splitter configuration, `chunk_size=1000` should not be described as “1000 tokens.”**

You are using a character-oriented splitter without a tokenizer-based length function configured in the shown code.

So the safe project-specific explanation is:

> **The splitter targets chunks around the configured character-length limit of 1000, subject to its splitting/merging behavior.**

Do **not** say:

> “My chunks are exactly 1000 tokens.”

That would be inaccurate.

---

# 14. Characters vs tokens

These are different concepts.

### Characters

Examples:

```text
A
m
a
z
o
n
```

Each letter is a character.

### Words

```text
Amazon Bedrock
```

contains two ordinary English words.

### Tokens

LLMs process text in tokenized units determined by their tokenizer.

A token is not necessarily equal to:

```text
one character
```

or:

```text
one word
```

Therefore:

```text
1000 characters
≠
1000 words
≠
1000 tokens
```

This is an important interview distinction.

---

# 15. Why use a chunk size around 1000?

In this project, `1000` is the configured value.

A reasonable explanation is:

> **It was chosen as a starting configuration intended to preserve enough surrounding policy context while still creating smaller retrieval units.**

But don't claim:

> **“1000 is the perfect chunk size.”**

The project does not contain evidence proving that.

A stronger answer is:

> **“1000 is my current PoC configuration. In production I would evaluate chunk size using representative HR questions and retrieval/answer quality.”**

That's engineering thinking.

---

# 16. Now understand overlap

Your project also configures:

```python
chunk_overlap=100
```

Overlap means neighboring chunks can share some text.

Simplified example:

Without overlap:

```text
Chunk 1:
ABCDEFGHIJ

Chunk 2:
KLMNOPQRST
```

With overlap:

```text
Chunk 1:
ABCDEFGHIJ

Chunk 2:
IJKLMNOPQR
         ↑
Some previous content repeated
```

The actual splitter behavior is more nuanced than this toy example, but the purpose is what matters.

---

# 17. Why do we need overlap?

Suppose the source says:

```text
Employees are allowed to carry forward unused
privilege leave into the following calendar year,
subject to the limits described below.
```

Imagine a chunk boundary occurs here:

```text
Chunk 1:
Employees are allowed to carry forward unused
privilege leave

---------------- CHUNK BOUNDARY ----------------

Chunk 2:
into the following calendar year, subject to
the limits described below.
```

Now the meaning is split.

Chunk 1 doesn't contain the complete rule.

Chunk 2 doesn't clearly state what is being carried forward.

Overlap can preserve some shared context:

```text
Chunk 1:
Employees are allowed to carry forward unused
privilege leave...

Chunk 2:
...carry forward unused privilege leave into
the following calendar year...
```

Now both chunks retain more useful meaning.

---

# 18. Your overlap is 100

Your configuration:

```python
chunk_overlap=100
```

means the splitter is configured to preserve overlap between neighboring chunks up to the intended overlap behavior.

Again:

> Don't call it “100 tokens.”

In this code, think in terms of the splitter's character-based length configuration.

---

# 19. Why not use zero overlap?

You could configure:

```python
chunk_overlap=0
```

But then important ideas crossing a chunk boundary may lose surrounding context.

Example:

```text
Chunk 1:
Employees with more than five years of...

Chunk 2:
service are eligible for...
```

Retrieving only one chunk could miss part of the statement.

Overlap reduces this boundary problem.

---

# 20. Why not use huge overlap?

Suppose:

```text
chunk_size = 1000
chunk_overlap = 900
```

Then neighboring chunks could contain a large amount of repeated text.

Conceptually:

```text
Chunk 1
████████████████████

Chunk 2
  ████████████████████

Chunk 3
    ████████████████████
```

That can create:

```text
Lots of duplicated text
+
More chunks
+
More embedding work
+
Potentially repetitive retrieval results
```

So overlap also has a trade-off.

---

# 21. Chunk size and overlap work together

Don't evaluate them independently.

Think:

```text
chunk_size
    ↓
How much content each retrieval unit contains

chunk_overlap
    ↓
How much neighboring context can be shared
```

Your configuration:

```text
chunk_size    = 1000
chunk_overlap = 100
```

is therefore a **chunking strategy**, not two unrelated numbers.

---

# 22. What does `split_documents()` do?

After configuring the splitter:

```python
data_split = RecursiveCharacterTextSplitter(...)
```

your code executes:

```python
chunks = data_split.split_documents(documents)
```

This is where splitting actually happens.

Remember from File 05:

```text
RecursiveCharacterTextSplitter(...)
        ↓
CONFIGURE SPLITTER

split_documents(documents)
        ↓
ACTUALLY SPLIT DOCUMENTS
```

The output is:

```python
chunks
```

which contains smaller document objects.

---

# 23. Why use `split_documents()` instead of just splitting a string?

Your input came from:

```text
PyPDFLoader
     ↓
Document objects
```

Using the document-oriented splitting method allows the pipeline to continue working with document objects rather than reducing everything immediately to unrelated plain strings.

Conceptually:

```text
Document
├── page_content
└── metadata

       ↓ split

Chunk Document
├── page_content
└── associated metadata
```

Preserving metadata can become useful for things such as source tracking and citations.

Your current UI does not yet surface proper citations, but maintaining document structure makes such improvements more feasible.

---

# 24. What happens after chunking?

Your backend then creates:

```python
data_embeddings = BedrockEmbeddings(...)
```

and:

```python
db_index = FAISS.from_documents(
    chunks,
    data_embeddings
)
```

So:

```text
Chunks
  ↓
Titan Embeddings
  ↓
Vectors
  ↓
FAISS
```

This means:

> **The unit being embedded and indexed is the chunk, not the complete PDF.**

That's a critical point.

---

# 25. One chunk → one embedding conceptually

At a simplified level:

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

Chunk 3
   ↓
Titan
   ↓
Vector 3
```

Then FAISS indexes these vectors:

```text
FAISS

Vector 1 → Chunk 1
Vector 2 → Chunk 2
Vector 3 → Chunk 3
...
```

When a question arrives, the system can find relevant chunks through vector similarity.

---

# 26. Chunking directly affects retrieval

This relationship is extremely important:

```text
CHUNKING
   ↓
EMBEDDINGS
   ↓
RETRIEVAL
   ↓
CONTEXT
   ↓
CLAUDE ANSWER
```

Bad chunking can therefore produce bad answers even when Claude is working correctly.

---

# 27. Example of bad chunking

Suppose the policy says:

```text
Employees are entitled to privilege leave.

Unused privilege leave can be carried forward
subject to a maximum accumulation limit of X.
```

If chunking separates important information badly:

```text
Chunk A:
Employees are entitled to privilege leave.

Chunk B:
subject to a maximum accumulation limit of X.
```

Chunk B has lost what the limit refers to.

If Chunk B is retrieved alone, the context is weak.

That's why chunk boundaries matter.

---

# 28. Example of better chunking

Ideally:

```text
Chunk:

Employees are entitled to privilege leave.
Unused privilege leave can be carried forward
subject to a maximum accumulation limit of X.
```

Now the chunk contains a coherent idea.

When retrieved:

```text
Question
   ↓
Relevant coherent chunk
   ↓
Claude
```

the model receives more useful evidence.

---

# 29. Chunking is not “just preprocessing”

This is a common mistake.

You might think:

> “Chunking is only data cleaning.”

But in RAG:

> **Chunking is part of retrieval design.**

Because you're deciding:

> **What unit of knowledge can the retriever return?**

If you chunk by paragraph:

```text
Retriever returns paragraph-sized knowledge
```

If you chunk into larger sections:

```text
Retriever returns section-sized knowledge
```

So chunking defines the **retrieval granularity**.

---

# 30. Chunk size trade-off

Remember this:

| Smaller chunks | Larger chunks |
|---|---|
| More precise retrieval possible | More surrounding context |
| Less information per chunk | More information per chunk |
| More chunks/vectors | Fewer chunks/vectors |
| Can lose surrounding context | Can include irrelevant text |

There is no universally perfect value.

---

# 31. Overlap trade-off

Similarly:

| Smaller overlap | Larger overlap |
|---|---|
| Less duplication | More boundary context |
| Fewer repeated embeddings | More repeated content |
| Lower processing/storage overhead | More processing/storage overhead |
| Greater boundary-loss risk | Greater duplication risk |

Again:

> **It is an optimization problem, not a magic number.**

---

# 32. How would you choose chunk size properly?

A weak answer:

> “I chose 1000 because everyone uses 1000.”

A much stronger approach:

```text
Choose candidate configurations
        ↓
Create representative HR questions
        ↓
Run retrieval
        ↓
Check expected policy sections
        ↓
Measure retrieval quality
        ↓
Check final answer quality
        ↓
Compare configurations
```

For example, conceptually you might evaluate different configurations.

But don't claim your current project performed this experiment unless it actually did.

The current project gives us:

```text
1000 / 100
```

as configuration—not proof that it is optimal.

---

# 33. What would you evaluate?

Suppose you have:

```text
Question:
"Can privilege leave be carried forward?"
```

You know which policy section should answer it.

Run retrieval:

```text
Question
   ↓
FAISS
   ↓
Top 3 chunks
```

Then ask:

```text
Did the correct section appear?

Was it ranked highly?

Did the retrieved chunk contain enough context?

Did unrelated information dominate?

Did Claude answer correctly from it?
```

This is how chunking connects to RAG evaluation.

We'll go deeper in:

`19-Testing-and-RAG-Evaluation.md`.

---

# 34. Could you chunk by policy section instead?

Potentially, yes.

Imagine the document has reliable headings:

```text
1. Privilege Leave
2. Casual Leave
3. Sick Leave
4. Maternity Leave
```

A more document-aware production strategy might consider logical sections.

But your current implementation does **not** implement heading-aware policy chunking.

It uses:

```python
RecursiveCharacterTextSplitter
```

with character-based configuration.

So distinguish:

```text
CURRENT
Recursive character splitting
```

from:

```text
POSSIBLE FUTURE
Structure-aware/section-aware splitting
```

---

# 35. Does your project summarize chunks before embedding?

No evidence in the current implementation shows:

```text
Chunk
 ↓
LLM Summary
 ↓
Embedding
```

Instead:

```text
Chunk
 ↓
Titan Embedding
```

directly.

Don't invent an intermediate summarization stage.

---

# 36. Does your project use semantic chunking?

Not in the current implementation.

Semantic chunking generally refers to using semantic signals to determine chunk boundaries.

Your current splitter uses:

```text
Recursive character-based splitting
```

with configured separators.

So don't say:

> “I implemented semantic chunking.”

You didn't in this project.

---

# 37. Does your project use token-based chunking?

Not based on the inspected code.

You use:

```python
RecursiveCharacterTextSplitter(...)
```

with the shown character-oriented configuration.

There is no shown tokenizer-based splitter configuration.

So:

```text
CURRENT
Character-oriented recursive splitting

NOT CURRENT
Explicit token-based chunking
```

---

# 38. Document processing in this project

Let's put everything together.

```text
Remote HR Policy PDF
         ↓
    PyPDFLoader
         ↓
Loaded Document Objects
         ↓
RecursiveCharacterTextSplitter
         │
         ├── chunk_size = 1000
         ├── overlap = 100
         └── separators:
             \n\n
             \n
             space
             character fallback
         ↓
Chunk Documents
         ↓
BedrockEmbeddings
         ↓
Titan
         ↓
Vectors
         ↓
FAISS
```

This is your document-processing pipeline.

---

# 39. Current limitations

Your current chunking design is intentionally simple.

It does not demonstrate:

```text
✗ Chunk-size evaluation
✗ Semantic chunking
✗ Heading-aware chunking
✗ Table-specific processing
✗ OCR-aware processing
✗ Document-layout analysis
✗ Chunk quality scoring
✗ Reranking
```

These are not necessarily required for the PoC.

The important point is:

> **Don't claim features that aren't implemented.**

---

# 40. How would you improve chunking for production?

A strong answer is not:

> “I would just reduce chunk size to 500.”

You don't know that 500 is better without evaluation.

Instead:

```text
Understand document structure
       ↓
Build representative HR Q&A test set
       ↓
Evaluate current 1000/100 baseline
       ↓
Compare alternative strategies
       ↓
Measure retrieval quality
       ↓
Measure final answer quality
       ↓
Choose evidence-based configuration
```

You might also evaluate whether policy headings or sections should influence boundaries.

That's much stronger engineering reasoning.

---

# 41. The three things to remember

If this lesson feels large, remember only:

### 1. Chunk size

> How much text goes into each retrieval unit.

### 2. Chunk overlap

> How much neighboring context is shared to reduce information loss around boundaries.

### 3. Separators

> Where the recursive splitter prefers to break the text.

For your project:

```text
Chunk size    → 1000
Overlap       → 100

Separators:

Paragraph
 ↓
Line
 ↓
Space
 ↓
Character fallback
```

---

# Interview Questions & Answers — `09-Chunking-and-Document-Processing.md`

## Q1. What is chunking?

> “Chunking is the process of dividing a large document into smaller pieces before embedding and indexing it. In my project, I load the HR policy and use RecursiveCharacterTextSplitter to divide the document into chunks. Those chunks become the units that Titan embeds and FAISS later retrieves.”

---

## Q2. Why do you need chunking in RAG?

> “I need chunking because retrieving the entire HR policy for every question would provide poor retrieval granularity and potentially a lot of irrelevant context. By dividing the policy into smaller meaningful pieces, FAISS can retrieve only the portions that are most relevant to the employee's question.”

---

## Q3. Which text splitter do you use?

> “I use LangChain's RecursiveCharacterTextSplitter. My current configuration uses a chunk size of 1000, overlap of 100 and the separators double newline, newline, space and an empty-string fallback.”

---

## Q4. Why did you use RecursiveCharacterTextSplitter?

> “I used it because it provides a simple way to split text while preferring larger natural boundaries where possible. With my separator configuration, it tries paragraph boundaries first, then line boundaries, then spaces and finally a smaller character-level fallback when necessary.”

---

## Q5. What does `chunk_size=1000` mean?

> “It defines the target maximum chunk length used by my current splitter configuration. Because my implementation uses the character-oriented RecursiveCharacterTextSplitter without an explicit tokenizer-based length function, I describe this as approximately a character-based configuration rather than saying it is 1000 tokens.”

---

## Q6. Why did you choose chunk size 1000?

> “It is the current starting configuration for this proof of concept. The intention is to retain enough policy context while still producing smaller retrieval units. I don't claim that 1000 is universally optimal. For production, I would compare chunking configurations using representative HR questions and retrieval and answer-quality evaluation.”

---

## Q7. What is chunk overlap?

> “Chunk overlap means neighboring chunks share some text. Its purpose is to reduce the chance of losing important context when a sentence or policy rule crosses a chunk boundary.”

---

## Q8. Why did you use overlap 100?

> “The current project uses an overlap of 100 as a simple way to preserve some context between neighboring chunks. Like chunk size, I treat it as a configuration to evaluate rather than a universally correct value.”

---

## Q9. Why not use zero overlap?

> “With zero overlap, important information that crosses a chunk boundary can become separated. A retrieved chunk may then contain only part of a policy rule. Some overlap helps preserve continuity around those boundaries.”

---

## Q10. Why not use very large overlap?

> “A very large overlap creates significant duplicated content between chunks. That can increase the number of chunks and embedding work and may also produce repetitive retrieval results. So overlap needs to balance context preservation against duplication.”

---

## Q11. What separators are you using?

> “My splitter uses `\n\n`, `\n`, a space and an empty string. Conceptually, that lets the recursive splitter prefer paragraph boundaries first, then lines, then word boundaries and finally a character-level fallback.”

---

## Q12. What happens after chunking?

> “After chunking, I pass the chunks together with my Bedrock embedding integration to `FAISS.from_documents()`. Titan generates vector representations for the chunks, and FAISS builds the searchable vector index.”

---

## Q13. Does each chunk get an embedding?

> “Conceptually, yes. Each chunk is represented by an embedding generated through the configured Titan embedding model, and those representations are indexed so FAISS can perform semantic retrieval.”

---

## Q14. What happens if chunks are too small?

> “If chunks are too small, they can lose important surrounding context. A policy rule may be split across several pieces, and a retrieved chunk might not contain enough information for Claude to answer correctly.”

---

## Q15. What happens if chunks are too large?

> “If chunks are too large, each chunk can contain multiple unrelated policy topics. Retrieval can become less precise and Claude may receive unnecessary context. Larger chunks also consume more context when included in the prompt.”

---

## Q16. How does chunking affect RAG quality?

> “Chunking defines the units that are embedded and retrieved. Poor boundaries or inappropriate chunk sizes can cause FAISS to return incomplete or noisy context. Since Claude generates its answer from that retrieved context, chunking can directly affect final answer quality.”

---

## Q17. Are you using semantic chunking?

> “No. The current implementation uses RecursiveCharacterTextSplitter with character-oriented size, overlap and separator settings. I have not implemented a separate semantic chunking algorithm in this project.”

---

## Q18. How would you determine the best chunk size?

> “I would build a representative HR question set where I know the expected supporting policy sections. Then I would compare different chunking configurations and measure whether the correct sections are retrieved and whether the final answers are grounded and accurate. I would choose the configuration based on evaluation results rather than assuming one chunk size is always best.”

---

## Q19. Would you change the chunking strategy for production?

> “Possibly, but only based on the document structure and evaluation results. For example, if HR policies have reliable headings and sections, I could evaluate structure-aware chunking. I would compare it against my current recursive splitting baseline before deciding whether the additional complexity improves retrieval.”

---

## Q20. Explain your chunking strategy in 30 seconds.

> “After loading the HR policy, I use RecursiveCharacterTextSplitter with a chunk size of 1000, overlap of 100 and separators for paragraphs, lines, spaces and a character fallback. The goal is to create smaller retrieval units while preserving some neighboring context across chunk boundaries. Those chunks are then embedded using Titan and indexed in FAISS. The 1000/100 configuration is my current PoC setting, not something I claim is universally optimal.”

---

# Important interview traps

**“Your chunk size is 1000 tokens, correct?”**

> **“No. In my current RecursiveCharacterTextSplitter configuration, I haven't configured token-based length measurement, so I describe it as character-oriented rather than 1000 tokens.”**

**“Why exactly is 1000 the best chunk size?”**

> **“I don't claim it's the best. It's the current PoC configuration. The optimal value should be selected through retrieval and answer-quality evaluation.”**

**“Overlap means duplicated vectors are useless, right?”**

> **No. Some overlap intentionally preserves context around chunk boundaries, although excessive overlap can introduce unnecessary duplication.**

**“Are you doing semantic chunking?”**

> **No. The current project uses recursive character-based splitting.**

**“Does Claude split the document?”**

> **No. My Python preprocessing pipeline splits the document before embeddings and FAISS indexing.**

---

# Five questions to master first

Focus on:

**Q1 — What is chunking?**

**Q2 — Why is chunking required?**

**Q5 — What does `chunk_size=1000` mean?**

**Q7 — Why overlap?**

**Q18 — How would you choose chunk size properly?**

Keep this mental picture:

```text
                 HR POLICY

                     ↓

                  CHUNKING

                     ↓

      ┌──────────────┼──────────────┐
      ↓              ↓              ↓
   Chunk 1        Chunk 2        Chunk 3
      │              │              │
      └──────────────┼──────────────┘
                     ↓
              Titan Embeddings
                     ↓
                   FAISS
                     ↓

              Employee Question
                     ↓
             Relevant Chunks
                     ↓
                   Claude
                     ↓
                   Answer
```

The most important sentence from `09-Chunking-and-Document-Processing.md` is:

> **“Chunking defines the pieces of knowledge my retriever can return, so chunk size, overlap and boundaries directly affect retrieval quality and therefore the quality of the final RAG answer.”**