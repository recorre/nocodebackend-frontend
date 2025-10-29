#!/bin/bash
# Docker PyAutoGUI Runner

echo "🐳 Building PyAutoGUI Docker image..."
docker-compose -f docker-compose.pyautogui.yml build

echo "🚀 Running PyAutoGUI automation..."
docker-compose -f docker-compose.pyautogui.yml up --abort-on-container-exit

echo "🧹 Cleaning up..."
docker-compose -f docker-compose.pyautogui.yml down
