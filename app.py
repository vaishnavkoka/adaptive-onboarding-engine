"""
Flask Web Application for Adaptive Onboarding Engine
"""

from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import io
from onboarding_engine import AdaptiveOnboardingEngine
import traceback

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the engine
engine = AdaptiveOnboardingEngine()

# Job categories available
JOB_CATEGORIES = [
    'ACCOUNTANT',
    'ADVOCATE',
    'AGRICULTURE',
    'APPAREL',
    'ARTS',
    'AUTOMOBILE',
    'AVIATION',
    'BANKING',
    'BPO',
    'BUSINESS-DEVELOPMENT',
    'CHEF',
    'CONSTRUCTION',
    'CONSULTANT',
    'DESIGNER',
    'DIGITAL-MEDIA',
    'ENGINEERING',
    'FINANCE',
    'FITNESS',
    'HEALTHCARE',
    'HR',
    'INFORMATION-TECHNOLOGY',
    'PUBLIC-RELATIONS',
    'SALES',
    'TEACHER',
]

# Supported file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(file):
    """Extract text from uploaded file (supports TXT, PDF, DOCX)"""
    try:
        filename = file.filename.lower()
        
        if filename.endswith('.txt'):
            return file.read().decode('utf-8', errors='ignore')
        
        elif filename.endswith('.pdf'):
            try:
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
            except ImportError:
                return "[PDF file detected - PDF parsing requires PyPDF2 library. Please install: pip install PyPDF2]"
            except Exception as e:
                return f"Error reading PDF: {str(e)}"
        
        elif filename.endswith(('.docx', '.doc')):
            try:
                from docx import Document
                doc = Document(io.BytesIO(file.read()))
                text = "\n".join([para.text for para in doc.paragraphs])
                return text
            except ImportError:
                return "[DOCX file detected - DOCX parsing requires python-docx library. Please install: pip install python-docx]"
            except Exception as e:
                return f"Error reading DOCX: {str(e)}"
        
        else:
            # Try to read as text
            return file.read().decode('utf-8', errors='ignore')
    
    except Exception as e:
        return f"Error reading file: {str(e)}"



@app.route('/')
def index():
    """Main home page"""
    return render_template('index.html', job_categories=JOB_CATEGORIES)


@app.route('/api/extract-text', methods=['POST'])
def extract_text():
    """Extract text from uploaded file (PDF, DOCX, TXT)"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'File type not allowed. Supported: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Extract text from file
        text = extract_text_from_file(file)
        
        if text.startswith('[') and text.endswith(']'):
            # This is an error or info message
            return jsonify({
                'success': False,
                'error': text
            }), 400
        
        return jsonify({
            'success': True,
            'text': text,
            'filename': file.filename
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"File extraction failed: {str(e)}"
        }), 500


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Main analysis endpoint"""
    try:
        data = request.get_json()
        
        resume_text = data.get('resume_text', '').strip()
        job_description = data.get('job_description', '').strip()
        job_category = data.get('job_category', 'IT')
        max_weeks = int(data.get('max_weeks', 12))
        
        # Validation
        if not resume_text or len(resume_text) < 50:
            return jsonify({
                'success': False,
                'error': 'Resume text must be at least 50 characters'
            }), 400
        
        if not job_description or len(job_description) < 50:
            return jsonify({
                'success': False,
                'error': 'Job description must be at least 50 characters'
            }), 400
        
        if max_weeks < 1 or max_weeks > 52:
            return jsonify({
                'success': False,
                'error': 'Training duration must be between 1 and 52 weeks'
            }), 400
        
        # Run analysis
        analysis = engine.analyze_resume_and_job(
            resume_text,
            job_description,
            job_category,
            max_weeks
        )
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Analysis failed: {str(e)}",
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/report/<analysis_id>', methods=['GET'])
def get_report(analysis_id):
    """Generate formatted report"""
    try:
        # In a real app, would retrieve from database
        # For now, accept the analysis as part of request
        data = request.args.get('data', None)
        if not data:
            return jsonify({'error': 'No analysis data provided'}), 400
        
        analysis = json.loads(data)
        report = engine.format_report(analysis)
        
        return jsonify({
            'success': True,
            'report': report
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export-csv', methods=['POST'])
def export_csv():
    """Export pathway as CSV"""
    try:
        data = request.get_json()
        analysis = data.get('analysis', {})
        
        pathway = analysis.get('learning_pathway', {})
        modules = pathway.get('modules', [])
        
        # Generate CSV
        csv_lines = [
            "Module ID,Module Name,Skill Area,Difficulty,Duration (hours),Prerequisites",
        ]
        
        for module in modules:
            prerequisites = '|'.join(module.get('prerequisites', [])) or 'None'
            csv_lines.append(
                f"{module['id']},{module['name']},{module['skill']},"
                f"{module['difficulty']},{module['duration_hours']},{prerequisites}"
            )
        
        csv_content = '\n'.join(csv_lines)
        
        return send_file(
            io.BytesIO(csv_content.encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"learning_pathway_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'API endpoint not found'}), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Development settings - change for production
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        threaded=True
    )
