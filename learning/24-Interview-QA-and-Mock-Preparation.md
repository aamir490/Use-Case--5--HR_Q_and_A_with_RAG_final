# `24-Interview-QA-and-Mock-Preparation.md`

## NovaMindAI HR Q&A RAG — Final Interview Q&A + Mock Interview Preparation

This is the **final interview-preparation file** for this project.

File 23 taught you how to **tell the project story**. File 24 prepares you for what happens next:

> **Interviewer asks → You answer → Interviewer drills deeper → You defend your design → You troubleshoot scenarios → You explain limitations → You propose production improvements.**

The answers below are **word-to-word practice answers**, but the goal is to understand the logic rather than memorize blindly.

Your project's implemented core is a manual RAG pipeline: policy PDF → chunking → Titan embeddings → in-memory FAISS → top-3 retrieval → manual context/prompt construction → Claude → Streamlit response. :chatgpt-content-reference{index="0"}

---

# Part 1 — Opening Questions

## Q1. Tell me about your project.

### Word-to-word answer

> “One of my projects is NovaMindAI HR Q&A, which is a RAG-based proof of concept for answering employee questions from an HR leave-policy document.
>
> The problem I wanted to address was that employees may need to manually search policy documents for information such as leave eligibility or carry-forward rules.
>
> I built the application using Python and Streamlit. The HR policy is loaded using PyPDFLoader and divided into chunks using RecursiveCharacterTextSplitter with a chunk size of 1000 and overlap of 100.
>
> I use Amazon Titan through Bedrock for embeddings and FAISS as the in-memory vector index.
>
> When an employee asks a question, FAISS retrieves the top three relevant policy chunks. My Python backend joins those chunks into context, constructs an augmented prompt containing the context and question, and invokes Claude Haiku 4.5 through Amazon Bedrock.
>
> LangChain provides the document-processing, vector-store and Bedrock integrations, while my Python backend explicitly orchestrates the retrieve, augment and generate workflow.
>
> The current version is a proof of concept rather than a production-ready HR platform.”

---

# Q2. What business problem does your project solve?

### Answer

> “The project addresses the difficulty of manually searching an HR leave-policy document.
>
> Instead of requiring an employee to read through the complete policy, the application allows the employee to ask a natural-language question.
>
> The system retrieves relevant sections from the policy and provides those sections as context to Claude, which generates a readable response.
>
> The main goal is therefore to make policy information easier to access while grounding the response in the source document.”

---

# Q3. Why did you choose RAG?

### Answer

> “I chose RAG because the HR policy is external, domain-specific knowledge that should come from the policy document rather than only from the LLM's general knowledge.
>
> With RAG, I keep that knowledge outside the model. At query time, I retrieve relevant policy content and provide it to Claude as context.
>
> This also means I don't need to fine-tune Claude just to provide policy information.
>
> RAG improves grounding, although I don't claim that it completely eliminates hallucinations.”

---

# Part 2 — Architecture Questions

## Q4. Explain the architecture.

### Answer

> “I divide the architecture into two main flows: knowledge preparation and query-time RAG.
>
> During knowledge preparation, PyPDFLoader loads the fixed remote HR leave-policy PDF. RecursiveCharacterTextSplitter divides the document into chunks using a chunk size of 1000 and overlap of 100.
>
> Amazon Titan through Bedrock provides the embedding capability, and `FAISS.from_documents()` creates an in-memory vector index from those chunks.
>
> The FAISS index is stored in Streamlit session state for reuse within the session.
>
> During query time, the employee submits a question through Streamlit. The backend performs FAISS similarity search with `k=3`, retrieves the top three relevant chunks, extracts their `page_content` and joins them into context.
>
> My backend then constructs a prompt containing the retrieved context and employee question and invokes Claude Haiku 4.5 through ChatBedrock.
>
> Finally, the generated content is returned to Streamlit.”

---

# Q5. Explain the complete request flow.

### Answer

> “When the application starts, Streamlit checks whether `vector_index` exists in session state.
>
> If it doesn't exist, the backend calls `hr_index()`. That function loads the policy, splits it into chunks, configures Titan embeddings and builds the FAISS index.
>
> Once the index is stored in session state, the employee enters a question.
>
> The frontend passes the existing index and question to `hr_rag_response()`.
>
> That function performs similarity search with `k=3`, extracts the retrieved chunk text, joins the text into context and constructs the RAG prompt.
>
> It then invokes Claude through ChatBedrock and returns the generated `.content` to Streamlit.”

---

# Q6. Where exactly is RAG implemented?

### Answer

> “RAG is explicitly implemented in three stages.
>
> Retrieval happens when I call FAISS `similarity_search(question, k=3)`.
>
> Augmentation happens when my Python code takes the retrieved `page_content`, joins it into context and combines that context with the employee's question in the prompt.
>
> Generation happens when that augmented prompt is sent to Claude through ChatBedrock.
>
> So the simple explanation is: FAISS retrieves, Python augments and Claude generates.”

---

# Part 3 — Document Processing

## Q7. How do you load the HR policy?

### Answer

> “I use LangChain's PyPDFLoader. In the current backend, the loader points to a fixed remote UPL Leave Policy India PDF URL.
>
> Calling `.load()` loads and extracts the PDF content into document objects, which are then passed to the text splitter.”

---

# Q8. Why do you split the PDF?

### Answer

> “I split the document because retrieving an entire PDF for every question would provide poor retrieval granularity and unnecessary context.
>
> By creating smaller chunks, the retriever can return the sections that are more relevant to the employee's question.
>
> Chunking therefore directly affects retrieval quality and, indirectly, the final answer quality.”

---

# Q9. Why `chunk_size=1000` and `chunk_overlap=100`?

### Answer

> “The current PoC uses a configured chunk size of 1000 and overlap of 100.
>
> The chunk size creates smaller retrieval units, while the overlap helps preserve information that may cross chunk boundaries.
>
> I don't claim those values are universally optimal. For production, I would compare different chunking strategies against representative HR questions and measure retrieval and answer quality.”

---

# Q10. Is that 1000 tokens?

### Answer

> “No. I would not describe it as 1000 tokens. In my current RecursiveCharacterTextSplitter configuration, I haven't configured a token-based length function, so the safe description is a character-oriented chunk-size configuration.”

Excellent trap to remember.

---

# Part 4 — Embeddings

## Q11. What are embeddings?

### Answer

> “Embeddings are numerical vector representations of text designed to capture semantic relationships.
>
> In my project, HR policy chunks are converted into embeddings using Amazon Titan through Bedrock.
>
> At query time, the employee's question also needs a representation in the same embedding space so that the vector store can identify semantically related policy chunks.”

---

# Q12. Why do you use Titan?

### Answer

> “Titan is used for embeddings, not answer generation.
>
> It converts the HR policy chunks and query into vector representations that support semantic retrieval.
>
> FAISS then uses those representations for similarity search, while Claude has a separate role: generating the final natural-language answer.”

---

# Q13. What is the embedding dimension?

### Answer

> “I haven't manually configured the vector dimension in my application code, so I wouldn't invent a number in an interview. The code specifies `amazon.titan-embed-text-v1` as the embedding model. If the exact dimension were operationally important, I would verify it against the documentation for that exact model configuration.”

This answer is intentionally precise because the project's interview notes contain dimension claims that were not established by the inspected application code.

---

# Q14. Are embeddings stored in Bedrock?

### Answer

> “Not in my current architecture. Bedrock provides access to the Titan embedding model. The resulting vector representations are used to create my in-memory FAISS index.
>
> Bedrock isn't acting as my vector database.”

---

# Part 5 — FAISS

## Q15. What is FAISS?

### Answer

> “FAISS is the vector indexing and similarity-search technology used by this project.
>
> After the policy chunks are converted into embeddings, I create the FAISS vector index. At query time, I use that index to retrieve policy chunks that are semantically relevant to the employee's question.”

---

# Q16. Why did you choose FAISS?

### Answer

> “This project is a small proof of concept, so FAISS gives me a lightweight way to demonstrate vector retrieval without introducing a larger managed vector architecture.
>
> It keeps the RAG pipeline simple and visible.
>
> For production, I would evaluate the vector-store architecture based on persistence, scale, availability, filtering, security and operational requirements.”

---

# Q17. Why do you retrieve three chunks?

### Answer

> “The current configuration uses `k=3`, which means I retrieve the top three relevant chunks.
>
> The intention is to provide Claude with multiple relevant pieces of evidence without supplying too much potentially irrelevant context.
>
> I don't consider three universally optimal. I would tune `k` through retrieval evaluation.”

---

# Q18. Is FAISS an AWS service?

### Answer

> “No. FAISS is not an AWS managed service in my architecture. It runs as part of the Python application and the current index is in memory.”

---

# Part 6 — Prompt + Claude

## Q19. How do you construct the prompt?

### Answer

> “After retrieving the top three documents, I extract each document's `page_content` and join them into one context string.
>
> I then manually construct a prompt containing an instruction to use the HR policy context, the retrieved context itself and the employee's current question.
>
> That augmented prompt is sent to Claude.”

---

# Q20. What does Claude receive?

### Answer

> “Claude receives text containing the instruction, retrieved HR policy context and current employee question.
>
> Claude doesn't directly receive the raw PDF, FAISS index or embedding vectors.”

---

# Q21. Why Claude Haiku?

### Answer

> “In the current implementation, Claude Haiku 4.5 is configured as the generation model through Bedrock.
>
> Its role is to take the retrieved HR policy evidence and employee question and generate the natural-language response.
>
> I would evaluate model choice for production based on answer quality, latency, cost and the specific workload rather than assuming one model is always the best choice.”

---

# Q22. Why is temperature 0.1?

### Answer

> “This is policy Q&A, so I want relatively low output variability rather than highly creative responses.
>
> The current configuration therefore uses temperature 0.1.
>
> However, low temperature does not guarantee factual correctness or eliminate hallucinations. Retrieval and grounding still matter.”

---

# Q23. What does `max_tokens=3000` mean?

### Answer

> “It is the configured maximum output allowance for the model response. It doesn't mean every answer contains exactly 3000 tokens. The actual answer can be much shorter.”

---

# Part 7 — LangChain

## Q24. What is LangChain?

### Answer

> “LangChain is a framework and ecosystem that provides reusable components and integrations for LLM and RAG applications.
>
> In my project, I use PyPDFLoader, RecursiveCharacterTextSplitter, BedrockEmbeddings, the FAISS vector-store integration and ChatBedrock.”

---

# Q25. Does LangChain automatically perform your entire RAG workflow?

### Answer

> “No. LangChain provides the components and integrations, but my Python backend explicitly orchestrates the workflow.
>
> I perform similarity search, extract and join the retrieved content, construct the prompt and invoke Claude myself.”

---

# Q26. Are you using LangGraph or agents?

### Answer

> “No. This project is a standard RAG application, not an agentic AI system.
>
> There is no LangGraph workflow, agent routing or autonomous tool selection. The application follows a predetermined retrieve, augment and generate flow.”

---

# Part 8 — State and Memory

## Q27. Why do you use Streamlit session state?

### Answer

> “I use Streamlit session state to keep the FAISS index available across reruns within the same session.
>
> If `vector_index` doesn't exist, I build it. Once it exists, later interactions can reuse it instead of rebuilding all policy embeddings for every question.”

---

# Q28. Does your chatbot have conversation memory?

### Answer

> “No. Streamlit session state is being used to retain the vector index, but previous user questions and answers are not explicitly passed to Claude.
>
> Therefore, the current application doesn't implement conversational memory.”

---

# Q29. Is the FAISS index persistent?

### Answer

> “No. The current design uses an in-memory FAISS index stored in Streamlit session state for session-level reuse.
>
> It isn't a durable shared vector index.”

The project analysis likewise distinguishes the current in-memory design from persistent/shared storage and conversation memory, which are not implemented. :chatgpt-content-reference{index="1"}

---

# Part 9 — AWS Questions

## Q30. Which AWS service is actually important in this project?

### Answer

> “The main AWS service in the implemented RAG pipeline is Amazon Bedrock.
>
> I use Bedrock for two model capabilities: Amazon Titan for embeddings and Claude for answer generation.
>
> The rest of the core application includes Python, Streamlit, LangChain components and in-memory FAISS.”

---

# Q31. How does your application authenticate to AWS?

### Answer

> “The current code configures `credentials_profile_name='default'` for the Bedrock integrations, so it relies on the local default AWS profile.
>
> For a production AWS deployment, I would prefer workload identity through an appropriate IAM role rather than embedding or manually managing long-lived credentials in the application.”

---

# Q32. What IAM permissions would the application need?

### Answer

> “The application needs the permissions required to invoke the Bedrock models it actually uses.
>
> I would follow least privilege and grant only the model-invocation permissions and resources required by the workload rather than broad Bedrock or administrator access.”

---

# Part 10 — Security

## Q33. What are the security limitations?

### Answer

> “The current PoC doesn't implement user authentication or role-based authorization. It also accepts user input that becomes part of the LLM prompt, so prompt-injection behavior should be considered.
>
> For production HR usage, I would add authentication and authorization, least-privilege IAM, controlled policy ingestion, appropriate logging and privacy controls, stronger grounding rules and protection around sensitive information.”

---

# Q34. How would you protect HR data?

### Answer

> “I would first classify what HR data the application is allowed to process. I would enforce authentication and authorization, encrypt data in transit and at rest where storage is involved, use least-privilege IAM, control logging so sensitive data isn't unnecessarily exposed, and define appropriate retention policies.
>
> I would also distinguish public policy documents from employee-specific confidential information because those require different access controls.”

---

# Part 11 — Troubleshooting

## Q35. The user gets a wrong answer. What do you do?

### Answer

> “I would first determine whether it is a retrieval problem or a generation problem.
>
> I would inspect the chunks returned by FAISS. If the correct evidence isn't present, I would investigate document extraction, chunking, embeddings, retrieval settings and the `k` value.
>
> If the correct evidence is retrieved but Claude still produces the wrong answer, I would investigate context construction, prompt instructions and model behavior.
>
> This prevents me from assuming every RAG failure is an LLM failure.”

---

# Q36. Titan invocation fails. What do you check?

### Answer

> “I would check the AWS credentials profile, region configuration, Bedrock model access and IAM permissions first.
>
> I would then inspect the actual Bedrock error, confirm the configured model identifier and verify network access from the runtime environment.
>
> Since Titan is needed during index creation, a failure there prevents the FAISS index from being built correctly.”

---

# Q37. Claude invocation fails. What do you check?

### Answer

> “I would inspect the Bedrock error first, then verify AWS credentials, IAM permissions, region and model access.
>
> I would also validate the configured model identifier and request parameters.
>
> I would troubleshoot the actual failure message rather than changing multiple parts of the application blindly.”

---

# Q38. The application is very slow when a new user opens it. Why?

### Answer

> “One likely reason in the current architecture is index initialization.
>
> A new session without `vector_index` calls `hr_index()`, which loads the policy, splits it, generates embeddings and creates FAISS.
>
> That means knowledge preparation is coupled to session initialization. For production, I would separate ingestion from query serving and reuse a persistent shared index.”

---

# Q39. Retrieval is poor. What would you tune?

### Answer

> “I would not immediately change the LLM.
>
> I would evaluate the source document and extraction quality first, then chunk size, overlap and boundaries, embedding behavior, retrieval `k`, and whether metadata filtering or reranking is required.
>
> I would measure these changes against a representative retrieval dataset instead of tuning them only by intuition.”

---

# Part 12 — RAG Evaluation

## Q40. How would you test this RAG system?

### Answer

> “I would test the pipeline at multiple levels.
>
> I would test document loading and chunking, then create representative HR questions with known supporting policy sections to evaluate retrieval.
>
> For generation, I would check whether the answer is supported by the retrieved context, relevant to the question and consistent with the policy.
>
> I would also include unsupported questions to verify that the application can avoid inventing policy information.”

---

# Q41. What metrics would you use?

### Answer

> “I would separate retrieval metrics from generation quality.
>
> For retrieval, I would evaluate whether the expected supporting evidence appears in the top-k results and at what rank.
>
> For generation, I would evaluate groundedness or faithfulness to the supplied context, answer relevance and correctness against the policy.
>
> The exact metric set should match the business requirements and evaluation dataset rather than relying on one overall score.”

---

# Q42. How do you know your RAG is better than asking Claude directly?

### Answer

> “I would verify that experimentally rather than assume it.
>
> I would create an evaluation dataset of policy questions and compare a baseline model-only approach against the RAG approach using the same questions.
>
> I would measure whether answers are supported by the actual policy, whether required policy facts are correctly captured and whether unsupported questions are handled appropriately.”

---

# Part 13 — Cost and Scalability

## Q43. What are the main cost drivers?

### Answer

> “The main managed-model usage comes from Bedrock. Titan is used for embeddings during index creation, and Claude is invoked for answer generation.
>
> In the current architecture, repeated index creation across new sessions can unnecessarily repeat embedding work.
>
> Therefore, separating ingestion from query serving and avoiding re-embedding unchanged documents would be an important cost and latency improvement.”

---

# Q44. How would you scale the application?

### Answer

> “I would first separate indexing from query serving.
>
> The policy would be processed through a controlled ingestion workflow, and the resulting index would be made available through an appropriate persistent shared retrieval architecture.
>
> Application instances could then query already prepared knowledge rather than rebuilding it.
>
> After that I would evaluate concurrency, Bedrock quotas, latency, availability, caching where appropriate and observability based on measured traffic.”

---

# Part 14 — Limitations

## Q45. What are the biggest current limitations?

### Answer

> “The current implementation is intentionally a PoC.
>
> The policy source is a fixed remote PDF, the FAISS index is in memory and session-oriented, there is no conversation memory, no implemented authentication or RBAC, no user-facing citations, no automated policy-versioning pipeline, limited error handling and no systematic automated RAG evaluation.
>
> The current prompt also doesn't have a strong explicit abstention rule when the policy context is insufficient.”

These gaps align with the project's current-vs-not-present analysis. :chatgpt-content-reference{index="2"}

---

# Q46. Is your application production-ready?

### Answer

> “No. I would describe the current version as a functional proof of concept.
>
> It demonstrates the complete RAG pipeline, but production would require stronger security, controlled ingestion and policy versioning, shared persistent retrieval infrastructure, citations, error handling, monitoring and systematic evaluation.”

---

# Part 15 — Production Design

## Q47. How would you redesign it for production?

### Answer

> “I would separate the architecture into an ingestion pipeline and a query-serving pipeline.
>
> The ingestion side would accept approved HR policy documents, validate and version them, extract and chunk the content, generate embeddings and update an appropriate persistent shared vector index.
>
> The query side would authenticate the employee, retrieve relevant evidence from that shared index and send only the required evidence and question to the generation model.
>
> I would add authorization, source citations, stronger grounding and abstention behavior, observability, error handling and a systematic RAG evaluation pipeline.
>
> I would choose the actual AWS services based on requirements rather than adding services simply to make the architecture look complex.”

---

# Q48. Would you use OpenSearch in production?

### Answer

> “I would evaluate it rather than automatically choosing it.
>
> The current project uses FAISS. If production requirements include shared persistent retrieval, larger scale, metadata filtering, operational availability or search capabilities that justify a managed architecture, I would compare suitable options based on those requirements.
>
> OpenSearch is not part of the current implementation.”

---

# Q49. Would you use Bedrock Knowledge Bases?

### Answer

> “It would be an option to evaluate, but it isn't used in this project.
>
> This implementation intentionally exposes the RAG stages through PyPDFLoader, explicit chunking, Titan embeddings, FAISS retrieval and manual prompt construction.
>
> For production, I would compare a managed knowledge-base approach with a custom retrieval pipeline based on control, operational effort, retrieval requirements and cost.”

---

# Part 16 — Difficult Interview Questions

## Q50. Why should I believe the LLM's answer?

### Answer

> “I wouldn't ask the user to trust the LLM simply because it generated a confident response.
>
> In a production policy application, the answer should be grounded in approved policy evidence and ideally show the supporting source or citation.
>
> My current PoC retrieves policy evidence but doesn't yet expose user-facing citations. That's one of the improvements I would prioritize before production.”

---

# Q51. What if the policy does not contain the answer?

### Answer

> “The safest behavior is to explicitly say that the answer isn't available in the provided policy rather than invent information.
>
> My current prompt doesn't enforce that strongly enough. For production, I would add an explicit abstention rule and test it using unsupported questions.”

---

# Q52. Why not fine-tune Claude?

### Answer

> “The main requirement is to answer from changing external policy knowledge rather than change the model's fundamental behavior.
>
> RAG lets me keep policy information external and retrieve it at runtime. If a policy changes, I can update the knowledge pipeline rather than retraining a model simply to change policy facts.
>
> I would consider fine-tuning only if there were a separate demonstrated need that RAG and prompting didn't solve.”

---

# Q53. What if the HR policy changes tomorrow?

### Answer

> “The current PoC doesn't have an automated controlled policy-update pipeline.
>
> In production, I would version approved policy documents and tie the source version, chunking configuration, embedding model and vector index together. When an approved policy changes, the ingestion pipeline would process the new version and update the retrieval index in a controlled way.”

---

# Q54. What if you change the embedding model?

### Answer

> “I would rebuild the corresponding vector index using the new embedding model rather than assuming the old vectors remain compatible.
>
> I would also version the embedding model and index together and evaluate retrieval quality before switching production traffic.”

---

# Q55. Why isn't this Agentic AI?

### Answer

> “Because there is no autonomous decision-making or tool-routing layer.
>
> The application follows a predetermined pipeline: retrieve from FAISS, construct context and invoke Claude.
>
> There is no LangGraph, no agent selecting tools and no multi-agent workflow, so I describe it as RAG rather than Agentic AI.”

---

# Part 17 — “What Did You Do?” Questions

## Q56. What did you implement in the backend?

### Answer

> “The backend contains three main responsibilities.
>
> `hr_index()` handles document loading, chunking, embedding integration and FAISS index creation.
>
> `hr_llm()` configures the Claude model through ChatBedrock.
>
> `hr_rag_response()` performs top-three similarity retrieval, constructs the context and prompt, invokes Claude and returns the generated content.”

---

# Q57. What does the frontend do?

### Answer

> “The Streamlit frontend manages the user interaction. It initializes the vector index when needed, stores it in session state, accepts the employee's question, validates that the input isn't empty, passes the question and index to the backend and displays the returned answer.”

---

# Q58. Did you use REST APIs between frontend and backend?

### Answer

> “No. In the current implementation, the Streamlit frontend imports the backend Python module and calls its functions directly.
>
> There is no REST API, API Gateway or separate backend microservice between them.”

---

# Q59. Is it a microservices architecture?

### Answer

> “No. I would describe it as a small single-application Streamlit-based RAG proof of concept. I wouldn't call it a microservices architecture.”

---

# Q60. What would you improve first?

### Answer

> “I would prioritize correctness and knowledge lifecycle before adding unnecessary complexity.
>
> I would separate ingestion from query serving, introduce controlled policy versioning and shared persistent retrieval, strengthen grounding and abstention behavior, and add citations and RAG evaluation.
>
> For actual HR use, authentication and authorization would also be essential.”

---

# Part 18 — Mock Interview Round 1: Project

Now don't read the answers immediately.

Imagine I am the interviewer.

### Interviewer

> **“Tell me about NovaMindAI HR Q&A.”**

Your answer should follow:

```text id="0nlnkl"
Problem
↓
RAG Solution
↓
Document Processing
↓
Titan
↓
FAISS
↓
Prompt
↓
Claude
↓
PoC Boundary
```

### Strong target answer

> “NovaMindAI HR Q&A is a RAG-based proof of concept that allows employees to ask natural-language questions against an HR leave-policy document.
>
> The policy is loaded and divided into chunks, Amazon Titan through Bedrock creates embeddings and FAISS provides semantic vector retrieval.
>
> When the employee asks a question, I retrieve the top three relevant chunks, combine them into context and construct a prompt containing that context and the question. Claude Haiku 4.5 through Bedrock generates the final response.
>
> I use LangChain components for the integrations, while the RAG orchestration itself is explicit in Python.
>
> The current version is a PoC with an in-memory FAISS index, so I clearly separate it from the production architecture I would build next.”

---

# Part 19 — Mock Interview Round 2: Technical Drill-Down

### Interviewer

> “What happens internally after I ask, ‘Can I carry unused leave forward?’”

### Your target answer

> “The question is passed to my backend along with the FAISS index. The vector-store integration represents the query using the configured Titan embedding integration and performs similarity search against the indexed policy chunks.
>
> My current configuration retrieves the top three matching documents. I extract their `page_content`, join it into one context string and construct a prompt containing the policy context and your question.
>
> I then invoke Claude Haiku 4.5 through ChatBedrock, extract the generated response content and return it to Streamlit.”

---

# Part 20 — Mock Interview Round 3: Challenge

### Interviewer

> “Your answer is wrong. Claude is bad, right?”

### Your target answer

> “Not necessarily. In a RAG application, I would first identify where the failure occurred.
>
> I would inspect the top three chunks retrieved from FAISS. If the correct policy evidence wasn't retrieved, then the issue is upstream of Claude and I would investigate extraction, chunking, embeddings and retrieval.
>
> If the correct evidence was retrieved but the generated answer was still wrong, then I would investigate prompt construction and generation behavior.
>
> So I separate retrieval quality from generation quality before deciding which component is responsible.”

---

# Part 21 — Mock Interview Round 4: System Design

### Interviewer

> “Now 10,000 employees need to use it. What will you change?”

### Your target answer

> “The first architectural change I would make is separating knowledge ingestion from query serving.
>
> I wouldn't want each new Streamlit session to rebuild embeddings for the same HR policy.
>
> I would create a controlled ingestion workflow that processes approved policy versions and updates a shared persistent vector index. The query application would retrieve from that existing index.
>
> I would then address authentication and authorization, concurrency, availability, Bedrock quotas, citations, observability and RAG evaluation based on the actual workload.
>
> I would choose the infrastructure from those requirements rather than simply adding more AWS services.”

---

# Part 22 — Mock Interview Round 5: Security

### Interviewer

> “Would you deploy this as-is for confidential employee HR information?”

### Your target answer

> “No. The current version is a proof of concept and doesn't implement the security controls I would require for confidential employee data.
>
> Before using it for sensitive HR information, I would add authentication and authorization, least-privilege IAM, appropriate encryption and network controls, sensitive-data-aware logging and retention policies, and clearly separate general policy access from employee-specific records.
>
> I would also evaluate prompt injection and ensure that model responses cannot bypass authorization boundaries.”

---

# Part 23 — Mock Interview Round 6: Honesty Test

### Interviewer

> “So you've built a production enterprise HR AI platform?”

### Your target answer

> “I would describe the current implementation as a functional RAG proof of concept rather than a production enterprise HR platform.
>
> It implements the core document loading, chunking, embeddings, retrieval, prompt construction and generation workflow.
>
> Production capabilities such as authentication, shared persistent retrieval, controlled policy versioning, citations, monitoring and systematic evaluation would be the next engineering phase.”

That answer is much stronger than exaggerating.

---

# Part 24 — Rapid-Fire Interview Round

You should eventually be able to answer these in **one or two sentences**.

| Interviewer asks | Your short answer |
|---|---|
| What is RAG? | “Retrieve external evidence, augment the prompt with it, then generate an answer.” |
| Embedding model? | “Amazon Titan through Bedrock.” |
| Vector store? | “In-memory FAISS.” |
| Generation model? | “Claude Haiku 4.5 through Bedrock.” |
| Top-k? | “`k=3` in the current implementation.” |
| Chunk size? | “1000 with overlap 100 in the current splitter configuration.” |
| LangChain role? | “Reusable components and integrations; Python explicitly orchestrates RAG.” |
| LangGraph? | “Not used.” |
| Agents? | “Not used.” |
| Bedrock Knowledge Base? | “Not used.” |
| OpenSearch? | “Not used.” |
| Conversation memory? | “Not implemented.” |
| Persistent FAISS? | “Not in the current architecture.” |
| Frontend? | “Streamlit.” |
| API Gateway? | “Not used.” |
| Lambda? | “Not used.” |
| Microservices? | “No.” |
| Citations? | “Not surfaced to users currently.” |
| Production-ready? | “No; current version is a PoC.” |
| Main AWS service? | “Amazon Bedrock.” |

---

# Part 25 — The 10 Questions You MUST Master

If you cannot remember all 60 immediately, that's okay.

Start with these ten:

1. **Tell me about your project.**
2. **Explain the architecture.**
3. **Walk me through the request flow.**
4. **Where exactly is RAG?**
5. **Why RAG instead of directly using Claude?**
6. **Titan vs FAISS vs Claude?**
7. **What exactly does LangChain do?**
8. **How do you troubleshoot a wrong answer?**
9. **What are the current limitations?**
10. **How would you make it production-ready?**

If these ten become natural, many follow-up questions become much easier.

---

# Your Emergency Mental Map

If you become nervous in an interview, don't try to remember 60 answers.

Visualize:

```text id="xwlq5i"
                 NovaMindAI HR Q&A

                       PDF
                        ↓
                   PyPDFLoader
                        ↓
                    Chunking
                   1000 / 100
                        ↓
                      Titan
                        ↓
                     Vectors
                        ↓
                      FAISS
                        ↓
                  Vector Index
                        ↑
                        │
Employee Question ──────┘
        ↓
Similarity Search
      k = 3
        ↓
Top 3 Policy Chunks
        ↓
Join Context
        ↓
Context + Question
        ↓
Prompt
        ↓
Claude Haiku 4.5
        ↓
Answer
        ↓
Streamlit
```

Then remember:

> **Titan represents.**

> **FAISS retrieves.**

> **Python augments.**

> **Claude generates.**

> **Streamlit interacts.**

> **LangChain integrates.**

> **Bedrock provides managed model access.**

---

# Final Word-to-Word Answer

If the interviewer gives you only one opportunity to explain the project, use this:

> **“NovaMindAI HR Q&A is a RAG-based proof of concept that allows employees to ask natural-language questions against an HR leave-policy document.**
>
> **I built the application using Python, Streamlit and LangChain components. The policy is loaded using PyPDFLoader and divided using RecursiveCharacterTextSplitter with a chunk size of 1000 and overlap of 100.**
>
> **Amazon Titan through Bedrock provides the embeddings, and FAISS creates an in-memory vector index. When an employee asks a question, I perform similarity search with `k=3` to retrieve the top three relevant policy chunks.**
>
> **My Python backend extracts those chunks, joins them into context and constructs an augmented prompt containing the policy context and the employee's question. I then invoke Claude Haiku 4.5 through Amazon Bedrock and return the generated response to Streamlit.**
>
> **LangChain provides reusable components and integrations, but the retrieve, augment and generate workflow is explicitly orchestrated in my Python code.**
>
> **I consider the current implementation a proof of concept rather than production-ready. Its main limitations include an in-memory session-oriented FAISS index, no conversation memory, no authentication or RBAC, no user-facing citations and no automated policy-versioning or systematic RAG evaluation pipeline.**
>
> **For production, I would separate ingestion from query serving, introduce controlled document versioning and a shared persistent retrieval architecture, add authentication and authorization, citations, stronger grounding and abstention behavior, observability and systematic RAG evaluation.”**

## Your project learning is now connected end-to-end

```text id="61oxn4"
PROJECT UNDERSTANDING
        ↓
ARCHITECTURE
        ↓
APPLICATION FLOW
        ↓
CODE
        ↓
RAG
        ↓
PDF PROCESSING
        ↓
CHUNKING
        ↓
EMBEDDINGS
        ↓
FAISS
        ↓
PROMPT + CLAUDE
        ↓
LANGCHAIN
        ↓
STATE / MEMORY
        ↓
AWS + SECURITY
        ↓
DEPLOYMENT
        ↓
TROUBLESHOOTING
        ↓
EVALUATION
        ↓
COST + SCALE
        ↓
LIMITATIONS
        ↓
PRODUCTION DESIGN
        ↓
PROJECT STORYTELLING
        ↓
INTERVIEW Q&A
        ↓
MOCK INTERVIEW
```

The next useful step is **not another theory file**. It is to practice these answers without reading them: first the 10 core questions, then technical follow-ups, then scenario questions.