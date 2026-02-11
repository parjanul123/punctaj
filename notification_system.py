"""
Real-Time Permission Notification System
========================================
Notifică utilizatorii când permisiunile se schimbă
Forțează sincronizare automată
"""

import threading
import time
from datetime import datetime
from typing import Dict, Callable, Optional, List
import json


class PermissionNotificationSystem:
    """Sistem de notificări real-time pentru permisiuni"""
    
    def __init__(self, permission_manager, supabase_sync, check_interval: int = 30):
        """
        Inițializează sistemul de notificări
        
        Args:
            permission_manager: InstitutionPermissionManager instance
            supabase_sync: SupabaseSync instance
            check_interval: Interval în secunde pentru verificare permisiuni
        """
        self.perm_manager = permission_manager
        self.supabase_sync = supabase_sync
        self.check_interval = check_interval
        
        # Ține istoric de permisiuni per user
        self.user_permissions_cache = {}  # {discord_id: permissions_hash}
        self.monitoring_users = {}  # {discord_id: active}
        
        # Callback-uri pentru notificări
        self.notification_callbacks = []  # [(callback, user_id), ...]
        
        # Thread de monitoring
        self.monitor_thread = None
        self.running = False
        
        print("✅ Permission Notification System initialized")
    
    def start_monitoring(self, discord_id: str):
        """Pornește monitorizarea permisiunilor pentru un user"""
        self.monitoring_users[discord_id] = True
        
        # Salvează permisiuni inițiale
        current_perms = self.perm_manager.get_all_permissions(discord_id)
        self.user_permissions_cache[discord_id] = self._hash_permissions(current_perms)
        
        print(f"✅ Started monitoring permissions for {discord_id}")
        
        # Pornește thread de monitoring dacă nu rulează
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(
                target=self._monitor_loop,
                daemon=True
            )
            self.monitor_thread.start()
    
    def stop_monitoring(self, discord_id: str):
        """Oprește monitorizarea pentru un user"""
        if discord_id in self.monitoring_users:
            self.monitoring_users[discord_id] = False
            print(f"⏹️ Stopped monitoring permissions for {discord_id}")
    
    def register_notification_callback(self, callback: Callable, discord_id: str):
        """
        Înregistrează un callback pentru notificări
        
        Args:
            callback: Funcție cu semnatura: callback(discord_id, notification)
            discord_id: ID user-ul pentru care să se notifice
        """
        self.notification_callbacks.append((callback, discord_id))
        print(f"✅ Registered notification callback for {discord_id}")
    
    def _monitor_loop(self):
        """Thread loop care monitorizează permisiunile"""
        print("🔄 Permission monitoring loop started")
        
        while self.running:
            try:
                # Verifică fiecare user monitorizat
                for discord_id, is_active in list(self.monitoring_users.items()):
                    if not is_active:
                        continue
                    
                    # Obține permisiuni curente
                    current_perms = self.perm_manager.get_all_permissions(discord_id)
                    current_hash = self._hash_permissions(current_perms)
                    
                    # Compară cu cache
                    cached_hash = self.user_permissions_cache.get(discord_id)
                    
                    if cached_hash and cached_hash != current_hash:
                        # PERMISIUNI S-AU SCHIMBAT!
                        print(f"🔔 PERMISIUNI SCHIMBATE PENTRU {discord_id}!")
                        
                        # Notifică
                        self._notify_permission_change(discord_id, current_perms)
                        
                        # Actualizează cache
                        self.user_permissions_cache[discord_id] = current_hash
                
                # Așteptă înainte de următoarea verificare
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                time.sleep(self.check_interval)
    
    def _notify_permission_change(self, discord_id: str, new_permissions: Dict):
        """Notifică user-ul despre schimbarea permisiunilor"""
        
        notification = {
            "type": "permission_changed",
            "discord_id": discord_id,
            "timestamp": datetime.now().isoformat(),
            "message": "⚠️ Permisiunile tale s-au schimbat! Sincronizează imediat!",
            "new_permissions": new_permissions,
            "action": "FORCE_SYNC"
        }
        
        # Apelează toți callback-urile pentru acest user
        for callback, user_id in self.notification_callbacks:
            if user_id == discord_id:
                try:
                    callback(discord_id, notification)
                except Exception as e:
                    print(f"❌ Error in notification callback: {e}")
    
    def _hash_permissions(self, permissions: Dict) -> str:
        """Generează hash al permisiunilor pentru comparație"""
        try:
            # Convertește permisiuni la JSON string și face hash
            perm_str = json.dumps(permissions, sort_keys=True, ensure_ascii=False)
            return str(hash(perm_str))
        except:
            return ""
    
    def stop(self):
        """Oprește sistemul de monitoring"""
        self.running = False
        print("⏹️ Permission Notification System stopped")


class PermissionChangeNotifier:
    """Notificator pentru schimbări de permisiuni cu UI"""
    
    def __init__(self, root_window, notification_system: PermissionNotificationSystem):
        """
        Inițializează notificatorul
        
        Args:
            root_window: Fereastra principală Tkinter
            notification_system: PermissionNotificationSystem instance
        """
        self.root = root_window
        self.notif_system = notification_system
        self.current_user_id = None
    
    def set_current_user(self, discord_id: str):
        """Setează user-ul curent pentru monitoring"""
        self.current_user_id = discord_id
        self.notif_system.start_monitoring(discord_id)
        self.notif_system.register_notification_callback(
            self._on_permission_changed,
            discord_id
        )
    
    def _on_permission_changed(self, discord_id: str, notification: Dict):
        """Handler pentru schimbări de permisiuni"""
        
        import tkinter as tk
        from tkinter import messagebox
        
        # Afișează dialog cu avertisment
        messagebox.showwarning(
            "⚠️ PERMISIUNI SCHIMBATE",
            f"""Permisiunile tale s-au schimbat!

⚠️ Trebuie să sincronizezi imediat pentru a vedea noile setări.

Fă click OK pentru a sincroniza automat."""
        )
        
        # Forțează sincronizare
        print(f"🔄 Forțând sincronizare pentru {discord_id}...")
        self._force_sync(discord_id)
    
    def _force_sync(self, discord_id: str):
        """Forțează sincronizare din cloud"""
        try:
            # Sincronizează permisiuni
            perms = self.notif_system.perm_manager.get_all_permissions(discord_id)
            
            # Sincronizează și datele din cloud
            if hasattr(self.notif_system.supabase_sync, 'sync_all_from_cloud'):
                result = self.notif_system.supabase_sync.sync_all_from_cloud("d:/punctaj/data")
                print(f"✅ Sync complet: {result}")
            
            # Notifică user că e gata
            import tkinter.messagebox as messagebox
            messagebox.showinfo(
                "✅ SINCRONIZARE COMPLETĂ",
                "Datele și permisiunile au fost actualizate din cloud!"
            )
            
        except Exception as e:
            print(f"❌ Error forțând sync: {e}")
            import tkinter.messagebox as messagebox
            messagebox.showerror(
                "❌ EROARE",
                f"Eroare la sincronizare: {str(e)}"
            )


# Exemplu de utilizare în punctaj.py
"""
from notification_system import PermissionNotificationSystem, PermissionChangeNotifier

# În __init__ din PunctajApp:

self.notif_system = PermissionNotificationSystem(
    self.perm_manager,
    self.supabase_sync,
    check_interval=30  # Verifică la fiecare 30 secunde
)

self.notifier = PermissionChangeNotifier(self.root, self.notif_system)

# După login:
self.notifier.set_current_user(current_discord_id)

# La ieșire:
self.notif_system.stop()
"""
