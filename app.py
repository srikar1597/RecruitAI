"""
Resume Ranker - AI-Powered Candidate Matching
Patil Group Internal HR Tool
"""

import os
import json
import tempfile
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


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Main endpoint — processes all resumes and returns JSON results"""

    jd_text = request.form.get('jd_text', '').strip()
    resume_files = request.files.getlist('resumes')

    if not GROQ_API_KEY or GROQ_API_KEY == "gsk_REPLACE_WITH_YOUR_GROQ_API_KEY":
        return jsonify({'type': 'error', 'message': 'Groq API key not configured. Please set GROQ_API_KEY in Render environment variables.'})

    if not jd_text:
        return jsonify({'type': 'error', 'message': 'No job description found. Please upload a JD file.'})

    if not resume_files or all(f.filename == '' for f in resume_files):
        return jsonify({'type': 'error', 'message': 'No resume files uploaded. Please select PDF, DOCX, or TXT files.'})

    results = []

    for i, file in enumerate(resume_files):
        filename = file.filename or f"resume_{i+1}"
        ext = os.path.splitext(filename)[1].lower()
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                temp_path = tmp.name
            file.save(temp_path)
            text = extract_text(temp_path)
            if not text.strip():
                raise ValueError("Could not extract text (possibly a scanned/image PDF)")
            result = rank_resume(text, jd_text, filename)
            results.append(result)
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
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass

    results.sort(key=lambda x: x['score'], reverse=True)
    return jsonify({'type': 'done', 'results': results, 'total': len(results)})


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

Answer HR questions concisely. Keep answers under 150 words. Be direct and specific."""

        messages = [{"role": "system", "content": system}] + history

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=400,
            messages=messages,
            temperature=0.4,
        )

        reply = response.choices[0].message.content or ''
        return jsonify({'reply': reply})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=False, port=5000, threaded=True)
