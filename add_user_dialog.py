#!/usr/bin/env python3
"""
UI Dialog for Adding New Users to the System
Integrates with Users Permissions JSON Manager
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, Callable

class AddUserDialog:
    """Dialog for adding new users to the system"""
    
    def __init__(self, parent, users_json_manager, on_user_added: Optional[Callable] = None):
        """
        Initialize the dialog
        
        Args:
            parent: Parent window
            users_json_manager: UsersPermissionsJsonManager instance
            on_user_added: Callback function when user is added
        """
        self.parent = parent
        self.manager = users_json_manager
        self.on_user_added = on_user_added
        self.result = None
    
    def show(self) -> Optional[dict]:
        """Show the add user dialog"""
        
        # Create dialog window
        dialog = tk.Toplevel(self.parent)
        dialog.title("➕ Add New User")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center on parent
        dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - 200
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - 150
        dialog.geometry(f"+{x}+{y}")
        
        # Frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Discord ID
        ttk.Label(main_frame, text="Discord ID:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        discord_id_var = tk.StringVar()
        discord_id_entry = ttk.Entry(main_frame, textvariable=discord_id_var, width=30)
        discord_id_entry.grid(row=0, column=1, sticky="w", pady=5)
        
        # Username
        ttk.Label(main_frame, text="Username:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
        username_var = tk.StringVar()
        username_entry = ttk.Entry(main_frame, textvariable=username_var, width=30)
        username_entry.grid(row=1, column=1, sticky="w", pady=5)
        
        # Is Admin checkbox
        is_admin_var = tk.BooleanVar(value=False)
        is_admin_check = ttk.Checkbutton(main_frame, text="Grant Admin Privileges", variable=is_admin_var)
        is_admin_check.grid(row=2, column=0, columnspan=2, sticky="w", pady=10)
        
        # Info
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️  Information", padding="10")
        info_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=10)
        
        info_text = """• Discord ID: Get from Discord profile or right-click user
• Username: Discord username (e.g., username#1234)
• Admin: Check to grant administrative permissions
• New user will be added to both local JSON and Supabase
• Permissions can be configured later"""
        
        ttk.Label(info_frame, text=info_text, font=("Arial", 9), justify="left").pack(anchor="w")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)
        
        def add_user():
            """Add the user"""
            discord_id_str = discord_id_var.get().strip()
            username = username_var.get().strip()
            is_admin = is_admin_var.get()
            
            # Validation
            if not discord_id_str:
                messagebox.showerror("Error", "Please enter Discord ID")
                return
            
            if not username:
                messagebox.showerror("Error", "Please enter username")
                return
            
            # Try to convert ID to int
            try:
                discord_id = int(discord_id_str)
            except ValueError:
                messagebox.showerror("Error", "Discord ID must be a number")
                return
            
            # Check if user already exists
            existing_users = self.manager.list_users()
            if any(u['discord_id'] == discord_id for u in existing_users):
                messagebox.showerror("Error", f"User {discord_id} already exists")
                return
            
            # Add user with immediate sync
            try:
                success = self.manager.add_user_and_sync(discord_id, username, is_admin)
                
                if success:
                    messagebox.showinfo("Success", f"User '{username}' added successfully!\n\n"
                                                   f"ID: {discord_id}\n"
                                                   f"Admin: {'Yes' if is_admin else 'No'}\n\n"
                                                   f"Changes synced to cloud.")
                    
                    # Call callback if provided
                    if self.on_user_added:
                        self.on_user_added({
                            "discord_id": discord_id,
                            "username": username,
                            "is_admin": is_admin
                        })
                    
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to add user")
            
            except Exception as e:
                messagebox.showerror("Error", f"Error adding user: {e}")
        
        ttk.Button(button_frame, text="✅ Add User", command=add_user).pack(side="left", padx=5)
        ttk.Button(button_frame, text="❌ Cancel", command=dialog.destroy).pack(side="right", padx=5)
        
        # Focus on first field
        discord_id_entry.focus()
        
        # Wait for dialog to close
        self.parent.wait_window(dialog)
        return self.result


def open_add_user_dialog(parent, users_json_manager, on_user_added: Optional[Callable] = None):
    """
    Open the add user dialog
    
    Args:
        parent: Parent window
        users_json_manager: UsersPermissionsJsonManager instance
        on_user_added: Callback when user is added
    """
    dialog = AddUserDialog(parent, users_json_manager, on_user_added)
    return dialog.show()
