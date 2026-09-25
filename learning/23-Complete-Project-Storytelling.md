# `23-Complete-Project-Storytelling.md`

## NovaMindAI HR Q&A RAG — Complete Interview Storytelling

Yes. For this file, we should **not only learn the theory of storytelling**. We should prepare the **actual words you can speak in an interview**.

The goal is that when an interviewer says:

> **“Tell me about your project.”**

you should not start randomly listing AWS services or code. You should tell a structured engineering story:

```text
Problem
   ↓
Solution
   ↓
Architecture
   ↓
End-to-End Flow
   ↓
Your Implementation
   ↓
Design Decisions
   ↓
Challenges / Limitations
   ↓
Production Improvements
```

Your current project is a small HR leave-policy RAG proof of concept: a Streamlit application loads a fixed HR policy PDF, splits it, uses Titan embeddings through Bedrock, builds an in-memory FAISS index, retrieves the top three relevant chunks, constructs the context manually, and invokes Claude through Bedrock. :chatgpt-content-reference{index="0"}

---

# 1. First rule: don't explain architecture immediately

A common weak answer sounds like:

> “I used Python, Streamlit, LangChain, Bedrock, Titan, FAISS and Claude...”

The interviewer still doesn't know:

**Why did you build it?**

Instead use:

> **Problem → Solution → Technical implementation.**

For example:

> “I built NovaMindAI HR Q&A to solve the problem of employees manually searching through HR leave-policy documents. Instead of asking employees to read the complete policy, I built a RAG-based application where they can ask a natural-language question and receive an answer grounded in relevant sections of the policy.”

Now the interviewer understands **why the technology exists**.

---

# 2. Your master storytelling structure

Memorize the structure, not every sentence:

```text
1. PROJECT NAME
        ↓
2. BUSINESS PROBLEM
        ↓
3. SOLUTION
        ↓
4. ARCHITECTURE
        ↓
5. INDEXING FLOW
        ↓
6. QUERY FLOW
        ↓
7. TECHNOLOGY DECISIONS
        ↓
8. MY IMPLEMENTATION
        ↓
9. LIMITATIONS
        ↓
10. PRODUCTION V2
```

If you understand these ten sections, you can answer almost any project-introduction question.

---

# 3. Interview Question 1 — “Tell me about your project.”

## Word-to-word answer — approximately 1 minute

> **“One of my projects is NovaMindAI HR Q&A. It is a proof-of-concept RAG application that allows employees to ask natural-language questions against an HR leave-policy document.**
>
> **The problem I wanted to solve was that employees may need to manually search through policy documents to find information such as leave eligibility or carry-forward rules. So I built a RAG pipeline that retrieves relevant policy content before generating an answer.**
>
> **The application is built in Python with Streamlit. I load the HR policy using PyPDFLoader and split it using RecursiveCharacterTextSplitter with a chunk size of 1000 and overlap of 100. I use Amazon Titan embeddings through Bedrock to create vector representations and FAISS as the in-memory vector index.**
>
> **When an employee asks a question, the application performs similarity search with `k=3`, retrieves the top three relevant chunks, joins their text into context and manually constructs a prompt containing the policy context and the employee's question. I then invoke Claude Haiku 4.5 through Amazon Bedrock to generate the final response.**
>
> **I used LangChain components for document loading, splitting, Bedrock integrations and FAISS, but the actual retrieve, augment and generate flow is explicitly orchestrated in my Python backend.”**

Stop there.

Don't immediately talk for five minutes.

Let the interviewer choose the next area.

---

# 4. Why this answer works

Notice the order:

```text
NovaMindAI
   ↓
HR problem
   ↓
RAG solution
   ↓
Python + Streamlit
   ↓
PDF processing
   ↓
Chunking
   ↓
Titan
   ↓
FAISS
   ↓
Top 3 retrieval
   ↓
Prompt
   ↓
Claude
```

You haven't just listed technologies.

You've explained **why each technology exists**.

---

# 5. Interview Question 2 — “Can you explain the architecture?”

## Word-to-word answer

> **“Sure. I divide the architecture into two main flows: knowledge preparation and query-time RAG.**
>
> **In the knowledge-preparation flow, the application loads a fixed HR leave-policy PDF using PyPDFLoader. I split the document using RecursiveCharacterTextSplitter with a chunk size of 1000 and an overlap of 100. The chunks are then converted into embeddings using Amazon Titan through Bedrock, and those embeddings are indexed using FAISS.**
>
> **The FAISS index is currently in memory and stored in Streamlit session state so it can be reused across reruns within that session.**
>
> **In the query flow, the employee enters a question through Streamlit. The application performs FAISS similarity search with `k=3` and retrieves the top three relevant policy chunks. My Python backend extracts their `page_content`, joins them into a context string and constructs a prompt containing that context and the employee's question.**
>
> **That prompt is sent through ChatBedrock to Claude Haiku 4.5, and the generated response content is returned to Streamlit and displayed to the employee.”**

That is your actual architecture story.

---

# 6. Interview Question 3 — “Walk me through what happens when a user asks a question.”

## Word-to-word answer

> **“When the user opens the application, Streamlit first checks whether `vector_index` already exists in session state. If it doesn't, the application calls my `hr_index()` function.**
>
> **That function loads the HR policy PDF, splits it into chunks, configures Titan embeddings through Bedrock and uses `FAISS.from_documents()` to create the vector index. The resulting index is stored in Streamlit session state.**
>
> **When the employee submits a question, the frontend passes the existing index and the question to my `hr_rag_response()` function.**
>
> **Inside that function, I call `similarity_search(question, k=3)` to retrieve the top three relevant policy chunks. I extract the `page_content` from those documents and join it into one context string.**
>
> **Then I construct a prompt containing an instruction, the retrieved HR policy context and the current question. Finally, I invoke Claude through ChatBedrock, extract the returned `.content`, and send that answer back to Streamlit.”**

The inspected project analysis confirms this manual retrieve → context construction → prompt → Claude flow. :chatgpt-content-reference{index="1"}

---

# 7. Interview Question 4 — “Where exactly is RAG in this project?”

This is an excellent question.

## Word-to-word answer

> **“RAG in my project has three explicit stages.**
>
> **Retrieval is performed by FAISS. I use the employee's question to search the vector index and retrieve the top three relevant HR policy chunks.**
>
> **Augmentation happens in my Python code. I extract the retrieved chunk text, join it into context and combine that context with the employee's question in the prompt.**
>
> **Generation is performed by Claude through Amazon Bedrock. Claude receives the augmented prompt and generates the final natural-language answer.**
>
> **So in short: FAISS retrieves, my Python code augments, and Claude generates.”**

Excellent sentence to remember:

> **“FAISS retrieves, Python augments, Claude generates.”**

---

# 8. Interview Question 5 — “Why did you use RAG instead of directly asking Claude?”

## Word-to-word answer

> **“Because the HR leave policy is external domain-specific knowledge. I don't want to depend only on Claude's general model knowledge for company-policy questions.**
>
> **With RAG, I first retrieve relevant information from the actual policy document and provide that information to Claude as context at runtime. This improves grounding and also allows the knowledge source to remain external rather than fine-tuning the model on the policy.**
>
> **However, I would not claim that RAG completely eliminates hallucinations. Retrieval quality, prompt design and model behavior still need to be evaluated.”**

That final sentence makes your answer stronger.

---

# 9. Interview Question 6 — “Why did you use Titan and Claude together?”

## Word-to-word answer

> **“They solve two different problems in the pipeline. Amazon Titan is used as the embedding model. It converts the HR policy chunks and query into numerical representations that support semantic retrieval.**
>
> **FAISS uses those vector representations to find relevant policy chunks.**
>
> **Claude is then used for generation. It receives the retrieved policy text together with the employee's question and produces the final natural-language response.**
>
> **So my simple mental model is: Titan represents, FAISS retrieves and Claude generates.”**

Memorize:

> **Titan represents → FAISS retrieves → Claude generates.**

---

# 10. Interview Question 7 — “What exactly is LangChain doing?”

## Word-to-word answer

> **“I use LangChain as a component and integration layer rather than letting it hide the complete RAG flow.**
>
> **PyPDFLoader loads the policy document, RecursiveCharacterTextSplitter handles chunking, BedrockEmbeddings integrates with Titan through Bedrock, the FAISS integration handles vector indexing and retrieval, and ChatBedrock integrates with Claude.**
>
> **But my Python backend explicitly controls the workflow. I call similarity search, extract and join the retrieved content, construct the prompt and invoke the model myself.**
>
> **So LangChain provides reusable components and integrations, while my Python code orchestrates the RAG pipeline.”**

This is one of your strongest interview answers.

---

# 11. Interview Question 8 — “Why did you use FAISS?”

## Word-to-word answer

> **“I used FAISS because this project is a small proof of concept and I needed a lightweight way to perform vector similarity search over the HR policy chunks.**
>
> **Titan generates the embeddings, and FAISS indexes and searches those vector representations. When a user asks a question, I perform similarity search with `k=3` to retrieve the top three relevant policy chunks.**
>
> **For this PoC, an in-memory FAISS index keeps the architecture simple. For a larger production environment, I would evaluate a shared persistent vector architecture based on scalability, availability, filtering and operational requirements.”**

Notice you didn't say:

> “FAISS is best.”

You explained why it fits **this project**.

---

# 12. Interview Question 9 — “Why `chunk_size=1000` and `chunk_overlap=100`?”

## Word-to-word answer

> **“The current proof of concept uses RecursiveCharacterTextSplitter with a configured chunk size of 1000 and overlap of 100.**
>
> **The goal is to create retrieval units that are small enough for targeted search while retaining enough surrounding context. The overlap helps preserve information that may cross chunk boundaries.**
>
> **I don't claim that 1000 and 100 are universally optimal. For production, I would test different chunking configurations using representative HR questions and compare retrieval and final answer quality.”**

Very important:

Don't say:

> “1000 tokens.”

Your current splitter configuration is character-oriented/default length behavior, not explicitly token-based.

---

# 13. Interview Question 10 — “Why `k=3`?”

## Word-to-word answer

> **“The current PoC retrieves the top three chunks using `k=3`. The idea is to provide Claude with several relevant pieces of policy evidence without adding a very large amount of potentially noisy context.**
>
> **However, three is not a universal best value. If `k` is too small, I may miss important supporting information, while a very large `k` can introduce irrelevant context. I would tune it through retrieval evaluation rather than choosing it only by intuition.”**

---

# 14. Interview Question 11 — “What does Streamlit session state do?”

## Word-to-word answer

> **“I use Streamlit session state to keep the FAISS vector index available across reruns within a user's session.**
>
> **When the session starts, I check whether `vector_index` exists. If it doesn't, I build the index and store it in session state. Later interactions in the same session can reuse that index instead of rebuilding the policy embeddings every time.**
>
> **But I want to make an important distinction: this is session-level application state. It is not conversation memory and it is not durable shared vector storage.”**

That's an excellent interview distinction.

---

# 15. Interview Question 12 — “Does your chatbot have memory?”

## Word-to-word answer

> **“No, not conversation memory in the current implementation.**
>
> **The application keeps the FAISS index in Streamlit session state, but previous user questions and Claude answers are not explicitly added to future prompts. Each request uses the current employee question and the policy context retrieved for that question.**
>
> **So session state exists for index reuse, but conversational history is not implemented.”**

---

# 16. Interview Question 13 — “How do you reduce hallucination?”

## Word-to-word answer

> **“The main grounding mechanism is RAG. Instead of asking Claude to answer only from its general knowledge, I retrieve relevant HR policy chunks and include them in the prompt. I also use a low temperature of 0.1 to reduce output variability.**
>
> **However, I would not say hallucination is fully solved. My current prompt is relatively simple and doesn't have a strict abstention rule or user-facing citations.**
>
> **For production, I would strengthen the prompt so the model answers only from supplied evidence, explicitly says when the information is unavailable, and returns citations to the supporting policy sections. I would then evaluate this behavior using supported and unsupported questions.”**

This answer shows both implementation and engineering maturity.

---

# 17. Interview Question 14 — “What happens if the answer is wrong?”

## Word-to-word answer

> **“I would first separate retrieval failure from generation failure.**
>
> **My first step would be to inspect the chunks returned by FAISS. If the correct policy evidence was not retrieved, I would investigate the source document, PDF extraction, chunking strategy, embedding behavior, `k` value and retrieval configuration.**
>
> **If the correct evidence was retrieved but Claude still produced an incorrect answer, I would investigate the prompt, grounding instructions, model configuration and generation behavior.**
>
> **I don't immediately blame the LLM because a wrong RAG answer can originate earlier in the pipeline.”**

This is one of the best troubleshooting answers for your project.

---

# 18. Interview Question 15 — “What was the biggest design challenge?”

Because the source material does not document a verified personal “biggest challenge” you experienced, don't invent one.

Instead, frame it as a technical challenge:

> **“One important technical challenge in this type of RAG application is ensuring that the model receives the correct policy evidence. The final answer depends heavily on retrieval quality.**
>
> **That's why I separated the pipeline mentally into document processing, embeddings, retrieval and generation. If an answer is wrong, I can inspect each stage independently instead of treating the entire application as one black box.**
>
> **The current project is still a PoC, so systematic retrieval and answer evaluation is an area I would strengthen before production.”**

This stays grounded without inventing a personal incident.

---

# 19. Interview Question 16 — “What are the limitations of your current project?”

## Word-to-word answer

> **“The current application is a proof of concept, so there are several limitations I would not hide.**
>
> **The knowledge source is a fixed remote HR policy PDF. The FAISS index is in memory and session-oriented rather than a durable shared production index. There is no implemented authentication or role-based access control, no conversation memory, no user-facing citations, no automated policy-versioning pipeline and no systematic automated RAG evaluation.**
>
> **The prompt also doesn't have a strong explicit abstention rule when the answer isn't available in the retrieved context.**
>
> **These limitations are acceptable for demonstrating the RAG workflow, but I would address them before treating the system as a production HR platform.”**

These current-vs-not-present distinctions match the inspected project analysis. :chatgpt-content-reference{index="2"}

---

# 20. Interview Question 17 — “Is this production-ready?”

## Word-to-word answer

> **“I would describe the current implementation as a functional proof of concept rather than a production-ready HR platform.**
>
> **It demonstrates the complete RAG concept—document loading, chunking, embeddings, vector retrieval, prompt augmentation and Bedrock generation—but production would require stronger authentication, controlled policy ingestion and versioning, persistent shared retrieval infrastructure, citations, security controls, monitoring, error handling and systematic RAG evaluation.**
>
> **So I would clearly separate what I have implemented today from the production architecture I would design next.”**

Never pretend PoC = production.

That honesty makes the project story stronger, not weaker.

---

# 21. Interview Question 18 — “How would you make it production-ready?”

## Word-to-word answer

> **“I would first separate document ingestion from query serving. Approved HR policies would go through a controlled ingestion process where I validate the source, extract the content, chunk it, generate embeddings and update a versioned persistent shared index.**
>
> **The query application would then search that existing index instead of rebuilding the same policy for new sessions.**
>
> **I would add authentication and authorization, preserve metadata for citations, strengthen the grounding and abstention prompt, add proper exception handling and observability, and create a RAG evaluation dataset containing representative HR questions with expected supporting sections.**
>
> **I would then select infrastructure based on measured scale and requirements rather than adding services unnecessarily.”**

That final sentence is good system-design thinking.

---

# 22. Interview Question 19 — “How would you scale this application?”

## Word-to-word answer

> **“The first scalability issue I would address is repeated knowledge preparation. In the current PoC, the FAISS index is created in memory and stored in Streamlit session state. For larger usage, I would move indexing into a separate ingestion workflow and make the resulting vector index available through an appropriate shared persistent architecture.**
>
> **That allows multiple application instances or users to query already prepared knowledge rather than repeatedly embedding the same policy.**
>
> **I would then evaluate application concurrency, model latency, Bedrock quotas, caching where appropriate, availability and observability based on actual traffic requirements.”**

---

# 23. Interview Question 20 — “How would you evaluate this RAG system?”

## Word-to-word answer

> **“I would evaluate retrieval and generation separately.**
>
> **For retrieval, I would create representative HR questions with known supporting policy sections and check whether the expected evidence appears in the top retrieved results and at what rank.**
>
> **For generation, I would evaluate whether the answer is supported by the retrieved context, factually consistent with the policy, relevant to the question and able to abstain when the source doesn't contain enough information.**
>
> **I would also include unsupported and adversarial questions because a good RAG system should know when not to invent an answer.”**

---

# 24. Interview Question 21 — “What exactly did YOU implement?”

This question is especially important.

Don't answer with vague “we”.

## Word-to-word answer

> **“At the implementation level, the project code contains the complete manual RAG flow. The backend loads the policy through PyPDFLoader, configures RecursiveCharacterTextSplitter, integrates Titan embeddings through Bedrock, creates the FAISS index, performs top-three similarity retrieval, constructs the context and prompt and invokes Claude through ChatBedrock.**
>
> **The Streamlit frontend initializes and reuses the vector index through session state, collects the employee question, calls the backend RAG function and displays the generated answer.**
>
> **I can explain each of those stages independently because the pipeline is explicitly visible in the code rather than hidden behind a prebuilt end-to-end RAG chain.”**

Use this answer to describe the implementation. If an interviewer specifically asks what you personally authored versus adapted, answer according to what you actually did rather than claiming unsupported authorship.

---

# 25. Interview Question 22 — “Why didn't you use Bedrock Knowledge Bases?”

## Word-to-word answer

> **“For this project, I wanted to implement the RAG stages explicitly so I could control and understand document loading, chunking, embeddings, FAISS retrieval, context construction and model invocation.**
>
> **The current application therefore doesn't use Bedrock Knowledge Bases. It uses Titan embeddings and Claude through Bedrock, but retrieval is implemented using FAISS in my Python application.**
>
> **For another use case, I could evaluate Bedrock Knowledge Bases based on operational and product requirements, but it isn't part of this implementation.”**

This is especially useful because you have worked with both approaches.

---

# 26. Interview Question 23 — “Is this an Agentic AI project?”

## Word-to-word answer

> **“No. I would classify this project as a standard RAG application rather than an agentic AI system.**
>
> **The workflow is deterministic: load and index the document, retrieve relevant chunks for a question, construct the prompt and invoke Claude. There is no agent deciding which tools to use, no LangGraph workflow and no multi-agent routing.**
>
> **I prefer to describe the architecture accurately rather than label every LLM application as agentic AI.”**

Very strong answer.

---

# 27. Interview Question 24 — “What did you learn from this project?”

## Word-to-word answer

> **“The biggest technical learning for me was understanding that RAG is not just calling an LLM with a PDF. It is a pipeline where each stage affects the final answer.**
>
> **Document quality affects chunking, chunking affects embeddings, embeddings affect retrieval, retrieval determines the context and that context affects generation.**
>
> **I also learned to separate retrieval failures from generation failures and to distinguish a proof-of-concept architecture from a production architecture.**
>
> **That gave me a much better understanding of how to design, troubleshoot and improve RAG systems rather than treating them as a single black-box model call.”**

---

# 28. Your 30-second project story

Use this when HR or an interviewer asks for a quick summary:

> **“NovaMindAI HR Q&A is a RAG proof of concept that lets employees ask questions against an HR leave-policy document. I built the pipeline using Python, Streamlit and LangChain components. The policy is loaded and chunked, Titan through Amazon Bedrock generates embeddings, and FAISS provides vector retrieval. For each employee question, I retrieve the top three relevant chunks, build a context-grounded prompt and send it to Claude Haiku 4.5 through Bedrock. The current version is intentionally a PoC, with an in-memory FAISS index and no conversation memory or production authentication.”**

---

# 29. Your 1-minute project story

This should be your **main interview version**:

> **“One of my projects is NovaMindAI HR Q&A, a RAG-based proof of concept for answering employee questions from an HR leave-policy document.**
>
> **The problem is that employees may need to manually search policy documents for information such as leave eligibility or carry-forward rules. I wanted users to ask those questions in natural language while grounding the answers in the actual policy.**
>
> **I built the application using Python and Streamlit. PyPDFLoader loads the policy, and RecursiveCharacterTextSplitter creates chunks using a chunk size of 1000 and overlap of 100. I use Amazon Titan through Bedrock for embeddings and FAISS as the in-memory vector index.**
>
> **At query time, FAISS retrieves the top three relevant chunks. My Python backend joins those chunks into context, combines the context with the employee's question and invokes Claude Haiku 4.5 through Bedrock.**
>
> **LangChain provides the integrations, but I explicitly orchestrate the retrieve, augment and generate flow in Python. The current system is a PoC, and for production I would improve persistent indexing, security, citations, policy versioning, observability and RAG evaluation.”**

---

# 30. Your 3-minute deep-dive story

If the interviewer says:

> **“Explain it in detail.”**

Use this structure:

> **“Sure. The project is called NovaMindAI HR Q&A. The goal is to make an HR leave-policy document easier to query using natural language. Rather than asking employees to manually search a long policy, the application retrieves the relevant policy content and uses an LLM to produce a readable answer.**
>
> **I divide the architecture into two flows: indexing and query-time RAG.**
>
> **During indexing, PyPDFLoader loads the fixed remote HR leave-policy PDF. RecursiveCharacterTextSplitter splits the loaded documents with a chunk size of 1000 and overlap of 100. I configure Amazon Titan embeddings through LangChain's BedrockEmbeddings integration, and `FAISS.from_documents()` uses the chunks and embedding integration to build the in-memory vector index.**
>
> **On the frontend, Streamlit checks whether the vector index already exists in session state. If not, it calls the indexing function. Once created, the index can be reused across reruns in that session instead of rebuilding the policy embeddings for every question.**
>
> **At query time, the employee enters a question. My backend calls `similarity_search(question, k=3)` on the FAISS index. That returns the top three relevant document chunks. I extract their `page_content` and join them into a context string.**
>
> **I then manually construct the RAG prompt containing an instruction, the retrieved HR policy context and the employee's current question. For generation, I use Claude Haiku 4.5 through LangChain's ChatBedrock integration with a temperature of 0.1 and maximum output configuration of 3000 tokens. I invoke the model and return the generated content to Streamlit.**
>
> **I use LangChain as the component and integration layer, but the RAG orchestration is explicit in Python. There is no LangGraph, agent routing or Bedrock Knowledge Base in this project.**
>
> **I also treat the current version as a proof of concept rather than production-ready. The FAISS index is in memory and session-oriented, conversation memory isn't implemented, there is no authentication or user-facing citation flow, and policy ingestion isn't automatically versioned.**
>
> **For production, I would separate ingestion from query serving, introduce an appropriate shared persistent index, add controlled policy versioning, authentication and authorization, source citations, stronger grounding and abstention behavior, error handling, observability and systematic retrieval and answer evaluation.”**

Then stop.

Let the interviewer drill down.

---

# 31. How the interview should naturally continue

Your story should cause the interviewer to ask things like:

```text
Tell me about your project.
        ↓
Why RAG?
        ↓
How does RAG work?
        ↓
Why Titan?
        ↓
Why FAISS?
        ↓
How does similarity search work?
        ↓
Why chunk size 1000?
        ↓
Why k=3?
        ↓
What does LangChain do?
        ↓
How do you prevent hallucination?
        ↓
How do you evaluate RAG?
        ↓
What are the limitations?
        ↓
How would you make it production-ready?
```

This is good.

You don't need to explain all 24 learning files in the first answer.

Your opening answer should **create useful follow-up questions**.

---

# 32. Storytelling when you forget something

Don't panic and start inventing.

Suppose the interviewer asks:

> “Which exact FAISS distance metric are you using?”

A good response is:

> **“In this implementation, I use LangChain's FAISS similarity-search integration and I haven't explicitly configured a custom distance metric in my application code. I would verify the underlying configuration rather than claim a metric that I haven't explicitly set.”**

This is far better than guessing:

> “Cosine similarity.”

Interview confidence does not mean pretending to know everything.

---

# 33. What NOT to say about this project

Do not accidentally say:

```text
❌ “It is an enterprise HR platform.”

❌ “It is a multi-agent application.”

❌ “I used LangGraph.”

❌ “I used Bedrock Knowledge Bases.”

❌ “I use OpenSearch.”

❌ “FAISS is running as an AWS managed service.”

❌ “The application has conversation memory.”

❌ “The vector index is permanently shared.”

❌ “Claude reads the PDF directly.”

❌ “Titan generates the answers.”

❌ “RAG eliminates hallucinations.”

❌ “1000 means 1000 tokens.”

❌ “k=3 is the optimal value.”

❌ “The application is fully production-ready.”
```

The Codex analysis explicitly distinguishes the current implementation from several documented/future/unverified capabilities, so keeping these boundaries clear is part of telling the project accurately. :chatgpt-content-reference{index="3"}

---

# 34. Your strongest project sentences

You don't need to memorize the entire file.

Memorize these concepts:

> **“NovaMindAI HR Q&A is a RAG proof of concept for answering employee questions from an HR leave-policy document.”**

> **“Titan represents, FAISS retrieves and Claude generates.”**

> **“FAISS retrieves, my Python code augments and Claude generates.”**

> **“LangChain provides reusable components and integrations, while my Python backend explicitly orchestrates the RAG workflow.”**

> **“Streamlit session state reuses my FAISS index across reruns, but it is not conversation memory or durable shared storage.”**

> **“When an answer is wrong, I first determine whether it is a retrieval failure or a generation failure.”**

> **“I treat the current implementation as a PoC and clearly separate what is implemented today from what I would add for production.”**

---

# 35. Final interview storytelling formula

When the interviewer asks:

> **“Tell me about your project.”**

Think internally:

```text
WHY?
↓
What business problem?


WHAT?
↓
What did I build?


HOW?
↓
How does the architecture work?


WHY THESE TECHNOLOGIES?
↓
Titan / FAISS / Claude / LangChain


WHAT HAPPENS AT RUNTIME?
↓
Question → Retrieve → Augment → Generate


WHAT ARE THE LIMITATIONS?
↓
PoC gaps


WHAT NEXT?
↓
Production V2
```

You don't have to speak every section immediately.

Start with the 1-minute answer.

Then let the interviewer choose where to go deeper.

---

# Final Word-to-Word Answer to Practice First

For your first practice, focus only on this:

> **“One of my projects is NovaMindAI HR Q&A, which is a RAG-based proof of concept for answering employee questions from an HR leave-policy document.**
>
> **The business problem was that employees may need to manually search policy documents to find information such as leave eligibility or carry-forward rules. So I built a RAG pipeline that retrieves relevant policy information before generating the answer.**
>
> **The application uses Python and Streamlit. I load the HR policy using PyPDFLoader and split it using RecursiveCharacterTextSplitter with a chunk size of 1000 and overlap of 100. I use Amazon Titan embeddings through Bedrock and build an in-memory FAISS vector index.**
>
> **When an employee asks a question, FAISS retrieves the top three relevant chunks. My Python backend joins those chunks into context and constructs a prompt containing the policy context and the employee's question. I then invoke Claude Haiku 4.5 through Amazon Bedrock to generate the final answer.**
>
> **I use LangChain components for document loading, splitting, Bedrock integration and FAISS, but the retrieve, augment and generate workflow is explicitly orchestrated in my Python code.**
>
> **The current implementation is a proof of concept. For production, I would improve the architecture with controlled policy ingestion and versioning, a shared persistent vector index, authentication and authorization, citations, stronger grounding, monitoring and systematic RAG evaluation.”**

**Don't try to memorize this mechanically.** Learn the sequence:

> **Problem → RAG solution → Indexing → Retrieval → Prompt → Claude → Current limitations → Production improvement.**

Once that sequence becomes natural, you can explain the project even if you forget the exact wording.