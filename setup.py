#!/usr/bin/env python3

"""
Wanderlog AI Setup Script
Automated setup for development environment
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, check=True):
    """Run a command and return the result"""
    print(f"🔧 Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return None

def check_requirements():
    """Check if required software is installed"""
    print("🔍 Checking requirements...")
    
    requirements = {
        'python': 'python --version',
        'pip': 'pip --version',
        'git': 'git --version'
    }
    
    missing = []
    for name, command in requirements.items():
        result = run_command(command, check=False)
        if result is None or result.returncode != 0:
            missing.append(name)
        else:
            print(f"✅ {name} found")
    
    if missing:
        print(f"❌ Missing requirements: {', '.join(missing)}")
        return False
    
    return True

def setup_virtual_environment():
    """Create and activate virtual environment"""
    print("🐍 Setting up virtual environment...")
    
    backend_path = Path("backend")
    venv_path = backend_path / "venv"
    
    if not venv_path.exists():
        os.chdir(backend_path)
        run_command("python -m venv venv")
        os.chdir("..")
    else:
        print("✅ Virtual environment already exists")
    
    # Check if requirements are installed
    os.chdir(backend_path)
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip.exe"
        activate_script = venv_path / "Scripts" / "activate.bat"
    else:
        pip_path = venv_path / "bin" / "pip"
        activate_script = venv_path / "bin" / "activate"
    
    if pip_path.exists():
        print("📦 Installing Python dependencies...")
        run_command(f"{pip_path} install -r requirements.txt")
    
    os.chdir("..")
    
    print("✅ Virtual environment ready!")
    if sys.platform == "win32":
        print(f"To activate: {activate_script}")
    else:
        print(f"To activate: source {activate_script}")

def setup_environment_file():
    """Create .env file from template"""
    print("⚙️ Setting up environment configuration...")
    
    backend_path = Path("backend")
    env_example = backend_path / ".env.example"
    env_file = backend_path / ".env"
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from template...")
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ .env file created!")
        print("⚠️ Please edit backend/.env with your actual API keys and database URLs")
    else:
        print("✅ .env file already exists")

def check_docker():
    """Check if Docker is available"""
    print("🐳 Checking Docker availability...")
    
    result = run_command("docker --version", check=False)
    if result and result.returncode == 0:
        print("✅ Docker found")
        
        compose_result = run_command("docker-compose --version", check=False)
        if compose_result and compose_result.returncode == 0:
            print("✅ Docker Compose found")
            return True
        else:
            print("⚠️ Docker Compose not found")
    else:
        print("⚠️ Docker not found")
    
    return False

def main():
    """Main setup function"""
    print("🚀 Wanderlog AI Setup Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("backend").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Check requirements
    if not check_requirements():
        print("❌ Please install missing requirements and run again")
        sys.exit(1)
    
    # Setup virtual environment
    setup_virtual_environment()
    
    # Setup environment file
    setup_environment_file()
    
    # Check Docker
    has_docker = check_docker()
    
    print("\n🎉 Setup complete!")
    print("=" * 50)
    print("📋 Next steps:")
    print("1. Edit backend/.env with your API keys")
    print("2. Set up PostgreSQL and Redis")
    print("3. Run database migrations: cd backend && alembic upgrade head")
    
    if has_docker:
        print("4. Or use Docker: docker-compose up -d")
    
    print("5. Start the application: cd backend && uvicorn app.main:app --reload")
    print("6. Visit http://localhost:8000/api/docs")
    
    print("\n📖 For detailed instructions, see README.md")

if __name__ == "__main__":
    main()