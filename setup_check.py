"""
Setup and Initialization Script
Run this script to verify your installation and setup
"""
import sys
import os

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python version {version.major}.{version.minor} is too old. Need 3.9+")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    required = [
        'streamlit',
        'pandas',
        'numpy',
        'sqlalchemy',
        'psycopg2',
        'plotly',
        'prophet',
        'scikit-learn',
        'streamlit_option_menu',
        'streamlit_lottie'
    ]
    
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - NOT INSTALLED")
            missing.append(package)
    
    return len(missing) == 0


def check_env_file():
    """Check if .env file exists"""
    if os.path.exists('.env'):
        print("✓ .env file found")
        return True
    else:
        print("✗ .env file not found")
        print("  → Copy .env.example to .env and configure your settings")
        return False


def check_database():
    """Check database connection"""
    try:
        from database import init_db
        init_db()
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {str(e)}")
        print("  → Check your PostgreSQL installation and .env configuration")
        return False


def main():
    """Main setup check"""
    print("=" * 60)
    print("InsightIQ - Setup Verification")
    print("=" * 60)
    print()
    
    print("Checking Python version...")
    py_ok = check_python_version()
    print()
    
    print("Checking dependencies...")
    deps_ok = check_dependencies()
    print()
    
    print("Checking configuration...")
    env_ok = check_env_file()
    print()
    
    print("Checking database...")
    db_ok = check_database()
    print()
    
    print("=" * 60)
    if py_ok and deps_ok and env_ok and db_ok:
        print("✓ Setup verification PASSED!")
        print()
        print("You're ready to run the application:")
        print("  streamlit run app.py")
    else:
        print("✗ Setup verification FAILED!")
        print()
        print("Please fix the issues above and run this script again.")
        if not deps_ok:
            print()
            print("To install missing dependencies:")
            print("  pip install -r requirements.txt")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
