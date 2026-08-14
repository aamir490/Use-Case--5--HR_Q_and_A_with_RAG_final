# 🚀 GitHub Upload Guide — NovaMindAI HR Q&A

> Repository: https://github.com/aamir490/Use-Case--5--HR_Q_and_A_with_RAG_final

---

## ⚠️ Before You Start — Files to NEVER Upload

These files must NOT go to GitHub. They are already covered by `.gitignore` below:

| File / Folder | Reason |
|---|---|
| `.venv/` | Virtual environment — huge, machine-specific |
| `__pycache__/` | Python bytecode cache |
| `.aws/` | AWS credentials |
| `*.pem` | SSH private keys |
| `command.txt` | Contains AWS Access Keys — sensitive |
| `aws_cli_commnd.txt` | May contain credentials |

---

## 🟢 STEP 1: Navigate to Project Directory

```powershell
cd "E:\GenAi-Project-Udemy\HR_QA_26June2025\HR_QA_26June2025"
```

---

## 🟢 STEP 2: Initialize Git Repository

```powershell
git init
```

Expected output:
```
Initialized empty Git repository in E:/GenAi-Project-Udemy/HR_QA_26June2025/HR_QA_26June2025/.git/
```

---

## 🟢 STEP 3: Create .gitignore

```powershell
# Already created — see .gitignore in this folder
```

Contents of `.gitignore`:
```
# Virtual environment
.venv/
venv/
env/

# Python cache
__pycache__/
*.py[cod]
*.pyo

# AWS credentials — NEVER commit these
command.txt
aws_cli_commnd.txt
*.pem

# Environment files
.env
*.env

# OS files
.DS_Store
Thumbs.db

# Streamlit cache
.streamlit/
```

---

## 🟢 STEP 4: Check Git Remote (if already exists)

```powershell
git remote -v
```

If a remote already exists, remove it first:
```powershell
git remote remove origin
```

Then add the correct remote:
```powershell
git remote add origin https://github.com/aamir490/Use-Case--5--HR_Q_and_A_with_RAG_final.git
```

Verify it was added:
```powershell
git remote -v
```

Expected:
```
origin  https://github.com/aamir490/Use-Case--5--HR_Q_and_A_with_RAG_final.git (fetch)
origin  https://github.com/aamir490/Use-Case--5--HR_Q_and_A_with_RAG_final.git (push)
```

---

## 🟢 STEP 5: Configure Git Identity (first time only)

```powershell
git config --global user.name "Aamir"
git config --global user.email "your-email@example.com"
```

---

## 🟢 STEP 6: Stage Files

Stage all files (respecting .gitignore):
```powershell
git add .
```

Check what will be committed:
```powershell
git status
```

You should see these files staged (green):
```
rag_backend.py
rag_frontend.py
data_load_test.py
data_split_test.py
titien_model_test.py
requirements.txt
steps_to_do.md
interview.md
github_upload.md
ec2_steps.txt
Leave-Policy-India.pdf
RAG_Install.pdf
mylogo2.png
project_Architecture.png
HR Question and Answer App with Rag.png
question_for_rag.txt
.gitignore
```

---

## 🟢 STEP 7: Create Initial Commit

```powershell
git commit -m "Initial commit — NovaMindAI HR Q&A RAG app with Amazon Bedrock and FAISS"
```

---

## 🟢 STEP 8: Set Main Branch

```powershell
git branch -M main
```

---

## 🟢 STEP 9: Push to GitHub

```powershell
git push -u origin main
```

If prompted, enter your GitHub username and password/token.

> ⚠️ GitHub no longer accepts passwords. Use a **Personal Access Token (PAT)** instead of your password.
> Generate one at: https://github.com/settings/tokens → New token → Select `repo` scope → Copy the token → Use as password.

---

## 🟢 STEP 10: Verify on GitHub

Open in browser:
```
https://github.com/aamir490/Use-Case--5--HR_Q_and_A_with_RAG_final
```

You should see all files listed there.

---

## 🔁 How to Update GitHub After Code Changes

Whenever you make changes to files:

```powershell
cd "E:\GenAi-Project-Udemy\HR_QA_26June2025\HR_QA_26June2025"

# Stage changed files
git add rag_backend.py rag_frontend.py

# Or stage all changes
git add .

# Commit with a meaningful message
git commit -m "Fix: updated Claude model to Haiku 4.5 inference profile"

# Push to GitHub
git push origin main
```

---

## 🔎 Useful Git Commands

```powershell
# Check current status
git status

# View commit history
git log --oneline

# Check remote URL
git remote -v

# See what changed in a file
git diff rag_backend.py

# Undo last commit (keep changes)
git reset --soft HEAD~1
```

---

## ⚠️ Important Security Reminders

1. **Never commit AWS credentials** — check `command.txt` is in `.gitignore`
2. **Never commit `.venv/`** — it's large and machine-specific
3. If you accidentally commit credentials — immediately rotate your AWS keys at https://console.aws.amazon.com/iam
4. Use GitHub Secrets for CI/CD pipelines, not hardcoded keys

---

*NovaMindAI · HR Q&A · GitHub Upload Guide · Built by Aamir*
