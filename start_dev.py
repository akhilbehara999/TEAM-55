import subprocess
import threading
import time
import sys

def start_backend():
    """Start the backend server"""
    print("Starting backend server...")
    try:
        # Run the backend server
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"
        ])
        print("Backend server started on http://localhost:8000")
        return backend_process
    except Exception as e:
        print(f"Error starting backend server: {e}")
        return None

def start_frontend():
    """Start the frontend development server"""
    print("Starting frontend development server...")
    try:
        # Run the frontend development server
        frontend_process = subprocess.Popen(["npm", "run", "dev"])
        print("Frontend development server started on http://localhost:5173")
        return frontend_process
    except Exception as e:
        print(f"Error starting frontend development server: {e}")
        return None

def main():
    """Main function to start both servers"""
    print("Starting CareerFlow AI Development Environment...")
    print("=" * 50)
    
    # Start backend server
    backend_process = start_backend()
    if not backend_process:
        print("Failed to start backend server. Exiting.")
        return
    
    # Wait a moment for backend to start
    time.sleep(2)
    
    # Start frontend development server
    frontend_process = start_frontend()
    if not frontend_process:
        print("Failed to start frontend development server.")
        # Terminate backend process
        backend_process.terminate()
        return
    
    print("\n" + "=" * 50)
    print("Development environment is now running!")
    print("Backend API: http://localhost:8000")
    print("Frontend App: http://localhost:5173")
    print("Press Ctrl+C to stop both servers")
    print("=" * 50)
    
    try:
        # Wait for both processes
        while True:
            if backend_process.poll() is not None or frontend_process.poll() is not None:
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down servers...")
        backend_process.terminate()
        frontend_process.terminate()
        print("Servers stopped.")

if __name__ == "__main__":
    main()