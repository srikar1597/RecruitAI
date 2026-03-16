"""
Resume Ranker - AI-Powered Candidate Matching
Patil Group Internal HR Tool
"""

import os
import json
import threading
import webbrowser
from flask import Flask, render_template, request, jsonify, Response
from utils.ranker import rank_resume, GROQ_API_KEY
from utils.file_reader import extract_text

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/extract-text', methods=['POST'])
def extract_text_endpoint():
    """Extract text from an uploaded JD file"""
    if 'file' not in request.files:
        return jsonify({'text': '', 'error': 'No file'}), 400
    file = request.files['file']
    import tempfile
    filename = file.filename or ''
    ext = os.path.splitext(filename)[1].lower()
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            temp_path = tmp.name
        file.save(temp_path)
        text = extract_text(temp_path)
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'text': '', 'error': str(e)})
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass


@app.route('/api/browse', methods=['POST'])
def browse_folder():
    """Open native OS folder picker dialog"""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes('-topmost', 1)
        folder = filedialog.askdirectory(title="Select Resume Folder")
        root.destroy()
        if folder:
            extensions = ('.pdf', '.docx', '.doc', '.txt')
            files = [f for f in os.listdir(folder) if f.lower().endswith(extensions)]
            return jsonify({'path': folder, 'count': len(files)})
        return jsonify({'path': '', 'count': 0})
    except Exception as e:
        return jsonify({'error': str(e), 'path': '', 'count': 0}), 200


@app.route('/api/validate-folder', methods=['POST'])
def validate_folder():
    """Validate a manually typed folder path"""
    data = request.json
    folder = data.get('path', '').strip()
    if not folder or not os.path.isdir(folder):
        return jsonify({'valid': False, 'count': 0, 'error': 'Folder not found'})
    extensions = ('.pdf', '.docx', '.doc', '.txt')
    files = [f for f in os.listdir(folder) if f.lower().endswith(extensions)]
    return jsonify({'valid': True, 'count': len(files)})


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Main SSE endpoint — streams progress + results back to browser"""

    folder_path = request.form.get('folder_path', '').strip()
    jd_text = request.form.get('jd_text', '').strip()

    if not GROQ_API_KEY or GROQ_API_KEY == "gsk_REPLACE_WITH_YOUR_GROQ_API_KEY":
        def err():
            yield f"data: {json.dumps({'type':'error','message':'Groq API key not configured. Please set the GROQ_API_KEY in utils/ranker.py.'})}\n\n"
        return Response(err(), mimetype='text/event-stream')

    if not folder_path or not os.path.isdir(folder_path):
        def err():
            yield f"data: {json.dumps({'type':'error','message':'Invalid folder path. Please browse and select a valid folder.'})}\n\n"
        return Response(err(), mimetype='text/event-stream')

    if not jd_text:
        def err():
            yield f"data: {json.dumps({'type':'error','message':'No job description found. Please upload a JD file.'})}\n\n"
        return Response(err(), mimetype='text/event-stream')

    extensions = ('.pdf', '.docx', '.doc', '.txt')
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(extensions)]

    if not files:
        def err():
            yield f"data: {json.dumps({'type':'error','message':'No resume files found. Make sure folder contains PDF, DOCX, or TXT files.'})}\n\n"
        return Response(err(), mimetype='text/event-stream')

    def generate():
        results = []
        total = len(files)
        yield f"data: {json.dumps({'type': 'start', 'total': total})}\n\n"

        for i, filename in enumerate(files):
            filepath = os.path.join(folder_path, filename)
            progress = int(5 + (i / total) * 85)
            yield f"data: {json.dumps({'type': 'progress', 'progress': progress, 'message': f'Analyzing {filename} ({i+1}/{total})...'})}\n\n"

            try:
                text = extract_text(filepath)
                if not text.strip():
                    raise ValueError("Could not extract text (possibly a scanned/image PDF)")
                result = rank_resume(text, jd_text, filename)
                results.append(result)
                yield f"data: {json.dumps({'type': 'candidate_done', 'name': result.get('candidate_name', filename)})}\n\n"
            except Exception as e:
                results.append({
                    'score': 0,
                    'candidate_name': filename.rsplit('.', 1)[0],
                    'fileName': filename,
                    'education': '',
                    'years_exp': '',
                    'matched_skills': [],
                    'experience': 'Could not process this resume',
                    'strengths': [],
                    'gaps': [str(e)]
                })

        results.sort(key=lambda x: x['score'], reverse=True)
        yield f"data: {json.dumps({'type': 'progress', 'progress': 99, 'message': 'Sorting and ranking results...'})}\n\n"
        yield f"data: {json.dumps({'type': 'done', 'results': results, 'total': len(results)})}\n\n"

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'}
    )


@app.route('/api/ask', methods=['POST'])
def ask():
    """Follow-up AI chat about a specific candidate"""
    data = request.json
    candidate = data.get('candidate', {})
    history = data.get('history', [])

    if not GROQ_API_KEY or GROQ_API_KEY == "gsk_REPLACE_WITH_YOUR_GROQ_API_KEY":
        return jsonify({'error': 'Groq API key not configured on server.'}), 400

    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)

        system = f"""You are an expert HR analyst assistant at a railway infrastructure company.
You have analyzed this candidate against the job description:

Candidate: {candidate.get('candidate_name', 'Unknown')}
Score: {candidate.get('score', 0)}/100
Matched Skills: {', '.join(candidate.get('matched_skills', []))}
Experience Summary: {candidate.get('experience', '')}
Strengths: {', '.join(candidate.get('strengths', []))}
Gaps: {', '.join(candidate.get('gaps', []))}
Education: {candidate.get('education', '')}
Years of Experience: {candidate.get('years_exp', '')}

Answer the HR professional's questions concisely and practically. Keep answers under 150 words.
Be direct, specific, and useful. Avoid generic advice."""

        messages = [{"role": "system", "content": system}] + history

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=400,
            messages=messages,
            temperature=0.4,
        )

        reply = response.choices[0].message.content or ''

        return jsonify({'reply': reply})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def open_browser():
    import time
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')


if __name__ == '__main__':
    print("\n" + "="*50)
    print("  RecruitAI - Starting up...")
    print("  Browser will open automatically")
    print("  Press Ctrl+C to stop")
    print("="*50 + "\n")
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(debug=False, port=5000, threaded=True)
