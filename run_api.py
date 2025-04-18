import os
import sys
import subprocess
import signal

# Colors for console output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def run_backend():
    """Run the FastAPI backend server."""
    try:
        print(f"{Colors.HEADER}Starting FastAPI backend...{Colors.ENDC}")
        print(f"{Colors.BLUE}Press Ctrl+C to stop the server{Colors.ENDC}")
        
        # Create required directories
        os.makedirs("data/uploads", exist_ok=True)
        os.makedirs("data/outputs", exist_ok=True)
        
        # Run the backend directly in the current process
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        )
        
        return True
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Shutting down backend server...{Colors.ENDC}")
        return True
    except Exception as e:
        print(f"{Colors.FAIL}Error starting backend: {str(e)}{Colors.ENDC}")
        return False

def signal_handler(sig, frame):
    """Handle Ctrl+C signal."""
    print(f"\n{Colors.WARNING}Shutting down backend server...{Colors.ENDC}")
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    print(f"{Colors.BOLD}===== Indian Law Tutor - API Backend ====={Colors.ENDC}")
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print(f"{Colors.WARNING}Warning: .env file not found. Creating a template .env file...{Colors.ENDC}")
        with open(".env", "w") as f:
            f.write("GROQ_API_KEY=your_groq_api_key\n")
            f.write("LLM_MODEL=llama-3.3-70b-versatile\n")
            f.write("LLM_PROVIDER=groq\n")
            f.write("UPLOAD_FOLDER=data/uploads\n")
            f.write("OUTPUT_FOLDER=data/outputs\n")
        print(f"{Colors.WARNING}Please edit the .env file with your API keys before continuing.{Colors.ENDC}")
        sys.exit(1)
    
    # Run the backend
    success = run_backend()
    if not success:
        print(f"{Colors.FAIL}Failed to start the backend. Exiting...{Colors.ENDC}")
        sys.exit(1) 