# -*- coding: utf-8 -*-
"""
Supabase Real-time WebSocket Manager
Handles real-time data sync via WebSocket for instant updates
"""

import threading
import time
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Callable, Optional, List
import sys

try:
    import websockets
    import websockets.client
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    print("⚠️  websockets not installed. Run: pip install websockets")


class SupabaseRealtimeWS:
    """
    Manages WebSocket connection to Supabase for real-time updates
    Automatically syncs data across multiple devices instantly
    """
    
    def __init__(self, url: str, key: str, tables: List[str] = None):
        """
        Initialize WebSocket manager
        
        Args:
            url: Supabase URL
            key: Supabase API key
            tables: List of tables to listen to (e.g., ['employees', 'institutions'])
        """
        if not WEBSOCKETS_AVAILABLE:
            print("❌ websockets library not available - real-time sync disabled")
            self.enabled = False
            return
        
        self.enabled = True
        self.url = url
        self.key = key
        self.tables = tables or ['employees', 'institutions', 'cities']
        
        # Extract WebSocket URL from REST API URL
        self.ws_url = self._get_ws_url(url)
        
        # Connection state
        self.ws = None
        self.connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 2
        
        # Thread control
        self.ws_thread = None
        self.stop_event = threading.Event()
        self.loop = None
        
        # Callbacks for UI updates
        self.on_insert_callbacks: Dict[str, Callable] = {}
        self.on_update_callbacks: Dict[str, Callable] = {}
        self.on_delete_callbacks: Dict[str, Callable] = {}
        self.on_error_callback: Optional[Callable] = None
        
        print(f"🔌 Supabase WebSocket Manager initialized")
        print(f"   URL: {self.ws_url}")
        print(f"   Tables: {', '.join(self.tables)}")
    
    def _get_ws_url(self, rest_url: str) -> str:
        """Convert REST URL to WebSocket URL"""
        # Transform: https://xxxxx.supabase.co → wss://xxxxx.supabase.co/realtime/v1
        ws_url = rest_url.replace("https://", "wss://").replace("http://", "ws://")
        if not ws_url.endswith("/"):
            ws_url += "/"
        ws_url += "realtime/v1"
        return ws_url
    
    def register_callback(self, event_type: str, table: str, callback: Callable):
        """
        Register callback for table events
        
        Args:
            event_type: 'insert', 'update', or 'delete'
            table: Table name
            callback: Function to call with payload
        """
        if event_type == "insert":
            self.on_insert_callbacks[table] = callback
            print(f"✅ INSERT callback registered for {table}")
        elif event_type == "update":
            self.on_update_callbacks[table] = callback
            print(f"✅ UPDATE callback registered for {table}")
        elif event_type == "delete":
            self.on_delete_callbacks[table] = callback
            print(f"✅ DELETE callback registered for {table}")
    
    def start(self):
        """Start WebSocket connection thread"""
        if not self.enabled:
            print("⚠️  WebSocket sync disabled")
            return
        
        if self.ws_thread and self.ws_thread.is_alive():
            print("⚠️  WebSocket already running")
            return
        
        self.stop_event.clear()
        self.ws_thread = threading.Thread(target=self._ws_loop, daemon=True)
        self.ws_thread.start()
        print("✅ WebSocket connection thread started")
    
    def stop(self):
        """Stop WebSocket connection"""
        self.stop_event.set()
        if self.ws_thread:
            self.ws_thread.join(timeout=5)
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
        print("🛑 WebSocket stopped")
    
    def _ws_loop(self):
        """Main WebSocket loop running in background thread"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        while not self.stop_event.is_set():
            try:
                self.loop.run_until_complete(self._connect_and_listen())
            except Exception as e:
                print(f"❌ WebSocket error: {e}")
                if self.on_error_callback:
                    self.on_error_callback(str(e))
                
                # Reconnect with backoff
                if self.reconnect_attempts < self.max_reconnect_attempts:
                    self.reconnect_attempts += 1
                    wait_time = self.reconnect_delay * (2 ** (self.reconnect_attempts - 1))
                    print(f"🔄 Reconnecting in {wait_time}s (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})")
                    time.sleep(wait_time)
                else:
                    print(f"❌ Max reconnection attempts reached")
                    break
    
    async def _connect_and_listen(self):
        """Connect to WebSocket and listen for events"""
        try:
            async with websockets.client.connect(
                self.ws_url,
                subprotocols=["realtime"],
                ping_interval=30,
                ping_timeout=10
            ) as ws:
                self.ws = ws
                self.connected = True
                self.reconnect_attempts = 0
                print(f"✅ WebSocket connected!")
                
                # Subscribe to table changes
                await self._subscribe_to_tables()
                
                # Listen for messages
                async for message in ws:
                    if self.stop_event.is_set():
                        break
                    
                    try:
                        payload = json.loads(message)
                        await self._handle_payload(payload)
                    except json.JSONDecodeError:
                        print(f"⚠️  Invalid JSON received: {message}")
                    except Exception as e:
                        print(f"❌ Error processing message: {e}")
        
        except asyncio.CancelledError:
            print("🛑 WebSocket connection cancelled")
        except Exception as e:
            self.connected = False
            print(f"❌ WebSocket connection error: {e}")
            raise
    
    async def _subscribe_to_tables(self):
        """Subscribe to changes on all configured tables"""
        for table in self.tables:
            subscribe_msg = {
                "type": "SUBSCRIBE",
                "topic": f"realtime:public:{table}",
                "payload": {
                    "events": ["INSERT", "UPDATE", "DELETE"]
                }
            }
            await self.ws.send(json.dumps(subscribe_msg))
            print(f"📥 Subscribed to {table} changes")
    
    async def _handle_payload(self, payload: Dict[str, Any]):
        """Handle incoming WebSocket message"""
        event_type = payload.get("type")
        
        if event_type in ["INSERT", "UPDATE", "DELETE"]:
            new_record = payload.get("data", {})
            old_record = payload.get("old_record", {})
            table = payload.get("table", "unknown")
            
            if event_type == "INSERT" and table in self.on_insert_callbacks:
                callback = self.on_insert_callbacks[table]
                print(f"✅ INSERT in {table}: {new_record.get('id', 'N/A')}")
                self._run_callback(callback, new_record)
            
            elif event_type == "UPDATE" and table in self.on_update_callbacks:
                callback = self.on_update_callbacks[table]
                print(f"🔄 UPDATE in {table}: {new_record.get('id', 'N/A')}")
                self._run_callback(callback, new_record)
            
            elif event_type == "DELETE" and table in self.on_delete_callbacks:
                callback = self.on_delete_callbacks[table]
                print(f"❌ DELETE in {table}: {old_record.get('id', 'N/A')}")
                self._run_callback(callback, old_record)
    
    def _run_callback(self, callback: Callable, data: Dict[str, Any]):
        """Run callback in a separate thread to not block WebSocket"""
        def run():
            try:
                callback(data)
            except Exception as e:
                print(f"❌ Error in callback: {e}")
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def get_status(self) -> Dict[str, Any]:
        """Get WebSocket connection status"""
        return {
            "enabled": self.enabled,
            "connected": self.connected,
            "url": self.ws_url,
            "tables": self.tables,
            "reconnect_attempts": self.reconnect_attempts,
            "insert_callbacks": len(self.on_insert_callbacks),
            "update_callbacks": len(self.on_update_callbacks),
            "delete_callbacks": len(self.on_delete_callbacks)
        }


def create_realtime_ws_manager(url: str, key: str, tables: List[str] = None) -> Optional[SupabaseRealtimeWS]:
    """Factory function to create WebSocket manager"""
    if not WEBSOCKETS_AVAILABLE:
        print("❌ websockets library not installed")
        return None
    
    return SupabaseRealtimeWS(url, key, tables)
