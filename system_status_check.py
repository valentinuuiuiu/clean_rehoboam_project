#!/usr/bin/env python3
"""
🔧 SYSTEM STATUS CHECKER - Post-OpenHands Integration
Verify that all services are properly configured and working.
"""

import requests
import json
import subprocess
import socket
from datetime import datetime

def check_port(host, port):
    """Check if a port is open"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

def check_service_status():
    """Check the status of all services"""
    print("🚀 SYSTEM STATUS CHECK - POST-OPENHANDS")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Port Configuration
    print("🔧 PORT CONFIGURATION:")
    print("Frontend (Vite):     Port 12000")
    print("Backend (API):       Port 12001")
    print("WebSocket:           Port 12001/ws")
    print()
    
    # Check if ports are open
    print("📡 PORT STATUS:")
    ports_to_check = [
        (12000, "Frontend"),
        (12001, "Backend/API"),
        (5001, "Old Frontend"),
        (5002, "Old Backend")
    ]
    
    for port, service in ports_to_check:
        is_open = check_port('127.0.0.1', port)
        status = "✅ ACTIVE" if is_open else "❌ INACTIVE"
        print(f"{service:15} Port {port:5}: {status}")
    
    print()
    
    # Check API endpoints
    print("🌐 API ENDPOINTS:")
    api_endpoints = [
        ("http://localhost:12001/", "Root"),
        ("http://localhost:12001/health", "Health Check"),
        ("http://localhost:12001/api/status", "API Status"),
        ("http://localhost:12000/", "Frontend")
    ]
    
    for url, name in api_endpoints:
        try:
            response = requests.get(url, timeout=5)
            status = f"✅ {response.status_code}"
        except requests.exceptions.ConnectionError:
            status = "❌ CONNECTION REFUSED"
        except requests.exceptions.Timeout:
            status = "⏰ TIMEOUT"
        except Exception as e:
            status = f"❌ ERROR: {str(e)[:30]}"
        
        print(f"{name:15}: {status}")
    
    print()
    
    # Check running processes
    print("🔄 RUNNING PROCESSES:")
    try:
        # Check for Python processes
        result = subprocess.run(['pgrep', '-f', 'python.*api_server'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            print("✅ API Server process running")
        else:
            print("❌ No API Server process found")
        
        # Check for Node/Vite processes
        result = subprocess.run(['pgrep', '-f', 'vite'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            print("✅ Vite process running")
        else:
            print("❌ No Vite process found")
            
    except Exception as e:
        print(f"❌ Process check failed: {e}")
    
    print()
    
    # Quick Start Instructions
    print("🚀 QUICK START (if services not running):")
    print("1. Start Backend:  python3 api_server.py")
    print("2. Start Frontend: npm run dev")
    print("3. Open Browser:   http://localhost:12000")
    print()
    
    # Configuration Summary
    print("⚙️  CONFIGURATION SUMMARY:")
    print("- OpenHands changed ports from 5001/5002 to 12000/12001")
    print("- Vite proxy configured for new backend port")
    print("- WebSocket connections updated")
    print("- All changes committed and pushed to GitHub")
    print()
    
    print("✨ Status check complete!")

if __name__ == "__main__":
    check_service_status()
