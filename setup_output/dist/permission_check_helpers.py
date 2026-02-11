# -*- coding: utf-8 -*-
"""
Permission Check Helpers for Institution-Level Actions

Provides granular permission checking for add/edit/delete operations on institutions and employees
"""

def check_can_add_employee_to_institution(city: str, institution: str, discord_id: str, institution_perm_manager=None, discord_auth=None) -> tuple:
    """
    Check if user can add employee to an institution
    
    Returns:
        (can_perform: bool, message: str)
    """
    # Superusers always have access
    if discord_auth and discord_auth.is_superuser():
        return True, ""
    
    # If no manager/discord_id, DENY access (don't allow by default)
    if not institution_perm_manager or not discord_id:
        return False, "❌ Sistem de permisiuni nu este disponibil"
    
    # Check granular permission
    can_add = institution_perm_manager.can_add_employee(discord_id, city, institution)
    
    if not can_add:
        return False, f"❌ Nu ai permisiunea să adaugi angajați la {institution}"
    
    return True, ""


def check_can_edit_employee_in_institution(city: str, institution: str, discord_id: str, institution_perm_manager=None, discord_auth=None) -> tuple:
    """
    Check if user can edit employee in an institution
    
    Returns:
        (can_perform: bool, message: str)
    """
    # Superusers always have access
    if discord_auth and discord_auth.is_superuser():
        return True, ""
    
    # If no manager/discord_id, DENY access (don't allow by default)
    if not institution_perm_manager or not discord_id:
        return False, "❌ Sistem de permisiuni nu este disponibil"
    
    # Check granular permission
    can_edit = institution_perm_manager.can_edit_employee(discord_id, city, institution)
    
    if not can_edit:
        return False, f"❌ Nu ai permisiunea să editezi angajații la {institution}"
    
    return True, ""


def check_can_delete_employee_from_institution(city: str, institution: str, discord_id: str, institution_perm_manager=None, discord_auth=None) -> tuple:
    """
    Check if user can delete employee from an institution
    
    Returns:
        (can_perform: bool, message: str)
    """
    # Superusers always have access
    if discord_auth and discord_auth.is_superuser():
        return True, ""
    
    # If no manager/discord_id, DENY access (don't allow by default)
    if not institution_perm_manager or not discord_id:
        return False, "❌ Sistem de permisiuni nu este disponibil"
    
    # Check granular permission
    can_delete = institution_perm_manager.can_delete_employee(discord_id, city, institution)
    
    if not can_delete:
        return False, f"❌ Nu ai permisiunea să ștergi angajați de la {institution}"
    
    return True, ""


def check_can_add_score_to_institution(city: str, institution: str, discord_id: str, institution_perm_manager=None, discord_auth=None) -> tuple:
    """
    Check if user can add/edit scores (punctaj) in an institution
    
    Returns:
        (can_perform: bool, message: str)
    """
    # Superusers always have access
    if discord_auth and discord_auth.is_superuser():
        return True, ""
    
    # If no manager/discord_id, DENY access (don't allow by default)
    if not institution_perm_manager or not discord_id:
        return False, "❌ Sistem de permisiuni nu este disponibil"
    
    # Check granular permission
    can_add_score = institution_perm_manager.can_add_score(discord_id, city, institution)
    
    if not can_add_score:
        return False, f"❌ Nu ai permisiunea să adaugi punctaj la {institution}"
    
    return True, ""



def check_can_add_city(discord_id: str, institution_perm_manager=None, discord_auth=None) -> tuple:
    """
    Check if user can add a new city
    
    Returns:
        (can_perform: bool, message: str)
    """
    # Superusers always have access
    if discord_auth and discord_auth.is_superuser():
        return True, ""
    
    # If no manager/discord_id, DENY access (don't allow by default)
    if not institution_perm_manager or not discord_id:
        return False, "❌ Sistem de permisiuni nu este disponibil"
    
    # Check global permission
    can_add = institution_perm_manager.can_add_city(discord_id)
    
    if not can_add:
        return False, "❌ Nu ai permisiunea să adaugi orase noi"
    
    return True, ""


def check_can_edit_city(discord_id: str, institution_perm_manager=None, discord_auth=None) -> tuple:
    """
    Check if user can edit a city
    
    Returns:
        (can_perform: bool, message: str)
    """
    # Superusers always have access
    if discord_auth and discord_auth.is_superuser():
        return True, ""
    
    # If no manager/discord_id, DENY access (don't allow by default)
    if not institution_perm_manager or not discord_id:
        return False, "❌ Sistem de permisiuni nu este disponibil"
    
    # Check global permission
    can_edit = institution_perm_manager.can_edit_city(discord_id)
    
    if not can_edit:
        return False, "❌ Nu ai permisiunea să editezi orase"
    
    return True, ""


def check_can_delete_city(discord_id: str, institution_perm_manager=None, discord_auth=None) -> tuple:
    """
    Check if user can delete a city
    
    Returns:
        (can_perform: bool, message: str)
    """
    # Superusers always have access
    if discord_auth and discord_auth.is_superuser():
        return True, ""
    
    # If no manager/discord_id, DENY access (don't allow by default)
    if not institution_perm_manager or not discord_id:
        return False, "❌ Sistem de permisiuni nu este disponibil"
    
    # Check global permission
    can_delete = institution_perm_manager.can_delete_city(discord_id)
    
    if not can_delete:
        return False, "❌ Nu ai permisiunea să ștergi orase"
    
    return True, ""


def update_button_states(buttons_dict: dict, discord_id: str, city: str, institution: str, institution_perm_manager=None, discord_auth=None):
    """
    Update button states based on user permissions
    
    Args:
        buttons_dict: Dictionary with button names as keys and tk.Button objects as values
                      Expected keys: 'add_employee', 'edit_employee', 'delete_employee', 'add_score'
        discord_id: User's Discord ID
        city: Current city
        institution: Current institution
        institution_perm_manager: InstitutionPermissionManager instance
        discord_auth: DiscordAuth instance
    """
    
    # Check each button permission
    permission_checks = {
        'add_employee': lambda: check_can_add_employee_to_institution(city, institution, discord_id, institution_perm_manager, discord_auth),
        'edit_employee': lambda: check_can_edit_employee_in_institution(city, institution, discord_id, institution_perm_manager, discord_auth),
        'delete_employee': lambda: check_can_delete_employee_from_institution(city, institution, discord_id, institution_perm_manager, discord_auth),
        'add_score': lambda: check_can_add_score_to_institution(city, institution, discord_id, institution_perm_manager, discord_auth),
    }
    
    # Update button states
    for btn_name, check_func in permission_checks.items():
        if btn_name in buttons_dict:
            btn = buttons_dict[btn_name]
            can_perform, message = check_func()
            
            if can_perform:
                btn.config(state='normal')
            else:
                btn.config(state='disabled')


def update_city_button_states(buttons_dict: dict, discord_id: str, institution_perm_manager=None, discord_auth=None):
    """
    Update city-level button states based on user permissions
    
    Args:
        buttons_dict: Dictionary with button names as keys and tk.Button objects as values
                      Expected keys: 'add_city', 'edit_city', 'delete_city'
        discord_id: User's Discord ID
        institution_perm_manager: InstitutionPermissionManager instance
        discord_auth: DiscordAuth instance
    """
    
    # Check each button permission
    permission_checks = {
        'add_city': lambda: check_can_add_city(discord_id, institution_perm_manager, discord_auth),
        'edit_city': lambda: check_can_edit_city(discord_id, institution_perm_manager, discord_auth),
        'delete_city': lambda: check_can_delete_city(discord_id, institution_perm_manager, discord_auth),
    }
    
    # Update button states
    for btn_name, check_func in permission_checks.items():
        if btn_name in buttons_dict:
            btn = buttons_dict[btn_name]
            can_perform, message = check_func()
            
            if can_perform:
                btn.config(state='normal')
            else:
                btn.config(state='disabled')
