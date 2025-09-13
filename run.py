#!/usr/bin/env python3
"""
Startup script for the AI Loan Recommendation System
"""
import os
import sys
import subprocess
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        "fastapi", "uvicorn", "langchain", "langchain-anthropic", 
        "chromadb", "sentence-transformers", "pydantic", "python-dotenv"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall with: pip install -r requirements.txt")
        return False
    
    return True

def check_environment():
    """Check if environment is properly configured"""
    env_file = Path(".env")
    if not env_file.exists():
        print("Warning: .env file not found. Copy .env.example to .env and add your API keys.")
        return False
    
    # Check for API key
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Warning: ANTHROPIC_API_KEY not found in .env file.")
        print("Add your Anthropic API key to continue.")
        return False
    
    return True

def setup_data():
    """Set up sample data if needed"""
    data_dir = Path("data/raw")
    if not data_dir.exists() or not list(data_dir.glob("*.txt")):
        print("Setting up sample bank documents...")
        try:
            from src.utils.sample_data import create_sample_bank_documents, create_sample_client_profiles
            create_sample_bank_documents()
            create_sample_client_profiles()
            print("✓ Sample data created successfully")
        except Exception as e:
            print(f"Error creating sample data: {e}")
            return False
    
    return True

def run_application():
    """Run the FastAPI application"""
    try:
        print("Starting AI Loan Recommendation System...")
        print("API will be available at: http://localhost:8000")
        print("Press Ctrl+C to stop the server")
        print("-" * 50)
        
        os.chdir("src/api")
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
        
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
    except Exception as e:
        print(f"Error running application: {e}")

def main():
    """Main startup function"""
    print("🤖 AI Loan Recommendation System")
    print("=" * 40)
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✓ Dependencies OK")
    
    # Check environment
    print("Checking environment...")
    if not check_environment():
        print("⚠️  Environment issues detected. Please fix and try again.")
        sys.exit(1)
    print("✓ Environment OK")
    
    # Setup data
    print("Setting up data...")
    if not setup_data():
        sys.exit(1)
    print("✓ Data setup OK")
    
    print("\n🚀 All systems ready!")
    print("\nSystem Features:")
    print("  • AI-powered loan recommendations")
    print("  • 3-second processing time")
    print("  • 90%+ accuracy target")
    print("  • Multi-stage validation")
    print("  • Built-in web interface")
    
    input("\nPress Enter to start the server...")
    run_application()

if __name__ == "__main__":
    main()