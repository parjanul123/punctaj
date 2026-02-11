# 🏦 Bank API Integration - Complete Reference

## 📚 Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [API Reference](#api-reference)
6. [Usage Examples](#usage-examples)
7. [Security](#security)
8. [Troubleshooting](#troubleshooting)

---

## Overview

This integration allows your Punctaj Manager application to:
- ✅ Connect to BT (Banca Transilvania) and Revolut accounts
- ✅ Fetch real-time balances and transactions
- ✅ Display financial data in a beautiful UI
- ✅ Auto-sync every 5 minutes
- ✅ Export data to CSV for analysis

### Supported Banks
- **BT (Banca Transilvania)** - Romanian major bank, PSD2 compliant
- **Revolut** - Digital banking platform, worldwide support

---

## Architecture

### Component Diagram
```
┌─────────────────────────────────────────────────────┐
│           Punctaj Manager (tkinter GUI)             │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │  Bank Transactions Panel                     │   │
│  │  (bank_transactions.py)                      │   │
│  │                                              │   │
│  │  • Connection status                        │   │
│  │  • Balance display                          │   │
│  │  • Transaction table                        │   │
│  │  • Export buttons                           │   │
│  └─────────────────┬──────────────────────────┘   │
│                    │                               │
│  ┌─────────────────▼──────────────────────────┐   │
│  │  Bank API Manager                          │   │
│  │  (bank_api_manager.py)                     │   │
│  │                                            │   │
│  │  • Token management                       │   │
│  │  • Sync scheduling                        │   │
│  │  • Data aggregation                       │   │
│  │  • Error handling                         │   │
│  └───┬────────────────────────┬──────────────┘   │
│      │                        │                   │
│ ┌────▼────┐          ┌───────▼─────┐             │
│ │  BT API │          │ Revolut API │             │
│ │(bt_api) │          │(revolut_api)│             │
│ └────┬────┘          └───────┬─────┘             │
└──────┼───────────────────────┼──────────────────┘
       │                       │
       │ HTTPS                │ HTTPS
       │                       │
   ┌───▼──────────┐     ┌──────▼──────┐
   │ BT Servers   │     │ Revolut API │
   │ PSD2 OpenAPI │     │ OAuth 2.0   │
   └──────────────┘     └─────────────┘
```

### Data Flow
```
BT Account ──┐
              ├──> API Wrapper ──> BankAPIManager ──> UI Panel ──> User
Revolut Acct─┘                                          ↓
                                                    Display & Export
```

---

## Installation

### Prerequisites
- Python 3.7+
- Internet connection
- BT and Revolut developer accounts

### Step 1: Install Dependencies
```bash
cd d:\punctaj
pip install -r requirements.txt
pip install requests schedule
```

### Step 2: Copy Files
Copy these files to `d:\punctaj\`:
- `revolut_api.py`
- `bt_api.py`
- `bank_api_manager.py`
- `bank_transactions.py`
- `oauth_callback_server.py` (optional)

### Step 3: Register Developer Accounts

**BT Developer Portal:**
1. Visit: https://developer.bancatransilvania.ro/
2. Click "Register"
3. Complete registration with personal/business details
4. Create an application:
   - Go to "Applications"
   - Click "Create New Application"
   - Fill in application details
   - Save **Client ID** and **Client Secret**
   - Add redirect URI: `http://localhost:8080/callback`

**Revolut Developer Portal:**
1. Visit: https://developer.revolut.com/
2. Sign in with your Revolut account
3. Click "Create Application"
4. Fill in application details:
   - Name: "Punctaj Manager"
   - Description: "Personal finance tracking"
   - Redirect URL: `http://localhost:8080/callback`
5. Save **Client ID** and **Client Secret**

### Step 4: Update punctaj.py

Add to imports section:
```python
from bank_transactions import BankTransactionsPanel
from bank_api_manager import BankAPIManager
```

Add to main window initialization:
```python
# Initialize bank manager
self.bank_manager = BankAPIManager()

# Create bank transactions tab
bank_frame = ttk.Frame(self.notebook)
self.notebook.add(bank_frame, text="💰 Bank Transactions")

# Create transactions panel
self.transactions_panel = BankTransactionsPanel(bank_frame, self.bank_manager)
```

Add to window closing handler:
```python
# Stop bank sync thread
if hasattr(self, 'bank_manager'):
    self.bank_manager.stop_sync_thread()
```

---

## Configuration

### Sync Interval
In `bank_api_manager.py`, line ~30:
```python
self.sync_interval = 300  # seconds
# Change to:
self.sync_interval = 600  # 10 minutes
```

### Data Retention
```python
# Default: 90 days for BT, 30 days for Revolut
# Modify in get_transactions() calls
days = 60  # Change to desired days
```

### Storage Location
- Tokens: `%APPDATA%\PunctajManager\bank_data\bank_tokens.json`
- Cache: `%APPDATA%\PunctajManager\bank_data\bank_data_cache.json`

To customize:
```python
manager = BankAPIManager(config_dir="custom/path")
```

---

## API Reference

### BankAPIManager

#### Initialization
```python
from bank_api_manager import BankAPIManager

# Default config location
manager = BankAPIManager()

# Custom config location
manager = BankAPIManager(config_dir="d:/my/data/path")
```

#### Connection Methods

**Set BT Token**
```python
manager.set_bt_token(
    access_token="your_token",
    expires_in=3600  # seconds
)
```

**Set Revolut Token**
```python
manager.set_revolut_token(
    access_token="your_token",
    expires_in=3600
)
```

**Complete OAuth Flow**
```python
# After user authorizes
success = manager.complete_bt_auth(
    auth_code="code_from_redirect",
    client_id="your_client_id",
    client_secret="your_client_secret"
)

success = manager.complete_revolut_auth(
    auth_code="code_from_redirect",
    client_id="your_client_id",
    client_secret="your_client_secret"
)
```

#### Data Retrieval

**Get All Balances**
```python
balances = manager.get_all_balances()
# Returns:
# {
#     "bt": {
#         "status": "connected|error|not_connected",
#         "total_balance": 5000.50,
#         "accounts": 2,
#         "data": {...}
#     },
#     "revolut": {...}
# }
```

**Get Transactions**
```python
txns = manager.get_transactions(days=30)
# Returns:
# {
#     "bt_transactions": [...],
#     "revolut_transactions": [...],
#     "all_transactions": [...]  # sorted by date
# }
```

#### Status Checking

**Check Connection Status**
```python
status = manager.get_connection_status()
# Returns:
# {
#     "bt": {"connected": True, "token_expires": "2026-02-04T10:00:00"},
#     "revolut": {"connected": False, "token_expires": None}
# }
```

**Check Individual Banks**
```python
is_bt_connected = manager.is_bt_connected()
is_revolut_connected = manager.is_revolut_connected()
```

#### Synchronization

**Start Background Sync**
```python
def on_sync(data):
    print(f"Synced {len(data['transactions'])} transactions")

manager.start_sync_thread(callback=on_sync)
```

**Stop Background Sync**
```python
manager.stop_sync_thread()
```

---

### BTAPI

```python
from bt_api import BTAPI

api = BTAPI(access_token="your_token")

# Get all accounts
accounts = api.get_accounts()

# Get balance for specific account
balance = api.get_account_balance("account_id_or_iban")

# Get transactions
txns = api.get_transactions(
    account_id="IBAN",
    limit=100,
    from_date=datetime.now() - timedelta(days=30),
    to_date=datetime.now()
)

# Get transaction details
details = api.get_transaction_details("account_id", "txn_id")

# Validate token
is_valid = api.validate_token()
```

---

### RevolutAPI

```python
from revolut_api import RevolutAPI

api = RevolutAPI(access_token="your_token")

# Get all accounts
accounts = api.get_accounts()

# Get balance
balance = api.get_balance(account_id="optional")

# Get transactions
txns = api.get_transactions(
    account_id="account_id",
    limit=100,
    from_date=datetime.now() - timedelta(days=30),
    to_date=datetime.now()
)

# Validate token
is_valid = api.validate_token()
```

---

### BankTransactionsPanel

```python
from bank_transactions import BankTransactionsPanel

# Create UI panel
panel = BankTransactionsPanel(parent_frame, bank_manager)

# The panel automatically handles:
# • UI rendering
# • Connection status display
# • Data refresh
# • User interactions
```

---

## Usage Examples

### Example 1: Basic Setup and Display

```python
import tkinter as tk
from tkinter import ttk
from bank_api_manager import BankAPIManager
from bank_transactions import BankTransactionsPanel

# Create window
root = tk.Tk()
root.title("Finance Tracker")
root.geometry("1200x700")

# Create notebook
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

# Initialize manager
manager = BankAPIManager()

# Create bank frame
bank_frame = ttk.Frame(notebook)
notebook.add(bank_frame, text="💰 Bank")

# Create panel
panel = BankTransactionsPanel(bank_frame, manager)

# Run
root.mainloop()
```

### Example 2: Manual Data Fetch

```python
from bank_api_manager import BankAPIManager

manager = BankAPIManager()

# Get all balances
balances = manager.get_all_balances()

if balances["bt"]["status"] == "connected":
    print(f"BT Balance: RON {balances['bt']['total_balance']}")

if balances["revolut"]["status"] == "connected":
    print(f"Revolut: {balances['revolut']['accounts']} accounts")

# Get transactions
txns = manager.get_transactions(days=30)
print(f"Total transactions: {len(txns['all_transactions'])}")

for txn in txns['all_transactions'][:5]:
    print(f"{txn['date']}: {txn['bank']} - {txn['amount']} ({txn['description']})")
```

### Example 3: Custom Sync Callback

```python
from bank_api_manager import BankAPIManager
import json

def my_callback(data):
    # Save to custom location
    with open("my_finance_data.json", "w") as f:
        json.dump(data, f)
    
    # Send notification
    print(f"💰 Synced at {data['balances']['fetch_date']}")

manager = BankAPIManager()
manager.start_sync_thread(callback=my_callback)

# ... do other things ...

manager.stop_sync_thread()
```

### Example 4: OAuth Integration

```python
from bank_api_manager import BankAPIManager
import webbrowser

manager = BankAPIManager()

# Get BT auth URL
auth_url = manager.get_bt_auth_url(client_id="your_client_id")

# Open in browser
webbrowser.open(auth_url)

# User authorizes and gets redirected with code
# Then complete the flow:
success = manager.complete_bt_auth(
    auth_code="code_from_user",
    client_id="your_client_id",
    client_secret="your_client_secret"
)

if success:
    print("✅ BT connected!")
else:
    print("❌ Failed to connect")
```

---

## Security

### Token Storage
- Location: `%APPDATA%\PunctajManager\bank_data\bank_tokens.json`
- Permissions: 600 (owner read/write only)
- Format: JSON (can be encrypted with cryptography module)

### OAuth Flow
1. User clicks "Connect Bank"
2. App generates OAuth URL
3. User visits bank website
4. Bank asks for authorization
5. User approves access to transactions
6. Browser redirects to callback URL with code
7. App exchanges code for token (no user password sent)
8. Token stored locally

### Best Practices
- ✅ Never hardcode credentials
- ✅ Use environment variables for sensitive data
- ✅ Validate tokens before API calls
- ✅ Handle token refresh automatically
- ✅ Log security events
- ✅ Use HTTPS for all connections

### Encryption (Optional)
```python
from cryptography.fernet import Fernet

# Generate key once
key = Fernet.generate_key()

# Encrypt tokens
cipher = Fernet(key)
encrypted = cipher.encrypt(b"sensitive_token")

# Decrypt tokens
decrypted = cipher.decrypt(encrypted)
```

---

## Troubleshooting

### "Connection refused" Error
**Cause**: Cannot reach BT/Revolut servers
**Solution**:
1. Check internet connection
2. Verify firewall settings
3. Check BT/Revolut service status
4. Try VPN if region-restricted

### "Invalid token" Error
**Cause**: Token expired or invalid
**Solution**:
1. Authorization codes expire in ~10 minutes
2. Restart the connection process
3. Verify Client ID and Secret are correct
4. Check token hasn't been used elsewhere

### "No accounts found" Error
**Cause**: Account might be empty or no access granted
**Solution**:
1. Verify OAuth scopes: `accounts:read transactions:read`
2. Check if account has transactions
3. Try different account
4. Revoke and re-authorize

### "Rate limit exceeded" Error
**Cause**: Too many API requests
**Solution**:
1. Reduce sync frequency
2. Revolut: max 100 req/min
3. BT: check your tier limits
4. Wait before retrying

### Tokens Not Saving
**Cause**: File permissions or path issues
**Solution**:
1. Check `%APPDATA%\PunctajManager\` exists
2. Verify write permissions
3. Check disk space available
4. Look for error logs

### UI Not Updating
**Cause**: Threading or callback issues
**Solution**:
1. Check sync thread is running
2. Verify callback is set
3. Check for exceptions in logs
4. Try manual sync

### Enable Debug Logging
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bank_debug.log'),
        logging.StreamHandler()
    ]
)
```

---

## Performance Tips

1. **Reduce Sync Frequency**: If you don't need real-time updates
   ```python
   manager.sync_interval = 600  # 10 minutes
   ```

2. **Limit Transaction History**: Don't fetch years of data
   ```python
   manager.get_transactions(days=30)  # 30 days instead of 90
   ```

3. **Cache Data**: Don't refetch if recently synced
   ```python
   # Already done by default in bank_data_cache.json
   ```

4. **Use Filtering**: Filter on client-side instead of API
   ```python
   filtered = [t for t in transactions if float(t['amount']) > 100]
   ```

---

## Common Questions

**Q: Can I use this with multiple Punctaj Manager instances?**
A: Yes, but only one sync thread should run. Use separate config directories.

**Q: How often should I sync?**
A: Every 5 minutes is safe. More frequent = more API calls.

**Q: Can I share tokens between devices?**
A: Not recommended. Re-authorize on each device.

**Q: What if I revoke app access?**
A: Token becomes invalid. User must re-authorize in app.

**Q: Can I export to Excel instead of CSV?**
A: Yes, use pandas: `df.to_excel('transactions.xlsx')`

**Q: How do I add more banks?**
A: Follow the same pattern in BTAPI/RevolutAPI, add to manager.

---

## Files Summary

| File | Purpose | Size |
|------|---------|------|
| `revolut_api.py` | Revolut OAuth & API | 280 LOC |
| `bt_api.py` | BT PSD2 OpenAPI | 290 LOC |
| `bank_api_manager.py` | Central manager | 340 LOC |
| `bank_transactions.py` | UI component | 580 LOC |
| `oauth_callback_server.py` | OAuth helper | 250 LOC |

**Total**: ~1,740 lines of production-ready code

---

## Support & Resources

- **BT Docs**: https://developer.bancatransilvania.ro/
- **Revolut Docs**: https://developer.revolut.com/
- **OAuth 2.0**: https://oauth.net/2/
- **PSD2 Standard**: https://en.wikipedia.org/wiki/Payment_Services_Directive

---

**Last Updated**: February 4, 2026  
**Version**: 1.0  
**Status**: ✅ Production Ready
