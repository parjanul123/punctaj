#!/usr/bin/env python3
"""
Generate and setup encryption key for users_permissions.json
Run this if you get encryption errors
"""

import os
from pathlib import Path

def setup_encryption_key():
    """Generate new encryption key"""
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║       🔐 SETUP ENCRYPTION KEY                                      ║
║         Generate new encryption key for data security              ║
╚════════════════════════════════════════════════════════════════════╝
""")
    
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        print("❌ cryptography module not found")
        print("   Install with: pip install cryptography")
        return False
    
    data_dir = Path("data")
    key_file = data_dir / ".encryption_key"
    
    print(f"\nGenerating new encryption key...")
    
    # Generate key
    key = Fernet.generate_key().decode()
    
    # Create data dir if needed
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Write key
    with open(key_file, 'w') as f:
        f.write(key)
    
    # Set permissions (600 - read/write for owner only)
    os.chmod(str(key_file), 0o600)
    
    print(f"""
✅ ENCRYPTION KEY CREATED

📂 File: {key_file}
🔐 Permissions: 600 (owner read/write only)
🔑 Type: Fernet (AES-128)

Key (base64):
{key}

⚠️  IMPORTANT:
  • This key is unique to this device
  • Do NOT share it
  • Keep it safe - if lost, encrypted data cannot be read
  • But cloud copy is always available (re-sync and re-encrypt)
    """)
    
    return True

if __name__ == "__main__":
    setup_encryption_key()
