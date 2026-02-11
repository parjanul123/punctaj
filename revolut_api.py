"""
Revolut API Integration Module
Handles authentication and transaction fetching from Revolut
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class RevolutAPI:
    """
    Integration with Revolut API for balance and transaction retrieval
    
    Revolut uses OAuth 2.0 for authentication
    Documentation: https://developer.revolut.com/
    """
    
    BASE_URL = "https://api.revolut.com"
    SANDBOX_URL = "https://sandbox-api.revolut.com"
    
    def __init__(self, access_token: str, sandbox: bool = False):
        """
        Initialize Revolut API client
        
        Args:
            access_token: Revolut OAuth access token (from user authorization)
            sandbox: Use sandbox environment for testing
        """
        self.access_token = access_token
        self.base_url = self.SANDBOX_URL if sandbox else self.BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        })
    
    def get_accounts(self) -> List[Dict]:
        """
        Fetch all Revolut accounts
        
        Returns:
            List of account dictionaries with id, name, currency, type
        """
        try:
            response = self.session.get(f"{self.base_url}/2.0/accounts")
            response.raise_for_status()
            accounts = response.json()
            logger.info(f"✅ Fetched {len(accounts)} Revolut accounts")
            return accounts
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error fetching Revolut accounts: {e}")
            return []
    
    def get_balance(self, account_id: Optional[str] = None) -> Dict:
        """
        Get balance for specific account or all accounts
        
        Args:
            account_id: Specific account ID (optional)
        
        Returns:
            Dictionary with balance information
        """
        try:
            if account_id:
                response = self.session.get(f"{self.base_url}/2.0/accounts/{account_id}")
            else:
                response = self.session.get(f"{self.base_url}/2.0/accounts")
            
            response.raise_for_status()
            data = response.json()
            logger.info(f"✅ Fetched Revolut balance")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error fetching Revolut balance: {e}")
            return {}
    
    def get_transactions(self, 
                        account_id: str,
                        limit: int = 100,
                        from_date: Optional[datetime] = None,
                        to_date: Optional[datetime] = None) -> List[Dict]:
        """
        Fetch transactions for an account
        
        Args:
            account_id: Account ID to fetch transactions for
            limit: Maximum number of transactions to return
            from_date: Start date filter (optional)
            to_date: End date filter (optional)
        
        Returns:
            List of transaction dictionaries
        """
        try:
            params = {"limit": limit}
            
            # Add date filters if provided
            if from_date:
                params["from"] = from_date.isoformat()
            if to_date:
                params["to"] = to_date.isoformat()
            
            response = self.session.get(
                f"{self.base_url}/2.0/accounts/{account_id}/transactions",
                params=params
            )
            response.raise_for_status()
            transactions = response.json()
            logger.info(f"✅ Fetched {len(transactions)} transactions from Revolut account {account_id}")
            return transactions
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error fetching Revolut transactions: {e}")
            return []
    
    def get_all_transactions_summary(self, days: int = 30) -> Dict:
        """
        Get summary of all transactions across all accounts for last N days
        
        Args:
            days: Number of days to look back
        
        Returns:
            Dictionary with account summaries
        """
        try:
            accounts = self.get_accounts()
            from_date = datetime.now() - timedelta(days=days)
            to_date = datetime.now()
            
            summary = {
                "fetch_date": datetime.now().isoformat(),
                "period_days": days,
                "accounts": []
            }
            
            for account in accounts:
                account_id = account.get("id")
                transactions = self.get_transactions(
                    account_id,
                    limit=100,
                    from_date=from_date,
                    to_date=to_date
                )
                
                # Calculate totals
                income = sum(t.get("amount", 0) for t in transactions 
                            if t.get("amount", 0) > 0)
                expenses = sum(t.get("amount", 0) for t in transactions 
                              if t.get("amount", 0) < 0)
                
                account["transactions"] = transactions
                account["summary"] = {
                    "total_transactions": len(transactions),
                    "income": income,
                    "expenses": abs(expenses),
                    "net": income + expenses  # Already negative for expenses
                }
                
                summary["accounts"].append({
                    "account_info": {k: v for k, v in account.items() 
                                    if k not in ["transactions"]},
                    "summary": account["summary"],
                    "transactions": transactions[:10]  # Return last 10 for preview
                })
            
            logger.info(f"✅ Generated Revolut summary for {len(accounts)} accounts")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error generating Revolut summary: {e}")
            return {}
    
    def validate_token(self) -> bool:
        """
        Validate if the access token is still valid
        
        Returns:
            True if token is valid, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/2.0/accounts")
            return response.status_code == 200
        except:
            return False


class RevolutAuthFlow:
    """
    Handle Revolut OAuth 2.0 authentication flow
    """
    
    CLIENT_ID = None  # Set from config
    CLIENT_SECRET = None  # Set from config
    REDIRECT_URI = "http://localhost:8080/callback"
    
    @staticmethod
    def get_authorization_url(client_id: str) -> str:
        """
        Generate the authorization URL for user to visit
        
        Args:
            client_id: Revolut application client ID
        
        Returns:
            Authorization URL
        """
        return (
            f"https://app.revolut.com/api/auth/login"
            f"?client_id={client_id}"
            f"&redirect_uri={RevolutAuthFlow.REDIRECT_URI}"
            f"&response_type=code"
            f"&scope=transactions:read accounts:read"
        )
    
    @staticmethod
    def exchange_code_for_token(code: str, client_id: str, client_secret: str) -> Optional[Dict]:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from redirect
            client_id: Revolut application client ID
            client_secret: Revolut application client secret
        
        Returns:
            Token response with access_token, or None if failed
        """
        try:
            response = requests.post(
                "https://api.revolut.com/auth/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret
                }
            )
            response.raise_for_status()
            token_data = response.json()
            logger.info("✅ Successfully exchanged code for Revolut token")
            return token_data
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error exchanging Revolut code for token: {e}")
            return None
