"""
INTEGRATION EXAMPLE - How to add Bank Transactions to Punctaj Manager

Copy this code snippet into your punctaj.py file
"""

# ============= ADD THESE IMPORTS AT THE TOP OF punctaj.py =============
# (around where your other imports are)

from bank_transactions import BankTransactionsPanel
from bank_api_manager import BankAPIManager


# ============= ADD THIS IN YOUR MAIN APPLICATION CLASS/WINDOW SETUP =============
# (in the __init__ method where you create tabs/frames, around where other UI is set up)

class PunctajManagerApp:
    def __init__(self, root):
        # ... your existing code ...
        
        # Create notebook/tabs if you don't have one
        # self.notebook = ttk.Notebook(main_frame)
        # self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # -------- ADD THIS SECTION FOR BANK INTEGRATION --------
        
        # Initialize Bank API Manager (global, so it persists)
        try:
            self.bank_manager = BankAPIManager()
            print("✅ Bank API Manager initialized")
        except Exception as e:
            print(f"⚠️ Warning: Bank API Manager initialization failed: {e}")
            self.bank_manager = None
        
        # Create Bank Transactions Tab
        if self.bank_manager:
            try:
                bank_frame = ttk.Frame(self.notebook)
                self.notebook.add(bank_frame, text="💰 Bank Transactions")
                
                # Initialize the transactions panel
                self.transactions_panel = BankTransactionsPanel(
                    bank_frame,
                    self.bank_manager
                )
                print("✅ Bank Transactions Panel created")
                
            except Exception as e:
                print(f"⚠️ Warning: Bank Transactions Panel creation failed: {e}")
        
        # -------- END BANK INTEGRATION SECTION --------
        
        # ... rest of your existing code ...


# ============= CLEANUP IN YOUR WINDOW CLOSE HANDLER =============
# (in the method that runs when window closes, like on_closing())

def on_closing():
    """Called when main window closes"""
    
    # Stop bank sync thread if it's running
    try:
        if hasattr(self, 'bank_manager') and self.bank_manager:
            self.bank_manager.stop_sync_thread()
            print("✅ Bank sync thread stopped")
    except Exception as e:
        print(f"⚠️ Warning: Error stopping bank sync: {e}")
    
    # ... rest of your existing cleanup code ...
    
    # Close window
    root.destroy()


# ============= OPTIONAL: Add Menu Items =============
# (in your menu creation code)

def create_menus():
    """Setup menu bar"""
    
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    # ... your existing menus ...
    
    # Bank menu
    bank_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="🏦 Bank", menu=bank_menu)
    
    def open_bank_transactions():
        # Switch to bank transactions tab
        self.notebook.select(tab_id_for_bank_frame)
    
    bank_menu.add_command(label="View Transactions", command=open_bank_transactions)
    bank_menu.add_command(
        label="Sync Now",
        command=lambda: self.transactions_panel._manual_sync() if hasattr(self, 'transactions_panel') else None
    )
    bank_menu.add_separator()
    bank_menu.add_command(label="Connect BT", command=lambda: self.transactions_panel._show_bt_auth_window() if hasattr(self, 'transactions_panel') else None)
    bank_menu.add_command(label="Connect Revolut", command=lambda: self.transactions_panel._show_revolut_auth_window() if hasattr(self, 'transactions_panel') else None)


# ============= FULL MINIMAL EXAMPLE =============
# Here's a minimal standalone example to test everything:
#
# import tkinter as tk
# from tkinter import ttk
# from bank_transactions import BankTransactionsPanel
# from bank_api_manager import BankAPIManager
#
# # Create root window
# root = tk.Tk()
# root.title("Bank Transactions Test")
# root.geometry("1200x700")
#
# # Create notebook
# notebook = ttk.Notebook(root)
# notebook.pack(fill=tk.BOTH, expand=True)
#
# # Initialize bank manager
# bank_manager = BankAPIManager()
#
# # Create transactions frame
# bank_frame = ttk.Frame(notebook)
# notebook.add(bank_frame, text="💰 Bank Transactions")
#
# # Create transactions panel
# transactions_panel = BankTransactionsPanel(bank_frame, bank_manager)
#
# # Run
# root.mainloop()
