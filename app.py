import subprocess
import sys
import os

def run_app():
    try:
        
        # Construct path to the Streamlit app
        streamlit_app = os.path.join("src", "main.py")
        
        # Set up environment variables if needed
        env = os.environ.copy()
        
        # Command to run Streamlit
        streamlit_command = [
            sys.executable,  # Use the current Python interpreter
            "-m",
            "streamlit",
            "run",
            streamlit_app,
            "--server.port=8501",
            "--browser.serverAddress=localhost",
            "--server.address=localhost"
        ]
        
        print("Starting Scout Sense Resume Analyzer...")
        print("=" * 50)
        print(f"🚀 Launching application...")
        
        # Run Streamlit
        process = subprocess.Popen(
            streamlit_command,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        print(f"✨ Application started successfully!")
        print("=" * 50)
        print("📝 Access the application at: http://localhost:8501")
        print("Press Ctrl+C to stop the application")
        
        # Wait for the process to complete or user interruption
        process.wait()
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down the application...")
        process.terminate()
        process.wait()
        print("✅ Application stopped successfully")
        
    except Exception as e:
        print(f"❌ Error starting the application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_app()