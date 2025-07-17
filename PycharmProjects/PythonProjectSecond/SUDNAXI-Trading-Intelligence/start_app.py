#!/usr/bin/env python3
"""
Simple launcher for SUDNAXI Trading Platform
Perfect for PyCharm and other IDEs
"""
import subprocess
import sys
import os

def main():
    """Launch the Streamlit app"""
    print("Starting SUDNAXI Trading Platform...")
    print("Professional Trading Intelligence System")
    print("=" * 50)
    
    # Change to the script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Launch Streamlit
        print("Opening browser at: http://localhost:8501")
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
        
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'app.py',
            '--server.port=8501',
            '--server.address=localhost'
        ])
        
    except KeyboardInterrupt:
        print("\nShutting down SUDNAXI Trading Platform...")
        print("Session ended.")
        
    except FileNotFoundError:
        print("Error: Streamlit not found!")
        print("Install with: pip install streamlit")
        print("Or run: pip install -r production_requirements.txt")
        
    except Exception as e:
        print(f"Error starting app: {e}")
        print("Make sure you're in the correct directory")
        print("Try: pip install -r production_requirements.txt")

if __name__ == "__main__":
    main()