# -*- coding: utf-8 -*-
"""
Setup & Verification Tool pentru Sistem Permisiuni Instituții

Rulează acest script pentru:
1. Verifică dacă Supabase e configurat corect
2. Verifică dacă coloana granular_permissions există
3. Setează permisiuni de test
4. Afișează permisiunile curente pentru un utilizator
"""

import requests
import json
import sys
import os

# Adaugă path pentru imports
sys.path.insert(0, os.path.dirname(__file__))

try:
    from supabase_sync import SupabaseSync
except ImportError:
    print("❌ Eroare: Nu gasesc supabase_sync.py")
    sys.exit(1)


class PermissionSetupTool:
    """Tool pentru setup și verificare permisiuni"""
    
    def __init__(self):
        try:
            self.supabase = SupabaseSync()
            self.url = self.supabase.url
            self.key = self.supabase.key
            self.headers = {
                "apikey": self.key,
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json"
            }
            print("✅ Conectat la Supabase")
        except Exception as e:
            print(f"❌ Eroare conexiune Supabase: {e}")
            sys.exit(1)
    
    def check_column_exists(self):
        """Verifică dacă coloana granular_permissions există"""
        try:
            print("\n🔍 Verificare coloană granular_permissions...")
            
            # Încearcă să fetcheze data cu acea coloană
            url = f"{self.url}/rest/v1/discord_users?select=granular_permissions&limit=1"
            response = requests.get(url, headers=self.headers, timeout=5)
            
            if response.status_code == 200:
                print("✅ Coloana granular_permissions EXISTĂ în baza de date")
                return True
            else:
                print(f"❌ Coloana NU EXISTĂ. Status: {response.status_code}")
                print(f"   Trebuie să rulezi SQL-ul din SETUP_INSTITUTION_PERMISSIONS.sql")
                return False
        except Exception as e:
            print(f"❌ Eroare verificare: {e}")
            return False
    
    def list_users(self):
        """Afișează toți utilizatorii"""
        try:
            print("\n👥 Lista utilizatori:")
            url = f"{self.url}/rest/v1/discord_users?select=id,discord_id,username,is_superuser,is_admin"
            response = requests.get(url, headers=self.headers, timeout=5)
            
            if response.status_code == 200:
                users = response.json()
                if not users:
                    print("   ❌ Niciun utilizator găsit")
                    return None
                
                for user in users:
                    role = "Superuser" if user.get('is_superuser') else ("Admin" if user.get('is_admin') else "User")
                    print(f"   • {user['username']} (ID: {user['discord_id']}) - {role}")
                
                return users
            else:
                print(f"❌ Eroare: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Eroare: {e}")
            return None
    
    def show_user_permissions(self, discord_id: str):
        """Afișează permisiunile unui utilizator"""
        try:
            print(f"\n📋 Permisiuni pentru {discord_id}:")
            
            url = f"{self.url}/rest/v1/discord_users?discord_id=eq.{discord_id}&select=username,granular_permissions"
            response = requests.get(url, headers=self.headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if not data:
                    print(f"   ❌ Utilizator nu găsit")
                    return
                
                user = data[0]
                username = user.get('username', 'Unknown')
                perms = user.get('granular_permissions', {})
                
                if isinstance(perms, str):
                    perms = json.loads(perms)
                
                print(f"   Utilizator: {username}")
                
                institutions = perms.get('institutions', {})
                if not institutions:
                    print(f"   ⚠️  Nu are permisiuni setate")
                    return
                
                for city, insts in institutions.items():
                    print(f"\n   🏙️  {city}:")
                    for inst, perms_dict in insts.items():
                        can_view = perms_dict.get('can_view', False)
                        can_edit = perms_dict.get('can_edit', False)
                        can_delete = perms_dict.get('can_delete', False)
                        
                        view_icon = "✅" if can_view else "❌"
                        edit_icon = "✅" if can_edit else "❌"
                        del_icon = "✅" if can_delete else "❌"
                        
                        print(f"      🏢 {inst}: {view_icon} View | {edit_icon} Edit | {del_icon} Delete")
            else:
                print(f"❌ Eroare: {response.status_code}")
        except Exception as e:
            print(f"❌ Eroare: {e}")
    
    def set_test_permissions(self, discord_id: str):
        """Setează permisiuni de test pentru un utilizator"""
        try:
            print(f"\n⚙️  Setare permisiuni de test pentru {discord_id}...")
            
            # Obține user ID
            url = f"{self.url}/rest/v1/discord_users?discord_id=eq.{discord_id}&select=id"
            response = requests.get(url, headers=self.headers, timeout=5)
            
            if response.status_code != 200 or not response.json():
                print(f"❌ Utilizator nu găsit")
                return False
            
            user_id = response.json()[0]['id']
            
            # Setează permisiuni
            test_permissions = {
                "institutions": {
                    "Blackwater": {
                        "Politie": {
                            "can_view": True,
                            "can_edit": True,
                            "can_delete": True
                        },
                        "Medical": {
                            "can_view": False,
                            "can_edit": False,
                            "can_delete": False
                        }
                    },
                    "Saint-Denis": {
                        "Politie": {
                            "can_view": True,
                            "can_edit": False,
                            "can_delete": False
                        }
                    }
                }
            }
            
            update_url = f"{self.url}/rest/v1/discord_users?id=eq.{user_id}"
            update_data = {"granular_permissions": json.dumps(test_permissions)}
            
            update_response = requests.patch(
                update_url,
                headers=self.headers,
                json=update_data,
                timeout=5
            )
            
            if update_response.status_code in [200, 204]:
                print("✅ Permisiuni de test setate!")
                self.show_user_permissions(discord_id)
                return True
            else:
                print(f"❌ Eroare salvare: {update_response.status_code}")
                print(f"   {update_response.text}")
                return False
        except Exception as e:
            print(f"❌ Eroare: {e}")
            return False
    
    def reset_user_permissions(self, discord_id: str):
        """Resetează permisiunile unui utilizator"""
        try:
            print(f"\n🔄 Resetare permisiuni pentru {discord_id}...")
            
            # Obține user ID
            url = f"{self.url}/rest/v1/discord_users?discord_id=eq.{discord_id}&select=id"
            response = requests.get(url, headers=self.headers, timeout=5)
            
            if response.status_code != 200 or not response.json():
                print(f"❌ Utilizator nu găsit")
                return False
            
            user_id = response.json()[0]['id']
            
            # Resetează
            update_url = f"{self.url}/rest/v1/discord_users?id=eq.{user_id}"
            update_data = {"granular_permissions": json.dumps({"institutions": {}})}
            
            update_response = requests.patch(
                update_url,
                headers=self.headers,
                json=update_data,
                timeout=5
            )
            
            if update_response.status_code in [200, 204]:
                print("✅ Permisiuni resetate!")
                return True
            else:
                print(f"❌ Eroare: {update_response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Eroare: {e}")
            return False
    
    def run_interactive_menu(self):
        """Meniu interactiv"""
        while True:
            print("\n" + "="*50)
            print("🔐 INSTITUTION PERMISSIONS SETUP TOOL")
            print("="*50)
            print("\n1. ✅ Verifică dacă Supabase e configurat")
            print("2. 👥 Afișează toți utilizatorii")
            print("3. 📋 Afișează permisiuni utilizator")
            print("4. ⚙️  Setează permisiuni de test")
            print("5. 🔄 Resetează permisiuni utilizator")
            print("6. ❌ Ieși")
            
            choice = input("\nAlege opțiune (1-6): ").strip()
            
            if choice == "1":
                self.check_column_exists()
            
            elif choice == "2":
                self.list_users()
            
            elif choice == "3":
                users = self.list_users()
                if users:
                    discord_id = input("\nIntroduceți discord_id: ").strip()
                    self.show_user_permissions(discord_id)
            
            elif choice == "4":
                users = self.list_users()
                if users:
                    discord_id = input("\nIntroduceți discord_id pentru test permissions: ").strip()
                    self.set_test_permissions(discord_id)
            
            elif choice == "5":
                users = self.list_users()
                if users:
                    discord_id = input("\nIntroduceți discord_id pentru resetare: ").strip()
                    confirm = input(f"Ești sigur? (y/n): ").strip().lower()
                    if confirm == 'y':
                        self.reset_user_permissions(discord_id)
            
            elif choice == "6":
                print("\n👋 Goodbye!")
                break
            
            else:
                print("❌ Opțiune invalidă")
    
    def run_check(self):
        """Rulează verificări automate"""
        print("="*50)
        print("🔐 VERIFICARE SISTEM PERMISIUNI")
        print("="*50)
        
        # 1. Verifică coloană
        if not self.check_column_exists():
            print("\n⚠️  TREBUIE să rulezi SQL-ul din SETUP_INSTITUTION_PERMISSIONS.sql")
            print("   Mergi în Supabase SQL Editor și copiază comenzile din:")
            print("   d:/punctaj/SETUP_INSTITUTION_PERMISSIONS.sql")
            return False
        
        # 2. Afișează utilizatori
        users = self.list_users()
        if not users:
            print("\n⚠️  Nu sunt utilizatori în baza de date")
            return False
        
        # 3. Afișează permisiuni pentru primul user
        if users:
            print("\n📋 Permisiuni pentru primul utilizator:")
            self.show_user_permissions(users[0]['discord_id'])
        
        return True


if __name__ == "__main__":
    tool = PermissionSetupTool()
    
    # Dacă e lansat cu argument, rulează check
    if len(sys.argv) > 1 and sys.argv[1] == '--check':
        tool.run_check()
    else:
        # Meniu interactiv
        tool.run_interactive_menu()
