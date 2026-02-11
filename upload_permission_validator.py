"""
Permission Validator for Upload Operations
==========================================
Validează dacă utilizatorul are dreptul să uploadeaze anumite modificări
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


class UploadPermissionValidator:
    """Validează permisiuni înainte de upload"""
    
    def __init__(self, permission_manager):
        """
        Inițializează validator
        
        Args:
            permission_manager: InstitutionPermissionManager instance
        """
        self.perm_manager = permission_manager
    
    def validate_upload(
        self,
        discord_id: str,
        city: str,
        institution: str,
        action: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validează dacă user poate face o anumită acțiune
        
        Args:
            discord_id: Discord ID al user-ului
            city: Orașul
            institution: Instituția
            action: Tipul acțiunii (add_employee, delete_employee, reset_scores, deduct_scores)
            data: Datele de uploat
        
        Returns:
            {
                'valid': True/False,
                'message': 'Mesajul de eroare (dacă valid=False)',
                'reason': 'add_employee|delete_employee|reset_scores|deduct_scores|no_permission'
            }
        """
        
        # Mapare acțiuni la permisiuni
        action_to_permission = {
            'add_employee': 'can_edit',
            'edit_employee': 'can_edit',
            'delete_employee': 'can_delete',
            'reset_scores': 'can_reset_scores',
            'deduct_scores': 'can_deduct_scores',
            'add_city': 'can_add_cities',
            'add_institution': 'can_add_institutions'
        }
        
        # Validează acțiunea
        if action not in action_to_permission:
            return {
                'valid': False,
                'message': f'❌ Acțiune necunoscută: {action}',
                'reason': 'unknown_action'
            }
        
        required_perm = action_to_permission[action]
        
        # Acțiuni globale (orașul)
        if action == 'add_city':
            has_perm = self.perm_manager.can_add_cities(discord_id)
            if not has_perm:
                return {
                    'valid': False,
                    'message': '❌ Nu ai voie să adaugi orașe!',
                    'reason': 'no_permission'
                }
            return {'valid': True, 'message': 'OK'}
        
        # Acțiuni per-instituție
        has_perm = self.perm_manager.check_institution_permission(
            discord_id, city, institution, required_perm
        )
        
        if not has_perm:
            return {
                'valid': False,
                'message': f'❌ Nu ai permisiune: {required_perm} în {city}/{institution}',
                'reason': 'no_permission'
            }
        
        return {'valid': True, 'message': 'OK'}
    
    def validate_bulk_upload(
        self,
        discord_id: str,
        city: str,
        institution: str,
        employees_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validează upload în bulk pentru angajați
        
        Args:
            discord_id: Discord ID
            city: Orașul
            institution: Instituția
            employees_data: Lista de angajați din upload
        
        Returns:
            {
                'valid': True/False,
                'can_add': True/False,
                'can_edit': True/False,
                'can_delete': True/False,
                'message': 'Mesaj detaliat'
            }
        """
        
        # Verifică permisiuni generale
        can_view = self.perm_manager.check_institution_permission(
            discord_id, city, institution, 'can_view'
        )
        
        if not can_view:
            return {
                'valid': False,
                'message': f'❌ Nu ai acces la {city}/{institution}',
                'can_add': False,
                'can_edit': False,
                'can_delete': False
            }
        
        # Verifică permisiuni specifice
        can_add = self.perm_manager.check_institution_permission(
            discord_id, city, institution, 'can_edit'
        )
        can_edit = self.perm_manager.check_institution_permission(
            discord_id, city, institution, 'can_edit'
        )
        can_delete = self.perm_manager.check_institution_permission(
            discord_id, city, institution, 'can_delete'
        )
        
        # Determina ce poate face
        if can_add and can_edit and can_delete:
            message = f'✅ Acces complet la {city}/{institution}'
            valid = True
        elif can_add or can_edit:
            message = f'⚠️ Acces parțial: Poți Vedea/Edita, dar NU poți Șterge'
            valid = True
        else:
            message = f'❌ Acces refuzat la {city}/{institution}'
            valid = False
        
        return {
            'valid': valid,
            'message': message,
            'can_add': can_add,
            'can_edit': can_edit,
            'can_delete': can_delete
        }
    
    def get_upload_restrictions(
        self,
        discord_id: str,
        city: str,
        institution: str
    ) -> Dict[str, bool]:
        """
        Obține o imagine clară a permisiunilor user-ului
        
        Returns:
            {
                'can_view': bool,
                'can_edit': bool,
                'can_delete': bool,
                'can_reset_scores': bool,
                'can_deduct_scores': bool,
                'summary': 'String cu permisiuni'
            }
        """
        
        perms = {
            'can_view': self.perm_manager.check_institution_permission(
                discord_id, city, institution, 'can_view'
            ),
            'can_edit': self.perm_manager.check_institution_permission(
                discord_id, city, institution, 'can_edit'
            ),
            'can_delete': self.perm_manager.check_institution_permission(
                discord_id, city, institution, 'can_delete'
            ),
            'can_reset_scores': self.perm_manager.check_institution_permission(
                discord_id, city, institution, 'can_reset_scores'
            ),
            'can_deduct_scores': self.perm_manager.check_institution_permission(
                discord_id, city, institution, 'can_deduct_scores'
            )
        }
        
        # Generează sumar
        summary = f"Permisiuni în {city}/{institution}:\n"
        summary += f"  👁️ Vizualizare: {'✅' if perms['can_view'] else '❌'}\n"
        summary += f"  ✏️ Editare: {'✅' if perms['can_edit'] else '❌'}\n"
        summary += f"  ❌ Ștergere: {'✅' if perms['can_delete'] else '❌'}\n"
        summary += f"  🔄 Reset: {'✅' if perms['can_reset_scores'] else '❌'}\n"
        summary += f"  📉 Deduct: {'✅' if perms['can_deduct_scores'] else '❌'}"
        
        perms['summary'] = summary
        return perms


# Exemplu utilizare în supabase_upload
"""
def supabase_upload(discord_id, city, institution, json_data, file_path=None):
    validator = UploadPermissionValidator(permission_manager)
    
    # Validează bulk upload
    validation = validator.validate_bulk_upload(
        discord_id, city, institution, json_data.get('rows', [])
    )
    
    if not validation['valid']:
        return {
            'status': 'error',
            'message': validation['message']
        }
    
    # Dacă validare OK, procedează cu upload
    # ... rest of upload logic ...
"""
