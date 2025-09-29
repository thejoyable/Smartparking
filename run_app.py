#!/usr/bin/env python3
"""
Smart Parking Streamlit Application Launcher
This script ensures all dependencies are available and launches the app
"""

import sys
import subprocess
import os
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'streamlit',
        'streamlit_webrtc', 
        'cv2',
        'mediapipe',
        'ultralytics',
        'pandas',
        'numpy',
        'av',
        'aiortc'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'streamlit_webrtc':
                import streamlit_webrtc
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_requirements():
    """Install requirements from requirements.txt"""
    requirements_file = Path("requirements.txt")
    
    if requirements_file.exists():
        print("📦 Installing requirements from requirements.txt...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Requirements installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing requirements: {e}")
            return False
    else:
        print("⚠️ requirements.txt not found!")
        return False

def check_files():
    """Check if all required files exist"""
    required_files = [
        "app.py",
        "parking_manager.py", 
        "detection_engine.py",
        "csv_data_manager.py",
        "West_Bengal_Holidays_2025.csv"
    ]
    
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    return missing_files

def main():
    """Main launcher function"""
    print("🚗 Smart Parking Streamlit Application Launcher")
    print("=" * 50)
    
    # Check required files
    print("🔍 Checking required files...")
    missing_files = check_files()
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("Please ensure all application files are present.")
        return False
    
    print("✅ All required files present")
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    missing_packages = check_dependencies()
    
    if missing_packages:
        print(f"⚠️ Missing packages: {', '.join(missing_packages)}")
        print("📦 Attempting to install requirements...")
        
        if not install_requirements():
            print("❌ Failed to install requirements automatically.")
            print("Please run: pip install -r requirements.txt")
            return False
        
        # Re-check dependencies
        missing_packages = check_dependencies()
        if missing_packages:
            print(f"❌ Still missing packages: {', '.join(missing_packages)}")
            print("Please install manually: pip install " + " ".join(missing_packages))
            return False
    
    print("✅ All dependencies available")
    
    # Launch Streamlit app
    print("🚀 Launching Smart Parking Application...")
    print("📱 Open your browser and go to: http://localhost:8501")
    print("🎥 Make sure your camera is connected and accessible")
    print("=" * 50)
    
    try:
        # Launch streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--server.headless=true"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
