# -*- coding: utf-8 -*-
"""
Real-Time Cloud Sync Manager
Sincronizeaza datele in timp real de la Supabase la client
Verifica schimbari din cloud la fiecare 30 secunde
"""

import threading
import time
import json
import os
from datetime import datetime
from typing import Dict, Any, Callable

class RealTimeSyncManager:
    """
    Gestionează sincronizarea în timp real a datelor din Supabase
    - Verifică la fiecare 30 secunde dacă au fost schimbări în cloud
    - Descarcă datele noi automat
    - Actualiza tabelele din interfață dacă datele s-au schimbat
    """
    
    def __init__(self, supabase_sync, data_dir, sync_interval=30):
        """
        Initializează sync manager
        
        Args:
            supabase_sync: Instanța SupabaseSync
            data_dir: Calea hacia folderul de date local
            sync_interval: Interval de verificare în secunde (default 30)
        """
        self.supabase_sync = supabase_sync
        self.data_dir = data_dir
        self.sync_interval = sync_interval
        self.running = False
        self.sync_thread = None
        self.last_sync_time = {}  # Ține minte ultima sincronizare per instituție
        self.sync_callbacks = {}  # Callback-uri pentru notificări UI per instituție
        self.global_sync_callback = None  # 🔔 GLOBAL callback - apelat dupa FIECARE sincronizare
        
        print(f"📡 RealTimeSyncManager initialized (interval: {sync_interval}s)")
    
    def set_global_sync_callback(self, callback: Callable):
        """
        🔔 Seteaza un global callback care va fi apelat dupa fiecare sincronizare
        Aceasta e util pentru a reîncarca UI-ul dupa descarcarea datelor din cloud
        
        Args:
            callback: Functie care va fi apelata dupa fiecare sync (fara parametri)
        """
        self.global_sync_callback = callback
        print(f"✅ Global sync callback registered")
    
    
    def start(self):
        """Pornește firul de sincronizare"""
        if self.running:
            return
        
        self.running = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        print(f"✅ RealTimeSyncManager started - will sync every {self.sync_interval} seconds")
    
    def stop(self):
        """Oprește firul de sincronizare"""
        self.running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        print("🛑 RealTimeSyncManager stopped")
    
    def register_sync_callback(self, city: str, institution: str, callback: Callable):
        """
        Înregistrează un callback pentru a fi notificat când datele s-au schimbat
        
        Args:
            city: Orașul
            institution: Instituția
            callback: Funcție care va fi apelată cu noile date (data_dict)
        """
        key = f"{city}_{institution}"
        self.sync_callbacks[key] = callback
        print(f"✅ Callback registered for {city}/{institution}")
    
    def _sync_loop(self):
        """Bucla principală de sincronizare"""
        while self.running:
            try:
                # Sincronizează de la cloud
                result = self.supabase_sync.sync_all_from_cloud(self.data_dir)
                
                if result.get('status') == 'success':
                    synced_institutions = result.get('synced', [])
                    
                    # Pentru fiecare instituție sincronizată
                    for city, institution in synced_institutions:
                        self._handle_sync_change(city, institution)
                    
                    # 🔔 APELEAZĂ GLOBAL CALLBACK DUPA SINCRONIZARE
                    if self.global_sync_callback:
                        try:
                            print(f"   🔔 Calling global sync callback to refresh UI...")
                            self.global_sync_callback()
                        except Exception as e:
                            print(f"   ⚠️ Error calling global sync callback: {e}")
                
                # Așteaptă până la următoarea sincronizare
                time.sleep(self.sync_interval)
                
            except Exception as e:
                print(f"❌ Sync error: {e}")
                time.sleep(self.sync_interval)
    
    def _handle_sync_change(self, city: str, institution: str):
        """Notifică observatorii despre schimbări"""
        key = f"{city}_{institution}"
        
        # Dacă e înregistrat un callback, apelează-l
        if key in self.sync_callbacks:
            try:
                # Încarcă datele locale (care au fost tocmai sincronizate)
                inst_path = os.path.join(self.data_dir, city, f"{institution}.json")
                if os.path.exists(inst_path):
                    with open(inst_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Apelează callback-ul cu noile date
                    self.sync_callbacks[key](data)
                    print(f"✅ Updated {city}/{institution} in UI (callback executed)")
                    
            except Exception as e:
                print(f"❌ Error calling sync callback for {city}/{institution}: {e}")
    
    def force_sync_now(self):
        """Forțează sincronizare imediată (nu așteaptă interval)"""
        print("⚡ Forcing immediate sync...")
        try:
            result = self.supabase_sync.sync_all_from_cloud(self.data_dir)
            print(f"✅ Force sync complete: {result}")
            return result
        except Exception as e:
            print(f"❌ Force sync error: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Returnează status-ul sincronizării"""
        return {
            "running": self.running,
            "interval": self.sync_interval,
            "last_sync": max(self.last_sync_time.values()) if self.last_sync_time else None,
            "callbacks_registered": len(self.sync_callbacks)
        }


def integrate_realtime_sync(app_window, supabase_sync, data_dir):
    """
    Integrează sincronizarea în timp real în aplicația principală
    
    Returns:
        RealTimeSyncManager instance
    """
    sync_manager = RealTimeSyncManager(supabase_sync, data_dir)
    
    # Pornește sincronizarea
    sync_manager.start()
    
    # Oprește sincronizarea la închiderea aplicației
    def on_app_close():
        sync_manager.stop()
    
    app_window.on_close = on_app_close
    
    return sync_manager


# Test mode
if __name__ == "__main__":
    print("🔍 Real-Time Sync Manager")
    print("=" * 60)
    print("This module provides real-time cloud sync for punctaj app")
    print()
    print("Usage in punctaj.py:")
    print("  from realtime_sync import RealTimeSyncManager")
    print("  REALTIME_SYNC = RealTimeSyncManager(SUPABASE_SYNC, DATA_DIR)")
    print("  REALTIME_SYNC.start()")
    print()
    print("Register callbacks to be notified of changes:")
    print("  def on_data_changed(new_data):")
    print("      # Update UI with new data")
    print("  ")
    print("  REALTIME_SYNC.register_sync_callback(city, institution, on_data_changed)")
