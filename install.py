#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Installation helper script for the Indian Law Tutor project.
This script installs all the required dependencies and fixes known issues.
"""

import os
import sys
import subprocess
import platform
import shutil
import importlib.util
from pathlib import Path

# Constants
BACKUP_SUFFIX = ".bak"
REQUIREMENTS_FILE = "requirements.txt"
FIX_SCRIPT_PATH = "fix_dependencies.py"

def print_status(message):
    """Print a status message with a border"""
    width = len(message) + 4
    print("\n" + "=" * width)
    print(f"| {message} |")
    print("=" * width + "\n")

def run_command(command, shell=True, check=False, capture_output=False):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command,
            shell=shell,
            check=check,
            capture_output=capture_output,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {command}")
        print(f"Error: {e}")
        return None

def check_python_version():
    """Check if the current Python version is compatible"""
    print_status("Checking Python version")
    major, minor, _ = sys.version_info
    if major != 3 or minor < 8:
        print(f"❌ Incompatible Python version: {major}.{minor}")
        print("This project requires Python 3.8 or higher")
        sys.exit(1)
    print(f"✅ Python {major}.{minor} detected (compatible)")

def setup_virtual_env():
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
        result = run_command([sys.executable, "-m", "venv", "venv"], shell=False)
        if result is None or result.returncode != 0:
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
    print(f"    python install.py\n")
    
    return False

def update_pip():
    """Update pip to the latest version"""
    print_status("Updating pip")
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], shell=False)
    print("✅ Pip updated to the latest version")

def install_requirements():
    """Install requirements from requirements.txt"""
    print_status("Installing requirements")
    
    if not os.path.exists(REQUIREMENTS_FILE):
        # Create requirements.txt if it doesn't exist
        create_requirements_file()
    
    result = run_command([sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS_FILE], shell=False)
    if result is None or result.returncode != 0:
        print("⚠️ Some requirements may not have installed correctly")
        # Continue with the installation anyway
    else:
        print("✅ Base requirements installed")

def create_requirements_file():
    """Create requirements.txt file with the necessary dependencies"""
    print("Creating requirements.txt file...")
    
    requirements = """
# Core dependencies
langchain>=0.0.325
langchain-core>=0.1.0
langchain-groq>=0.1.0
langchain_groq>=0.1.0
langchain-community>=0.0.10
groq>=0.4.0,<0.23.0
llama-index>=0.9.0
llama_index>=0.9.0
sentence-transformers>=2.2.2
transformers>=4.30.2,<4.36.0
tokenizers>=0.13.3
fastapi>=0.105.0
uvicorn>=0.24.0
streamlit>=1.28.2
pydantic>=1.10.13,<2.0.0
python-dotenv>=1.0.0
typing-extensions>=4.8.0
coloredlogs>=15.0.1

# Optional dependencies
nltk>=3.8.1
matplotlib>=3.7.1
scikit-learn>=1.2.2
tqdm>=4.66.1
"""
    
    with open(REQUIREMENTS_FILE, "w") as f:
        f.write(requirements.strip())
    
    print(f"✅ Created {REQUIREMENTS_FILE}")

def fix_safe_serialization_issue():
    """Fix the safe_serialization issue in the HuggingFace embeddings"""
    print_status("Applying fixes for known issues")
    
    # First, look for the problematic file
    try:
        import llama_index
        base_path = Path(llama_index.__file__).parent
        file_path = base_path / "embeddings" / "huggingface" / "base.py"
        
        if not file_path.exists():
            print(f"⚠️ Could not find the file to fix at {file_path}")
            return False
        
        # Create a backup
        backup_path = str(file_path) + BACKUP_SUFFIX
        if not os.path.exists(backup_path):
            shutil.copy2(file_path, backup_path)
            print(f"✅ Created backup at {backup_path}")
        
        # Read the file content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if the file already has the fix
        if "safe_serialization=False" in content:
            print("✅ Safe serialization fix already applied")
            return True
        
        # Apply the fix
        modified_content = content.replace(
            "from_pretrained(model_name, device=device)",
            "from_pretrained(model_name, device=device, safe_serialization=False)"
        )
        
        # If the original pattern wasn't found, try an alternative
        if modified_content == content:
            modified_content = content.replace(
                "from_pretrained(embed_model_id, device=device)",
                "from_pretrained(embed_model_id, device=device, safe_serialization=False)"
            )
        
        # Write the modified content back to the file
        with open(file_path, 'w') as f:
            f.write(modified_content)
        
        print("✅ Applied safe_serialization fix")
        return True
    
    except ImportError:
        print("❌ llama_index not installed yet, will apply fix later")
        return False
    except Exception as e:
        print(f"❌ Error applying safe_serialization fix: {str(e)}")
        return False

def install_langchain_groq_from_github():
    """Install langchain-groq directly from GitHub"""
    print_status("Installing langchain-groq from GitHub")
    
    # Uninstall existing langchain-groq
    run_command([sys.executable, "-m", "pip", "uninstall", "-y", "langchain-groq", "langchain_groq"], shell=False)
    
    # Install from GitHub
    cmd = [
        sys.executable, 
        "-m", 
        "pip", 
        "install", 
        "git+https://github.com/langchain-ai/langchain.git@master#subdirectory=libs/partners/groq"
    ]
    result = run_command(cmd, shell=False)
    
    if result is None or result.returncode != 0:
        print("❌ Failed to install langchain-groq from GitHub")
        return False
    
    print("✅ Installed langchain-groq from GitHub")
    return True

def verify_imports():
    """Verify that critical imports work"""
    print_status("Verifying imports")
    
    # Run the verification script if it exists
    if os.path.exists("verify_imports.py"):
        result = run_command([sys.executable, "verify_imports.py"], shell=False)
        if result is None or result.returncode != 0:
            print("⚠️ Some imports failed verification")
            return False
        return True
    
    # If verification script doesn't exist, do basic checks
    critical_modules = [
        "langchain",
        "langchain_core",
        "langchain_groq",
        "groq",
        "llama_index",
        "sentence_transformers",
        "transformers"
    ]
    
    success = True
    for module in critical_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module} can be imported")
        except ImportError as e:
            print(f"❌ {module} import error: {str(e)}")
            success = False
    
    return success

def create_required_directories():
    """Create any required directories for the project"""
    dirs = ["data", "output", "logs", "models"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    print("✅ Created required directories")

def create_env_file():
    """Create a .env file template if it doesn't exist"""
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("""# Environment variables
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME=llama3-8b-8192
# Set to "hf" for HuggingFace or "openai" for OpenAI
EMBEDDING_MODEL_TYPE=hf
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
OPENAI_API_KEY=your_openai_api_key_here_if_using_openai_embeddings
""")
        print("✅ Created .env template file")
        print("⚠️ Don't forget to add your API keys to the .env file")

def print_success_message():
    """Print a success message"""
    print("\n" + "=" * 80)
    print(" " * 20 + "INSTALLATION COMPLETED SUCCESSFULLY" + " " * 20)
    print("=" * 80)
    print("\nTo run the application, use one of the following commands:")
    print("   python run.py         - Run the main application")
    print("   python run_api.py     - Run the API server")
    print("   python run_streamlit.py - Run the Streamlit interface")
    print("\nBefore running, make sure to:")
    print("1. Set your API keys in the .env file")
    print("2. Activate the virtual environment if not already active")
    print("\nIf you encounter any issues, run the verification script:")
    print("   python verify_imports.py")
    print("\nHappy coding!\n")

def main():
    """Main installation function"""
    print("\n" + "=" * 80)
    print(" " * 25 + "INDIAN LAW TUTOR INSTALLER" + " " * 25)
    print("=" * 80 + "\n")
    
    # Check Python version
    check_python_version()
    
    # Set up virtual environment
    in_venv = setup_virtual_env()
    if not in_venv and not (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
        # Exit if not in venv and we just created one
        return
    
    # Update pip
    update_pip()
    
    # Install requirements
    install_requirements()
    
    # Apply fixes for known issues
    fix_safe_serialization_issue()
    
    # Install langchain-groq from GitHub
    install_langchain_groq_from_github()
    
    # Create required directories and files
    create_required_directories()
    create_env_file()
    
    # Verify imports
    verified = verify_imports()
    
    if verified:
        print_success_message()
    else:
        print("\n⚠️ Installation completed with warnings. Some components may not work correctly.")
        print("Run 'python verify_imports.py' to check which imports are failing.\n")

if __name__ == "__main__":
    main() 