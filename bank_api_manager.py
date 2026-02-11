"""
Bank API Manager
Central module to manage both BT and Revolut integrations
Handles token storage, refreshing, and unified transaction display
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import threading
import schedule

from revolut_api import RevolutAPI, RevolutAuthFlow
from bt_api import BTAPI, BTAuthFlow

logger = logging.getLogger(__name__)

class BankAPIManager:
    """
    Unified manager for all bank integrations
    Handles authentication, token management, and data aggregation
    """
    
    def __init__(self, config_dir: str = None):
        """
        Initialize Bank API Manager
        
        Args:
            config_dir: Directory to store bank credentials and tokens
        """
        if config_dir is None:
            # Default to APPDATA\PunctajManager\bank_data
            config_dir = os.path.join(
                os.environ.get("APPDATA", os.path.expanduser("~")),
                "PunctajManager",
                "bank_data"
            )
        
        self.config_dir = config_dir
        Path(self.config_dir).mkdir(parents=True, exist_ok=True)
        
        self.credentials_file = os.path.join(config_dir, "bank_credentials.json")
        self.tokens_file = os.path.join(config_dir, "bank_tokens.json")
        
        self.bt_api: Optional[BTAPI] = None
        self.revolut_api: Optional[RevolutAPI] = None
        
        self.sync_thread: Optional[threading.Thread] = None
        self.sync_running = False
        self.sync_interval = 300  # Sync every 5 minutes
        
        # Load existing tokens
        self._load_tokens()
        self._init_apis()
    
    def _load_tokens(self):
        """Load saved bank tokens from file"""
        if os.path.exists(self.tokens_file):
            try:
                with open(self.tokens_file, 'r') as f:
                    self.tokens = json.load(f)
                logger.info("✅ Loaded bank tokens from file")
                return
            except Exception as e:
                logger.error(f"❌ Error loading tokens: {e}")
        
        self.tokens = {
            "bt": {"access_token": None, "expires_at": None},
            "revolut": {"access_token": None, "expires_at": None}
        }
    
    def _save_tokens(self):
        """Save bank tokens to secure file"""
        try:
            # Create parent directories if needed
            os.makedirs(os.path.dirname(self.tokens_file), exist_ok=True)
            
            with open(self.tokens_file, 'w') as f:
                json.dump(self.tokens, f, indent=2)
            
            # Set restrictive permissions (owner read/write only)
            os.chmod(self.tokens_file, 0o600)
            logger.info("✅ Saved bank tokens securely")
        except Exception as e:
            logger.error(f"❌ Error saving tokens: {e}")
    
    def _init_apis(self):
        """Initialize API clients with stored tokens"""
        # Initialize BT API
        if self.tokens["bt"]["access_token"]:
            try:
                self.bt_api = BTAPI(
                    access_token=self.tokens["bt"]["access_token"],
                    sandbox=False
                )
                logger.info("✅ BT API initialized")
            except Exception as e:
                logger.error(f"❌ Error initializing BT API: {e}")
        
        # Initialize Revolut API
        if self.tokens["revolut"]["access_token"]:
            try:
                self.revolut_api = RevolutAPI(
                    access_token=self.tokens["revolut"]["access_token"],
                    sandbox=False
                )
                logger.info("✅ Revolut API initialized")
            except Exception as e:
                logger.error(f"❌ Error initializing Revolut API: {e}")
    
    def set_bt_token(self, access_token: str, expires_in: int = 3600):
        """
        Set or update BT access token
        
        Args:
            access_token: OAuth access token
            expires_in: Token expiration time in seconds
        """
        self.tokens["bt"]["access_token"] = access_token
        self.tokens["bt"]["expires_at"] = (
            datetime.now() + timedelta(seconds=expires_in)
        ).isoformat()
        
        self.bt_api = BTAPI(access_token=access_token)
        self._save_tokens()
        logger.info("✅ BT token set and saved")
    
    def set_revolut_token(self, access_token: str, expires_in: int = 3600):
        """
        Set or update Revolut access token
        
        Args:
            access_token: OAuth access token
            expires_in: Token expiration time in seconds
        """
        self.tokens["revolut"]["access_token"] = access_token
        self.tokens["revolut"]["expires_at"] = (
            datetime.now() + timedelta(seconds=expires_in)
        ).isoformat()
        
        self.revolut_api = RevolutAPI(access_token=access_token)
        self._save_tokens()
        logger.info("✅ Revolut token set and saved")
    
    def get_bt_auth_url(self, client_id: str) -> str:
        """
        Get BT authorization URL for user
        
        Args:
            client_id: BT application client ID
        
        Returns:
            Authorization URL
        """
        return BTAuthFlow.get_authorization_url(client_id)
    
    def get_revolut_auth_url(self, client_id: str) -> str:
        """
        Get Revolut authorization URL for user
        
        Args:
            client_id: Revolut application client ID
        
        Returns:
            Authorization URL
        """
        return RevolutAuthFlow.get_authorization_url(client_id)
    
    def complete_bt_auth(self, auth_code: str, client_id: str, client_secret: str) -> bool:
        """
        Complete BT OAuth flow with authorization code
        
        Args:
            auth_code: Authorization code from callback
            client_id: BT client ID
            client_secret: BT client secret
        
        Returns:
            True if successful, False otherwise
        """
        try:
            token_data = BTAuthFlow.exchange_code_for_token(
                auth_code, client_id, client_secret
            )
            
            if token_data and "access_token" in token_data:
                self.set_bt_token(
                    token_data["access_token"],
                    token_data.get("expires_in", 3600)
                )
                return True
            
            logger.error("❌ Invalid token response from BT")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error completing BT auth: {e}")
            return False
    
    def complete_revolut_auth(self, auth_code: str, client_id: str, client_secret: str) -> bool:
        """
        Complete Revolut OAuth flow with authorization code
        
        Args:
            auth_code: Authorization code from callback
            client_id: Revolut client ID
            client_secret: Revolut client secret
        
        Returns:
            True if successful, False otherwise
        """
        try:
            token_data = RevolutAuthFlow.exchange_code_for_token(
                auth_code, client_id, client_secret
            )
            
            if token_data and "access_token" in token_data:
                self.set_revolut_token(
                    token_data["access_token"],
                    token_data.get("expires_in", 3600)
                )
                return True
            
            logger.error("❌ Invalid token response from Revolut")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error completing Revolut auth: {e}")
            return False
    
    def get_all_balances(self) -> Dict:
        """
        Get all account balances from both banks
        
        Returns:
            Dictionary with balances from both banks
        """
        balances = {
            "fetch_date": datetime.now().isoformat(),
            "bt": None,
            "revolut": None
        }
        
        # Fetch BT balances
        if self.bt_api:
            try:
                bt_data = self.bt_api.get_all_transactions_summary(days=90)
                balances["bt"] = {
                    "status": "connected",
                    "total_balance": bt_data.get("total_balance", 0),
                    "accounts": len(bt_data.get("accounts", [])),
                    "data": bt_data
                }
            except Exception as e:
                logger.error(f"❌ Error fetching BT balances: {e}")
                balances["bt"] = {"status": "error", "error": str(e)}
        else:
            balances["bt"] = {"status": "not_connected"}
        
        # Fetch Revolut balances
        if self.revolut_api:
            try:
                revolut_data = self.revolut_api.get_all_transactions_summary(days=30)
                balances["revolut"] = {
                    "status": "connected",
                    "accounts": len(revolut_data.get("accounts", [])),
                    "data": revolut_data
                }
            except Exception as e:
                logger.error(f"❌ Error fetching Revolut balances: {e}")
                balances["revolut"] = {"status": "error", "error": str(e)}
        else:
            balances["revolut"] = {"status": "not_connected"}
        
        return balances
    
    def get_transactions(self, days: int = 30) -> Dict:
        """
        Get aggregated transactions from all connected banks
        
        Args:
            days: Number of days to look back
        
        Returns:
            Dictionary with transactions from all banks
        """
        transactions = {
            "fetch_date": datetime.now().isoformat(),
            "period_days": days,
            "bt_transactions": [],
            "revolut_transactions": [],
            "all_transactions": []
        }
        
        # Fetch BT transactions
        if self.bt_api:
            try:
                bt_data = self.bt_api.get_all_transactions_summary(days=days)
                for account in bt_data.get("accounts", []):
                    for txn in account.get("transactions", []):
                        txn["bank"] = "BT"
                        txn["account_name"] = account.get("name", "BT Account")
                        transactions["bt_transactions"].append(txn)
                logger.info(f"✅ Fetched {len(transactions['bt_transactions'])} BT transactions")
            except Exception as e:
                logger.error(f"❌ Error fetching BT transactions: {e}")
        
        # Fetch Revolut transactions
        if self.revolut_api:
            try:
                revolut_data = self.revolut_api.get_all_transactions_summary(days=days)
                for account in revolut_data.get("accounts", []):
                    for txn in account.get("summary", {}).get("transactions", []):
                        txn["bank"] = "Revolut"
                        txn["account_name"] = account.get("account_info", {}).get("name", "Revolut")
                        transactions["revolut_transactions"].append(txn)
                logger.info(f"✅ Fetched {len(transactions['revolut_transactions'])} Revolut transactions")
            except Exception as e:
                logger.error(f"❌ Error fetching Revolut transactions: {e}")
        
        # Combine all transactions and sort by date
        transactions["all_transactions"] = sorted(
            transactions["bt_transactions"] + transactions["revolut_transactions"],
            key=lambda x: x.get("date", ""),
            reverse=True
        )
        
        return transactions
    
    def start_sync_thread(self, callback=None):
        """
        Start background thread to periodically sync bank data
        
        Args:
            callback: Optional callback function to call after each sync
        """
        if self.sync_running:
            logger.warning("Sync thread already running")
            return
        
        self.sync_running = True
        self.sync_callback = callback
        
        def sync_loop():
            scheduler = schedule.Scheduler()
            scheduler.every(self.sync_interval).seconds.do(self._sync_data)
            
            while self.sync_running:
                scheduler.run_pending()
                time.sleep(1)
        
        self.sync_thread = threading.Thread(daemon=True, target=sync_loop)
        self.sync_thread.start()
        logger.info("✅ Bank sync thread started")
    
    def stop_sync_thread(self):
        """Stop background sync thread"""
        self.sync_running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        logger.info("✅ Bank sync thread stopped")
    
    def _sync_data(self):
        """Internal method to fetch and cache bank data"""
        try:
            data = {
                "balances": self.get_all_balances(),
                "transactions": self.get_transactions(days=30)
            }
            
            # Save to cache file
            cache_file = os.path.join(self.config_dir, "bank_data_cache.json")
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info("✅ Bank data synced successfully")
            
            # Call callback if provided
            if hasattr(self, 'sync_callback') and self.sync_callback:
                self.sync_callback(data)
        
        except Exception as e:
            logger.error(f"❌ Error syncing bank data: {e}")
    
    def is_bt_connected(self) -> bool:
        """Check if BT is connected and token is valid"""
        return self.bt_api is not None and self.bt_api.validate_token()
    
    def is_revolut_connected(self) -> bool:
        """Check if Revolut is connected and token is valid"""
        return self.revolut_api is not None and self.revolut_api.validate_token()
    
    def get_connection_status(self) -> Dict:
        """Get status of all bank connections"""
        return {
            "bt": {
                "connected": self.is_bt_connected(),
                "token_expires": self.tokens["bt"].get("expires_at")
            },
            "revolut": {
                "connected": self.is_revolut_connected(),
                "token_expires": self.tokens["revolut"].get("expires_at")
            }
        }


# Import time for sync thread
import time
