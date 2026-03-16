# RecruitAI — AI-Powered Candidate Matching
**Patil Group Internal HR Tool | Version 2**

---

## Quick Start (After Setup)

| Platform | Action |
|----------|--------|
| **macOS** | Double-click `launch.command` |
| **Windows** | Double-click `ResumeRanker.bat` (or use the Desktop shortcut below) |

Then open browser → `http://127.0.0.1:5000`

### Windows Desktop App Shortcut (Optional but recommended)

#### Step A: Create the Launcher Script (if missing)
1. Open Notepad.
2. Paste:
   ```bat
   @echo off
   cd /d "%~dp0"
   start http://127.0.0.1:5000
   python app.py
   ```
3. Save as `ResumeRanker.bat` in your project folder (or on Desktop).
4. Change Save as type to **All Files**.

#### Step B: Make it Look Professional
1. Right-click `ResumeRanker.bat` on Desktop.
2. Select **Create shortcut**.
3. Right-click shortcut → **Properties** → **Change Icon**.
4. Rename shortcut to **RecruitAI**.

#### Step C: Use Daily
1. Double-click **RecruitAI**.
2. Command Prompt opens and browser opens automatically.
3. Use app at `http://127.0.0.1:5000`.
4. Close CMD to stop.

---

## First-Time Setup

### 1. Install Python dependencies
```bash
# macOS
cd ~/Desktop/resume-sorter
python3 -m pip install -r requirements.txt

# Windows
cd %USERPROFILE%\Desktop\resume-sorter
pip install -r requirements.txt
```

### 2. Configure API Key
Create a `.env` file in your project folder and add your Groq API key:
```bash
GROQ_API_KEY=gsk_your_api_key_here
```

---

## Daily Workflow

1. Double-click launcher → browser opens
2. Click **Browse** → select folder with downloaded Naukri/LinkedIn resumes
3. Drag & drop the **Job Description** file
4. Click **Analyze & Rank Resumes**
5. View ranked results → click **Ask AI** for any candidate
6. Click **Export CSV** or **Export Excel**

---

## Model Configuration

Edit `utils/ranker.py` line 14:
```python
MODEL_NAME = "llama-3.3-70b-versatile"   # Recommended
MODEL_NAME = "llama-3.1-8b-instant"      # Cheaper, basic screening
MODEL_NAME = "mixtral-8x7b-32768"        # Good alternative
```

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `Address already in use` | App already running — check other terminal windows |
| `No module named flask` | Run: `pip install -r requirements.txt` |
| `API key invalid` | Check key at console.groq.com |
| Resumes not showing | Use PDF, DOCX, or TXT — scanned image PDFs not supported |
| Browser can't connect | Keep Terminal/CMD window open while using app |

---

*RecruitAI by Patil Group — Powered by Groq AI*
