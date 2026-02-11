"""
BT (BRD) API Integration Module
Handles authentication and transaction fetching from Banca Transilvania (BT)
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import base64

logger = logging.getLogger(__name__)

class BTAPI:
    """
    Integration with Banca Transilvania (BT) Open Banking API
    
    BT uses PSD2 Open Banking standard with OAuth 2.0
    Documentation: https://developer.bancatransilvania.ro/
    """
    
    BASE_URL = "https://api.bancatransilvania.ro"
    SANDBOX_URL = "https://sandbox-api.bancatransilvania.ro"
    
    def __init__(self, access_token: str, client_id: str = None, sandbox: bool = False):
        """
        Initialize BT API client
        
        Args:
            access_token: OAuth access token from BT authorization
            client_id: BT application client ID (for some endpoints)
            sandbox: Use sandbox environment for testing
        """
        self.access_token = access_token
        self.client_id = client_id
        self.base_url = self.SANDBOX_URL if sandbox else self.BASE_URL
        self.session = requests.Session()
        self._setup_headers()
    
    def _setup_headers(self):
        """Setup request headers with authorization"""
        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest"
        })
        if self.client_id:
            self.session.headers["X-Client-ID"] = self.client_id
    
    def get_accounts(self) -> List[Dict]:
        """
        Fetch all BT accounts accessible to the user
        
        Returns:
            List of account dictionaries
        """
        try:
            response = self.session.get(
                f"{self.base_url}/v1/accounts",
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            accounts = data.get("accounts", [])
            logger.info(f"✅ Fetched {len(accounts)} BT accounts")
            return accounts
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error fetching BT accounts: {e}")
            return []
    
    def get_account_balance(self, account_id: str) -> Dict:
        """
        Get balance for a specific account
        
        Args:
            account_id: BT account ID (IBAN)
        
        Returns:
            Dictionary with balance information
        """
        try:
            # Some APIs use IBAN directly, others use account ID
            response = self.session.get(
                f"{self.base_url}/v1/accounts/{account_id}/balances",
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Fetched balance for BT account {account_id}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error fetching BT balance for {account_id}: {e}")
            return {}
    
    def get_transactions(self,
                        account_id: str,
                        limit: int = 90,
                        from_date: Optional[datetime] = None,
                        to_date: Optional[datetime] = None) -> List[Dict]:
        """
        Fetch transactions for a specific account
        
        Args:
            account_id: BT account ID (IBAN)
            limit: Maximum number of transactions
            from_date: Start date for filtering
            to_date: End date for filtering
        
        Returns:
            List of transaction dictionaries
        """
        try:
            # Default to last 90 days if no dates provided
            if not from_date:
                from_date = datetime.now() - timedelta(days=90)
            if not to_date:
                to_date = datetime.now()
            
            params = {
                "dateFrom": from_date.strftime("%Y-%m-%d"),
                "dateTo": to_date.strftime("%Y-%m-%d"),
                "limit": limit
            }
            
            response = self.session.get(
                f"{self.base_url}/v1/accounts/{account_id}/transactions",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            transactions = data.get("transactions", [])
            logger.info(f"✅ Fetched {len(transactions)} transactions from BT account {account_id}")
            return transactions
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error fetching BT transactions for {account_id}: {e}")
            return []
    
    def get_transaction_details(self, account_id: str, transaction_id: str) -> Dict:
        """
        Get detailed information about a specific transaction
        
        Args:
            account_id: BT account ID
            transaction_id: Transaction ID
        
        Returns:
            Detailed transaction information
        """
        try:
            response = self.session.get(
                f"{self.base_url}/v1/accounts/{account_id}/transactions/{transaction_id}",
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Fetched details for BT transaction {transaction_id}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error fetching BT transaction details: {e}")
            return {}
    
    def get_all_transactions_summary(self, days: int = 90) -> Dict:
        """
        Get comprehensive summary of all BT accounts and transactions
        
        Args:
            days: Number of days to look back
        
        Returns:
            Dictionary with complete summary
        """
        try:
            accounts = self.get_accounts()
            from_date = datetime.now() - timedelta(days=days)
            to_date = datetime.now()
            
            summary = {
                "fetch_date": datetime.now().isoformat(),
                "bank": "BT (Banca Transilvania)",
                "period_days": days,
                "total_balance": 0,
                "accounts": []
            }
            
            for account in accounts:
                account_id = account.get("id") or account.get("iban")
                
                # Get balance
                balance_data = self.get_account_balance(account_id)
                current_balance = balance_data.get("balances", [{}])[0].get("amount", 0)
                
                # Get transactions
                transactions = self.get_transactions(
                    account_id,
                    limit=100,
                    from_date=from_date,
                    to_date=to_date
                )
                
                # Calculate totals
                income = sum(t.get("amount", 0) for t in transactions 
                            if t.get("amount", 0) > 0)
                expenses = sum(abs(t.get("amount", 0)) for t in transactions 
                              if t.get("amount", 0) < 0)
                
                account_summary = {
                    "account_id": account_id,
                    "iban": account.get("iban", ""),
                    "name": account.get("name", ""),
                    "currency": account.get("currency", "RON"),
                    "current_balance": current_balance,
                    "transactions_count": len(transactions),
                    "income": income,
                    "expenses": expenses,
                    "net": income - expenses,
                    "transactions": transactions[:10]  # Preview
                }
                
                summary["accounts"].append(account_summary)
                summary["total_balance"] += current_balance
            
            logger.info(f"✅ Generated BT summary for {len(accounts)} accounts")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error generating BT summary: {e}")
            return {}
    
    def validate_token(self) -> bool:
        """
        Validate if the access token is still valid
        
        Returns:
            True if token is valid, False otherwise
        """
        try:
            response = self.session.get(
                f"{self.base_url}/v1/accounts",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False


class BTAuthFlow:
    """
    Handle BT OAuth 2.0 and PSD2 authentication flow
    """
    
    CLIENT_ID = None
    CLIENT_SECRET = None
    REDIRECT_URI = "http://localhost:8080/callback"
    
    @staticmethod
    def get_authorization_url(client_id: str, sandbox: bool = False) -> str:
        """
        Generate the authorization URL for user to visit
        
        Args:
            client_id: BT application client ID
            sandbox: Use sandbox environment
        
        Returns:
            Authorization URL
        """
        base = "https://sandbox.bancatransilvania.ro" if sandbox else "https://online.bancatransilvania.ro"
        return (
            f"{base}/oauth/authorize"
            f"?client_id={client_id}"
            f"&redirect_uri={BTAuthFlow.REDIRECT_URI}"
            f"&response_type=code"
            f"&scope=accounts:read transactions:read"
            f"&state=state123"
        )
    
    @staticmethod
    def exchange_code_for_token(code: str, 
                                client_id: str, 
                                client_secret: str,
                                sandbox: bool = False) -> Optional[Dict]:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from redirect
            client_id: BT application client ID
            client_secret: BT application client secret
            sandbox: Use sandbox environment
        
        Returns:
            Token response with access_token, or None if failed
        """
        try:
            base = "https://sandbox-api.bancatransilvania.ro" if sandbox else "https://api.bancatransilvania.ro"
            
            # BT uses Basic Auth for token endpoint
            auth_string = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
            
            headers = {
                "Authorization": f"Basic {auth_string}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": BTAuthFlow.REDIRECT_URI,
                "client_id": client_id
            }
            
            response = requests.post(
                f"{base}/oauth/token",
                headers=headers,
                data=data,
                timeout=10
            )
            response.raise_for_status()
            
            token_data = response.json()
            logger.info("✅ Successfully exchanged code for BT token")
            return token_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error exchanging BT code for token: {e}")
            return None
