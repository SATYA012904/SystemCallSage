/**
 * Upload.js - Handles file upload and processing
 */

document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const uploadBtn = document.getElementById('upload-btn');
    const fileLabel = document.getElementById('file-label');
    const progressBar = document.getElementById('upload-progress-bar');
    const progressContainer = document.getElementById('upload-progress');
    const alertContainer = document.getElementById('alert-container');
    
    // Update file label when a file is selected
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (fileInput.files.length > 0) {
                const fileName = fileInput.files[0].name;
                fileLabel.textContent = fileName;
                uploadBtn.disabled = false;
            } else {
                fileLabel.textContent = 'Choose file';
                uploadBtn.disabled = true;
            }
        });
    }
    
    // Handle file upload
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (fileInput.files.length === 0) {
                showAlert('Please select a file first.', 'warning');
                return;
            }
            
            const file = fileInput.files[0];
            const formData = new FormData();
            formData.append('file', file);
            
            // Show progress bar
            progressContainer.classList.remove('d-none');
            progressBar.style.width = '0%';
            progressBar.setAttribute('aria-valuenow', 0);
            
            // Disable submit button during upload
            uploadBtn.disabled = true;
            uploadBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Uploading...';
            
            // Send the file to the server
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                // Complete the progress bar
                progressBar.style.width = '100%';
                progressBar.setAttribute('aria-valuenow', 100);
                
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    showAlert(data.error, 'danger');
                } else {
                    showAlert('File uploaded and processed successfully!', 'success');
                    
                    // Update system call statistics display
                    updateSystemCallStats(data.system_call_stats);
                    
                    // Initialize visualization charts
                    initializeCharts(data.system_call_stats);
                    
                    // Show the next steps button
                    document.getElementById('next-step-container').classList.remove('d-none');
                }
            })
            .catch(error => {
                showAlert('Error: ' + error.message, 'danger');
            })
            .finally(() => {
                // Reset the upload button
                uploadBtn.disabled = false;
                uploadBtn.innerHTML = 'Upload';
                
                // Hide progress bar after a delay
                setTimeout(() => {
                    progressContainer.classList.add('d-none');
                }, 1000);
            });
        });
    }
    
    // Function to show alerts
    function showAlert(message, type) {
        const alertElement = document.createElement('div');
        alertElement.className = `alert alert-${type} alert-dismissible fade show`;
        alertElement.role = 'alert';
        alertElement.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        alertContainer.innerHTML = '';
        alertContainer.appendChild(alertElement);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertElement);
            bsAlert.close();
        }, 5000);
    }
    
    // Function to update the system call statistics display
    function updateSystemCallStats(stats) {
        const statsContainer = document.getElementById('system-call-stats');
        if (!statsContainer) return;
        
        statsContainer.classList.remove('d-none');
        
        // Update summary statistics
        document.getElementById('total-calls').textContent = stats.total_calls;
        document.getElementById('unique-calls').textContent = stats.unique_calls;
        document.getElementById('avg-latency').textContent = stats.average_latency.toFixed(3);
        document.getElementById('max-latency').textContent = stats.max_latency.toFixed(3);
        
        // Update top system calls table
        const tableBody = document.getElementById('top-calls-body');
        tableBody.innerHTML = '';
        
        // Sort calls by frequency
        const sortedCalls = Object.entries(stats.call_frequencies)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10); // Get top 10
        
        sortedCalls.forEach(([call, frequency], index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${call}</td>
                <td>${frequency}</td>
                <td>${stats.call_latencies[call] ? stats.call_latencies[call].toFixed(3) : 'N/A'}</td>
            `;
            tableBody.appendChild(row);
        });
    }
    
    // Function to initialize visualization charts
    function initializeCharts(stats) {
        const chartsContainer = document.getElementById('visualization-charts');
        if (!chartsContainer) return;
        
        chartsContainer.classList.remove('d-none');
        
        // Create frequency chart
        createSystemCallFrequencyChart('frequency-chart', stats.call_frequencies);
        
        // Create latency chart
        createSystemCallLatencyChart('latency-chart', stats.call_latencies);
    }
});
