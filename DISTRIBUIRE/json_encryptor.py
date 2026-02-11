# -*- coding: utf-8 -*-
"""
JSON File Encryptor Module
Protects JSON files from unauthorized modification outside the application
Provides transparent encryption/decryption for data files
"""

import json
import os
from cryptography.fernet import Fernet
from pathlib import Path
import base64
import hashlib

class JSONEncryptor:
    """Encrypts and decrypts JSON files to prevent modification outside the app"""
    
    def __init__(self, key_file: str = ".secure_key"):
        """
        Initialize encryptor with encryption key
        
        Args:
            key_file: File to store encryption key (hidden)
        """
        self.key_file = key_file
        self.cipher = self._load_or_create_key()
    
    def _load_or_create_key(self):
        """Load existing key or create new one"""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            # Save key with restricted permissions (Windows)
            with open(self.key_file, 'wb') as f:
                f.write(key)
            # Hide file on Windows
            try:
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(self.key_file, 2)  # 2 = Hidden
            except:
                pass  # Non-Windows system
        
        return Fernet(key)
    
    def save_json_encrypted(self, file_path: str, data: dict) -> bool:
        """
        Save JSON data as encrypted file
        
        Args:
            file_path: Path to save (will add .enc extension)
            data: Dictionary to encrypt
            
        Returns:
            True if successful
        """
        try:
            # Convert to JSON string
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            json_bytes = json_str.encode('utf-8')
            
            # Encrypt
            encrypted = self.cipher.encrypt(json_bytes)
            
            # Save as .enc file
            enc_path = file_path.replace('.json', '.enc')
            if not enc_path.endswith('.enc'):
                enc_path += '.enc'
            
            # Create directory if needed
            os.makedirs(os.path.dirname(enc_path), exist_ok=True)
            
            with open(enc_path, 'wb') as f:
                f.write(encrypted)
            
            # Delete original JSON if it exists
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return True
        except Exception as e:
            print(f"❌ Encryption error: {e}")
            return False
    
    def load_json_encrypted(self, file_path: str) -> dict:
        """
        Load encrypted JSON file
        
        Args:
            file_path: Path to encrypted file (.enc)
            
        Returns:
            Decrypted dictionary or empty dict if failed
        """
        try:
            # Try .enc file first
            enc_path = file_path.replace('.json', '.enc')
            if not enc_path.endswith('.enc'):
                enc_path += '.enc'
            
            if not os.path.exists(enc_path):
                # Fallback to regular JSON if .enc doesn't exist
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                return {}
            
            # Read encrypted file
            with open(enc_path, 'rb') as f:
                encrypted = f.read()
            
            # Decrypt
            decrypted = self.cipher.decrypt(encrypted)
            json_str = decrypted.decode('utf-8')
            
            # Parse JSON
            return json.loads(json_str)
        except Exception as e:
            print(f"❌ Decryption error: {e}")
            return {}
    
    def migrate_to_encrypted(self, file_path: str) -> bool:
        """
        Convert existing JSON file to encrypted format
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            True if successful
        """
        try:
            if not os.path.exists(file_path):
                return False
            
            # Read JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Save encrypted
            return self.save_json_encrypted(file_path, data)
        except Exception as e:
            print(f"❌ Migration error: {e}")
            return False


# Global encryptor instance
_encryptor = None

def get_encryptor(key_file: str = ".secure_key") -> JSONEncryptor:
    """Get or create global encryptor instance"""
    global _encryptor
    if _encryptor is None:
        _encryptor = JSONEncryptor(key_file)
    return _encryptor


def save_protected_json(file_path: str, data: dict, encrypt: bool = True) -> bool:
    """
    Convenient function to save JSON with optional encryption
    
    Args:
        file_path: Path to save
        data: Data to save
        encrypt: Whether to encrypt (default True)
        
    Returns:
        True if successful
    """
    if encrypt:
        encryptor = get_encryptor()
        return encryptor.save_json_encrypted(file_path, data)
    else:
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ Save error: {e}")
            return False


def load_protected_json(file_path: str, decrypt: bool = True) -> dict:
    """
    Convenient function to load JSON with optional decryption
    
    Args:
        file_path: Path to load
        decrypt: Whether to decrypt (default True)
        
    Returns:
        Loaded data or empty dict if failed
    """
    if decrypt:
        encryptor = get_encryptor()
        return encryptor.load_json_encrypted(file_path)
    else:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}


if __name__ == "__main__":
    # Test encryption
    print("🔐 JSON Encryptor Module Test")
    
    # Create test data
    test_data = {
        "employees": [
            {"id": 1, "name": "John", "rank": "Officer"},
            {"id": 2, "name": "Jane", "rank": "Sergeant"}
        ],
        "timestamp": "2026-02-02T10:30:00"
    }
    
    # Save encrypted
    encryptor = get_encryptor()
    print("\n1. Saving encrypted JSON...")
    encryptor.save_json_encrypted("test_data.json", test_data)
    print("   ✓ Saved as test_data.enc")
    
    # Show that .enc file is unreadable
    print("\n2. Content of .enc file (unreadable):")
    with open("test_data.enc", 'rb') as f:
        content = f.read()
        print(f"   {content[:50]}... (encrypted binary)")
    
    # Load decrypted
    print("\n3. Loading decrypted JSON...")
    loaded_data = encryptor.load_json_encrypted("test_data.json")
    print(f"   ✓ Loaded: {loaded_data}")
    
    print("\n✅ Encryption test complete!")
