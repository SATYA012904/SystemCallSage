/**
 * Results.js - Handles results page functionality and report generation
 */

document.addEventListener('DOMContentLoaded', function() {
    const reportBtn = document.getElementById('generate-report-btn');
    const alertContainer = document.getElementById('alert-container');
    const resetBtn = document.getElementById('reset-btn');
    
    // Load optimization results data
    loadOptimizationResults();
    
    // Handle report generation
    if (reportBtn) {
        reportBtn.addEventListener('click', function() {
            reportBtn.disabled = true;
            reportBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating...';
            
            // Redirect to report download endpoint
            window.location.href = '/generate-report';
            
            // Re-enable button after a delay
            setTimeout(() => {
                reportBtn.disabled = false;
                reportBtn.innerHTML = 'Generate Report';
            }, 2000);
        });
    }
    
    // Handle reset button click
    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to reset? This will clear all your data.')) {
                resetBtn.disabled = true;
                resetBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Resetting...';
                
                // Clear session data on the server
                fetch('/clear-session', {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Redirect to home page
                        window.location.href = '/';
                    } else {
                        showAlert('Error: ' + data.message, 'danger');
                        resetBtn.disabled = false;
                        resetBtn.innerHTML = 'Reset';
                    }
                })
                .catch(error => {
                    showAlert('Error: ' + error.message, 'danger');
                    resetBtn.disabled = false;
                    resetBtn.innerHTML = 'Reset';
                });
            }
        });
    }
    
    // Function to load optimization results
    function loadOptimizationResults() {
        fetch('/get-optimization-results')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load optimization results');
            }
            return response.json();
        })
        .then(data => {
            // Update performance metrics
            updatePerformanceMetrics(data.performance_metrics);
            
            // Create visualization charts
            createPerformanceComparisonChart('performance-chart', 
                data.performance_metrics.before, 
                data.performance_metrics.after);
            
            createOptimizationBreakdownChart('optimization-breakdown-chart', 
                data.performance_metrics.optimization_breakdown);
            
            // Show optimization details
            updateOptimizationDetails(data.optimized_data, data.performance_metrics);
        })
        .catch(error => {
            showAlert('Error: ' + error.message, 'danger');
        });
    }
    
    // Function to update performance metrics display
    function updatePerformanceMetrics(metrics) {
        const metricsContainer = document.getElementById('performance-metrics');
        if (!metricsContainer) return;
        
        // Update summary metrics
        document.getElementById('total-latency-before').textContent = metrics.before.total_latency.toFixed(2) + ' ms';
        document.getElementById('total-latency-after').textContent = metrics.after.total_latency.toFixed(2) + ' ms';
        document.getElementById('latency-improvement').textContent = metrics.improvement.latency_percent.toFixed(2) + '%';
        
        document.getElementById('avg-latency-before').textContent = metrics.before.average_latency.toFixed(2) + ' ms';
        document.getElementById('avg-latency-after').textContent = metrics.after.average_latency.toFixed(2) + ' ms';
        document.getElementById('avg-improvement').textContent = (metrics.before.average_latency - metrics.after.average_latency).toFixed(2) + ' ms';
        
        document.getElementById('total-calls-before').textContent = metrics.before.total_calls;
        document.getElementById('total-calls-after').textContent = metrics.after.total_calls;
        document.getElementById('calls-reduced').textContent = metrics.before.total_calls - metrics.after.total_calls;
    }
    
    // Function to update optimization details
    function updateOptimizationDetails(optimizedData, metrics) {
        const detailsContainer = document.getElementById('optimization-details');
        if (!detailsContainer) return;
        
        // Update optimization techniques list
        const techniquesList = document.getElementById('optimization-techniques');
        techniquesList.innerHTML = '';
        
        const techniques = [
            {
                name: 'System Call Batching',
                description: 'Combining multiple similar system calls into a single call to reduce context switching overhead.'
            },
            {
                name: 'Caching',
                description: 'Storing frequently accessed system call results to avoid redundant calls.'
            },
            {
                name: 'Asynchronous Processing',
                description: 'Using non-blocking calls to avoid waiting for I/O operations.'
            },
            {
                name: 'Call Elimination',
                description: 'Removing unnecessary system calls that don\'t affect the application behavior.'
            },
            {
                name: 'Resource Pooling',
                description: 'Reusing system resources to avoid repeated initialization and cleanup calls.'
            }
        ];
        
        techniques.forEach(technique => {
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item bg-dark text-light';
            listItem.innerHTML = `
                <h5 class="mb-1">${technique.name}</h5>
                <p class="mb-1">${technique.description}</p>
            `;
            techniquesList.appendChild(listItem);
        });
        
        // Update optimized calls table
        const tableBody = document.getElementById('optimized-calls-body');
        if (tableBody) {
            tableBody.innerHTML = '';
            
            // Get top optimized calls
            const optimizedCalls = metrics.optimization_breakdown;
            
            Object.entries(optimizedCalls)
                .sort((a, b) => b[1] - a[1])
                .forEach(([technique, value], index) => {
                    const row = document.createElement('tr');
                    const formattedTechnique = technique
                        .replace(/_/g, ' ')
                        .split(' ')
                        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                        .join(' ');
                    
                    row.innerHTML = `
                        <td>${index + 1}</td>
                        <td>${formattedTechnique}</td>
                        <td>${value}</td>
                        <td>${((value / metrics.before.total_calls) * 100).toFixed(2)}%</td>
                    `;
                    tableBody.appendChild(row);
                });
        }
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
});
