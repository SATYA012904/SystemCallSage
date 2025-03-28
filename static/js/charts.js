/**
 * Charts.js - Handles all chart visualizations for the application
 */

// Create system call frequency chart
function createSystemCallFrequencyChart(elementId, data) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Sort data by frequency (descending)
    const sortedData = Object.entries(data)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 15); // Get top 15 system calls
    
    const systemCalls = sortedData.map(item => item[0]);
    const frequencies = sortedData.map(item => item[1]);
    
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: systemCalls,
            datasets: [{
                label: 'Frequency',
                data: frequencies,
                backgroundColor: 'rgba(13, 110, 253, 0.7)',
                borderColor: 'rgba(13, 110, 253, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Top System Call Frequencies',
                    color: '#f8f9fa'
                },
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#adb5bd'
                    },
                    grid: {
                        color: '#2c3034'
                    }
                },
                x: {
                    ticks: {
                        color: '#adb5bd',
                        maxRotation: 45,
                        minRotation: 45
                    },
                    grid: {
                        color: '#2c3034'
                    }
                }
            }
        }
    });
}

// Create system call latency chart
function createSystemCallLatencyChart(elementId, data) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Sort data by latency (descending)
    const sortedData = Object.entries(data)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 15); // Get top 15 system calls by latency
    
    const systemCalls = sortedData.map(item => item[0]);
    const latencies = sortedData.map(item => item[1]);
    
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: systemCalls,
            datasets: [{
                label: 'Avg. Latency (ms)',
                data: latencies,
                backgroundColor: 'rgba(25, 135, 84, 0.7)',
                borderColor: 'rgba(25, 135, 84, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Top System Call Latencies',
                    color: '#f8f9fa'
                },
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#adb5bd'
                    },
                    grid: {
                        color: '#2c3034'
                    }
                },
                x: {
                    ticks: {
                        color: '#adb5bd',
                        maxRotation: 45,
                        minRotation: 45
                    },
                    grid: {
                        color: '#2c3034'
                    }
                }
            }
        }
    });
}

// Create system call timing chart
function createSystemCallTimingChart(elementId, data) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Extract timing data
    const timestamps = data.map(item => item.timestamp);
    const latencies = data.map(item => item.latency);
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: timestamps,
            datasets: [{
                label: 'Latency (ms)',
                data: latencies,
                backgroundColor: 'rgba(13, 202, 240, 0.2)',
                borderColor: 'rgba(13, 202, 240, 1)',
                borderWidth: 1,
                pointRadius: 0,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'System Call Latency Over Time',
                    color: '#f8f9fa'
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#adb5bd'
                    },
                    grid: {
                        color: '#2c3034'
                    },
                    title: {
                        display: true,
                        text: 'Latency (ms)',
                        color: '#adb5bd'
                    }
                },
                x: {
                    ticks: {
                        color: '#adb5bd',
                        maxTicksLimit: 10
                    },
                    grid: {
                        color: '#2c3034'
                    },
                    title: {
                        display: true,
                        text: 'Time',
                        color: '#adb5bd'
                    }
                }
            }
        }
    });
}

// Create performance comparison chart
function createPerformanceComparisonChart(elementId, beforeData, afterData) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Create comparison data
    const metrics = Object.keys(beforeData);
    const beforeValues = metrics.map(metric => beforeData[metric]);
    const afterValues = metrics.map(metric => afterData[metric]);
    
    // Format labels for better display
    const formattedLabels = metrics.map(metric => 
        metric.replace(/_/g, ' ')
              .split(' ')
              .map(word => word.charAt(0).toUpperCase() + word.slice(1))
              .join(' ')
    );
    
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: formattedLabels,
            datasets: [
                {
                    label: 'Before Optimization',
                    data: beforeValues,
                    backgroundColor: 'rgba(220, 53, 69, 0.7)',
                    borderColor: 'rgba(220, 53, 69, 1)',
                    borderWidth: 1
                },
                {
                    label: 'After Optimization',
                    data: afterValues,
                    backgroundColor: 'rgba(25, 135, 84, 0.7)',
                    borderColor: 'rgba(25, 135, 84, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Performance Comparison',
                    color: '#f8f9fa'
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)'
                },
                legend: {
                    labels: {
                        color: '#f8f9fa'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#adb5bd'
                    },
                    grid: {
                        color: '#2c3034'
                    },
                    title: {
                        display: true,
                        text: 'Value',
                        color: '#adb5bd'
                    }
                },
                x: {
                    ticks: {
                        color: '#adb5bd'
                    },
                    grid: {
                        color: '#2c3034'
                    }
                }
            }
        }
    });
}

// Create optimization breakdown pie chart
function createOptimizationBreakdownChart(elementId, data) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Prepare data for pie chart
    const labels = Object.keys(data);
    const values = Object.values(data);
    
    // Format labels for better display
    const formattedLabels = labels.map(label => 
        label.replace(/_/g, ' ')
             .split(' ')
             .map(word => word.charAt(0).toUpperCase() + word.slice(1))
             .join(' ')
    );
    
    return new Chart(ctx, {
        type: 'pie',
        data: {
            labels: formattedLabels,
            datasets: [{
                data: values,
                backgroundColor: [
                    'rgba(13, 110, 253, 0.7)',
                    'rgba(25, 135, 84, 0.7)',
                    'rgba(255, 193, 7, 0.7)',
                    'rgba(13, 202, 240, 0.7)',
                    'rgba(220, 53, 69, 0.7)'
                ],
                borderColor: [
                    'rgba(13, 110, 253, 1)',
                    'rgba(25, 135, 84, 1)',
                    'rgba(255, 193, 7, 1)',
                    'rgba(13, 202, 240, 1)',
                    'rgba(220, 53, 69, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Optimization Breakdown',
                    color: '#f8f9fa'
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)'
                },
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#f8f9fa',
                        padding: 15
                    }
                }
            }
        }
    });
}
