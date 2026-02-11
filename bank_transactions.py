"""
Bank Transactions UI Module
Provides UI components to display and manage bank transactions
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from datetime import datetime
from typing import Dict, List, Optional, Callable
import threading
from bank_api_manager import BankAPIManager
import logging

logger = logging.getLogger(__name__)

class BankTransactionsPanel:
    """
    UI Panel for displaying and managing bank transactions
    Can be embedded in the main Punctaj application
    """
    
    def __init__(self, parent_frame: tk.Frame, bank_manager: BankAPIManager = None):
        """
        Initialize Bank Transactions Panel
        
        Args:
            parent_frame: Parent tkinter frame to embed panel in
            bank_manager: BankAPIManager instance
        """
        self.parent = parent_frame
        self.bank_manager = bank_manager or BankAPIManager()
        
        self.current_transactions = []
        self.sync_thread = None
        self.is_running = False
        
        self._setup_ui()
        self._load_initial_data()
    
    def _setup_ui(self):
        """Setup UI components"""
        # Main container
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ========== CONNECTION STATUS FRAME ==========
        status_frame = ttk.LabelFrame(self.main_frame, text="🏦 Bank Connections", padding=10)
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # BT Connection
        self.bt_status_label = ttk.Label(
            status_frame,
            text="🔴 BT: Not Connected",
            font=("Arial", 10)
        )
        self.bt_status_label.pack(side=tk.LEFT, padx=20)
        
        self.bt_connect_btn = ttk.Button(
            status_frame,
            text="Connect BT",
            command=self._show_bt_auth_window
        )
        self.bt_connect_btn.pack(side=tk.LEFT, padx=5)
        
        # Revolut Connection
        self.revolut_status_label = ttk.Label(
            status_frame,
            text="🔴 Revolut: Not Connected",
            font=("Arial", 10)
        )
        self.revolut_status_label.pack(side=tk.LEFT, padx=20)
        
        self.revolut_connect_btn = ttk.Button(
            status_frame,
            text="Connect Revolut",
            command=self._show_revolut_auth_window
        )
        self.revolut_connect_btn.pack(side=tk.LEFT, padx=5)
        
        # ========== BALANCE SUMMARY FRAME ==========
        summary_frame = ttk.LabelFrame(self.main_frame, text="💰 Balance Summary", padding=10)
        summary_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # BT Balance
        ttk.Label(summary_frame, text="BT Total Balance:").pack(side=tk.LEFT, padx=10)
        self.bt_balance_label = ttk.Label(summary_frame, text="N/A", font=("Arial", 12, "bold"))
        self.bt_balance_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(summary_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=20)
        
        # Revolut Balance
        ttk.Label(summary_frame, text="Revolut Total Balance:").pack(side=tk.LEFT, padx=10)
        self.revolut_balance_label = ttk.Label(summary_frame, text="N/A", font=("Arial", 12, "bold"))
        self.revolut_balance_label.pack(side=tk.LEFT, padx=5)
        
        # ========== CONTROLS FRAME ==========
        controls_frame = ttk.Frame(self.main_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            controls_frame,
            text="🔄 Sync Now",
            command=self._manual_sync
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            controls_frame,
            text="📊 View Details",
            command=self._show_detailed_view
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            controls_frame,
            text="📥 Export to CSV",
            command=self._export_to_csv
        ).pack(side=tk.LEFT, padx=5)
        
        # ========== TRANSACTIONS TABLE FRAME ==========
        table_frame = ttk.LabelFrame(self.main_frame, text="📝 Recent Transactions", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create Treeview for transactions
        columns = ("Date", "Bank", "Account", "Type", "Description", "Amount", "Balance")
        self.transactions_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            height=15,
            show="headings"
        )
        
        # Define column headings and widths
        self.transactions_tree.heading("Date", text="Date")
        self.transactions_tree.column("Date", width=100)
        
        self.transactions_tree.heading("Bank", text="Bank")
        self.transactions_tree.column("Bank", width=80)
        
        self.transactions_tree.heading("Account", text="Account")
        self.transactions_tree.column("Account", width=120)
        
        self.transactions_tree.heading("Type", text="Type")
        self.transactions_tree.column("Type", width=60)
        
        self.transactions_tree.heading("Description", text="Description")
        self.transactions_tree.column("Description", width=200)
        
        self.transactions_tree.heading("Amount", text="Amount")
        self.transactions_tree.column("Amount", width=100)
        
        self.transactions_tree.heading("Balance", text="Balance")
        self.transactions_tree.column("Balance", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.transactions_tree.yview)
        self.transactions_tree.configure(yscroll=scrollbar.set)
        
        self.transactions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status bar
        self.status_label = ttk.Label(
            self.main_frame,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, padx=10, pady=5)
    
    def _load_initial_data(self):
        """Load initial data in background"""
        def load():
            self._update_status("Loading bank data...")
            self._update_connection_status()
            self._refresh_data()
        
        thread = threading.Thread(target=load, daemon=True)
        thread.start()
    
    def _update_connection_status(self):
        """Update connection status indicators"""
        status = self.bank_manager.get_connection_status()
        
        # Update BT status
        if status["bt"]["connected"]:
            self.bt_status_label.config(text="🟢 BT: Connected")
            self.bt_connect_btn.config(state=tk.DISABLED, text="Connected")
        else:
            self.bt_status_label.config(text="🔴 BT: Not Connected")
            self.bt_connect_btn.config(state=tk.NORMAL, text="Connect BT")
        
        # Update Revolut status
        if status["revolut"]["connected"]:
            self.revolut_status_label.config(text="🟢 Revolut: Connected")
            self.revolut_connect_btn.config(state=tk.DISABLED, text="Connected")
        else:
            self.revolut_status_label.config(text="🔴 Revolut: Not Connected")
            self.revolut_connect_btn.config(state=tk.NORMAL, text="Connect Revolut")
    
    def _refresh_data(self):
        """Refresh balances and transactions from APIs"""
        try:
            # Get balances
            balances = self.bank_manager.get_all_balances()
            
            # Update BT balance
            if balances["bt"]["status"] == "connected":
                total = balances["bt"]["data"].get("total_balance", 0)
                self.bt_balance_label.config(text=f"RON {total:,.2f}")
            else:
                self.bt_balance_label.config(text="N/A")
            
            # Update Revolut balance
            if balances["revolut"]["status"] == "connected":
                self.revolut_balance_label.config(text="Connected")
            else:
                self.revolut_balance_label.config(text="N/A")
            
            # Get transactions
            txn_data = self.bank_manager.get_transactions(days=30)
            self.current_transactions = txn_data["all_transactions"]
            
            # Update table
            self._populate_transactions_table()
            self._update_status(f"Loaded {len(self.current_transactions)} transactions")
            
        except Exception as e:
            logger.error(f"❌ Error refreshing data: {e}")
            self._update_status(f"Error loading data: {str(e)}")
    
    def _populate_transactions_table(self):
        """Populate transactions table with current data"""
        # Clear existing rows
        for row in self.transactions_tree.get_children():
            self.transactions_tree.delete(row)
        
        # Add transactions
        for txn in self.current_transactions[:100]:  # Show last 100
            date = txn.get("date", "N/A")[:10]  # Format date
            bank = txn.get("bank", "N/A")
            account = txn.get("account_name", "N/A")
            txn_type = "Income" if txn.get("amount", 0) > 0 else "Expense"
            description = txn.get("description", "")[:50]
            amount = f"RON {txn.get('amount', 0):,.2f}"
            balance = f"RON {txn.get('balance', 'N/A')}"
            
            self.transactions_tree.insert(
                "",
                "end",
                values=(date, bank, account, txn_type, description, amount, balance)
            )
    
    def _manual_sync(self):
        """Manual sync of bank data"""
        self._update_status("Syncing...")
        
        def sync():
            try:
                self._refresh_data()
                self._update_status("Sync completed")
            except Exception as e:
                self._update_status(f"Sync failed: {str(e)}")
        
        thread = threading.Thread(target=sync, daemon=True)
        thread.start()
    
    def _update_status(self, message: str):
        """Update status bar message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_label.config(text=f"[{timestamp}] {message}")
    
    def _show_bt_auth_window(self):
        """Show BT authentication window"""
        auth_window = tk.Toplevel(self.parent)
        auth_window.title("Connect to BT (Banca Transilvania)")
        auth_window.geometry("600x500")
        
        ttk.Label(
            auth_window,
            text="Connect your BT account",
            font=("Arial", 14, "bold")
        ).pack(pady=20)
        
        frame = ttk.Frame(auth_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="BT Client ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        client_id_entry = ttk.Entry(frame, width=50)
        client_id_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="BT Client Secret:").grid(row=1, column=0, sticky=tk.W, pady=5)
        client_secret_entry = ttk.Entry(frame, width=50, show="*")
        client_secret_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Authorization Code:").grid(row=2, column=0, sticky=tk.W, pady=5)
        auth_code_entry = ttk.Entry(frame, width=50)
        auth_code_entry.grid(row=2, column=1, pady=5)
        
        info_text = scrolledtext.ScrolledText(frame, height=10, width=50)
        info_text.grid(row=3, column=0, columnspan=2, pady=10, sticky=tk.NSEW)
        
        info_text.insert(
            tk.END,
            "Steps to connect BT:\n\n"
            "1. Get your BT Client ID and Secret from:\n"
            "   https://developer.bancatransilvania.ro/\n\n"
            "2. Click 'Open Authorization URL' to authorize\n\n"
            "3. Copy the authorization code from the redirect URL\n\n"
            "4. Paste it in 'Authorization Code' field above\n\n"
            "5. Click 'Connect' to complete\n"
        )
        info_text.config(state=tk.DISABLED)
        
        def get_auth_url():
            client_id = client_id_entry.get()
            if not client_id:
                messagebox.showwarning("Missing Input", "Please enter Client ID")
                return
            
            url = self.bank_manager.get_bt_auth_url(client_id)
            import webbrowser
            webbrowser.open(url)
            messagebox.showinfo(
                "Authorization",
                "Your browser has opened the BT authorization page.\n"
                "Complete the authorization and copy the code from the redirect URL."
            )
        
        def connect():
            client_id = client_id_entry.get()
            client_secret = client_secret_entry.get()
            auth_code = auth_code_entry.get()
            
            if not all([client_id, client_secret, auth_code]):
                messagebox.showerror("Missing Input", "Please fill in all fields")
                return
            
            if self.bank_manager.complete_bt_auth(auth_code, client_id, client_secret):
                messagebox.showinfo("Success", "BT connected successfully!")
                self._update_connection_status()
                self._refresh_data()
                auth_window.destroy()
            else:
                messagebox.showerror("Error", "Failed to connect BT")
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(
            button_frame,
            text="Open Authorization URL",
            command=get_auth_url
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Connect",
            command=connect
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=auth_window.destroy
        ).pack(side=tk.LEFT, padx=5)
    
    def _show_revolut_auth_window(self):
        """Show Revolut authentication window"""
        auth_window = tk.Toplevel(self.parent)
        auth_window.title("Connect to Revolut")
        auth_window.geometry("600x500")
        
        ttk.Label(
            auth_window,
            text="Connect your Revolut account",
            font=("Arial", 14, "bold")
        ).pack(pady=20)
        
        frame = ttk.Frame(auth_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Revolut Client ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        client_id_entry = ttk.Entry(frame, width=50)
        client_id_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Revolut Client Secret:").grid(row=1, column=0, sticky=tk.W, pady=5)
        client_secret_entry = ttk.Entry(frame, width=50, show="*")
        client_secret_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Authorization Code:").grid(row=2, column=0, sticky=tk.W, pady=5)
        auth_code_entry = ttk.Entry(frame, width=50)
        auth_code_entry.grid(row=2, column=1, pady=5)
        
        info_text = scrolledtext.ScrolledText(frame, height=10, width=50)
        info_text.grid(row=3, column=0, columnspan=2, pady=10, sticky=tk.NSEW)
        
        info_text.insert(
            tk.END,
            "Steps to connect Revolut:\n\n"
            "1. Get your Revolut Client ID and Secret from:\n"
            "   https://developer.revolut.com/\n\n"
            "2. Click 'Open Authorization URL' to authorize\n\n"
            "3. Copy the authorization code from the redirect URL\n\n"
            "4. Paste it in 'Authorization Code' field above\n\n"
            "5. Click 'Connect' to complete\n"
        )
        info_text.config(state=tk.DISABLED)
        
        def get_auth_url():
            client_id = client_id_entry.get()
            if not client_id:
                messagebox.showwarning("Missing Input", "Please enter Client ID")
                return
            
            url = self.bank_manager.get_revolut_auth_url(client_id)
            import webbrowser
            webbrowser.open(url)
            messagebox.showinfo(
                "Authorization",
                "Your browser has opened the Revolut authorization page.\n"
                "Complete the authorization and copy the code from the redirect URL."
            )
        
        def connect():
            client_id = client_id_entry.get()
            client_secret = client_secret_entry.get()
            auth_code = auth_code_entry.get()
            
            if not all([client_id, client_secret, auth_code]):
                messagebox.showerror("Missing Input", "Please fill in all fields")
                return
            
            if self.bank_manager.complete_revolut_auth(auth_code, client_id, client_secret):
                messagebox.showinfo("Success", "Revolut connected successfully!")
                self._update_connection_status()
                self._refresh_data()
                auth_window.destroy()
            else:
                messagebox.showerror("Error", "Failed to connect Revolut")
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(
            button_frame,
            text="Open Authorization URL",
            command=get_auth_url
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Connect",
            command=connect
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=auth_window.destroy
        ).pack(side=tk.LEFT, padx=5)
    
    def _show_detailed_view(self):
        """Show detailed view of transactions in new window"""
        detail_window = tk.Toplevel(self.parent)
        detail_window.title("Transaction Details")
        detail_window.geometry("900x600")
        
        # Create text widget with JSON data
        text_widget = scrolledtext.ScrolledText(detail_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Format transactions as readable text
        output = "=" * 80 + "\n"
        output += "DETAILED TRANSACTION VIEW\n"
        output += "=" * 80 + "\n\n"
        
        for i, txn in enumerate(self.current_transactions[:50], 1):
            output += f"Transaction #{i}\n"
            output += "-" * 80 + "\n"
            output += f"Bank:        {txn.get('bank', 'N/A')}\n"
            output += f"Account:     {txn.get('account_name', 'N/A')}\n"
            output += f"Date:        {txn.get('date', 'N/A')}\n"
            output += f"Amount:      {txn.get('amount', 'N/A')}\n"
            output += f"Description: {txn.get('description', 'N/A')}\n"
            output += f"Balance:     {txn.get('balance', 'N/A')}\n"
            output += "\n"
        
        text_widget.insert(tk.END, output)
        text_widget.config(state=tk.DISABLED)
    
    def _export_to_csv(self):
        """Export transactions to CSV file"""
        import csv
        from datetime import datetime
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ["Date", "Bank", "Account", "Amount", "Description", "Balance"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for txn in self.current_transactions:
                    writer.writerow({
                        "Date": txn.get("date", ""),
                        "Bank": txn.get("bank", ""),
                        "Account": txn.get("account_name", ""),
                        "Amount": txn.get("amount", ""),
                        "Description": txn.get("description", ""),
                        "Balance": txn.get("balance", "")
                    })
            
            messagebox.showinfo("Success", f"Exported {len(self.current_transactions)} transactions to CSV")
            self._update_status(f"Exported to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
