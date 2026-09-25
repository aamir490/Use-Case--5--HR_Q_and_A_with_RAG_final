| # | File name | Main topic / question | What you will learn | Why it matters here | Why interviewer may ask |
|---|---|---|---|---|---|
| 1 | `01-Project-Overview.md` | What exactly is NovaMindAI HR Q&A? | Problem, target user, scope, PoC maturity, what it does and does not do | You must first understand the real project boundary | “Tell me about your project” is usually the first question |
| 2 | `02-Current-Architecture.md` | What is the actual current architecture? | Browser, Streamlit, backend module, remote PDF, Titan, FAISS, Claude | Prevents you from calling this microservices or a separate API backend | Interviewers test whether you understand your architecture |
| 3 | `03-End-to-End-Application-Flow.md` | What happens from startup to answer? | First-session indexing, question flow, retrieval, prompt, generation | This is the core system behavior | “Walk me through the request flow” |
| 4 | `04-Technology-Stack.md` | Why is each technology used? | Python, Streamlit, LangChain integrations, PyPDFLoader, splitter, FAISS, Bedrock | Helps separate actually used libraries from unused requirements | “Why did you choose X?” |
| 5 | `05-Backend-Code-Walkthrough.md` | What do `hr_index()`, `hr_llm()`, and `hr_rag_response()` do? | Actual line-by-line backend responsibilities | These three functions are the heart of the project | Coding and implementation follow-ups are very likely |
| 6 | `06-Streamlit-and-Session-State.md` | How does Streamlit behave in this app? | Reruns, session state, UI/backend relationship, index reuse | Explains why the index is cached only within a session | Interviewer may ask why ingestion does not run on every click |
| 7 | `07-RAG-Fundamentals-in-This-Project.md` | Why is this genuine RAG? | Retrieve → augment → generate, and how this code implements all three | This project manually implements the RAG path | “Explain RAG using your own project” |
| 8 | `08-PDF-Loading-and-Policy-Data.md` | Where does knowledge come from? | Hardcoded remote UPL policy URL, local PDF, source/version concerns | Answer quality depends on the policy source | HR policy freshness and provenance are important design issues |
| 9 | `09-Chunking-and-Document-Processing.md` | Why split the PDF? | `RecursiveCharacterTextSplitter`, 1000/100 character settings, overlap, separators | Retrieval works on chunks, not whole PDF | Chunk-size questions are common in RAG interviews |
| 10 | `10-Titan-Embeddings.md` | What are embeddings and how are they used? | Document embeddings, query embeddings, semantic meaning, Titan role | Retrieval depends on embeddings | “What is an embedding?” is a standard GenAI question |
| 11 | `11-FAISS-Vector-Search.md` | How does retrieval work? | FAISS index creation, similarity search, `k=3`, in-memory lifecycle | FAISS is one of the biggest differences from your Bedrock KB project | Interviewers will ask why FAISS and how retrieval works |
| 12 | `12-Prompt-Construction-and-Claude.md` | What exactly is sent to Claude? | Retrieved context, question, prompt structure, temperature 0.1, max tokens 3000 | Explains generation behavior and grounding limits | “How do you control hallucination?” often leads here |
| 13 | `13-LangChain-in-This-Project.md` | What does LangChain actually do? | PyPDFLoader, splitter, BedrockEmbeddings, FAISS wrapper, ChatBedrock | Prevents you from overclaiming LangGraph/agents/chains | Interviewers may ask whether LangChain is orchestration or just wrappers here |
| 14 | `14-State-Memory-and-Index-Lifecycle.md` | What data is stored and for how long? | Session index, no persistent FAISS, no conversation memory, rebuild behavior | One of the project's major architectural limitations | “What happens after restart?” “Do you have memory?” |
| 15 | `15-AWS-Bedrock-IAM-and-Region.md` | How does the app authenticate to AWS? | `default` profile, Bedrock access, model permissions, inference profile issue | This is the actual AWS integration | Cloud interviewers will ask IAM, profile, region, access denied |
| 16 | `16-Security-and-Privacy.md` | What are the security gaps? | No login, no RBAC, prompt injection, data movement, public EC2 risk, credentials | HR data is sensitive and current implementation is not production secure | Very important for enterprise AI roles |
| 17 | `17-Deployment-and-EC2.md` | How is it run locally and how is EC2 intended to host it? | Local virtualenv, Streamlit 8501, manual EC2 steps, instance role concept | Deployment exists only as documentation, not verified infrastructure | “How did you deploy it?” is common |
| 18 | `18-Troubleshooting-and-Failure-Flow.md` | Where can the system fail? | PDF download, embedding, FAISS, model invocation, profile/region, UI | No try/except exists, so failure reasoning matters | Scenario-based interview questions |
| 19 | `19-Testing-and-RAG-Evaluation.md` | How do we know answers are correct? | Current diagnostic scripts vs real tests, sample questions, retrieval/grounding evaluation | Current project has no automated quality proof | RAG evaluation is increasingly important in interviews |
| 20 | `20-Cost-Scalability-and-Observability.md` | What happens with more users? | Per-session re-indexing cost, Bedrock calls, memory, lack of metrics, load testing | Current design repeats work for new sessions | “Will this scale?” “What are the cost drivers?” |
| 21 | `21-Current-Limitations-and-Gaps.md` | What is weak today? | No auth, no citations, policy freshness, no error recovery, no persistence, no eval | Shows engineering judgment | Interviewers often ask “What would you improve?” |
| 22 | `22-Production-V2-and-Design-Decisions.md` | How would you improve it realistically? | Shared versioned index, citations, auth, durable artifacts, controlled ingestion, better config | Helps you propose a better architecture without adding unnecessary services | Strong system-design follow-up |
| 23 | `23-Complete-Project-Storytelling.md` | How do I explain the project clearly? | 30-sec, 1-min, 3-min, deep-dive story | Converts technical knowledge into interview communication | Critical for confidence |
| 24 | `24-Interview-QA-and-Mock-Preparation.md` | What questions can they ask and how should I answer? | Project-specific interview Q&A, follow-ups, scenario questions, mock practice | Final conversion from understanding to interview performance | This is the final practice stage |

---

learning/
├── 01-Project-Overview.md
├── 02-Current-Architecture.md
├── 03-End-to-End-Application-Flow.md
├── 04-Technology-Stack.md
├── 05-Backend-Code-Walkthrough.md
├── 06-Streamlit-and-Session-State.md
├── 07-RAG-Fundamentals-in-This-Project.md
├── 08-PDF-Loading-and-Policy-Data.md
├── 09-Chunking-and-Document-Processing.md
├── 10-Titan-Embeddings.md
├── 11-FAISS-Vector-Search.md
├── 12-Prompt-Construction-and-Claude.md
├── 13-LangChain-in-This-Project.md
├── 14-State-Memory-and-Index-Lifecycle.md
├── 15-AWS-Bedrock-IAM-and-Region.md
├── 16-Security-and-Privacy.md
├── 17-Deployment-and-EC2.md
├── 18-Troubleshooting-and-Failure-Flow.md
├── 19-Testing-and-RAG-Evaluation.md
├── 20-Cost-Scalability-and-Observability.md
├── 21-Current-Limitations-and-Gaps.md
├── 22-Production-V2-and-Design-Decisions.md
├── 23-Complete-Project-Storytelling.md
└── 24-Interview-QA-and-Mock-Preparation.md