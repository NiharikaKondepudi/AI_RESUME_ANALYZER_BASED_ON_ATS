import os
import pdfkit
from flask import Flask, request, render_template, redirect, url_for, session, Response
from werkzeug.utils import secure_filename
from analyzer import analyze_resume

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max file size
app.config['SECRET_KEY'] = 'your-super-secret-key-change-me' # Important for session management

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """Renders the main upload page."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def upload_and_analyze():
    """Handles file upload, analysis, and renders the report or error page."""
    if 'resume' not in request.files:
        return redirect(request.url)
    
    file = request.files['resume']
    if file.filename == '':
        return redirect(request.url)

    job_description = request.form.get('job_description', '')

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Call the main analysis function from analyzer.py
        report = analyze_resume(filepath, job_description)
        
        # Clean up the uploaded file
        os.remove(filepath)
        
        # If the analyzer returns an error, show the error page
        if "error" in report:
            return render_template('error.html', message=report["error"])
        
        # Store the successful report in the session for the download feature
        session['report_data'] = report
            
        return render_template('report.html', report=report)

    return redirect(url_for('index'))

@app.route('/download_report')
def download_report():
    """Generates and serves a PDF version of the report."""
    report = session.get('report_data')
    if not report:
        return "No report found to download. Please analyze a resume first.", 404
        
    rendered_html = render_template('report.html', report=report)
    
    try:
        # --- START OF MANUAL PATH CONFIGURATION ---

        # **IMPORTANT**: Verify this path is correct for your system.
        # This is the default installation path for wkhtmltopdf on Windows.
        path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        
        # Create a configuration object that points to the executable
        config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
        
        # Pass the configuration to the pdfkit call
        pdf = pdfkit.from_string(rendered_html, False, configuration=config)
        
        # --- END OF MANUAL PATH CONFIGURATION ---

        response = Response(pdf, mimetype='application/pdf')
        response.headers['Content-Disposition'] = 'attachment; filename=resume_report.pdf'
        return response
        
    except OSError:
        # This error is returned if the executable is still not found at the specified path
        return ("Could not generate PDF. The 'wkhtmltopdf' executable was not found at the specified path. "
                "Please ensure it is installed correctly and the path in app.py is correct.")

if __name__ == '__main__':
    app.run(debug=True)