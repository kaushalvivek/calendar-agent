#!/usr/bin/env python3
"""
Setup script for Calendar Agent
Handles initial configuration and authentication
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_header():
    print("""
╔═══════════════════════════════════════════════════════════╗
║                  📅 Calendar Agent Setup                  ║
║           Your Intelligent Scheduling Assistant           ║
╚═══════════════════════════════════════════════════════════╝
    """)

def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--quiet"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        print("   Try running: pip install -r requirements.txt")
        sys.exit(1)

def check_credentials():
    """Check if Google OAuth credentials exist"""
    creds_path = Path("credentials.json")
    
    if creds_path.exists():
        print("✅ Credentials file found")
        return True
    
    print("\n⚠️  No credentials.json file found")
    print("\nTo set up Google Calendar API:")
    print("1. Go to: https://console.cloud.google.com")
    print("2. Create a new project or select existing")
    print("3. Enable Calendar API:")
    print("   https://console.cloud.google.com/apis/library/calendar-json.googleapis.com")
    print("4. Create OAuth 2.0 credentials:")
    print("   - Go to Credentials page")
    print("   - Click 'Create Credentials' → 'OAuth client ID'")
    print("   - Choose 'Desktop app'")
    print("   - Download JSON file")
    print("5. Save the file as 'credentials.json' in this directory")
    
    response = input("\nHave you completed these steps? (y/n): ")
    if response.lower() != 'y':
        print("\n📋 Setup incomplete. Please complete the steps above and run setup again.")
        sys.exit(0)
    
    if not creds_path.exists():
        print("❌ Still no credentials.json found. Please ensure the file is in the current directory.")
        sys.exit(1)
    
    return True

def authenticate():
    """Run initial authentication"""
    print("\n🔐 Running authentication...")
    print("   A browser window will open for Google sign-in")
    
    try:
        from calendar_manager import CalendarManager
        manager = CalendarManager()
        print("✅ Authentication successful!")
        
        # Test connection
        events = manager.get_today_events()
        print(f"✅ Connected to calendar - found {len(events)} events today")
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("\nTroubleshooting:")
        print("- Ensure you're signed into the correct Google account")
        print("- Check that Calendar API is enabled")
        print("- Try deleting token.pickle and running setup again")
        sys.exit(1)

def create_shortcuts():
    """Create convenient shell aliases"""
    print("\n🎯 Creating shortcuts...")
    
    shortcuts = """
# Calendar Agent Shortcuts
alias cal='python cal_cli.py'
alias cal-today='python cal_cli.py today'
alias cal-analyze='python cal_cli.py analyze'
alias cal-rank='python cal_cli.py rank'
alias cal-focus='python cal_cli.py focus'
"""
    
    print("\nAdd these aliases to your shell config (~/.bashrc or ~/.zshrc):")
    print(shortcuts)
    
    response = input("\nWould you like to save these to a file? (y/n): ")
    if response.lower() == 'y':
        with open("calendar_shortcuts.sh", "w") as f:
            f.write(shortcuts)
        print("✅ Saved to calendar_shortcuts.sh")
        print("   Run: source calendar_shortcuts.sh")

def test_installation():
    """Run basic tests to verify setup"""
    print("\n🧪 Testing installation...")
    
    tests = [
        ("Import calendar_manager", lambda: __import__("calendar_manager")),
        ("Import cal_cli", lambda: __import__("cal_cli")),
        ("Check timezone support", lambda: __import__("pytz")),
    ]
    
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"✅ {test_name}")
        except Exception as e:
            print(f"❌ {test_name}: {e}")
            return False
    
    return True

def print_next_steps():
    """Show next steps and usage examples"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║         ✅ Calendar Agent Setup Complete!                 ║
╚═══════════════════════════════════════════════════════════╝

🚀 Quick Start with Calendar Agent:

  View today's schedule:
    python cal_cli.py today

  Analyze your calendar:
    python cal_cli.py analyze

  Rank meetings by importance:
    python cal_cli.py rank

  Create focus time:
    python cal_cli.py focus "Deep Work" 14:00 17:00

  Decline a meeting:
    python cal_cli.py decline "Meeting Name"

📚 Documentation:
  See README.md for full documentation and examples

💡 Pro Tips:
  - Use 'python cal_cli.py --help' for all commands
  - Check calendar_manager.py for programmatic usage
  - Customize ranking keywords in calendar_manager.py
    """)

def main():
    """Main setup flow"""
    print_header()
    
    # Check environment
    check_python_version()
    
    # Install dependencies
    install_dependencies()
    
    # Check and set up credentials
    if check_credentials():
        authenticate()
    
    # Test installation
    if test_installation():
        create_shortcuts()
        print_next_steps()
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)