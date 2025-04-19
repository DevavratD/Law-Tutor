#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simplified installation script for the Law Tutor project.
This script installs all the required dependencies directly without complex logic.
"""

import os
import sys
import subprocess
import platform

def print_status(message):
    """Print a status message with formatting"""
    print(f"\n=== {message} ===\n")

def run_command(command, shell=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command,
            shell=shell,
            check=False,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Command failed: {command}")
        print(f"Error: {e}")
        return False

def setup_venv():
    """Set up or check virtual environment"""
    print_status("Setting up virtual environment")
    
    # Check if we're already in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Already running in a virtual environment")
        return True
    
    # Check if venv directory exists
    if os.path.exists("venv"):
        print("✅ Virtual environment directory exists")
    else:
        print("Creating virtual environment...")
        if not run_command([sys.executable, "-m", "venv", "venv"], shell=False):
            print("❌ Failed to create virtual environment")
            return False
        print("✅ Virtual environment created")
    
    # Remind the user to activate the environment
    if platform.system() == "Windows":
        activate_cmd = ".\\venv\\Scripts\\activate"
    else:
        activate_cmd = "source venv/bin/activate"
    
    print(f"\n⚠️ IMPORTANT: Activate the virtual environment using:")
    print(f"    {activate_cmd}")
    print(f"Then run this script again with:")
    print(f"    python quick_install.py\n")
    
    return False

def install_requirements():
    """Install requirements directly"""
    print_status("Installing requirements")
    
    # Update pip
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], shell=False)
    
    # Install core packages one by one to avoid build errors
    packages = [
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "streamlit>=1.28.1",
        "python-multipart==0.0.6",
        "pydantic>=2.4.2",
        "python-dotenv>=1.0.0",
        "langchain>=0.0.335",
        "langchain-core>=0.1.8",
        "langchain-community>=0.0.11",
        "pypdf>=3.17.1",
        "docx2txt>=0.8",
        "tiktoken>=0.5.1",
        "requests>=2.31.0",
        "numpy",
        "scipy",
        "transformers<4.36.0,>=4.35.0",
        "torch",
        "nltk",
        "groq==0.4.0",
        "langchain-groq>=0.0.1"
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        success = run_command([sys.executable, "-m", "pip", "install", package], shell=False)
        if not success:
            print(f"⚠️ Failed to install {package}, continuing with other packages")
    
    # Install sentence-transformers with --no-build-isolation to avoid build errors
    print("Installing sentence-transformers...")
    run_command([sys.executable, "-m", "pip", "install", "sentence-transformers==2.2.2", "--no-build-isolation"], shell=False)
    
    # Install llama-index packages
    llama_packages = [
        "llama-index==0.10.31",
        "llama-index-llms-groq==0.1.4",
        "llama-index-embeddings-huggingface==0.1.5"
    ]
    
    for package in llama_packages:
        print(f"Installing {package}...")
        success = run_command([sys.executable, "-m", "pip", "install", package], shell=False)
        if not success:
            print(f"⚠️ Failed to install {package}, continuing with other packages")
    
    return True

def create_directories():
    """Create required directories if they don't exist"""
    print_status("Creating required directories")
    
    dirs = ["data/uploads", "data/outputs", "static"]
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d, exist_ok=True)
            print(f"✅ Created directory: {d}")
        else:
            print(f"✅ Directory already exists: {d}")

def main():
    """Main installation function"""
    print("\n" + "=" * 80)
    print(" " * 25 + "SIMPLIFIED LAW TUTOR INSTALLER" + " " * 25)
    print("=" * 80 + "\n")
    
    # Set up virtual environment
    in_venv = setup_venv()
    if not in_venv and not (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
        # Exit if not in venv and we just created one
        return
    
    # Install requirements
    install_requirements()
    
    # Create required directories
    create_directories()
    
    print("\n✅ Installation completed. You can now run the application with:")
    print("   python run.py - Run both backend and frontend")
    print("   python run_api.py - Run only the backend API")
    print("   python run_streamlit.py - Run the Streamlit interface")
    print("\nBefore running, make sure the virtual environment is activated.")

if __name__ == "__main__":
    main() 