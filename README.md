# Resume Ranker — AI-Powered Candidate Matching
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
   pause
   ```
3. Save as `ResumeRanker.bat` in your project folder (or on Desktop).
4. Change Save as type to **All Files**.

#### Step B: Make it Look Professional
1. Right-click `ResumeRanker.bat` on Desktop.
2. Select **Create shortcut**.
3. Right-click shortcut → **Properties** → **Change Icon**.
4. Rename shortcut to **Resume Ranker**.

#### Step C: Use Daily
1. Double-click **Resume Ranker**.
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

### 2. Save API Key (optional but recommended)
```bash
# macOS — add to ~/.zshrc
echo 'export ANTHROPIC_API_KEY="sk-ant-YOUR-KEY"' >> ~/.zshrc
source ~/.zshrc

# Windows — Command Prompt (as Admin)
setx ANTHROPIC_API_KEY "sk-ant-YOUR-KEY"
```

---

## Daily Workflow

1. Double-click launcher → browser opens
2. Enter API key (or skip if saved as env variable)
3. Click **Browse** → select folder with downloaded Naukri/LinkedIn resumes
4. Drag & drop the **Job Description** file
5. Click **Analyze & Rank Resumes**
6. View ranked results → click **Ask AI** for any candidate
7. Click **Export CSV** or **Export Excel**

---

## Model Switching (Cost vs Accuracy)

Edit `utils/ranker.py` line 12:
```python
MODEL_NAME = "claude-haiku-4-5-20251001"   # Cheapest — basic screening
MODEL_NAME = "claude-sonnet-4-6"            # Recommended — smart matching  
MODEL_NAME = "claude-opus-4-6"              # Most accurate — premium
```

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `Address already in use` | App already running — check other terminal windows |
| `No module named flask` | Run: `pip install -r requirements.txt` |
| `API key invalid` | Check key at console.anthropic.com |
| Resumes not showing | Use PDF, DOCX, or TXT — scanned image PDFs not supported |
| Browser can't connect | Keep Terminal/CMD window open while using app |

---

*Resume Ranker v2 — For support contact your IT admin*
