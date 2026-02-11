#!/usr/bin/env python3
"""
Discord Authentication Testing Tool
Test and debug Discord OAuth2 configuration
"""

import os
import sys
import json
from discord_auth import DiscordAuth, DiscordWebhook
import configparser

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_status(status, message):
    symbol = "✓" if status else "❌"
    print(f"{symbol} {message}")

def load_config():
    """Load Discord configuration"""
    print_header("Loading Discord Configuration")
    
    config_paths = [
        "discord_config.ini",
        os.path.join(os.path.dirname(__file__), "discord_config.ini"),
        os.path.join(os.path.expanduser("~"), "Documents", "PunctajManager", "discord_config.ini"),
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            print_status(True, f"Found config at: {config_path}")
            
            config = configparser.ConfigParser()
            config.read(config_path)
            
            if 'discord' in config:
                return {
                    'CLIENT_ID': config.get('discord', 'CLIENT_ID', fallback=None),
                    'CLIENT_SECRET': config.get('discord', 'CLIENT_SECRET', fallback=None),
                    'REDIRECT_URI': config.get('discord', 'REDIRECT_URI', fallback='http://localhost:8888/callback'),
                    'WEBHOOK_URL': config.get('discord', 'WEBHOOK_URL', fallback=None),
                }
    
    print_status(False, "Discord configuration not found")
    return None

def check_config(config):
    """Validate configuration"""
    print_header("Validating Configuration")
    
    if not config:
        print_status(False, "No configuration loaded")
        return False
    
    client_id = config.get('CLIENT_ID')
    client_secret = config.get('CLIENT_SECRET')
    
    if not client_id:
        print_status(False, "CLIENT_ID is empty")
    else:
        print_status(True, f"CLIENT_ID: {client_id[:20]}...")
    
    if not client_secret:
        print_status(False, "CLIENT_SECRET is empty")
    else:
        print_status(True, f"CLIENT_SECRET: {client_secret[:20]}...")
    
    print_status(True, f"REDIRECT_URI: {config.get('REDIRECT_URI')}")
    
    if config.get('WEBHOOK_URL'):
        print_status(True, f"WEBHOOK_URL: {config['WEBHOOK_URL'][:50]}...")
    else:
        print_status(False, "WEBHOOK_URL not configured (optional)")
    
    return bool(client_id and client_secret)

def check_stored_token():
    """Check if stored token exists"""
    print_header("Checking Stored Tokens")
    
    token_file = os.path.join(
        os.path.expanduser("~"),
        "Documents",
        "PunctajManager",
        ".discord_token"
    )
    
    if os.path.exists(token_file):
        print_status(True, f"Token file found: {token_file}")
        
        try:
            with open(token_file, 'r') as f:
                token_data = json.load(f)
            
            user = token_data.get('user_info', {})
            username = user.get('username', 'Unknown')
            
            print_status(True, f"Stored user: {username}")
            print_status(True, f"Has access token: {'access_token' in token_data and bool(token_data['access_token'])}")
            print_status(True, f"Has refresh token: {'refresh_token' in token_data and bool(token_data['refresh_token'])}")
            
        except Exception as e:
            print_status(False, f"Error reading token: {e}")
    else:
        print_status(False, f"No stored token found at {token_file}")

def test_oauth_login(config):
    """Test OAuth login"""
    print_header("Testing OAuth2 Login")
    
    if not config.get('CLIENT_ID') or not config.get('CLIENT_SECRET'):
        print_status(False, "Configuration incomplete - skipping login test")
        return False
    
    try:
        auth = DiscordAuth(
            client_id=config['CLIENT_ID'],
            client_secret=config['CLIENT_SECRET'],
            redirect_uri=config['REDIRECT_URI']
        )
        
        # Check if already authenticated
        if auth.is_authenticated():
            user = auth.get_user_info()
            username = user.get('username', 'Unknown')
            print_status(True, f"Already authenticated as: {username}")
            return True
        
        # Prompt for login
        print("\n" + "="*60)
        print("  Please complete authentication in the browser")
        print("="*60)
        print("\nStarting OAuth2 server and opening browser...\n")
        
        if auth.start_oauth_server():
            user = auth.get_user_info()
            username = user.get('username', 'Unknown')
            user_id = user.get('id', 'N/A')
            email = user.get('email', 'N/A')
            
            print_status(True, f"OAuth Login successful!")
            print(f"\n  Username: {username}")
            print(f"  User ID: {user_id}")
            print(f"  Email: {email}")
            
            return True
        else:
            print_status(False, "OAuth Login failed or timed out")
            return False
            
    except Exception as e:
        print_status(False, f"Error during OAuth test: {e}")
        return False

def test_webhook(config):
    """Test webhook notification"""
    print_header("Testing Discord Webhook")
    
    webhook_url = config.get('WEBHOOK_URL') if config else None
    
    if not webhook_url:
        print_status(False, "WEBHOOK_URL not configured - skipping webhook test")
        return True
    
    try:
        webhook = DiscordWebhook(webhook_url)
        
        success = webhook.send_message(
            "✓ Punctaj Manager - Discord authentication test successful!",
            title="Test Message"
        )
        
        if success:
            print_status(True, "Webhook test message sent successfully!")
            return True
        else:
            print_status(False, "Webhook message failed")
            return False
            
    except Exception as e:
        print_status(False, f"Webhook test error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "Discord Authentication Diagnostic Tool" + " "*10 + "║")
    print("╚" + "="*58 + "╝")
    
    # Load configuration
    config = load_config()
    
    if not config:
        print("\n⚠️  No Discord configuration found!")
        print("\nTo set up Discord authentication:")
        print("1. Copy discord_config.ini to your project")
        print("2. Get credentials from https://discord.com/developers/applications")
        print("3. Fill in CLIENT_ID and CLIENT_SECRET")
        print("4. Run this tool again")
        sys.exit(1)
    
    # Validate configuration
    if not check_config(config):
        print("\n⚠️  Configuration is incomplete or invalid")
        sys.exit(1)
    
    # Check stored tokens
    check_stored_token()
    
    # Ask what to test
    print("\n" + "="*60)
    print("  What would you like to test?")
    print("="*60)
    print("1. OAuth2 Login (requires browser)")
    print("2. Webhook Notification")
    print("3. Full Test Suite")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        test_oauth_login(config)
    elif choice == "2":
        test_webhook(config)
    elif choice == "3":
        test_oauth_login(config)
        test_webhook(config)
    else:
        print("\nExiting...")
        sys.exit(0)
    
    print("\n" + "="*60)
    print("  Diagnostic Complete")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
