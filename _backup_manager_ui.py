# Funcție pentru deschiderea backup manager UI
def open_backup_manager():
    """Open Backup Manager UI"""
    if not BACKUP_MANAGER:
        import tkinter
        tkinter.messagebox.showwarning(
            "⚠️ Backup Manager",
            "Backup Manager nu este disponibil.\n\n"
            "Backup-uri nu vor fi create."
        )
        return
    
    try:
        create_backup_ui(root, BACKUP_MANAGER)
    except Exception as e:
        import tkinter
        tkinter.messagebox.showerror(
            "❌ Error",
            f"Error opening backup manager:\n{str(e)}"
        )
