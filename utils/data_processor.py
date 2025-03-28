"""
Data Processing Utilities

This module provides functions for processing system call log data.
"""

import re
import json
import logging
import os
import numpy as np
import pandas as pd
from collections import Counter, defaultdict

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def parse_strace_line(line):
    """
    Parse a single line from strace output
    
    Args:
        line: A string containing a line from strace output
        
    Returns:
        Dictionary with parsed system call information, or None if parsing failed
    """
    try:
        # Basic pattern for strace output with timing information (-T option)
        # Example: open("/etc/passwd", O_RDONLY)      = 3 <0.000123>
        pattern = r'(\w+)\((.*)\)\s+=\s+(-?\d+|\?)\s+<([0-9.]+)>'
        match = re.match(pattern, line.strip())
        
        if not match:
            # Try alternative pattern without return value
            # Example: open("/etc/passwd", O_RDONLY <unfinished ...>
            pattern = r'(\w+)\((.*)\)\s+<([0-9.]+)>'
            match = re.match(pattern, line.strip())
            
            if not match:
                return None
        
        if len(match.groups()) == 4:
            call, args, ret_val, duration = match.groups()
        else:
            call, args, duration = match.groups()
            ret_val = "?"
        
        # Convert duration to milliseconds
        duration_ms = float(duration) * 1000
        
        return {
            'call': call,
            'args': args,
            'return': ret_val,
            'latency': duration_ms
        }
    
    except Exception as e:
        logger.warning(f"Failed to parse line: {line.strip()} - {str(e)}")
        return None


def parse_syscall_log_format(line):
    """
    Try to detect and parse different log formats
    
    Args:
        line: A string containing a line from a system call log
        
    Returns:
        Dictionary with parsed system call information, or None if parsing failed
    """
    # Try strace format first
    result = parse_strace_line(line)
    if result:
        return result
    
    # Try JSON format
    try:
        data = json.loads(line)
        # Validate required fields
        if 'call' in data and 'latency' in data:
            return data
    except json.JSONDecodeError:
        pass
    
    # Try CSV-like format (call,args,return,latency)
    try:
        parts = line.strip().split(',')
        if len(parts) >= 2:  # At minimum need call and latency
            result = {
                'call': parts[0].strip(),
                'latency': float(parts[-1].strip())
            }
            if len(parts) >= 3:
                result['args'] = parts[1].strip()
            if len(parts) >= 4:
                result['return'] = parts[2].strip()
            return result
    except Exception:
        pass
    
    # Try simple format (call latency)
    try:
        parts = line.strip().split()
        if len(parts) >= 2:
            call = parts[0].strip()
            # Try to extract latency from the last part
            latency = float(parts[-1].strip())
            return {
                'call': call,
                'latency': latency
            }
    except Exception:
        pass
    
    return None


def process_system_call_data(file_path):
    """
    Process system call log file and extract relevant data
    
    Args:
        file_path: Path to the system call log file
        
    Returns:
        List of dictionaries containing processed system call data
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    logger.info(f"Processing system call log file: {file_path}")
    
    processed_data = []
    line_count = 0
    parsed_count = 0
    
    with open(file_path, 'r') as f:
        for line in f:
            line_count += 1
            if line.strip():  # Skip empty lines
                parsed_line = parse_syscall_log_format(line)
                if parsed_line:
                    # Add a timestamp for sequential ordering (important for pattern analysis)
                    parsed_line['timestamp'] = line_count
                    processed_data.append(parsed_line)
                    parsed_count += 1
    
    logger.info(f"Processed {line_count} lines, successfully parsed {parsed_count} system calls")
    
    # If we didn't parse any real data, generate some demo data
    if len(processed_data) == 0:
        logger.warning("No valid system call data found in the file. Generating demo data.")
        processed_data = generate_demo_data()
    
    return processed_data


def get_system_call_statistics(data):
    """
    Calculate statistics from system call data
    
    Args:
        data: List of dictionaries containing system call data
        
    Returns:
        Dictionary with system call statistics
    """
    if not data:
        return {
            'total_calls': 0,
            'unique_calls': 0,
            'average_latency': 0,
            'max_latency': 0,
            'call_frequencies': {},
            'call_latencies': {}
        }
    
    # Count frequencies of each system call
    call_counter = Counter(entry['call'] for entry in data)
    
    # Calculate average latency for each system call
    call_latencies = defaultdict(list)
    for entry in data:
        call_latencies[entry['call']].append(entry['latency'])
    
    avg_latencies = {call: sum(latencies) / len(latencies) 
                    for call, latencies in call_latencies.items()}
    
    # Calculate overall statistics
    total_calls = len(data)
    unique_calls = len(call_counter)
    overall_latencies = [entry['latency'] for entry in data]
    average_latency = sum(overall_latencies) / len(overall_latencies)
    max_latency = max(overall_latencies)
    
    return {
        'total_calls': total_calls,
        'unique_calls': unique_calls,
        'average_latency': average_latency,
        'max_latency': max_latency,
        'call_frequencies': dict(call_counter),
        'call_latencies': avg_latencies
    }


def generate_demo_data():
    """
    Generate demonstration system call data for testing purposes
    
    Returns:
        List of dictionaries containing demo system call data
    """
    # Common system calls
    common_calls = [
        'read', 'write', 'open', 'close', 'stat', 'fstat', 'lstat',
        'poll', 'lseek', 'mmap', 'mprotect', 'munmap', 'brk',
        'rt_sigaction', 'rt_sigprocmask', 'ioctl', 'pread64', 'pwrite64',
        'readv', 'writev', 'access', 'pipe', 'select', 'sched_yield',
        'mremap', 'msync', 'mincore', 'madvise', 'shmget', 'shmat',
        'shmctl', 'dup', 'dup2', 'pause', 'nanosleep', 'getitimer',
        'alarm', 'setitimer', 'getpid', 'sendfile', 'socket', 'connect',
        'accept', 'sendto', 'recvfrom', 'sendmsg', 'recvmsg', 'shutdown',
        'bind', 'listen', 'getsockname', 'getpeername', 'socketpair',
        'setsockopt', 'getsockopt', 'clone', 'fork', 'vfork', 'execve'
    ]
    
    # Calls with typically higher latency
    high_latency_calls = ['read', 'write', 'open', 'connect', 'accept', 'poll', 'select', 'nanosleep']
    
    # Common call patterns (for realism)
    patterns = [
        ['open', 'fstat', 'read', 'close'],
        ['socket', 'connect', 'send', 'recv', 'close'],
        ['open', 'read', 'read', 'read', 'close'],
        ['getpid', 'getuid', 'getgid', 'geteuid'],
        ['stat', 'open', 'read', 'close']
    ]
    
    # Generate data with some patterns and random elements
    demo_data = []
    timestamp = 0
    
    # Add some random calls
    for _ in range(500):
        timestamp += 1
        call = np.random.choice(common_calls)
        
        # Determine latency - higher for certain calls
        base_latency = 0.1
        if call in high_latency_calls:
            base_latency = 1.0
        
        # Add some randomness to latency
        latency = base_latency + np.random.exponential(0.5)
        
        demo_data.append({
            'call': call,
            'args': f"args for {call}",
            'return': '0',
            'latency': latency,
            'timestamp': timestamp
        })
    
    # Add some patterns
    for _ in range(50):
        pattern = np.random.choice(patterns)
        
        for call in pattern:
            timestamp += 1
            
            # Determine latency
            base_latency = 0.1
            if call in high_latency_calls:
                base_latency = 1.0
            
            # Add some randomness to latency
            latency = base_latency + np.random.exponential(0.5)
            
            demo_data.append({
                'call': call,
                'args': f"args for {call}",
                'return': '0',
                'latency': latency,
                'timestamp': timestamp
            })
    
    # Shuffle to mix patterns with random calls
    np.random.shuffle(demo_data)
    
    # Fix timestamps after shuffling
    for i, entry in enumerate(demo_data):
        entry['timestamp'] = i + 1
    
    return demo_data
