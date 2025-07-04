#!/usr/bin/env python
"""
Medicine Stock Management System Setup Script

This script helps set up the Django project with all necessary configurations.
"""

import os
import sys
import subprocess
import secrets
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e.stderr}")
        return None

def generate_secret_key():
    """Generate a Django secret key."""
    return secrets.token_urlsafe(50)

def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists() and env_example.exists():
        print("\nCreating .env file from template...")
        
        # Read template
        with open(env_example, 'r') as f:
            content = f.read()
        
        # Replace placeholder secret key
        secret_key = generate_secret_key()
        content = content.replace('your-secret-key-here-change-this-in-production', secret_key)
        
        # Write .env file
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✓ .env file created with generated secret key")
        print("  Please update database credentials in .env file")
    else:
        print("\n.env file already exists or template not found")

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")

def install_dependencies():
    """Install Python dependencies."""
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python dependencies"
    )

def setup_database():
    """Set up the database."""
    commands = [
        (f"{sys.executable} manage.py makemigrations", "Creating database migrations"),
        (f"{sys.executable} manage.py migrate", "Applying database migrations"),
    ]
    
    for command, description in commands:
        result = run_command(command, description)
        if result is None:
            return False
    return True

def create_superuser():
    """Create a superuser account."""
    print("\nCreating superuser account...")
    print("Please provide the following information:")
    
    try:
        result = subprocess.run(
            [sys.executable, 'manage.py', 'createsuperuser'],
            check=True
        )
        print("✓ Superuser created successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to create superuser")
        return False
    except KeyboardInterrupt:
        print("\n✗ Superuser creation cancelled")
        return False

def collect_static_files():
    """Collect static files."""
    return run_command(
        f"{sys.executable} manage.py collectstatic --noinput",
        "Collecting static files"
    )

def populate_sample_data():
    """Populate database with sample data."""
    response = input("\nWould you like to populate the database with sample data? (y/N): ")
    if response.lower() in ['y', 'yes']:
        return run_command(
            f"{sys.executable} manage.py populate_sample_data",
            "Populating database with sample data"
        )
    return True

def main():
    """Main setup function."""
    print("Medicine Stock Management System Setup")
    print("=" * 40)
    
    # Check Python version
    check_python_version()
    
    # Create .env file
    create_env_file()
    
    # Install dependencies
    if install_dependencies() is None:
        print("\n✗ Setup failed during dependency installation")
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        print("\n✗ Setup failed during database setup")
        print("Please check your database configuration in .env file")
        sys.exit(1)
    
    # Collect static files
    if collect_static_files() is None:
        print("\n⚠ Warning: Failed to collect static files")
    
    # Create superuser
    print("\n" + "="*40)
    print("SUPERUSER CREATION")
    print("="*40)
    if not create_superuser():
        print("\n⚠ Warning: Superuser not created")
        print("You can create one later using: python manage.py createsuperuser")
    
    # Populate sample data
    if populate_sample_data() is None:
        print("\n⚠ Warning: Failed to populate sample data")
    
    # Final instructions
    print("\n" + "="*40)
    print("SETUP COMPLETE!")
    print("="*40)
    print("\nNext steps:")
    print("1. Update database credentials in .env file if needed")
    print("2. Run the development server: python manage.py runserver")
    print("3. Open your browser to: http://127.0.0.1:8000/")
    print("4. Login with your superuser credentials")
    print("\nFor production deployment:")
    print("1. Set DEBUG=False in .env")
    print("2. Configure a production database")
    print("3. Set up a web server (nginx + gunicorn)")
    print("4. Configure SSL certificates")
    print("\nDocumentation: See README.md for detailed instructions")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Setup failed with error: {e}")
        sys.exit(1)