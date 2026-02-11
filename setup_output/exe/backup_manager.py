# -*- coding: utf-8 -*-
"""
Backup Manager - Auto-backup periodic al datelor locale
Salvează JSON-uri în folderul arhiva cu timestamp
Permite restaurare în caz de probleme
"""

import os
import json
import shutil
import zipfile
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple


class BackupManager:
    """Manages periodic backups of local JSON data"""
    
    def __init__(self, data_dir: str, archive_dir: str, backup_interval: int = 300):
        """
        Initialize backup manager
        
        Args:
            data_dir: Data directory (d:\\punctaj\\data)
            archive_dir: Archive directory (d:\\punctaj\\arhiva)
            backup_interval: Interval between backups in seconds (default: 300 = 5 minutes)
        """
        self.data_dir = Path(data_dir)
        self.archive_dir = Path(archive_dir)
        self.backup_interval = backup_interval
        
        # Create backup subdirectory
        self.backup_dir = self.archive_dir / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Thread control
        self.backup_thread = None
        self.stop_event = threading.Event()
        self.is_backing_up = False
        
        # Config
        self.max_backups = 10  # Keep last 10 backups
        self.important_files = [
            "users_permissions.json",
            "*.json"  # All JSON files from cities
        ]
        
        print(f"📦 Backup Manager initialized")
        print(f"   Data dir: {self.data_dir}")
        print(f"   Backup dir: {self.backup_dir}")
        print(f"   Interval: {backup_interval} seconds")
    
    def start(self):
        """Start automatic backup thread"""
        if self.backup_thread and self.backup_thread.is_alive():
            print("⚠️ Backup thread already running")
            return
        
        self.stop_event.clear()
        self.backup_thread = threading.Thread(
            target=self._backup_loop,
            daemon=True
        )
        self.backup_thread.start()
        print("✅ Automatic backup started")
    
    def stop(self):
        """Stop automatic backup thread"""
        self.stop_event.set()
        if self.backup_thread:
            self.backup_thread.join(timeout=5)
        print("⏹️ Automatic backup stopped")
    
    def _backup_loop(self):
        """Main backup loop running in background"""
        while not self.stop_event.is_set():
            try:
                self.create_backup()
                time.sleep(self.backup_interval)
            except Exception as e:
                print(f"❌ Backup error: {e}")
                time.sleep(self.backup_interval)
    
    def create_backup(self) -> Tuple[bool, str]:
        """
        Create a backup of all data
        
        Returns:
            (success, backup_path)
        """
        if self.is_backing_up:
            return False, "Backup already in progress"
        
        self.is_backing_up = True
        try:
            # Create timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}.zip"
            backup_path = self.backup_dir / backup_name
            
            # Create ZIP backup
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add data files
                for file_path in self.data_dir.glob("**/*.json"):
                    arcname = file_path.relative_to(self.data_dir.parent)
                    zipf.write(file_path, arcname)
                
                # Add city folders
                for city_dir in self.data_dir.iterdir():
                    if city_dir.is_dir() and city_dir.name not in ['__pycache__']:
                        for file_path in city_dir.glob("**/*"):
                            if file_path.is_file():
                                arcname = file_path.relative_to(self.data_dir.parent)
                                zipf.write(file_path, arcname)
            
            # Get backup size
            backup_size = backup_path.stat().st_size / (1024 * 1024)  # MB
            
            print(f"✅ Backup created: {backup_name} ({backup_size:.2f} MB)")
            
            # Cleanup old backups
            self._cleanup_old_backups()
            
            return True, str(backup_path)
            
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            return False, str(e)
        
        finally:
            self.is_backing_up = False
    
    def _cleanup_old_backups(self):
        """Remove old backups, keep only the last N backups"""
        try:
            # Get all backups sorted by date (newest first)
            backups = sorted(
                self.backup_dir.glob("backup_*.zip"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            # Delete old ones
            for old_backup in backups[self.max_backups:]:
                old_backup.unlink()
                print(f"   🗑️ Deleted old backup: {old_backup.name}")
                
        except Exception as e:
            print(f"⚠️ Error cleaning up old backups: {e}")
    
    def get_backup_list(self) -> List[Dict]:
        """Get list of available backups"""
        backups = []
        try:
            for backup_file in sorted(self.backup_dir.glob("backup_*.zip"), reverse=True):
                size_mb = backup_file.stat().st_size / (1024 * 1024)
                timestamp = datetime.fromtimestamp(backup_file.stat().st_mtime)
                
                backups.append({
                    "name": backup_file.name,
                    "path": str(backup_file),
                    "size_mb": round(size_mb, 2),
                    "created": timestamp.strftime("%Y-%m-%d %H:%M:%S")
                })
        except Exception as e:
            print(f"⚠️ Error listing backups: {e}")
        
        return backups
    
    def restore_backup(self, backup_name: str) -> Tuple[bool, str]:
        """
        Restore data from a backup
        
        Args:
            backup_name: Name of backup file (e.g., "backup_20260211_143022.zip")
        
        Returns:
            (success, message)
        """
        try:
            backup_path = self.backup_dir / backup_name
            
            if not backup_path.exists():
                return False, f"Backup not found: {backup_name}"
            
            # Create safety backup before restoring
            safety_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safety_backup = self.backup_dir / f"safety_before_restore_{safety_timestamp}.zip"
            
            print(f"🔐 Creating safety backup before restore...")
            with zipfile.ZipFile(safety_backup, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in self.data_dir.glob("**/*.json"):
                    arcname = file_path.relative_to(self.data_dir.parent)
                    zipf.write(file_path, arcname)
                for city_dir in self.data_dir.iterdir():
                    if city_dir.is_dir() and city_dir.name not in ['__pycache__']:
                        for file_path in city_dir.glob("**/*"):
                            if file_path.is_file():
                                arcname = file_path.relative_to(self.data_dir.parent)
                                zipf.write(file_path, arcname)
            
            # Extract backup
            print(f"📥 Restoring from: {backup_name}...")
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(self.data_dir.parent)
            
            print(f"✅ Restore successful!")
            print(f"   Safety backup at: {safety_backup}")
            
            return True, f"Restored from {backup_name}"
            
        except Exception as e:
            print(f"❌ Error restoring backup: {e}")
            import traceback
            traceback.print_exc()
            return False, str(e)
    
    def get_backup_info(self) -> Dict:
        """Get current backup status"""
        backups = self.get_backup_list()
        
        return {
            "total_backups": len(backups),
            "latest_backup": backups[0] if backups else None,
            "backups": backups,
            "backup_dir": str(self.backup_dir),
            "data_dir": str(self.data_dir),
        }


def create_backup_ui(root, backup_manager):
    """Create UI for manual backup/restore operations"""
    import tkinter as tk
    from tkinter import ttk, messagebox
    
    win = tk.Toplevel(root)
    win.title("💾 Backup & Restore")
    win.geometry("600x400")
    
    # Info frame
    info_frame = tk.Frame(win, bg="#e3f2fd", relief=tk.RAISED, borderwidth=2)
    info_frame.pack(fill=tk.X, padx=10, pady=10)
    
    backup_info = backup_manager.get_backup_info()
    
    tk.Label(
        info_frame,
        text=f"Total Backups: {backup_info['total_backups']}/{backup_manager.max_backups}",
        font=("Segoe UI", 10, "bold"),
        bg="#e3f2fd"
    ).pack(anchor="w", padx=10, pady=5)
    
    if backup_info.get('latest_backup'):
        latest = backup_info['latest_backup']
        tk.Label(
            info_frame,
            text=f"Latest: {latest['created']} ({latest['size_mb']} MB)",
            font=("Segoe UI", 9),
            bg="#e3f2fd",
            fg="#666"
        ).pack(anchor="w", padx=10, pady=2)
    
    # Buttons frame
    btn_frame = tk.Frame(win)
    btn_frame.pack(fill=tk.X, padx=10, pady=10)
    
    def manual_backup():
        success, path = backup_manager.create_backup()
        if success:
            messagebox.showinfo("✅ Backup Successful", f"Backup created at:\n{path}")
            refresh_list()
        else:
            messagebox.showerror("❌ Backup Failed", path)
    
    tk.Button(
        btn_frame,
        text="💾 Create Manual Backup",
        command=manual_backup,
        bg="#4CAF50",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        width=20
    ).pack(side=tk.LEFT, padx=5)
    
    # Backups list
    list_frame = tk.Frame(win)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    tk.Label(list_frame, text="Available Backups:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
    
    tree = ttk.Treeview(
        list_frame,
        columns=("Created", "Size"),
        height=12,
        show="headings"
    )
    tree.column("#0", width=250)
    tree.column("Created", width=150)
    tree.column("Size", width=80)
    
    tree.heading("#0", text="Backup")
    tree.heading("Created", text="Created")
    tree.heading("Size", text="Size (MB)")
    
    tree.pack(fill=tk.BOTH, expand=True)
    
    def refresh_list():
        for item in tree.get_children():
            tree.delete(item)
        
        for backup in backup_manager.get_backup_list():
            tree.insert("", "end", text=backup["name"],
                       values=(backup["created"], f"{backup['size_mb']} MB"))
    
    refresh_list()
    
    def restore_selected():
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Select a backup to restore")
            return
        
        backup_name = tree.item(selection[0])["text"]
        
        if messagebox.askyesno("Restore Backup", f"Restore from {backup_name}?\nA safety backup will be created first."):
            success, msg = backup_manager.restore_backup(backup_name)
            if success:
                messagebox.showinfo("✅ Restore Successful", msg)
                refresh_list()
            else:
                messagebox.showerror("❌ Restore Failed", msg)
    
    # Restore button
    tk.Button(
        win,
        text="↩️ Restore from Selected Backup",
        command=restore_selected,
        bg="#FF9800",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        width=25,
        height=2
    ).pack(pady=10)
    
    win.resizable(True, True)
