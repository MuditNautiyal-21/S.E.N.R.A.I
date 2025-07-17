"""
Setup script for SUDNAXI Trading Platform
"""
import os
import subprocess
import sys
from pathlib import Path

def create_virtual_environment():
    """Create a virtual environment"""
    print("Creating virtual environment...")
    subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
    
    # Determine the correct path for the virtual environment
    if os.name == 'nt':  # Windows
        venv_python = Path('venv') / 'Scripts' / 'python.exe'
        venv_pip = Path('venv') / 'Scripts' / 'pip.exe'
    else:  # Unix/Linux/macOS
        venv_python = Path('venv') / 'bin' / 'python'
        venv_pip = Path('venv') / 'bin' / 'pip'
    
    return str(venv_python), str(venv_pip)

def install_dependencies(pip_path):
    """Install required dependencies"""
    print("Installing dependencies...")
    subprocess.run([pip_path, 'install', '--upgrade', 'pip'], check=True)
    subprocess.run([pip_path, 'install', '-r', 'production_requirements.txt'], check=True)

def create_env_file():
    """Create .env file from template"""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists() and env_example.exists():
        print("Creating .env file from template...")
        env_file.write_text(env_example.read_text())
        print("✓ .env file created. Edit it with your configurations if needed.")
    else:
        print("✓ .env file already exists.")

def setup_database():
    """Initialize the database"""
    print("Setting up database...")
    # Database will be automatically created on first run
    print("✓ Database configuration ready.")

def main():
    """Main setup function"""
    print("SUDNAXI Trading Platform Setup")
    print("Professional Trading Intelligence System")
    print("=" * 50)
    
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            print("ERROR: Python 3.8 or higher is required")
            sys.exit(1)
        
        print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
        
        # Create virtual environment
        venv_python, venv_pip = create_virtual_environment()
        print("✓ Virtual environment created")
        
        # Install dependencies
        install_dependencies(venv_pip)
        print("✓ Dependencies installed")
        
        # Create .env file
        create_env_file()
        
        # Setup database
        setup_database()
        
        print("\n" + "=" * 50)
        print("Setup completed successfully!")
        print("\nTo run the application:")
        print("1. Activate virtual environment:")
        if os.name == 'nt':
            print("   .\\venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        print("2. Run the application:")
        print("   python run_production.py")
        print("   or")
        print("   streamlit run app.py --server.port=8501")
        print("\nThen open http://localhost:8501 in your browser")
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Setup failed - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()