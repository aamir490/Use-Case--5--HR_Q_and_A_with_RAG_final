# `07-RAG-Fundamentals-in-This-Project.md`

## NovaMindAI HR Q&A — RAG Fundamentals

### Main question

> **What exactly is RAG, why does my HR Q&A project need it, and where do Retrieval, Augmentation, and Generation happen in my actual code?**

This is one of the **most important files in the entire project**.

If an interviewer sees:

> **HR Q&A with RAG**

on your resume, questions about RAG are highly likely.

You should understand RAG well enough that you can explain it **without memorizing a textbook definition**.

---

# 1. First forget the term “RAG”

Imagine an employee asks:

> **“What is the privilege leave policy?”**

You could send that directly to Claude:

```text id="fh7tsj"
Employee Question
       ↓
Claude
       ↓
Answer
```

But there is a problem.

Claude does not automatically have your specific HR policy document available as current application context.

Your actual knowledge source is the HR Leave Policy PDF.

So ideally Claude should receive:

```text id="25ps4i"
Employee Question
       +
Relevant HR Policy Information
       ↓
Claude
       ↓
Answer
```

That is the basic reason your project uses **RAG**.

---

# 2. What does RAG mean?

**RAG = Retrieval-Augmented Generation**

Break the name into three words:

```text id="e41dgb"
R = Retrieval
A = Augmented
G = Generation
```

In simple English:

> **First find relevant information, add that information to the user's question, and then ask the LLM to generate an answer using that context.**

Your project implements exactly this pattern: it searches the FAISS index for relevant policy chunks, joins their text into context, adds the question, and invokes Claude. :chatgpt-content-reference{index="0"}

---

# 3. RAG in one simple example

Suppose your HR policy contains:

```text id="u7b69c"
HR POLICY DOCUMENT

Employees are entitled to ...
Privilege leave can ...
Unused leave may ...
...
```

An employee asks:

```text id="ueg54b"
"Can privilege leave be carried forward?"
```

Your system does not simply send that question directly to Claude.

Instead:

```text id="a1z2fa"
Employee Question
       ↓
Search HR Policy
       ↓
Find Relevant Sections
       ↓
Add Sections to Question
       ↓
Send Everything to Claude
       ↓
Generate Answer
```

That's RAG.

---

# 4. Why not just ask Claude directly?

Without RAG:

```text id="wnx2ka"
Employee
   ↓
"What is our company's leave policy?"
   ↓
Claude
```

Claude doesn't automatically know which specific policy document your application intends it to use.

It may rely on general model knowledge rather than your document.

For an HR policy application, that's undesirable.

You want:

```text id="xgr7p2"
Company Policy
      ↓
Relevant Information
      +
Employee Question
      ↓
Claude
```

So RAG provides **external knowledge as context at question time**.

---

# 5. RAG does not retrain Claude

This distinction is extremely important.

You are **not training Claude on the HR PDF**.

Your flow is:

```text id="gb0arh"
HR Policy
   ↓
Retrieve relevant information
   ↓
Put information in prompt
   ↓
Claude
```

Not:

```text id="5xy0mf"
HR Policy
   ↓
Train Claude
   ↓
New custom Claude model
```

Therefore:

> **RAG and model training/fine-tuning are different concepts.**

Your HR policy remains external knowledge that is retrieved when needed.

---

# 6. Two sides of your RAG system

Your RAG application is easiest to understand as two pipelines.

## Pipeline A — Indexing / Knowledge Preparation

```text id="rq7ttw"
HR Leave Policy PDF
        ↓
PyPDFLoader
        ↓
Document Text
        ↓
Text Splitter
        ↓
Chunks
        ↓
Titan Embeddings
        ↓
FAISS Vector Index
```

This prepares the knowledge for search.

## Pipeline B — RAG Question Answering

```text id="3a7z3s"
Employee Question
       ↓
FAISS
       ↓
Top 3 Relevant Chunks
       ↓
Context + Question
       ↓
Claude Haiku 4.5
       ↓
Answer
```

Pipeline A makes retrieval possible.

Pipeline B performs RAG for a user's question.

---

# 7. Important: indexing itself is not the whole RAG process

This is a useful distinction.

These steps:

```text id="o1z3vg"
Load PDF
↓
Chunk
↓
Embed
↓
Index
```

are primarily **knowledge preparation/indexing**.

The actual question-time RAG pattern is:

```text id="o6pfkq"
RETRIEVE
   ↓
AUGMENT
   ↓
GENERATE
```

Both are required for your application, but don't confuse their roles.

---

# 8. R = Retrieval

Let's start with:

# **R — Retrieval**

Retrieval means:

> **Find information from the knowledge source that is relevant to the user's question.**

In your project, retrieval is performed using:

**FAISS**

The key code is:

```python id="nx1dh5"
docs = index.similarity_search(question, k=3)
```

This is one of the most important lines in the project.

---

# 9. What happens during retrieval?

Suppose the user asks:

```text id="sivzhh"
"What is the privilege leave policy?"
```

Conceptually:

```text id="b7tkm3"
Question
   ↓
Semantic similarity search
   ↓
FAISS Vector Index
   ↓
Relevant Chunk #1
Relevant Chunk #2
Relevant Chunk #3
```

Why three?

Because your code uses:

```python id="zhjctc"
k=3
```

So the current configuration requests the top three relevant chunks.

---

# 10. Why semantic retrieval instead of exact keyword matching?

Imagine the policy says something conceptually related to:

```text id="5ec4i4"
"Employees may carry forward unused privilege leave..."
```

and the employee asks:

```text id="l0o9na"
"Can my unused PL move to next year?"
```

The wording may differ.

Semantic retrieval aims to find text based on similarity of meaning rather than requiring identical wording.

That's why embeddings are important.

At a high level:

```text id="eqoyzc"
Policy Chunks
     ↓
Titan Embeddings
     ↓
Vectors
     ↓
FAISS
```

And the question is searched against that vector representation.

We'll study embeddings deeply in:

`10-Titan-Embeddings.md`

and FAISS in:

`11-FAISS-Vector-Search.md`.

---

# 11. What does retrieval return?

Your code returns:

```python id="gyg86a"
docs
```

Conceptually:

```text id="nfy7ta"
docs =

[
  Relevant Document 1,
  Relevant Document 2,
  Relevant Document 3
]
```

These are document objects.

The actual text is accessed through:

```python id="4ydlrb"
doc.page_content
```

---

# 12. A = Augmentation

Now comes:

# **A — Augmentation**

This is sometimes the part beginners understand least.

Augmentation simply means:

> **Add the retrieved knowledge to the input given to the LLM.**

Your code first creates:

```python id="63wqlz"
context = "\n\n".join(
    [doc.page_content for doc in docs]
)
```

So:

```text id="u4ah6k"
Retrieved Chunk 1
       +
Retrieved Chunk 2
       +
Retrieved Chunk 3
       ↓
     CONTEXT
```

---

# 13. Then you construct the prompt

Your code builds:

```python id="6mp93h"
prompt = f"""Use the following HR policy context to answer the question.

Context:
{context}

Question: {question}

Answer:"""
```

Now Claude receives:

```text id="xdzh1i"
Instruction
    +
Retrieved Policy Context
    +
Employee Question
```

That is augmentation.

---

# 14. Before vs after augmentation

Before augmentation:

```text id="ulcq0e"
What is the privilege leave policy?
```

After augmentation:

```text id="m2nv35"
Use the following HR policy context
to answer the question.

Context:

[Relevant policy chunk]

[Relevant policy chunk]

[Relevant policy chunk]

Question:

What is the privilege leave policy?

Answer:
```

See the difference?

The model now has relevant external information available in its prompt.

---

# 15. G = Generation

Finally:

# **G — Generation**

Generation means:

> **Use the LLM to produce the final natural-language answer.**

Your code:

```python id="4oy71c"
hr_rag_query = rag_llm.invoke(prompt)
```

Conceptually:

```text id="z5rzre"
Retrieved Context
       +
Question
       ↓
Prompt
       ↓
ChatBedrock
       ↓
Amazon Bedrock
       ↓
Claude Haiku 4.5
       ↓
Generated Answer
```

Then:

```python id="n6c8zw"
return hr_rag_query.content
```

returns the generated text.

---

# 16. Your actual RAG code

This small code block is the heart of your RAG implementation:

```python id="h7m10d"
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

return hr_rag_query.content
```

Map it directly:

```text id="j28wga"
similarity_search()
        ↓
R — RETRIEVE


join(page_content)
+
construct prompt
        ↓
A — AUGMENT


invoke(prompt)
        ↓
G — GENERATE
```

If you understand this code, you understand the core RAG implementation of your project.

---

# 17. Who does what?

This is critical.

```text id="4r3ghn"
Titan
  ↓
Creates embeddings


FAISS
  ↓
Retrieves relevant chunks


Python
  ↓
Combines retrieved context
with the user's question


Claude
  ↓
Generates the final answer
```

Or:

| Component | Responsibility |
|---|---|
| Titan | Embeddings |
| FAISS | Retrieval |
| Python | Augmentation/orchestration |
| Claude | Generation |
| Bedrock | Managed model access |
| Streamlit | User interface |

Do not mix these roles.

---

# 18. Does Claude search FAISS?

**No.**

Your application does this:

```text id="e53dxq"
Python
  ↓
FAISS Search
  ↓
Retrieved Chunks
  ↓
Python builds prompt
  ↓
Claude
```

Claude receives the resulting prompt.

Claude itself is not executing:

```python id="7ks0y2"
index.similarity_search(...)
```

Your Python application does that.

---

# 19. Does FAISS generate the answer?

**No.**

FAISS returns relevant information.

```text id="4pxyuo"
FAISS
 ↓
Relevant chunks
```

Claude generates:

```text id="kyz89m"
Relevant chunks + question
          ↓
Claude
          ↓
Natural-language answer
```

Think:

> **FAISS finds. Claude writes.**

That's a very simple memory trick.

---

# 20. Does Titan generate the answer?

Again:

**No.**

Titan's role is:

```text id="f1ph5a"
Text
 ↓
Embedding Vector
```

Claude's role is:

```text id="2f3t2n"
Context + Question
 ↓
Natural-Language Answer
```

Memory trick:

> **Titan represents meaning. FAISS finds similarity. Claude generates language.**

---

# 21. Why chunk the document before RAG?

Imagine your complete HR policy is a large document.

Employee asks one small question:

> “What is the maternity leave policy?”

Sending an entire large policy every time can include lots of irrelevant material.

Instead:

```text id="sf1fjv"
Complete Policy
       ↓
Chunk 1
Chunk 2
Chunk 3
Chunk 4
...
Chunk N
```

Then retrieval selects relevant portions:

```text id="t5z3nf"
Question
   ↓
FAISS
   ↓
Chunk 7
Chunk 8
Chunk 12
```

Only those are used as context.

This is one reason chunking is central to RAG.

We'll study it properly in File 09.

---

# 22. What do embeddings solve?

Computers need a representation that allows semantic similarity search.

Conceptually:

```text id="q3etcb"
"Privilege leave can be carried forward"

             ↓

       Titan Embeddings

             ↓

      Numerical Vector
```

A question is also represented for retrieval:

```text id="x1cd6k"
"Can I move unused PL to next year?"

             ↓

        Embedding/Search

             ↓

      Numerical representation
```

FAISS can then find similar vectors.

So embeddings make semantic retrieval possible.

---

# 23. Why is RAG useful for this project?

For this project, RAG gives you several useful properties.

### External knowledge

The HR policy exists outside the model.

```text id="vdpdd8"
HR Policy
   ↓
RAG
   ↓
Claude
```

### More grounded responses

Claude receives relevant policy context before generating.

### No need to fine-tune for every policy update

Conceptually, changing the knowledge source/index is different from retraining the model.

### Targeted context

Only relevant chunks are retrieved rather than blindly supplying the whole document.

---

# 24. But RAG does NOT guarantee correctness

This is a very important interview point.

Don't say:

> **“RAG eliminates hallucinations.”**

That's too strong.

RAG can still fail.

For example:

```text id="yyx4qu"
Bad document extraction
        ↓
Bad chunks
        ↓
Poor embeddings/retrieval
        ↓
Wrong chunks retrieved
        ↓
Weak context
        ↓
Poor answer
```

Or:

```text id="lqhnsj"
Good retrieval
     ↓
Model still interprets
context incorrectly
     ↓
Wrong answer
```

So:

> **RAG improves grounding by providing external context, but retrieval and generation still need evaluation.**

---

# 25. Garbage in → garbage out

Suppose the HR policy is outdated.

Even perfect retrieval could retrieve:

```text id="k21j67"
OUTDATED POLICY
```

Claude may then produce an answer based on outdated information.

So RAG quality depends on:

```text id="os03ks"
Source Quality
      ↓
Document Extraction
      ↓
Chunking
      ↓
Embeddings
      ↓
Retrieval
      ↓
Prompt
      ↓
LLM Generation
      ↓
Final Answer
```

This is why RAG is a **system**, not simply an LLM call.

---

# 26. Your current RAG is manual/custom RAG

This is an important project distinction.

You are **not using Amazon Bedrock Knowledge Bases** in this application.

Instead, your Python code explicitly performs:

```text id="eqdhj3"
Document loading
      ↓
Chunking
      ↓
Embedding
      ↓
FAISS indexing
      ↓
Similarity retrieval
      ↓
Context construction
      ↓
Prompt construction
      ↓
Claude invocation
```

The project analysis specifically identifies this as a manual RAG workflow. :chatgpt-content-reference{index="1"}

This is useful in interviews because you can show exactly where each RAG stage occurs.

---

# 27. Your RAG is NOT Agentic RAG

Another important distinction.

Your current application doesn't have an agent deciding:

```text id="a92y3h"
Should I search?
Which tool should I use?
Should I call another agent?
Should I retry?
Should I search the web?
```

Instead, the workflow is fixed:

```text id="1g40tc"
Question
 ↓
FAISS
 ↓
Top 3
 ↓
Prompt
 ↓
Claude
 ↓
Answer
```

So this is:

> **A deterministic/custom RAG pipeline**

not an agentic AI workflow.

---

# 28. Your RAG does not currently rerank

Your current flow is:

```text id="vy1txj"
Question
 ↓
FAISS
 ↓
Top 3
 ↓
Claude
```

There is no additional implemented stage like:

```text id="v1zwhr"
FAISS candidates
       ↓
Reranking model
       ↓
Best candidates
```

So don't claim reranking.

It could be a future improvement if evaluation shows a need.

---

# 29. No hybrid search in current implementation

Your project uses FAISS semantic/vector retrieval.

It doesn't currently implement a combined approach like:

```text id="0ftj7u"
Semantic Vector Search
          +
Keyword Search
          ↓
Hybrid Results
```

Again, that's something you could evaluate later—not a current feature.

---

# 30. No citations shown to the employee

Your retrieved `Document` objects may contain useful content/metadata, but your response function ultimately returns:

```python id="2ynkhg"
hr_rag_query.content
```

So the user sees the generated answer.

The current application does not surface evidence like:

```text id="ynx8nb"
Answer: ...

Source:
Leave Policy — Page 4
```

as a proper citation feature.

That's an important production improvement.

---

# 31. RAG vs direct LLM

### Direct LLM

```text id="6f4c1w"
Question
   ↓
Claude
   ↓
Answer
```

Claude relies primarily on what is already represented by the model plus the supplied question.

### Your RAG application

```text id="a77gqi"
Question
   ↓
Retrieve HR Policy Information
   ↓
Question + Policy Context
   ↓
Claude
   ↓
Answer
```

The key difference is:

> **External knowledge retrieval before generation.**

---

# 32. RAG vs fine-tuning

Another common interview question.

### RAG

```text id="un3a1k"
External Documents
       ↓
Retrieve at runtime
       ↓
Add to prompt
       ↓
Existing LLM
```

### Fine-tuning

Conceptually:

```text id="4x1gsh"
Training Examples
       ↓
Training Process
       ↓
Model behavior/parameters adapted
```

For your HR policy project, the policy knowledge is being retrieved at runtime.

You did not fine-tune Claude on the Leave Policy PDF.

---

# 33. What happens if retrieval is wrong?

Suppose the employee asks:

```text id="pmuq26"
"What is the maternity leave policy?"
```

But FAISS retrieves unrelated chunks about:

```text id="yqohqp"
Casual Leave
+
Privilege Leave
+
Holiday Rules
```

Then Claude receives poor context.

```text id="gy7gpf"
Wrong Retrieval
      ↓
Wrong Context
      ↓
Claude
      ↓
Potentially Poor Answer
```

This teaches an important RAG principle:

> **Generation quality is heavily dependent on retrieval quality.**

A powerful LLM cannot magically repair every retrieval failure.

---

# 34. What if the answer isn't in the document?

This is another critical scenario.

Suppose someone asks:

> “What is the company's work-from-home reimbursement policy?”

but the Leave Policy PDF contains no such information.

The ideal system should recognize that the available evidence doesn't support an answer.

Your current prompt says:

```text id="6j64pk"
Use the following HR policy context
to answer the question.
```

It doesn't implement a strong explicit fallback instruction such as:

```text id="dplf6e"
If the answer is not available in the supplied context,
state that the policy information is not available.
```

That is one area you could improve.

---

# 35. Production RAG thinking

Your current pipeline is:

```text id="dmnszh"
PDF
 ↓
Chunk
 ↓
Titan
 ↓
FAISS
 ↓
Top 3
 ↓
Prompt
 ↓
Claude
```

A more mature RAG system might eventually consider things such as:

```text id="7rd4j4"
Controlled document ingestion
        ↓
Document versioning
        ↓
Improved chunking
        ↓
Persistent/shared index
        ↓
Metadata filtering
        ↓
Retrieval evaluation
        ↓
Optional reranking
        ↓
Grounded prompt
        ↓
LLM
        ↓
Citations
        ↓
Quality monitoring
```

But remember:

> **These are possible production improvements, not features currently implemented in your project.**

---

# 36. RAG in one sentence

A strong simple definition is:

> **“RAG is a technique where I retrieve relevant information from an external knowledge source, add that information to the user's question as context, and then ask the LLM to generate an answer using that context.”**

Now make it project-specific:

> **“In my HR Q&A project, FAISS retrieves the top three relevant HR policy chunks, my Python code adds those chunks to the employee's question, and Claude Haiku 4.5 generates the final answer through Amazon Bedrock.”**

That's an excellent explanation.

---

# 37. Your complete RAG mental model

```text id="qg1n0v"
               KNOWLEDGE PREPARATION

HR Policy PDF
      ↓
PyPDFLoader
      ↓
Text
      ↓
Chunking
      ↓
Titan Embeddings
      ↓
FAISS Index


                    RAG

Employee Question
      │
      ▼
┌─────────────────┐
│   RETRIEVAL     │
│                 │
│ FAISS → Top 3   │
└────────┬────────┘
         ↓
┌─────────────────┐
│  AUGMENTATION   │
│                 │
│ Context         │
│    +            │
│ Question        │
└────────┬────────┘
         ↓
┌─────────────────┐
│   GENERATION    │
│                 │
│ Claude Haiku    │
│ via Bedrock     │
└────────┬────────┘
         ↓
      Answer
```

---

# Interview Questions & Answers — `07-RAG-Fundamentals-in-This-Project.md`

## Q1. What is RAG?

### Word-to-word interview answer

> “RAG stands for Retrieval-Augmented Generation. Instead of sending only the user's question to an LLM, the application first retrieves relevant information from an external knowledge source. It then adds that retrieved information to the user's question as context and sends the combined prompt to the LLM for generation. In my project, FAISS handles retrieval, my Python code performs the augmentation, and Claude handles generation.”

---

## Q2. Why did you use RAG in your HR Q&A application?

### Word-to-word interview answer

> “I used RAG because the answers should be grounded in the specific HR Leave Policy rather than relying only on the model's general knowledge. RAG allows me to retrieve relevant policy sections at question time and provide them to Claude as context before it generates the answer.”

---

## Q3. Explain RAG using your actual project.

### Word-to-word interview answer

> “When an employee asks an HR policy question, my application performs a similarity search against the FAISS index and retrieves the top three relevant policy chunks. My Python code combines those chunks into context and adds the employee's question to construct a prompt. That prompt is sent to Claude Haiku 4.5 through Amazon Bedrock, and Claude generates the final answer. So FAISS performs retrieval, Python performs augmentation, and Claude performs generation.”

---

## Q4. Where does retrieval happen in your code?

### Word-to-word interview answer

> “Retrieval happens when I call `index.similarity_search(question, k=3)`. FAISS searches the vector index using the user's question and returns the top three relevant document chunks.”

---

## Q5. Where does augmentation happen?

### Word-to-word interview answer

> “After retrieval, I extract the `page_content` from the returned documents and join those chunks into a context string. I then construct a prompt containing that context together with the user's question. That is the augmentation stage.”

---

## Q6. Where does generation happen?

### Word-to-word interview answer

> “Generation happens when my backend calls `rag_llm.invoke(prompt)`. The augmented prompt is sent to Claude Haiku 4.5 through Amazon Bedrock, and Claude generates the final natural-language answer.”

---

## Q7. Why don't you send the question directly to Claude?

### Word-to-word interview answer

> “Because I want the answer to use the specific HR policy as its knowledge source. If I send only the question, the model doesn't automatically have that policy document as application context. With RAG, I retrieve relevant policy information first and include it in the prompt.”

---

## Q8. Is RAG the same as fine-tuning?

### Word-to-word interview answer

> “No. In RAG, the knowledge remains external to the model and relevant information is retrieved at runtime and added to the prompt. Fine-tuning involves adapting model behavior through a training process. In this project, I did not fine-tune Claude on the HR policy; I retrieve policy information at runtime.”

---

## Q9. Does RAG eliminate hallucinations?

### Word-to-word interview answer

> “No. I would not say that RAG eliminates hallucinations. RAG improves grounding because the model receives relevant external context, but the system can still fail if the wrong chunks are retrieved, the source data is outdated, the prompt is weak or the model interprets the context incorrectly. That's why RAG systems still require evaluation.”

---

## Q10. What is the role of embeddings in RAG?

### Word-to-word interview answer

> “Embeddings represent text numerically in a way that supports semantic similarity. In my project, Titan generates embeddings for the HR policy chunks. FAISS indexes those vectors and uses them to help retrieve policy chunks that are semantically relevant to the employee's question.”

---

## Q11. What is FAISS's role in RAG?

### Word-to-word interview answer

> “FAISS is the retrieval component in my RAG pipeline. It stores and searches the vector index created from the HR policy chunks. When the employee asks a question, I use FAISS similarity search with k equal to three to retrieve the relevant chunks that become context for Claude.”

---

## Q12. What is Claude's role in RAG?

### Word-to-word interview answer

> “Claude is the generation component. It doesn't search the FAISS index in my implementation. My Python application performs retrieval first, constructs a prompt containing the retrieved policy context and employee question, and then sends that prompt to Claude for generation.”

---

## Q13. What is Titan's role in RAG?

### Word-to-word interview answer

> “Titan is the embedding model in my project. During knowledge preparation, it converts HR policy chunks into vector representations that can be indexed and searched through FAISS. Titan doesn't generate the final HR answer; Claude does that.”

---

## Q14. Is your project using Bedrock Knowledge Bases?

### Word-to-word interview answer

> “No. This project implements a custom RAG pipeline. My Python code explicitly handles document loading, chunking, Titan embeddings, FAISS indexing, similarity retrieval, context construction and Claude invocation. Bedrock Knowledge Bases is not part of the current implementation.”

---

## Q15. What happens if FAISS retrieves the wrong chunks?

### Word-to-word interview answer

> “If FAISS retrieves irrelevant chunks, Claude receives poor context and the final answer quality can decrease. This is why retrieval quality is a critical part of a RAG system. I would evaluate retrieval using representative HR questions and inspect whether the expected policy sections appear in the retrieved results.”

---

## Q16. Why do you retrieve three chunks?

### Word-to-word interview answer

> “The current project uses `k=3`, so FAISS returns three relevant chunks. That is a configuration choice in this proof of concept rather than a universal best value. For production, I would evaluate different retrieval settings against a representative question set and choose them based on retrieval and answer quality.”

---

## Q17. Is your RAG system agentic?

### Word-to-word interview answer

> “No. The current project uses a fixed RAG pipeline. Every valid question follows the same basic path: FAISS retrieval, context construction and Claude generation. There is no agent deciding which tools to call or dynamically planning the workflow.”

---

## Q18. What happens if the answer isn't in the HR policy?

### Word-to-word interview answer

> “Ideally, the application should tell the user that the available policy context doesn't contain enough information rather than inventing an answer. The current prompt provides the HR context to Claude, but it doesn't implement a strong explicit fallback rule. That's one improvement I would make for a production version.”

---

## Q19. How would you improve this RAG pipeline?

### Word-to-word interview answer

> “I would first improve it based on evaluation results. Potential improvements include controlled and versioned document ingestion, a shared persistent index, better grounding instructions, source citations, metadata-aware retrieval, retrieval evaluation and, if justified by the results, techniques such as reranking. I would not add those components unless the quality or production requirements showed a need for them.”

---

## Q20. Explain RAG in 30 seconds using your project.

### Word-to-word interview answer

> “RAG means Retrieval-Augmented Generation. In my project, when an employee asks a question, FAISS retrieves the top three relevant chunks from the HR policy. My Python code combines those chunks with the employee's question to create an augmented prompt. I then send that prompt to Claude Haiku 4.5 through Amazon Bedrock, and Claude generates the final answer. So the flow is retrieve with FAISS, augment with policy context, and generate with Claude.”

---

# Important interview traps

### “Claude searches your HR document, right?”

> **No. My application searches FAISS first and then provides the retrieved information to Claude.**

### “Titan answers the employee's question?”

> **No. Titan creates embeddings; Claude generates the answer.**

### “FAISS is your LLM?”

> **No. FAISS performs vector retrieval; Claude is the generation model.**

### “RAG means you trained Claude on your PDF?”

> **No. The policy remains external knowledge and is retrieved at runtime.**

### “RAG guarantees no hallucination?”

> **No. RAG improves grounding, but retrieval and generation can still fail.**

### “You're using Bedrock Knowledge Bases?”

> **No. This project implements the RAG stages explicitly using Titan, FAISS, Python and Claude.**

---

# Five questions to master first

Focus especially on:

**Q1 — What is RAG?**

**Q2 — Why did you use RAG?**

**Q3 — Explain RAG using your project.**

**Q4–Q6 — Show retrieval, augmentation and generation in your code.**

**Q9 — Does RAG eliminate hallucinations?**

And remember only this if everything else feels complicated:

```text id="fb7tnk"
                 RAG

Question
   ↓
FAISS
   ↓
Relevant HR Policy Chunks
   │
   │ RETRIEVE
   ▼
Context + Question
   │
   │ AUGMENT
   ▼
Claude
   │
   │ GENERATE
   ▼
Answer
```

### The one sentence you should be able to say without memorizing

> **“In my project, RAG means FAISS retrieves relevant information from the HR policy, my Python code adds that information to the employee's question, and Claude generates the answer using that retrieved context.”**

If that sentence makes complete sense to you, you understand the **core idea of RAG in your project**.