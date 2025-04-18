import os
import sys
import subprocess
import webbrowser
import time
from threading import Thread
import signal
import platform
import socket

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

def print_banner():
    """Print a banner for the application."""
    banner = """
    ██╗███╗   ██╗██████╗ ██╗ █████╗ ███╗   ██╗    ██╗      █████╗ ██╗    ██╗    ████████╗██╗   ██╗████████╗ ██████╗ ██████╗ 
    ██║████╗  ██║██╔══██╗██║██╔══██╗████╗  ██║    ██║     ██╔══██╗██║    ██║    ╚══██╔══╝██║   ██║╚══██╔══╝██╔═══██╗██╔══██╗
    ██║██╔██╗ ██║██║  ██║██║███████║██╔██╗ ██║    ██║     ███████║██║ █╗ ██║       ██║   ██║   ██║   ██║   ██║   ██║██████╔╝
    ██║██║╚██╗██║██║  ██║██║██╔══██║██║╚██╗██║    ██║     ██╔══██║██║███╗██║       ██║   ██║   ██║   ██║   ██║   ██║██╔══██╗
    ██║██║ ╚████║██████╔╝██║██║  ██║██║ ╚████║    ███████╗██║  ██║╚███╔███╔╝       ██║   ╚██████╔╝   ██║   ╚██████╔╝██║  ██║
    ╚═╝╚═╝  ╚═══╝╚═════╝ ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝    ╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝        ╚═╝    ╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═╝
    """
    print(f"{Colors.BLUE}{banner}{Colors.ENDC}")
    print(f"{Colors.BOLD}AI-Powered Indian Law Tutor{Colors.ENDC}")
    print(f"Powered by FastAPI, Streamlit, and Groq's Llama-3\n")

def run_backend():
    """Run the FastAPI backend server."""
    try:
        print(f"{Colors.HEADER}Starting FastAPI backend...{Colors.ENDC}")
        backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Wait for the server to start
        started = False
        for line in backend_process.stdout:
            print(f"{Colors.GREEN}[Backend] {line.strip()}{Colors.ENDC}")
            if "Uvicorn running on" in line:
                started = True
                break
            
        if not started:
            print(f"{Colors.FAIL}Failed to start backend server{Colors.ENDC}")
            return None
            
        return backend_process
    except Exception as e:
        print(f"{Colors.FAIL}Error starting backend: {str(e)}{Colors.ENDC}")
        return None

def run_frontend():
    """Run the Streamlit frontend."""
    try:
        print(f"{Colors.HEADER}Starting Streamlit frontend...{Colors.ENDC}")
        frontend_process = subprocess.Popen(
            [
                sys.executable,
                "-m", "streamlit", "run", "app/streamlit_app.py",
                "--server.headless", "true",  # Prevent auto browser open
                "--browser.gatherUsageStats", "false",
                "--server.port", "8501"  # Explicitly set port
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Wait for the server to start
        started = False
        for line in frontend_process.stdout:
            print(f"{Colors.BLUE}[Frontend] {line.strip()}{Colors.ENDC}")
            if "You can now view your Streamlit app in your browser" in line:
                started = True
                break
        
        if not started:
            print(f"{Colors.FAIL}Failed to start frontend server{Colors.ENDC}")
            return None
            
        return frontend_process
    except Exception as e:
        print(f"{Colors.FAIL}Error starting frontend: {str(e)}{Colors.ENDC}")
        return None

def log_output(process, prefix):
    """Log the output of a process with a prefix."""
    color = Colors.GREEN if prefix == "[Backend]" else Colors.BLUE
    for line in process.stdout:
        print(f"{color}{prefix} {line.strip()}{Colors.ENDC}")

def open_browser():
    """Open the browser to the Streamlit app."""
    # Wait for servers to start
    time.sleep(3)
    print(f"{Colors.HEADER}Opening browser...{Colors.ENDC}")
    webbrowser.open("http://localhost:8501")

def signal_handler(sig, frame):
    """Handle Ctrl+C signal."""
    print(f"\n{Colors.WARNING}Shutting down servers...{Colors.ENDC}")
    sys.exit(0)

def is_port_in_use(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

if __name__ == "__main__":
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Print banner
    print_banner()
    
    # Check if Streamlit is already running
    if is_port_in_use(8501):
        print(f"{Colors.WARNING}Warning: Streamlit is already running on port 8501.{Colors.ENDC}")
        print(f"{Colors.WARNING}Please close the existing Streamlit instance before starting a new one.{Colors.ENDC}")
        print(f"{Colors.WARNING}You can access the running instance at: http://localhost:8501{Colors.ENDC}")
        
        # Ask user if they want to continue
        response = input("Do you want to start a new instance anyway? (y/n): ")
        if response.lower() != 'y':
            print(f"{Colors.GREEN}Exiting. Please use the already running Streamlit instance.{Colors.ENDC}")
            sys.exit(0)
    
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
        
    # Check if required directories exist
    os.makedirs("data/uploads", exist_ok=True)
    os.makedirs("data/outputs", exist_ok=True)
    
    # Start the backend
    backend_process = run_backend()
    if not backend_process:
        print(f"{Colors.FAIL}Failed to start the backend. Exiting...{Colors.ENDC}")
        sys.exit(1)
    
    # Start logging the backend output in a separate thread
    backend_thread = Thread(target=log_output, args=(backend_process, "[Backend]"))
    backend_thread.daemon = True
    backend_thread.start()
    
    # Start the frontend
    frontend_process = run_frontend()
    if not frontend_process:
        print(f"{Colors.FAIL}Failed to start the frontend. Exiting...{Colors.ENDC}")
        backend_process.terminate()
        sys.exit(1)
    
    # Start logging the frontend output in a separate thread
    frontend_thread = Thread(target=log_output, args=(frontend_process, "[Frontend]"))
    frontend_thread.daemon = True
    frontend_thread.start()
    
    # Open the browser
    open_browser()
    
    print(f"{Colors.BOLD}Both servers are running!{Colors.ENDC}")
    print(f"FastAPI backend: {Colors.UNDERLINE}http://localhost:8000{Colors.ENDC}")
    print(f"Streamlit frontend: {Colors.UNDERLINE}http://localhost:8501{Colors.ENDC}")
    print(f"API docs: {Colors.UNDERLINE}http://localhost:8000/docs{Colors.ENDC}")
    print(f"\nPress {Colors.BOLD}Ctrl+C{Colors.ENDC} to stop the servers.")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Shutting down servers...{Colors.ENDC}")
        # Terminate processes
        backend_process.terminate()
        frontend_process.terminate()
        print(f"{Colors.GREEN}Servers shut down successfully.{Colors.ENDC}") 