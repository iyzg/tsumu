#!/usr/bin/env python3
"""
Simple web interface for Anki card generation tools.

Provides a user-friendly interface for:
- Uploading files
- Selecting conversion type
- Previewing generated cards
- Downloading results
"""

from flask import Flask, render_template_string, request, send_file, jsonify
import tempfile
import os
import subprocess
import csv
from pathlib import Path
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'md', 'csv', 'py', 'js', 'java', 'cpp', 'html'}

# HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>anki card generator</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, monospace; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto;
            background: white;
            border-radius: 1rem;
            padding: 2rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 { 
            color: #333;
            margin-bottom: 0.5rem;
            font-size: 2rem;
        }
        .subtitle {
            color: #666;
            margin-bottom: 2rem;
            font-style: italic;
        }
        .upload-area {
            border: 2px dashed #ddd;
            border-radius: 0.5rem;
            padding: 2rem;
            text-align: center;
            transition: all 0.3s;
            cursor: pointer;
            margin-bottom: 1rem;
        }
        .upload-area:hover, .upload-area.dragover {
            border-color: #667eea;
            background: #f0f0ff;
        }
        input[type="file"] {
            display: none;
        }
        select, button {
            width: 100%;
            padding: 0.75rem;
            margin: 0.5rem 0;
            border: 1px solid #ddd;
            border-radius: 0.25rem;
            font-size: 1rem;
        }
        button {
            background: #667eea;
            color: white;
            cursor: pointer;
            transition: all 0.3s;
            border: none;
        }
        button:hover {
            background: #5a67d8;
            transform: translateY(-1px);
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .preview {
            margin-top: 2rem;
            padding: 1rem;
            background: #f9f9f9;
            border-radius: 0.5rem;
            max-height: 400px;
            overflow-y: auto;
        }
        .card {
            background: white;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 0.25rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .card-front {
            font-weight: bold;
            color: #333;
            margin-bottom: 0.5rem;
        }
        .card-back {
            color: #666;
            padding-left: 1rem;
        }
        .stats {
            background: #e0f2fe;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        .error {
            background: #fee;
            color: #c00;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        .success {
            background: #efe;
            color: #060;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        .options {
            display: none;
            margin: 1rem 0;
            padding: 1rem;
            background: #f9f9f9;
            border-radius: 0.5rem;
        }
        .loader {
            display: none;
            text-align: center;
            margin: 1rem 0;
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>anki card generator</h1>
        <p class="subtitle">transform your notes into flashcards</p>
        
        <div class="upload-area" id="uploadArea">
            <p>📁 drag & drop your file here or click to browse</p>
            <input type="file" id="fileInput" accept=".txt,.md,.csv,.py,.js,.java,.cpp,.html">
        </div>
        
        <select id="converterType">
            <option value="smart">smart parser (auto-detect)</option>
            <option value="markdown">markdown to cards</option>
            <option value="code">code to cards</option>
            <option value="cloze">cloze deletions</option>
            <option value="fact">fact to cards</option>
            <option value="csv">csv formatter</option>
        </select>
        
        <div class="options" id="codeOptions">
            <label>Card types for code:</label>
            <select id="codeTypes" multiple size="3" style="width: 100%">
                <option value="syntax" selected>syntax patterns</option>
                <option value="function">function cards</option>
                <option value="concept">concept cards</option>
            </select>
        </div>
        
        <div class="options" id="clozeOptions">
            <label>Cloze type:</label>
            <select id="clozeType">
                <option value="basic">basic</option>
                <option value="sentence">sentence</option>
                <option value="incremental">incremental</option>
            </select>
        </div>
        
        <button id="generateBtn" disabled>generate cards</button>
        
        <div class="loader" id="loader">
            <div class="spinner"></div>
            <p>generating cards...</p>
        </div>
        
        <div id="result"></div>
    </div>
    
    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const generateBtn = document.getElementById('generateBtn');
        const converterType = document.getElementById('converterType');
        const loader = document.getElementById('loader');
        const result = document.getElementById('result');
        
        let selectedFile = null;
        
        // File upload handling
        uploadArea.addEventListener('click', () => fileInput.click());
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            handleFile(e.dataTransfer.files[0]);
        });
        
        fileInput.addEventListener('change', (e) => {
            handleFile(e.target.files[0]);
        });
        
        converterType.addEventListener('change', () => {
            // Show/hide options based on converter type
            document.getElementById('codeOptions').style.display = 
                converterType.value === 'code' ? 'block' : 'none';
            document.getElementById('clozeOptions').style.display = 
                converterType.value === 'cloze' ? 'block' : 'none';
        });
        
        function handleFile(file) {
            if (!file) return;
            
            selectedFile = file;
            uploadArea.innerHTML = `<p>✅ ${file.name} (${formatFileSize(file.size)})</p>`;
            generateBtn.disabled = false;
        }
        
        function formatFileSize(bytes) {
            if (bytes < 1024) return bytes + ' bytes';
            if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
            return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
        }
        
        generateBtn.addEventListener('click', async () => {
            if (!selectedFile) return;
            
            const formData = new FormData();
            formData.append('file', selectedFile);
            formData.append('converter', converterType.value);
            
            // Add converter-specific options
            if (converterType.value === 'code') {
                const selected = Array.from(document.getElementById('codeTypes').selectedOptions)
                    .map(opt => opt.value);
                formData.append('code_types', selected.join(','));
            } else if (converterType.value === 'cloze') {
                formData.append('cloze_type', document.getElementById('clozeType').value);
            }
            
            generateBtn.disabled = true;
            loader.style.display = 'block';
            result.innerHTML = '';
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayResults(data);
                } else {
                    result.innerHTML = `<div class="error">Error: ${data.error}</div>`;
                }
            } catch (error) {
                result.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            } finally {
                generateBtn.disabled = false;
                loader.style.display = 'none';
            }
        });
        
        function displayResults(data) {
            let html = `
                <div class="success">✨ Generated ${data.card_count} cards successfully!</div>
                <div class="stats">
                    <strong>Statistics:</strong><br>
                    Cards: ${data.card_count}<br>
                    File: ${data.output_file}
                </div>
                <button onclick="downloadCards('${data.output_file}')">⬇ download cards.csv</button>
                <div class="preview">
                    <h3>Preview (first 5 cards):</h3>
            `;
            
            data.preview.forEach(card => {
                html += `
                    <div class="card">
                        <div class="card-front">${escapeHtml(card.front)}</div>
                        <div class="card-back">${escapeHtml(card.back)}</div>
                    </div>
                `;
            });
            
            html += '</div>';
            result.innerHTML = html;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function downloadCards(filename) {
            window.location.href = `/download/${filename}`;
        }
    </script>
</body>
</html>
'''

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the main interface."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate_cards():
    """Generate Anki cards from uploaded file."""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'File type not allowed'})
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        # Generate output filename
        output_filename = f"cards_{os.path.splitext(filename)[0]}.csv"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        # Get converter type and options
        converter = request.form.get('converter', 'smart')
        
        # Build command based on converter type
        if converter == 'smart':
            cmd = ['python', 'scripts/smart_parser.py', input_path, '-o', output_path]
        elif converter == 'markdown':
            cmd = ['python', 'scripts/markdown_to_anki.py', input_path, '-o', output_path]
        elif converter == 'code':
            code_types = request.form.get('code_types', 'syntax').split(',')
            cmd = ['python', 'scripts/code_to_anki.py', input_path, '-t'] + code_types + ['-o', output_path]
        elif converter == 'cloze':
            cloze_type = request.form.get('cloze_type', 'basic')
            cmd = ['python', 'scripts/cloze_generator.py', input_path, '--type', cloze_type, '-o', output_path]
        elif converter == 'fact':
            cmd = ['python', 'scripts/fact_to_cards.py', input_path, '-o', output_path]
        elif converter == 'csv':
            cmd = ['python', 'scripts/csv_formatter.py', input_path, '-o', output_path]
        else:
            return jsonify({'success': False, 'error': 'Unknown converter type'})
        
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return jsonify({'success': False, 'error': result.stderr})
        
        # Read generated cards for preview
        preview_cards = []
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                for i, row in enumerate(reader):
                    if i >= 5:  # Only preview first 5 cards
                        break
                    if len(row) >= 2:
                        preview_cards.append({
                            'front': row[0][:100],  # Truncate long text
                            'back': row[1][:100]
                        })
        
        # Count total cards
        with open(output_path, 'r', encoding='utf-8') as f:
            card_count = sum(1 for line in f if line.strip())
        
        return jsonify({
            'success': True,
            'card_count': card_count,
            'output_file': output_filename,
            'preview': preview_cards
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/<filename>')
def download_file(filename):
    """Download generated card file."""
    try:
        path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if os.path.exists(path):
            return send_file(path, as_attachment=True, download_name=filename)
        else:
            return "File not found", 404
    except Exception as e:
        return str(e), 500

def main():
    """Run the web application."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Web interface for Anki card generation')
    parser.add_argument('--port', type=int, default=5000, help='Port to run on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    args = parser.parse_args()
    
    print(f"Starting web interface at http://localhost:{args.port}")
    print("Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=args.port, debug=args.debug)

if __name__ == '__main__':
    main()