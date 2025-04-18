import os
import sys
import subprocess
import socket
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

def is_api_running():
    """Check if the FastAPI backend is running."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', 8000)) == 0

def is_port_in_use(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def run_streamlit():
    """Run the Streamlit frontend."""
    try:
        # Check if Streamlit is already running
        if is_port_in_use(8501):
            print(f"{Colors.WARNING}Warning: Streamlit is already running on port 8501.{Colors.ENDC}")
            print(f"{Colors.WARNING}Please close the existing Streamlit instance before starting a new one.{Colors.ENDC}")
            
            # Ask user if they want to continue
            response = input("Do you want to start a new instance anyway? (y/n): ")
            if response.lower() != 'y':
                print(f"{Colors.GREEN}Exiting. Please use the already running Streamlit instance.{Colors.ENDC}")
                return False
        
        # Check if the API is running
        if not is_api_running():
            print(f"{Colors.WARNING}Warning: The FastAPI backend does not appear to be running on port 8000.{Colors.ENDC}")
            print(f"{Colors.WARNING}The Streamlit frontend may not function correctly without the backend.{Colors.ENDC}")
            
            # Ask user if they want to continue
            response = input("Do you want to continue anyway? (y/n): ")
            if response.lower() != 'y':
                print(f"{Colors.GREEN}Exiting. Please start the backend with 'python run_api.py' first.{Colors.ENDC}")
                return False
        
        print(f"{Colors.HEADER}Starting Streamlit frontend...{Colors.ENDC}")
        print(f"{Colors.BLUE}Press Ctrl+C to stop the server{Colors.ENDC}")
        
        # Run Streamlit directly
        subprocess.run([
            sys.executable, 
            "-m", "streamlit", "run", "app/streamlit_app.py",
            "--server.port", "8501"
        ])
        
        return True
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Shutting down Streamlit server...{Colors.ENDC}")
        return True
    except Exception as e:
        print(f"{Colors.FAIL}Error starting Streamlit: {str(e)}{Colors.ENDC}")
        return False

def signal_handler(sig, frame):
    """Handle Ctrl+C signal."""
    print(f"\n{Colors.WARNING}Shutting down Streamlit server...{Colors.ENDC}")
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    print(f"{Colors.BOLD}===== Indian Law Tutor - Streamlit Frontend ====={Colors.ENDC}")
    
    # Run Streamlit
    success = run_streamlit()
    if not success:
        print(f"{Colors.FAIL}Failed to start Streamlit. Exiting...{Colors.ENDC}")
        sys.exit(1) 