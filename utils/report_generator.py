"""
Report Generator Module

This module provides functionality to generate PDF reports of system call optimization results.
"""

import io
import logging
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import io
import base64

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_bar_chart(data_before, data_after, width=5*inch, height=3*inch):
    """
    Create a bar chart comparing before and after metrics
    
    Args:
        data_before: Dictionary containing 'before' metrics
        data_after: Dictionary containing 'after' metrics
        width: Width of the chart
        height: Height of the chart
        
    Returns:
        A ReportLab Drawing object containing the bar chart
    """
    drawing = Drawing(width, height)
    
    metrics = ['total_latency', 'average_latency', 'max_latency']
    labels = ['Total Latency (ms)', 'Avg Latency (ms)', 'Max Latency (ms)']
    
    # Extract data
    data = [
        [data_before[metric] for metric in metrics], 
        [data_after[metric] for metric in metrics]
    ]
    
    # Create chart
    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 50
    bc.height = height - 100
    bc.width = width - 100
    bc.data = data
    bc.strokeColor = colors.black
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = max(max(data[0]), max(data[1])) * 1.1
    bc.valueAxis.valueStep = bc.valueAxis.valueMax / 5
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = 8
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.labels.angle = 30
    bc.categoryAxis.categoryNames = labels
    
    # Add colors
    bc.bars[0].fillColor = colors.red
    bc.bars[1].fillColor = colors.green
    
    drawing.add(bc)
    
    return drawing

def create_pie_chart(data, width=5*inch, height=3*inch):
    """
    Create a pie chart of optimization breakdown
    
    Args:
        data: Dictionary of optimization categories and their values
        width: Width of the chart
        height: Height of the chart
        
    Returns:
        A ReportLab Drawing object containing the pie chart
    """
    drawing = Drawing(width, height)
    
    # Format data for pie chart
    formatted_data = []
    labels = []
    
    for technique, value in data.items():
        if value > 0:  # Only include non-zero values
            formatted_label = technique.replace('_', ' ').title()
            labels.append(formatted_label)
            formatted_data.append(value)
    
    # Create pie chart
    pie = Pie()
    pie.x = width / 2
    pie.y = height / 2 - 50
    pie.width = min(width, height) - 100
    pie.height = min(width, height) - 100
    pie.data = formatted_data
    pie.labels = labels
    pie.slices.strokeWidth = 0.5
    
    # Add colors
    colors_list = [colors.blue, colors.green, colors.yellow, colors.cyan, colors.red]
    for i, color in enumerate(colors_list[:len(formatted_data)]):
        pie.slices[i].fillColor = color
    
    drawing.add(pie)
    
    return drawing

def generate_matplotlib_chart(data_before, data_after):
    """
    Generate a better looking chart using matplotlib
    
    Args:
        data_before: Dictionary containing 'before' metrics
        data_after: Dictionary containing 'after' metrics
        
    Returns:
        Image data as bytes
    """
    # Extract data
    metrics = ['total_latency', 'average_latency', 'max_latency']
    labels = ['Total Latency (ms)', 'Avg Latency (ms)', 'Max Latency (ms)']
    before_values = [data_before[metric] for metric in metrics]
    after_values = [data_after[metric] for metric in metrics]
    
    # Create figure and plot
    plt.figure(figsize=(8, 4), dpi=100)
    x = np.arange(len(labels))
    width = 0.35
    
    # Plot bars
    plt.bar(x - width/2, before_values, width, label='Before Optimization', color='#dc3545', alpha=0.7)
    plt.bar(x + width/2, after_values, width, label='After Optimization', color='#198754', alpha=0.7)
    
    # Add labels and styling
    plt.xlabel('Metrics')
    plt.ylabel('Value')
    plt.title('Performance Comparison')
    plt.xticks(x, labels)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # Save to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    
    return buf

def generate_matplotlib_pie(data):
    """
    Generate a pie chart using matplotlib
    
    Args:
        data: Dictionary of optimization categories and their values
        
    Returns:
        Image data as bytes
    """
    # Format data for pie chart
    labels = []
    values = []
    
    for technique, value in data.items():
        if value > 0:  # Only include non-zero values
            formatted_label = technique.replace('_', ' ').title()
            labels.append(formatted_label)
            values.append(value)
    
    # Create figure and plot
    plt.figure(figsize=(6, 4), dpi=100)
    
    # Plot pie chart
    colors = ['#0d6efd', '#198754', '#ffc107', '#0dcaf0', '#dc3545']
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, 
            shadow=False, colors=colors, wedgeprops={'edgecolor': 'white', 'linewidth': 1})
    
    # Equal aspect ratio ensures that pie is drawn as a circle
    plt.axis('equal')
    plt.title('Optimization Breakdown')
    plt.tight_layout()
    
    # Save to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    
    return buf

def generate_performance_report(original_data, optimized_data, performance_metrics, filename):
    """
    Generate a PDF report of system call optimization performance
    
    Args:
        original_data: Original system call data
        optimized_data: Optimized system call data
        performance_metrics: Dictionary containing performance metrics
        filename: Original filename of the system call log
        
    Returns:
        A BytesIO object containing the PDF report
    """
    try:
        logger.info("Generating performance report")
        
        # Create a file-like buffer to receive PDF data
        buffer = io.BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(buffer, pagesize=letter, 
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=72)
        
        # Container for the elements to build the PDF
        elements = []
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Add custom styles
        styles.add(ParagraphStyle(name='Title',
                                 parent=styles['Heading1'],
                                 fontSize=18,
                                 alignment=1,  # Center
                                 spaceAfter=24))
        
        styles.add(ParagraphStyle(name='Subtitle',
                                 parent=styles['Heading2'],
                                 fontSize=14,
                                 spaceAfter=12))
        
        styles.add(ParagraphStyle(name='Section',
                                 parent=styles['Heading3'],
                                 fontSize=12,
                                 spaceAfter=6))
        
        # Title
        elements.append(Paragraph("System Call Optimization Report", styles['Title']))
        
        # Report generation info
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elements.append(Paragraph(f"Generated: {current_time}", styles['Normal']))
        elements.append(Paragraph(f"Source File: {filename}", styles['Normal']))
        elements.append(Spacer(1, 0.25*inch))
        
        # Summary section
        elements.append(Paragraph("Executive Summary", styles['Subtitle']))
        
        # Create a summary table
        summary_data = [
            ["Metric", "Before", "After", "Improvement"],
            ["Total System Calls", f"{performance_metrics['before']['total_calls']}", 
             f"{performance_metrics['after']['total_calls']}", 
             f"{performance_metrics['before']['total_calls'] - performance_metrics['after']['total_calls']} calls"],
            ["Total Latency", f"{performance_metrics['before']['total_latency']:.2f} ms", 
             f"{performance_metrics['after']['total_latency']:.2f} ms", 
             f"{performance_metrics['improvement']['latency_percent']:.2f}%"],
            ["Average Latency", f"{performance_metrics['before']['average_latency']:.2f} ms", 
             f"{performance_metrics['after']['average_latency']:.2f} ms",
             f"{performance_metrics['before']['average_latency'] - performance_metrics['after']['average_latency']:.2f} ms"]
        ]
        
        # Create the table
        summary_table = Table(summary_data, colWidths=[2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.25*inch))
        
        # Add performance comparison chart
        elements.append(Paragraph("Performance Comparison", styles['Section']))
        
        try:
            # Try using matplotlib for better charts
            chart_buf = generate_matplotlib_chart(
                performance_metrics['before'],
                performance_metrics['after']
            )
            elements.append(Image(chart_buf, width=6*inch, height=3*inch))
        except Exception as e:
            logger.warning(f"Could not create matplotlib chart: {str(e)}")
            # Fallback to ReportLab charts
            chart = create_bar_chart(
                performance_metrics['before'],
                performance_metrics['after']
            )
            elements.append(chart)
        
        elements.append(Spacer(1, 0.25*inch))
        
        # Add optimization breakdown
        elements.append(Paragraph("Optimization Techniques Applied", styles['Section']))
        
        try:
            # Try using matplotlib for pie chart
            pie_buf = generate_matplotlib_pie(performance_metrics['optimization_breakdown'])
            elements.append(Image(pie_buf, width=4*inch, height=3*inch))
        except Exception as e:
            logger.warning(f"Could not create matplotlib pie chart: {str(e)}")
            # Fallback to ReportLab pie chart
            pie_chart = create_pie_chart(performance_metrics['optimization_breakdown'])
            elements.append(pie_chart)
        
        elements.append(Spacer(1, 0.25*inch))
        
        # Add optimization details
        elements.append(Paragraph("Optimization Details", styles['Section']))
        
        # Create a table for optimization breakdown
        opt_data = [["Technique", "Calls Affected"]]
        
        for technique, count in performance_metrics['optimization_breakdown'].items():
            formatted_technique = technique.replace('_', ' ').title()
            opt_data.append([formatted_technique, str(count)])
        
        # Create the table
        opt_table = Table(opt_data, colWidths=[3*inch, 2*inch])
        opt_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(opt_table)
        elements.append(Spacer(1, 0.25*inch))
        
        # Add optimization recommendations
        elements.append(Paragraph("Recommendations", styles['Section']))
        
        # Create a list of recommendations based on the optimization breakdown
        recommendations = []
        
        if performance_metrics['optimization_breakdown'].get('batching', 0) > 0:
            recommendations.append("""<b>System Call Batching:</b> Consider implementing system call batching in your application. 
            Group related system calls that operate on the same resources to reduce context switching overhead.""")
        
        if performance_metrics['optimization_breakdown'].get('caching', 0) > 0:
            recommendations.append("""<b>Result Caching:</b> Implement caching for frequently accessed data to avoid redundant 
            system calls. This is particularly effective for metadata operations like stat() and access().""")
        
        if performance_metrics['optimization_breakdown'].get('async_processing', 0) > 0:
            recommendations.append("""<b>Asynchronous I/O:</b> Consider using asynchronous I/O mechanisms to avoid blocking on 
            system calls. Libraries like libaio, io_uring, or high-level async frameworks can significantly reduce latency.""")
        
        if performance_metrics['optimization_breakdown'].get('call_elimination', 0) > 0:
            recommendations.append("""<b>Eliminate Redundant Calls:</b> Review your application logic to eliminate unnecessary 
            system calls. For example, avoid checking file existence before opening it - instead, handle the error if the 
            file doesn't exist.""")
        
        if performance_metrics['optimization_breakdown'].get('resource_pooling', 0) > 0:
            recommendations.append("""<b>Resource Pooling:</b> Implement resource pooling for frequently created and destroyed 
            resources like file descriptors or socket connections. This reduces the overhead of system calls like open() and close().""")
        
        # Add general recommendations
        recommendations.append("""<b>Use Efficient System Call Interfaces:</b> Consider using more efficient system call interfaces 
        like readv/writev instead of multiple read/write calls, or sendfile for data transfer between file descriptors.""")
        
        recommendations.append("""<b>Memory-Mapped I/O:</b> For large files, consider using memory-mapped I/O (mmap) instead of 
        read/write system calls. This can significantly reduce the number of system calls and improve performance.""")
        
        # Add recommendations to document
        for rec in recommendations:
            elements.append(Paragraph(rec, styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
        
        # Add statistics page
        elements.append(PageBreak())
        elements.append(Paragraph("System Call Statistics", styles['Subtitle']))
        
        # Original vs Optimized call counts
        elements.append(Paragraph("Call Count Comparison", styles['Section']))
        
        call_data = [
            ["Metric", "Value"],
            ["Original System Calls", str(len(original_data))],
            ["Optimized System Calls", str(len(optimized_data))],
            ["Reduction", f"{len(original_data) - len(optimized_data)} calls ({((len(original_data) - len(optimized_data)) / len(original_data) * 100):.2f}%)"]
        ]
        
        call_table = Table(call_data, colWidths=[3*inch, 2*inch])
        call_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(call_table)
        elements.append(Spacer(1, 0.25*inch))
        
        # Top system calls before optimization
        elements.append(Paragraph("Top System Calls Before Optimization", styles['Section']))
        
        # Count the frequency of each system call
        call_counter = {}
        for entry in original_data:
            call = entry['call']
            call_counter[call] = call_counter.get(call, 0) + 1
        
        # Sort by frequency (descending)
        sorted_calls = sorted(call_counter.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Create a table for top system calls
        top_calls_data = [["Rank", "System Call", "Count", "% of Total"]]
        
        for i, (call, count) in enumerate(sorted_calls, 1):
            percentage = (count / len(original_data)) * 100
            top_calls_data.append([str(i), call, str(count), f"{percentage:.2f}%"])
        
        # Create the table
        top_calls_table = Table(top_calls_data, colWidths=[0.7*inch, 2*inch, 1*inch, 1.5*inch])
        top_calls_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (2, 1), (3, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(top_calls_table)
        elements.append(Spacer(1, 0.25*inch))
        
        # Footer
        elements.append(Paragraph("This report was generated by the AI-Enhanced System Call Optimization tool.", styles['Normal']))
        elements.append(Paragraph("© 2023 AI-Enhanced System Call Optimization", styles['Normal']))
        
        # Build the PDF
        doc.build(elements)
        
        # Get the value of the BytesIO buffer
        pdf = buffer.getvalue()
        buffer.seek(0)
        
        logger.info("Performance report generated successfully")
        
        return buffer
        
    except Exception as e:
        logger.error(f"Error generating performance report: {str(e)}")
        raise
