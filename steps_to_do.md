# 🚀 HR QA Project — `steps_to_do.md`

> **Project Name:** HR QA  
> **Project Type:** Proof of Concept (PoC) — Retrieval-Augmented Generation (RAG) / Generative AI application  
> **Frontend:** Streamlit  
> **AI / LLM Integration:** Amazon Bedrock + LangChain  
> **Document Processing:** PyPDF + LangChain Text Splitters  
> **Vector Store:** FAISS  
> **Cloud:** AWS  
> **AWS Region:** `us-east-1`

---

# 🏗️ Basic Architecture

```text
👤 User
   │
   ▼
🖥️ Streamlit Frontend
   │
   ▼
🧠 RAG Application
   │
   ├── 📄 PDF / Document Processing
   │      ├── PyPDF
   │      └── LangChain Text Splitters
   │
   ├── 🔎 FAISS Vector Store
   │      └── Similarity Search / Retrieval
   │
   ├── 🔗 LangChain
   │
   └── ☁️ Amazon Bedrock
          └── Foundation Model / LLM
   │
   ▼
🤖 Generated HR Answer
   │
   ▼
🖥️ Streamlit UI
```

### 🔄 Basic Application Flow

```text
📄 HR Documents
      ↓
📖 Load Documents
      ↓
✂️ Split Documents into Chunks
      ↓
🔢 Create / Use Embeddings
      ↓
🗂️ Store / Search Vectors using FAISS
      ↓
🔎 Retrieve Relevant Context
      ↓
🧠 Send Context + Question to Amazon Bedrock
      ↓
🤖 Generate Answer
      ↓
🖥️ Display Answer in Streamlit
```

---

# 🟢 STEP 1: Navigate to the Project Directory

```powershell
# ==========================================================
# Step 1: Navigate to the Project Directory
# ==========================================================

# Display the current directory
Get-Location

# Copy the project's relative path and change to that directory
cd "E:\GenAi-Project-Udemy\HR_QA_26June2025\HR_QA_26June2025"

# Verify you are in the correct folder
pwd

# See all files
dir
```

### 💡 Comment

- Make sure the terminal is inside the correct **HR_QA_26June2025** project directory before continuing.
- `Get-Location` and `pwd` help confirm the current working directory.
- `dir` displays the project files and folders.

---

# 🟢 STEP 2: Check Python Versions

```powershell
# ==========================================================
# Step 2: Create a Python Virtual Environment
# ==========================================================

# Create a virtual environment named '.venv'

# Check current base core versions
python --version
py --version
```

Expected environment:

```text
python --version
Python 3.12.0

py --version
Python 3.14.6
```

### ⚠️ NOTE

This means `python` and `py` are pointing to different Python installations.

### ✅ NOTE

For this Kiro project, use **Python 3.12**.

---

## 🔎 Check All Installed Python Versions

Open **Command Prompt or AWS Kiro PowerShell**.

```powershell
py -0
py --list
```

Expected:

```text
-V:3.14 *        Python 3.14 (64-bit)
-V:3.12          Python 3.12 (64-bit)
```

### 💡 Comment

The `*` indicates the current default Python version for the `py` launcher.

Even though Python 3.14 is the default for `py`, this project will explicitly use Python 3.12.

---

# 🟢 STEP 3: Create the Virtual Environment

## ✅ Create `.venv` with Python 3.12

```powershell
py -3.12 -m venv .venv
```

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Expected prompt:

```text
(.venv) PS E:\GenAi-Project-Udemy\HR_QA_26June2025\HR_QA_26June2025>
```

---

## 🔎 Confirm Python 3.12

```powershell
py -3.12 --version
```

## 🔎 Confirm pip is working under Python 3.12

```powershell
py -3.12 -m pip --version
```

### Optional — Upgrade pip

```powershell
python -m pip install --upgrade pip
```

---

## 🔎 Confirm the Activated `.venv`

```powershell
python --version
```

Expected:

```text
Python 3.12.0
```

### Optional — Run a specific Python version

```powershell
py -3.12
```

---

# 🟢 STEP 4: Configure AWS Credentials

```powershell
# ==========================================================
# Step 4: Configure AWS Credentials
# ==========================================================

# Run the AWS configuration wizard
aws configure
```

When prompted, provide your AWS credentials.

> ⚠️ **Security Note:** Do NOT store real AWS Access Keys or Secret Access Keys inside this Markdown file, Git repository, screenshots, prompts, or project documentation. The credentials that were present in the original notes have intentionally been redacted here. If those credentials were real and have been exposed/shared, rotate or deactivate them immediately and create new credentials.

Use:

```text
AWS Access Key ID [None]: <YOUR_ACCESS_KEY_ID>
AWS Secret Access Key [None]: <YOUR_SECRET_ACCESS_KEY>
Default region name [None]: us-east-1
Default output format [None]: json
```

---

# 🟢 STEP 5: Verify AWS Configuration

```powershell
# ==========================================================
# Step 5: Verify AWS Configuration
# ==========================================================

# Run this command to verify who you are logged in as
aws sts get-caller-identity

# The Resource Test (List S3 Buckets)
aws s3 ls

# This shows your default profile — name, key, region, etc.
aws configure list

# To see all profiles you have configured
aws configure list-profiles

# To verify the default profile has the right credentials and region
aws configure list --profile default

# And to confirm it can actually connect to AWS
aws sts get-caller-identity --profile default
```

### ✅ Expected Result

`aws sts get-caller-identity` should return your AWS account / identity information without an authentication error.

---

# 🟢 STEP 6: HR QA Project — Additional Package Installation

```powershell
# ==========================================================
# HR QA Project — Additional Package Installation
# ==========================================================

# Install the required libraries
python -m pip install boto3 langchain langchain-aws langchain-community langchain-text-splitters streamlit transformers PyYAML pypdf faiss-cpu flask-sqlalchemy
```

### 📦 Main Libraries

- `boto3` → AWS SDK for Python
- `langchain` → LLM / RAG application framework
- `langchain-aws` → AWS integrations for LangChain
- `langchain-community` → Community integrations
- `langchain-text-splitters` → Document chunking
- `streamlit` → Web application frontend
- `transformers` → Hugging Face transformer ecosystem
- `PyYAML` → YAML configuration support
- `pypdf` → PDF processing
- `faiss-cpu` → Vector similarity search
- `flask-sqlalchemy` → Flask / SQLAlchemy integration

---

# 🟢 STEP 7: Create and Verify `requirements.txt`

```powershell
# Create requirements.txt from the current environment
python -m pip freeze > requirements.txt
```

### 🔎 Check whether the file was created

```powershell
dir requirements.txt
```

or:

```powershell
Get-Item requirements.txt
```

### 📖 View the contents

```powershell
Get-Content requirements.txt
```

### 📦 Install from `requirements.txt`

```powershell
python -m pip install -r requirements.txt
```

### 💡 Comment

`requirements.txt` records the installed Python packages and versions so the environment can be recreated later.

---

# 🟢 STEP 8: Before Starting Streamlit — Test the Model

```powershell
# ==========================================================
# Step 8: Before Start Streamlit Application Test Model
# ==========================================================

python titien_model_test.py
```

### 🔎 Comment

Run this test before starting the frontend.

The purpose is to verify that the model / AWS integration is working before troubleshooting the Streamlit application.

---

# 🟢 STEP 9: Run the Streamlit Application

```powershell
# ==========================================================
# Step 9: Run the Streamlit Application
# ==========================================================

# Start the Streamlit server
streamlit run rag_frontend.py
```

### 🌐 Typical Streamlit Address

```text
http://localhost:8501
```

or:

```text
http://127.0.0.1:8501
```

---

# 🟢 STEP 10: Run Streamlit in the Background

If you want to keep using the Kiro PowerShell terminal after starting Streamlit, run:

```powershell
Start-Process -FilePath "python" -ArgumentList "-m streamlit run rag_frontend.py --server.address 0.0.0.0 --server.port 8501" -WindowStyle Hidden
```

### 💡 Comment

This starts the Streamlit application as a background process so the current PowerShell terminal remains available for other commands.

---

# 🟢 STEP 11: Check Whether Streamlit Is Running

## 🔎 Option A — Check the Streamlit Process

```powershell
Get-Process python
```

For more detail:

```powershell
Get-Process python | Select-Object Id, ProcessName, StartTime
```

### 🔎 Search specifically for Streamlit

```powershell
Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" |
Where-Object { $_.CommandLine -like "*streamlit*" } |
Select-Object ProcessId, CommandLine
```

This is useful because it shows the **PID** and the command that started Streamlit.

---

# 🟢 STEP 12: Check Which Process Is Using Port 8501

```powershell
Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue
```

Or:

```powershell
netstat -ano | findstr :8501
```

Example:

```text
TCP    0.0.0.0:8501    0.0.0.0:0    LISTENING    12345
```

Here:

```text
12345 = PID
```

---

# 🟢 STEP 13: Find the Process from the PID

If the PID is `12345`:

```powershell
Get-Process -Id 12345
```

Or:

```powershell
tasklist /FI "PID eq 12345"
```

### 💡 Comment

This helps confirm which application currently owns port `8501`.

---

# 🟢 STEP 14: Stop / Kill the Streamlit Process

## Option A — Stop using PID

If the PID is `12345`:

```powershell
Stop-Process -Id 12345 -Force
```

## Option B — Using `taskkill`

```powershell
taskkill /PID 12345 /F
```

## Option C — Find Streamlit Python process and stop it

```powershell
Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" |
Where-Object { $_.CommandLine -like "*streamlit*" } |
ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

### ⚠️ Important

Only use the last command when you are sure the matching Python process belongs to your Streamlit application.

---

# 🟢 STEP 15: Verify Port 8501 Is Free

After killing the process:

```powershell
Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue
```

or:

```powershell
netstat -ano | findstr :8501
```

If nothing is returned, port `8501` is free.

You can then start Streamlit again.

---

# 🟢 STEP 16: Maintenance, Controls & Troubleshooting Reference

## 🛑 Stop a Foreground Streamlit Application

If Streamlit is running directly in the current terminal:

```text
Ctrl + C
```

---

## 🧹 Clear PowerShell Screen

```powershell
Clear-Host
```

or:

```powershell
clear
```

---

## 🔎 Check Python

```powershell
python --version
```

---

## 🔎 Check pip

```powershell
python -m pip --version
```

---

## 📦 Check Installed Packages

```powershell
pip list
```

or:

```powershell
python -m pip list
```

---

# 🟢 STEP 17: How to Run / Install `requirements.txt` on a Fresh Setup

If moving to a new machine or setting up a fresh environment later:

### 1️⃣ Navigate to the folder

```powershell
cd "E:\GenAi-Project-Udemy\Code_15042025\Code_15042025"
```

### 2️⃣ Activate the environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3️⃣ Run the installer

```powershell
pip install -r requirements.txt
```

### 4️⃣ Verify the packages

```powershell
pip list
```

### ✅ Recommended Alternative

```powershell
python -m pip install -r requirements.txt
```

Using `python -m pip` helps ensure that packages are installed into the Python environment currently being used by the project.

---

# 🏁 QUICK START — EXISTING PROJECT

When the project is already configured and `.venv` exists:

```powershell
cd "E:\GenAi-Project-Udemy\HR_QA_26June2025\HR_QA_26June2025"

.\.venv\Scripts\Activate.ps1

python --version

python -m pip --version

python titien_model_test.py

Start-Process -FilePath "python" -ArgumentList "-m streamlit run rag_frontend.py --server.address 0.0.0.0 --server.port 8501" -WindowStyle Hidden

netstat -ano | findstr :8501
```

Then open:

```text
http://localhost:8501
```

---

# 🔁 QUICK STOP / RESTART

### 🛑 Find Streamlit

```powershell
Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" |
Where-Object { $_.CommandLine -like "*streamlit*" } |
Select-Object ProcessId, CommandLine
```

### 🛑 Kill Streamlit

```powershell
Stop-Process -Id <PID> -Force
```

### 🚀 Start Again

```powershell
Start-Process -FilePath "python" -ArgumentList "-m streamlit run rag_frontend.py --server.address 0.0.0.0 --server.port 8501" -WindowStyle Hidden
```

### 🔎 Confirm Port

```powershell
netstat -ano | findstr :8501
```

---

# 🎯 FINAL PROJECT FLOW

```text
👤 User
   ↓
🖥️ Streamlit — rag_frontend.py
   ↓
🧠 RAG Pipeline
   ↓
📄 PDF Processing — PyPDF
   ↓
✂️ Text Splitting — LangChain
   ↓
🔎 Vector Retrieval — FAISS
   ↓
🔗 LangChain
   ↓
☁️ Amazon Bedrock
   ↓
🤖 AI / HR Answer
   ↓
🖥️ Streamlit UI
```

> 🔥 **Project Goal:** Build and run an HR Question-Answering Proof of Concept using a Retrieval-Augmented Generation (RAG) architecture with LangChain, FAISS, Streamlit, and Amazon Bedrock.
