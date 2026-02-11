# 🏦 Bank API Integration Guide - BT (Banca Transilvania) & Revolut

## Overview
This integration allows you to automatically fetch and track:
- ✅ **Account balances** from both BT and Revolut
- ✅ **Transactions** with full details (date, amount, description)
- ✅ **Real-time sync** every 5 minutes
- ✅ **Export to CSV** for analysis
- ✅ **Multi-account support**

---

## 📦 Files Added

1. **`revolut_api.py`** - Revolut API integration
   - Handles OAuth 2.0 authentication
   - Fetches accounts, balances, and transactions
   
2. **`bt_api.py`** - BT API integration  
   - Implements PSD2 Open Banking standard
   - Connects to Banca Transilvania
   
3. **`bank_api_manager.py`** - Central manager
   - Unified interface for both banks
   - Token management and caching
   - Background sync thread
   
4. **`bank_transactions.py`** - UI Component
   - Beautiful tkinter UI panel
   - Connection management
   - Transaction display and export

---

## 🔧 Setup Instructions

### Step 1: Update Requirements
Add these packages to `requirements.txt`:

```txt
requests>=2.31.0
schedule>=1.2.0
```

Install them:
```bash
pip install requests schedule
```

### Step 2: Create BT Developer Account

1. Go to: **https://developer.bancatransilvania.ro/**
2. Register for a developer account
3. Create a new application
4. Get your:
   - **Client ID**
   - **Client Secret**
   - **Redirect URI** (use: `http://localhost:8080/callback`)

### Step 3: Create Revolut Developer Account

1. Go to: **https://developer.revolut.com/**
2. Sign in with your Revolut account
3. Create a new application
4. Get your:
   - **Client ID**
   - **Client Secret**
   - **Redirect URI** (use: `http://localhost:8080/callback`)

### Step 4: Integrate into Main App

Add this to your main `punctaj.py` file:

```python
# At the top of imports
from bank_transactions import BankTransactionsPanel
from bank_api_manager import BankAPIManager

# In your main window setup (around where you create other frames):
# Create a new tab or frame for bank transactions
bank_frame = ttk.Frame(notebook)
notebook.add(bank_frame, text="💰 Bank Transactions")

# Initialize bank manager
bank_manager = BankAPIManager()

# Create transactions panel
transactions_panel = BankTransactionsPanel(bank_frame, bank_manager)
```

---

## 🚀 Usage

### Manual Sync
1. Click **"🔄 Sync Now"** to fetch latest data
2. Connection status shows in real-time

### Connect Banks
1. Click **"Connect BT"** or **"Connect Revolut"**
2. Enter your credentials (Client ID, Client Secret)
3. Click **"Open Authorization URL"**
4. Complete authorization in your browser
5. Copy the authorization code
6. Paste and click **"Connect"**

### View Transactions
- See recent transactions in the table
- Click **"📊 View Details"** for full transaction list
- Click **"📥 Export to CSV"** to download

### Auto-Sync
The app automatically syncs every 5 minutes in background

---

## 📊 Data Structure

### Balance Summary
```json
{
  "bt": {
    "total_balance": 5000.50,
    "currency": "RON",
    "accounts": 2
  },
  "revolut": {
    "total_balance": 1200.00,
    "accounts": 1
  }
}
```

### Transactions
```json
{
  "date": "2026-02-04",
  "bank": "BT",
  "account_name": "Main Account",
  "amount": -50.00,
  "description": "Grocery shopping",
  "balance": 5000.50
}
```

---

## 🔐 Security

- Tokens are stored in: `%APPDATA%\PunctajManager\bank_data\bank_tokens.json`
- Permissions are restricted to owner read/write only (600)
- Never commits secrets to git
- Uses HTTPS for all API calls
- Supports OAuth 2.0 industry standard

---

## 🐛 Troubleshooting

### "Connection refused"
- Check if internet connection is active
- Verify API endpoint URLs are correct
- Check if BT/Revolut APIs are accessible

### "Invalid token"
- Authorization code expired (usually 10 minutes)
- Restart the connection process
- Verify Client ID and Secret are correct

### "No transactions"
- Accounts might be empty
- Check date range (default: 30-90 days)
- Verify permissions in OAuth scopes

### Logging
All operations are logged. Check:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📝 Configuration Options

In `bank_api_manager.py`, you can customize:

```python
# Sync interval (seconds)
self.sync_interval = 300  # Default: 5 minutes

# Days to look back for transactions
days_history = 90  # Default for BT
days_history = 30  # Default for Revolut
```

---

## 🌐 API Documentation

### BT (Banca Transilvania)
- **Docs**: https://developer.bancatransilvania.ro/
- **Standard**: PSD2 Open Banking
- **Rate Limit**: Varies by account type
- **Sandbox**: https://sandbox-api.bancatransilvania.ro

### Revolut
- **Docs**: https://developer.revolut.com/
- **Rate Limit**: 100 requests/minute
- **Sandbox**: https://sandbox-api.revolut.com
- **Accounts**: Personal, Business

---

## 📋 Quick Reference

### Connection Flow
1. User clicks "Connect BT"
2. App generates OAuth URL
3. User authorizes on BT website
4. BT redirects with auth code
5. App exchanges code for token
6. Token stored locally
7. API ready to use

### Data Flow
```
BT/Revolut APIs
    ↓
BankAPIManager (caching)
    ↓
BankTransactionsPanel (UI)
    ↓
Transactions Table
```

---

## 📞 Support

For issues:
1. Check logs in `bank_data/` folder
2. Verify credentials in developer portal
3. Test API endpoints directly with curl/Postman
4. Check rate limits and quotas

---

## 🎯 Future Enhancements

- [ ] Category-based expense tracking
- [ ] Monthly budgets and alerts
- [ ] Recurring transaction detection
- [ ] Multi-currency support
- [ ] Charts and analytics
- [ ] Email notifications
- [ ] Automatic categorization (ML)
- [ ] Bank transfer automation

---

## 📄 License

Same as main Punctaj application

---

**Created**: February 4, 2026  
**Version**: 1.0  
**Status**: Ready for integration
