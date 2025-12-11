#!/usr/bin/env python3
"""
Simple launcher for the SJSU Virtual Assistant UI
Skips Streamlit's welcome prompts
"""
import os
import sys
import subprocess

# Change to project directory
project_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_dir)

# Set environment variable to skip welcome
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'

print(" Starting SJSU Virtual Assistant...")
print(" Using Groq Llama-3.3-70B (Cloud)")
print("")
print(" Launching UI at http://localhost:8501")
print(" (Press Ctrl+C to stop)")
print("")

# Launch Streamlit
cmd = [
 sys.executable, "-m", "streamlit", "run",
 "ui/streamlit_app.py",
 "--server.port", "8501",
 "--server.address", "localhost",
 "--browser.gatherUsageStats", "false",
 "--theme.primaryColor", "#0055A2",
 "--theme.backgroundColor", "#FFFFFF",
 "--theme.secondaryBackgroundColor", "#F0F2F6",
 "--theme.textColor", "#262730"
]

try:
 subprocess.run(cmd)
except KeyboardInterrupt:
 print("\n\n Shutting down SJSU Virtual Assistant...")
