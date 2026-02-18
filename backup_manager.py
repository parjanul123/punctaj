# -*- coding: utf-8 -*-
"""
Backup Manager - Periodic backup of local data
Optional module for data protection
"""

import os
import json
import shutil
import threading
import time
from datetime import datetime
from pathlib import Path


class BackupManager:
    """Manages periodic backups of local data"""
    
    def __init__(self, data_dir, archive_dir, backup_interval=300):
        self.data_dir = data_dir
        self.archive_dir = archive_dir
        self.backup_interval = backup_interval
        self.running = False
        self.backup_thread = None
    
    def start(self):
        """Start backup manager"""
        if self.running:
            return
        
        self.running = True
        self.backup_thread = threading.Thread(target=self._backup_loop, daemon=True)
        self.backup_thread.start()
        print(f"✅ Backup Manager started (interval: {self.backup_interval}s)")
    
    def stop(self):
        """Stop backup manager"""
        self.running = False
        if self.backup_thread:
            self.backup_thread.join(timeout=5)
        print("🛑 Backup Manager stopped")
    
    def _backup_loop(self):
        """Periodic backup loop"""
        while self.running:
            try:
                self.create_backup()
                time.sleep(self.backup_interval)
            except Exception as e:
                print(f"⚠️ Backup error: {e}")
                time.sleep(self.backup_interval)
    
    def create_backup(self):
        """Create a backup of data directory"""
        if not os.path.exists(self.data_dir):
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
            backup_path = os.path.join(self.archive_dir, backup_name)
            
            # Create backup
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
            
            shutil.copytree(self.data_dir, backup_path)
            print(f"✅ Backup created: {backup_name}")
            
            # Keep only last 10 backups
            self._cleanup_old_backups()
            
        except Exception as e:
            print(f"⚠️ Error creating backup: {e}")
    
    def _cleanup_old_backups(self):
        """Keep only the last 10 backups"""
        try:
            backups = sorted([d for d in os.listdir(self.archive_dir) 
                            if d.startswith('backup_')])
            
            if len(backups) > 10:
                for old_backup in backups[:-10]:
                    path = os.path.join(self.archive_dir, old_backup)
                    shutil.rmtree(path)
                    print(f"🗑️ Removed old backup: {old_backup}")
        except Exception as e:
            print(f"⚠️ Error cleaning backups: {e}")


def create_backup_ui(root, backup_manager):
    """Create UI for backup manager (stub)"""
    import tkinter as tk
    from tkinter import messagebox
    
    root.after(100, lambda: messagebox.showinfo(
        "Backup Manager",
        "✅ Backup Manager is running\n\n"
        "Backups are created automatically every 5 minutes\n"
        "Location: archive/ folder"
    ))
