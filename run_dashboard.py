#!/usr/bin/env python3
"""
AzSOAR Dashboard Launcher
Run this file to start the web UI.
"""

import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit.web.cli as stcli
import os

if __name__ == "__main__":
    os.system("streamlit run azsoar/dashboard.py --server.headless true")
