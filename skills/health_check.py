#!/usr/bin/env python3
"""System Health Check Script - OpenSpider Worker Agent"""

import os
import sys
import time
import platform
import socket
import shutil
from datetime import datetime, timezone

def health_check():
    results = {}
    anomalies = []
    
    # 1. Timestamp
    now_utc = datetime.now(timezone.utc)
    now_local = datetime.now()
    results['timestamp_utc'] = now_utc.isoformat()
    results['timestamp_local'] = now_local.isoformat()
    
    # 2. Workspace accessibility
    cwd = os.getcwd()
    results['workspace_path'] = cwd
    results['workspace_exists'] = os.path.isdir(cwd)
    results['workspace_readable'] = os.access(cwd, os.R_OK)
    results['workspace_writable'] = os.access(cwd, os.W_OK)
    
    if not results['workspace_readable']:
        anomalies.append('Workspace is NOT readable')
    if not results['workspace_writable']:
        anomalies.append('Workspace is NOT writable')
    
    # List workspace contents
    try:
        contents = os.listdir(cwd)
        results['workspace_contents_count'] = len(contents)
        results['workspace_contents'] = contents[:20]  # limit to first 20
    except Exception as e:
        anomalies.append(f'Failed to list workspace: {e}')
        results['workspace_contents'] = []
    
    # 3. System info
    results['platform'] = platform.platform()
    results['python_version'] = sys.version
    results['hostname'] = socket.gethostname()
    results['pid'] = os.getpid()
    
    # 4. Disk usage
    try:
        usage = shutil.disk_usage(cwd)
        results['disk_total_gb'] = round(usage.total / (1024**3), 2)
        results['disk_used_gb'] = round(usage.used / (1024**3), 2)
        results['disk_free_gb'] = round(usage.free / (1024**3), 2)
        results['disk_usage_percent'] = round((usage.used / usage.total) * 100, 1)
        if results['disk_usage_percent'] > 90:
            anomalies.append(f'High disk usage: {results["disk_usage_percent"]}%')
    except Exception as e:
        anomalies.append(f'Failed to check disk usage: {e}')
    
    # 5. Memory info (if available)
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
        for line in meminfo.split('\n'):
            if 'MemTotal' in line:
                results['mem_total_kb'] = line.split(':')[1].strip()
            elif 'MemAvailable' in line:
                results['mem_available_kb'] = line.split(':')[1].strip()
    except:
        results['mem_info'] = 'Not available (non-Linux or restricted)'
    
    # 6. Write test (non-destructive)
    test_file = os.path.join(cwd, '.health_check_test')
    try:
        with open(test_file, 'w') as f:
            f.write('health_check_ok')
        with open(test_file, 'r') as f:
            content = f.read()
        os.remove(test_file)
        results['write_test'] = 'PASS' if content == 'health_check_ok' else 'FAIL'
    except Exception as e:
        results['write_test'] = f'FAIL: {e}'
        anomalies.append(f'Write test failed: {e}')
    
    # 7. Network connectivity (basic)
    try:
        socket.setdefaulttimeout(5)
        socket.create_connection(('8.8.8.8', 53), timeout=5)
        results['network_connectivity'] = 'OK'
    except Exception as e:
        results['network_connectivity'] = f'Limited or unavailable: {e}'
        anomalies.append('Network connectivity issue detected')
    
    # Summary
    results['anomalies'] = anomalies if anomalies else ['None detected']
    results['overall_status'] = 'HEALTHY' if not anomalies else 'DEGRADED'
    
    # Print report
    print('='*60)
    print('  OPENSPIDER SYSTEM HEALTH CHECK REPORT')
    print('='*60)
    print(f"  Timestamp (UTC):    {results['timestamp_utc']}")
    print(f"  Timestamp (Local):  {results['timestamp_local']}")
    print(f"  Hostname:           {results['hostname']}")
    print(f"  Platform:           {results['platform']}")
    print(f"  Python:             {sys.version.split()[0]}")
    print(f"  PID:                {results['pid']}")
    print('-'*60)
    print(f"  Workspace:          {results['workspace_path']}")
    print(f"  Readable:           {results['workspace_readable']}")
    print(f"  Writable:           {results['workspace_writable']}")
    print(f"  Files in workspace: {results['workspace_contents_count']}")
    print(f"  Write test:         {results['write_test']}")
    print('-'*60)
    if 'disk_total_gb' in results:
        print(f"  Disk Total:         {results['disk_total_gb']} GB")
        print(f"  Disk Used:          {results['disk_used_gb']} GB ({results['disk_usage_percent']}%)")
        print(f"  Disk Free:          {results['disk_free_gb']} GB")
    if 'mem_total_kb' in results:
        print(f"  Memory Total:       {results['mem_total_kb']}")
        print(f"  Memory Available:   {results['mem_available_kb']}")
    print(f"  Network:            {results['network_connectivity']}")
    print('-'*60)
    print(f"  Anomalies:          {', '.join(results['anomalies'])}")
    print(f"  Overall Status:     {results['overall_status']}")
    print('='*60)
    
    return results

if __name__ == '__main__':
    health_check()
