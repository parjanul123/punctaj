#!/usr/bin/env python3
"""
Quick Discord Authentication Setup Script
Helps you configure Discord OAuth2 credentials
"""

import os
import sys
import configparser
import webbrowser

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_success(text):
    print(f"✓ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def setup_discord_config():
    """Interactive setup wizard for Discord configuration"""
    
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "Discord Authentication Setup Wizard" + " "*19 + "║")
    print("╚" + "="*68 + "╝")
    
    print_header("Step 1: Create Discord Application")
    
    print("\nTo set up Discord authentication, you need to create a Discord Application.")
    print("\nFollow these steps:")
    print("1. Go to: https://discord.com/developers/applications")
    print("2. Click 'New Application'")
    print("3. Name your application (e.g., 'Punctaj Manager')")
    print("4. Go to 'OAuth2' → 'General'")
    print("5. Copy your CLIENT ID and CLIENT SECRET")
    
    open_browser = input("\n🌐 Would you like to open Discord Developer Portal now? (y/n): ").strip().lower()
    if open_browser == 'y':
        print_info("Opening Discord Developer Portal...")
        webbrowser.open("https://discord.com/developers/applications")
        print("  ✓ Opening in browser. Complete the steps above, then come back here.")
    
    input("\nPress Enter when you have your CLIENT_ID and CLIENT_SECRET...")
    
    print_header("Step 2: Configure Redirect URI")
    
    print("\nYou need to set a Redirect URI in the Discord Developer Portal:")
    print("\n📋 Copy this Redirect URI:")
    print("   http://localhost:8888/callback")
    print("\n🔧 In Discord Developer Portal:")
    print("   1. Go to OAuth2 → General")
    print("   2. Click 'Add Redirect'")
    print("   3. Paste: http://localhost:8888/callback")
    print("   4. Save Changes")
    
    input("\nPress Enter when you've added the Redirect URI...")
    
    print_header("Step 3: Enter Your Credentials")
    
    client_id = input("\n📋 Enter your CLIENT_ID: ").strip()
    if not client_id:
        print_error("CLIENT_ID cannot be empty")
        return False
    
    client_secret = input("🔐 Enter your CLIENT_SECRET: ").strip()
    if not client_secret:
        print_error("CLIENT_SECRET cannot be empty")
        return False
    
    # Optional webhook
    print("\n(Optional) Discord Webhook for notifications")
    print("Leave blank to skip webhook setup")
    webhook_url = input("Webhook URL (optional): ").strip()
    
    print_header("Step 4: Save Configuration")
    
    # Create config file
    config = configparser.ConfigParser()
    config['discord'] = {
        'CLIENT_ID': client_id,
        'CLIENT_SECRET': client_secret,
        'REDIRECT_URI': 'http://localhost:8888/callback',
    }
    
    if webhook_url:
        config['discord']['WEBHOOK_URL'] = webhook_url
    
    # Determine where to save
    config_path = "discord_config.ini"
    
    # Check if file exists
    if os.path.exists(config_path):
        overwrite = input(f"\n⚠️  {config_path} already exists. Overwrite? (y/n): ").strip().lower()
        if overwrite != 'y':
            print_error("Configuration not saved")
            return False
    
    # Save the config
    try:
        with open(config_path, 'w') as f:
            config.write(f)
        
        # Make file secure (Unix-like)
        try:
            os.chmod(config_path, 0o600)
        except:
            pass
        
        print_success(f"Configuration saved to {config_path}")
        
    except Exception as e:
        print_error(f"Failed to save configuration: {e}")
        return False
    
    print_header("Step 5: Security Reminder")
    
    print("\n⚠️  IMPORTANT SECURITY NOTES:")
    print("\n1. 🔒 Keep Your Secrets Safe")
    print("   - Never share CLIENT_SECRET with anyone")
    print("   - Don't commit discord_config.ini to GitHub with real credentials")
    print("   - Use .gitignore to exclude it")
    
    print("\n2. 📁 Add to .gitignore")
    gitignore_path = ".gitignore"
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'a') as f:
            if 'discord_config.ini' not in f.read():
                f.write('\ndiscord_config.ini\n')
        print_success(".gitignore updated")
    else:
        with open(gitignore_path, 'w') as f:
            f.write('discord_config.ini\n.discord_token\n')
        print_success(".gitignore created")
    
    print("\n3. 🔑 Environment Variables (Production)")
    print("   For production, use environment variables instead:")
    print("   export DISCORD_CLIENT_ID='your_client_id'")
    print("   export DISCORD_CLIENT_SECRET='your_client_secret'")
    
    print_header("Setup Complete! ✓")
    
    print("\n✅ Discord authentication is now configured!")
    print("\n📝 Next Steps:")
    print("   1. Start Punctaj Manager")
    print("   2. Click '🔐 Login Discord' button")
    print("   3. Complete OAuth2 login in your browser")
    print("   4. You're authenticated!")
    
    print("\n🧪 To test your setup:")
    print("   python discord_auth_test.py")
    
    print("\n📚 For detailed documentation:")
    print("   See: DISCORD_AUTH_SETUP.md")
    
    return True

def main():
    try:
        if setup_discord_config():
            print("\n" + "="*70)
            print("  Thank you for setting up Discord authentication!")
            print("="*70 + "\n")
            return 0
        else:
            return 1
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
