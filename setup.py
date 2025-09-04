"""
Setup script for AI Personalized Learning System
"""

import subprocess
import sys
import os


def run_command(command, cwd=None):
    """Run a command and handle errors"""
    try:
        result = subprocess.run(command, shell=True, check=True, cwd=cwd, capture_output=True, text=True)
        print(f"✓ {command}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"✗ {command}")
        print(f"Error: {e.stderr}")
        return None


def setup_backend():
    """Setup backend dependencies and database"""
    print("🚀 Setting up backend...")
    
    # Install Python dependencies
    print("Installing Python dependencies...")
    run_command(f"{sys.executable} -m pip install --upgrade pip")
    run_command(f"{sys.executable} -m pip install -r requirements.txt")
    
    # Create database and sample data
    print("Creating database and sample data...")
    run_command(f"{sys.executable} app/data/sample_data.py")
    
    print("✅ Backend setup complete!")


def setup_frontend():
    """Setup frontend dependencies"""
    print("🎨 Setting up frontend...")
    
    frontend_path = "./frontend"
    
    if not os.path.exists(frontend_path):
        print(f"Frontend directory not found at {frontend_path}")
        return False
    
    # Install npm dependencies
    print("Installing npm dependencies...")
    run_command("npm install", cwd=frontend_path)
    
    print("✅ Frontend setup complete!")
    return True


def main():
    """Main setup function"""
    print("🤖 AI Personalized Learning System Setup")
    print("=" * 50)
    
    # Setup backend
    setup_backend()
    
    # Setup frontend
    frontend_success = setup_frontend()
    
    print("\n" + "=" * 50)
    print("🎉 Setup Complete!")
    print("\nNext steps:")
    print("1. Start the backend server:")
    print("   python main.py")
    print("\n2. Start the frontend development server:")
    if frontend_success:
        print("   cd frontend && npm run dev")
    else:
        print("   Frontend setup failed - check frontend directory")
    
    print("\n3. Open your browser to:")
    print("   Backend API: http://localhost:8000")
    print("   Frontend App: http://localhost:3000")
    print("   API Docs: http://localhost:8000/docs")
    
    print("\n4. Demo login credentials:")
    print("   Username: alice_chen, bob_garcia, or carol_smith")
    print("   Password: password123")


if __name__ == "__main__":
    main()