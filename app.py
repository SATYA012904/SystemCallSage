import os
import logging
from flask import Flask, render_template, request, jsonify, send_file, session, flash, redirect, url_for
import numpy as np
import pandas as pd
import io
import json
from werkzeug.utils import secure_filename
from utils.data_processor import process_system_call_data, get_system_call_statistics
from models.system_call_optimizer import predict_optimized_calls
from utils.report_generator import generate_performance_report

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fallback_secret_key_for_development")

# Configure upload settings
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'log', 'csv'}

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data-analysis')
def data_analysis():
    return render_template('data_analysis.html')

@app.route('/ai-model')
def ai_model():
    if 'processed_data' not in session:
        flash('Please upload and process system call data first.', 'warning')
        return redirect(url_for('data_analysis'))
    return render_template('ai_model.html')

@app.route('/results')
def results():
    if 'optimized_data' not in session:
        flash('Please run the optimization model first.', 'warning')
        return redirect(url_for('ai_model'))
    return render_template('results.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # Process the uploaded system call log
            processed_data = process_system_call_data(file_path)
            system_call_stats = get_system_call_statistics(processed_data)
            
            # Store processed data in session
            session['processed_data'] = processed_data
            session['system_call_stats'] = system_call_stats
            session['original_filename'] = filename
            
            return jsonify({
                'success': True,
                'message': 'File uploaded and processed successfully.',
                'system_call_stats': system_call_stats
            })
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/get-system-call-data')
def get_system_call_data():
    if 'processed_data' not in session:
        return jsonify({'error': 'No processed data available'}), 404
    
    return jsonify({
        'stats': session['system_call_stats'],
        'data': session['processed_data']
    })

@app.route('/run-optimization', methods=['POST'])
def run_optimization():
    if 'processed_data' not in session:
        return jsonify({'error': 'No processed data available'}), 404
    
    try:
        # Run optimization model on the processed data
        optimized_data, performance_metrics = predict_optimized_calls(session['processed_data'])
        
        # Store optimized data in session
        session['optimized_data'] = optimized_data
        session['performance_metrics'] = performance_metrics
        
        return jsonify({
            'success': True,
            'performance_metrics': performance_metrics
        })
    except Exception as e:
        logger.error(f"Error running optimization: {str(e)}")
        return jsonify({'error': f'Error running optimization: {str(e)}'}), 500

@app.route('/get-optimization-results')
def get_optimization_results():
    if 'optimized_data' not in session:
        return jsonify({'error': 'No optimization results available'}), 404
    
    return jsonify({
        'performance_metrics': session['performance_metrics'],
        'optimized_data': session['optimized_data']
    })

@app.route('/generate-report')
def generate_report():
    if 'processed_data' not in session or 'optimized_data' not in session:
        return jsonify({'error': 'Insufficient data for report generation'}), 404
    
    try:
        # Generate performance report
        report_buffer = generate_performance_report(
            session['processed_data'],
            session['optimized_data'],
            session['performance_metrics'],
            session.get('original_filename', 'system_call_log')
        )
        
        buffer = io.BytesIO(report_buffer.getvalue())
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name='system_call_optimization_report.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return jsonify({'error': f'Error generating report: {str(e)}'}), 500

@app.route('/clear-session', methods=['POST'])
def clear_session():
    session.clear()
    return jsonify({'success': True, 'message': 'Session cleared successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
