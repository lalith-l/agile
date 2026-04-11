from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from textblob import TextBlob
import re
import csv
import os
from datetime import datetime

app = FastAPI(title="GitGuard Validation Engine")

# Create the log file if it doesn't exist
LOG_FILE = "commit_logs.csv"
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Status", "Message", "Sentiment_Score", "Files_Changed", "Reason"])

def log_commit(status, msg, score, files_count, reason=""):
    with open(LOG_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), status, msg, round(score, 2), files_count, reason])

class CommitPayload(BaseModel):
    message: str
    files: list[str] = []

@app.post("/validate")
async def validate_commit(payload: CommitPayload):
    msg = payload.message.strip()
    files = payload.files
    files_count = len(files)

    # 🚀 NEW: Add this Bypass for automated Merge commits
   if msg.startswith("Merge ") or msg.startswith("Revert "):
        return {"status": "success", "message": "System commit accepted.", "score": 0.0}

    # Gate 1: Syntax
    if len(msg) < 10:
        log_commit("Rejected", msg, 0.0, files_count, "Too short")
        raise HTTPException(status_code=400, detail="Message too short (minimum 10 characters).")
    
    pattern = r"^(Feat|Fix|Docs|Style|Refactor|Perf|Test|Chore)(\([a-zA-Z0-9_-]+\))?:\s.+"
    match = re.match(pattern, msg, re.IGNORECASE)
    if not match:
        log_commit("Rejected", msg, 0.0, files_count, "Invalid Prefix")
        raise HTTPException(status_code=400, detail="Must follow Conventional Commits (e.g., 'Fix: resolve issue').")
    
    prefix = match.group(1).title()

    # Gate 2: NLP Tone
    blob = TextBlob(msg)
    sentiment = blob.sentiment.polarity
    if sentiment < -0.5:
        log_commit("Rejected", msg, sentiment, files_count, "Hostile Tone")
        raise HTTPException(status_code=400, detail=f"Tone is too negative/hostile (Score: {sentiment:.2f}).")

    vague_words = ["stuff", "things", "fixed bug", "updated code", "wip"]
    if any(vague in msg.lower() for vague in vague_words):
        log_commit("Rejected", msg, sentiment, files_count, "Vague Language")
        raise HTTPException(status_code=400, detail="Message contains banned vague words. Be specific.")

    # Gate 3: Context Lie Detector
    code_extensions = ('.py', '.js', '.ts', '.java', '.cpp', '.go', '.rs')
    doc_extensions = ('.md', '.txt', '.pdf')

    has_code = any(f.endswith(code_extensions) for f in files)
    has_doc = any(f.endswith(doc_extensions) for f in files)

    if prefix == "Docs" and has_code:
        log_commit("Rejected", msg, sentiment, files_count, "Context Mismatch (Docs -> Code)")
        raise HTTPException(status_code=400, detail="Context Mismatch: 'Docs:' prefix used for source code!")

    if prefix in ["Feat", "Fix"] and has_doc and not has_code:
        log_commit("Rejected", msg, sentiment, files_count, "Context Mismatch (Code -> Docs)")
        raise HTTPException(status_code=400, detail="Context Mismatch: Code prefix used for documentation!")

    # Success!
    log_commit("Accepted", msg, sentiment, files_count, "Passed all gates")
    return {"status": "success", "message": "Commit validated successfully.", "score": sentiment}