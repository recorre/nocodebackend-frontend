#!/bin/bash
# Complete PyAutoGUI X11 Environment Setup

echo "🔧 Setting up PyAutoGUI X11 environment..."

# Install system packages
echo "📦 Installing system packages..."
sudo apt-get update
sudo apt-get install -y xvfb x11vnc xauth x11-utils

# Install Python packages
echo "🐍 Installing Python packages..."
pip install pyautogui Pillow python-xlib

# Setup X11 authentication
echo "🔐 Setting up X11 authentication..."
export DISPLAY=${DISPLAY:-:0}
xauth add "$DISPLAY" MIT-MAGIC-COOKIE-1 "$(mcookie)"
xhost +local:

# Create directories
mkdir -p automation_screenshots
mkdir -p logs

echo "✅ Environment setup completed!"
echo "🚀 Run your PyAutoGUI script with:"
echo "   ./headless_pyautogui.py your_script.py"
