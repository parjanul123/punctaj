"""
Quick demo/test of Bank API Integration
Run this to verify everything works
"""

import logging
from bank_api_manager import BankAPIManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_bank_manager():
    """Test BankAPIManager functionality"""
    
    print("\n" + "="*80)
    print("🏦 BANK API INTEGRATION TEST")
    print("="*80 + "\n")
    
    # Initialize manager
    print("📌 Initializing Bank API Manager...")
    manager = BankAPIManager()
    print("✅ Bank API Manager initialized\n")
    
    # Check connection status
    print("🔍 Checking connection status...")
    status = manager.get_connection_status()
    print(f"  BT connected: {status['bt']['connected']}")
    print(f"  Revolut connected: {status['revolut']['connected']}\n")
    
    # Get authorization URLs (for testing)
    print("📋 Authorization URLs (for testing):")
    print(f"  BT: https://developer.bancatransilvania.ro/")
    print(f"  Revolut: https://developer.revolut.com/\n")
    
    # Simulate token setting (you would do this after OAuth flow)
    print("⚙️ Token Management:")
    print("  Use set_bt_token() to save BT token")
    print("  Use set_revolut_token() to save Revolut token\n")
    
    # Show data directory
    print(f"📁 Data directory: {manager.config_dir}")
    print(f"   Token file: {manager.tokens_file}\n")
    
    print("="*80)
    print("TEST COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Register at BT and Revolut developer portals")
    print("2. Get your Client ID and Client Secret")
    print("3. Connect through the UI in Punctaj Manager")
    print("4. Transactions will sync automatically\n")

if __name__ == "__main__":
    test_bank_manager()
