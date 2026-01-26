import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import shutil
import csv
from datetime import datetime
import schedule
import threading
import time
import sys

# Git support - complet opțional
try:
    from git import Repo
    from git.exc import InvalidGitRepositoryError
    GIT_AVAILABLE = True
except ImportError:
    # Git nu e instalat sau GitPython lipsește - aplicația va funcționa fără Git
    GIT_AVAILABLE = False
    print("⚠️ Git nu este disponibil - funcționalitatea Git este dezactivată")

# ================== CONFIG / PATHS ==================
# Detectează dacă rulează ca EXE sau ca script Python
if getattr(sys, 'frozen', False):
    # Rulează ca EXE - folosește folderul PĂRINTE al exe-ului pentru date partajate
    # Așa exe-ul din dist/ va folosi aceleași foldere ca și scriptul Python
    exe_dir = os.path.dirname(sys.executable)
    
    # Dacă exe-ul e în dist/, urcă un nivel sus
    if os.path.basename(exe_dir).lower() == 'dist':
        BASE_DIR = os.path.dirname(exe_dir)
    else:
        BASE_DIR = exe_dir
else:
    # Rulează ca script Python
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
ARCHIVE_DIR = os.path.join(BASE_DIR, "arhiva")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

# Git configuration
GIT_ENABLED = False
GIT_REPO = None
GIT_AUTHOR = "PunctajApp"
GIT_EMAIL = "app@punctaj.local"

# Inițializează Git repo doar dacă GitPython e disponibil
if GIT_AVAILABLE:
    try:
        GIT_REPO = Repo(BASE_DIR)
        GIT_ENABLED = True
    except (InvalidGitRepositoryError, NameError):
        try:
            print("Inițializez Git repository...")
            GIT_REPO = Repo.init(BASE_DIR)
            GIT_ENABLED = True
        except Exception as e:
            print(f"Nu pot inițializa Git: {e}")
            GIT_ENABLED = False
else:
    print("ℹ️ Aplicația rulează fără suport Git")


# Ora = tabel principal, institutia = sub-tabel, angajat = rand
def city_dir(city):
    return os.path.join(DATA_DIR, city)


def institution_path(city, institution):
    return os.path.join(city_dir(city), f"{institution}.json")


def ensure_city(city):
    os.makedirs(city_dir(city), exist_ok=True)


# ================== GIT SYNC FUNCTIONS ==================
def git_commit_and_push(file_path, message):
    """Face commit și push la Git pentru sincronizare multi-device"""
    if not GIT_ENABLED or not GIT_REPO:
        return
    
    try:
        # Convertește path-ul la relativ față de BASE_DIR pentru Git
        rel_path = os.path.relpath(file_path, BASE_DIR)
        
        # Adaugă fișierul la staging
        GIT_REPO.index.add([rel_path])
        
        # Face commit
        GIT_REPO.index.commit(message, author=None)
        
        # Push la remote (dacă există)
        try:
            origin = GIT_REPO.remote('origin')
            origin.push()
            print(f"✓ Git push: {rel_path}")
        except:
            # Dacă nu e setup remote, doar commit local
            print(f"✓ Git commit (local): {rel_path}")
    
    except Exception as e:
        print(f"✗ Git error: {str(e)}")


def git_pull_and_sync():
    """Face pull de pe Git și sincronizează datele locale"""
    if not GIT_ENABLED or not GIT_REPO:
        return
    
    try:
        # Încearcă să facă pull
        try:
            origin = GIT_REPO.remote('origin')
            origin.pull()
            print("✓ Git pull: Sincronizare cu serverul")
            return True
        except:
            # Dacă nu e setup remote, skip
            return False
    
    except Exception as e:
        print(f"✗ Git pull error: {str(e)}")
        return False


def ensure_institution(city, institution):
    ensure_city(city)
    path = institution_path(city, institution)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)


def load_institution(city, institution):
    with open(institution_path(city, institution), "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Pentru compatibilitate cu datele vechi (fără structură de coloane)
    if isinstance(data, list):
        return {"columns": ["DISCORD", "RANK", "PUNCTAJ"], "ranks": {}, "rows": data}
    
    # Asigură că au rankuri și rânduri dacă lipsesc
    if "ranks" not in data:
        data["ranks"] = {}
    if "rows" not in data:
        data["rows"] = []
    
    return data


def save_institution(city, institution, tree, update_timestamp=False, updated_items=None):
    # Încarcă datele existente pentru a păstra rankurile și timestamp-ul
    existing_data = load_institution(city, institution)
    ranks_map = existing_data.get("ranks", {})
    ranks_desc = existing_data.get("rankuri_desc", "")
    last_update = existing_data.get("last_punctaj_update", "")
    existing_rows = {str(row.get("DISCORD", "")): row for row in existing_data.get("rows", [])}
    
    # Dacă e o modificare de punctaj, actualizează timestamp-ul global
    if update_timestamp:
        last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Asigură că ULTIMA_MOD este în coloane
    columns = list(tree.columns)
    if "ULTIMA_MOD" not in columns:
        columns.append("ULTIMA_MOD")
    
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    data = {
        "columns": columns,
        "ranks": ranks_map,
        "rankuri_desc": ranks_desc,
        "last_punctaj_update": last_update,
        "rows": []
    }
    
    for item in tree.get_children():
        values = list(tree.item(item, "values"))
        row_dict = dict(zip(tree.columns, values))
        
        # Dacă rândul este în updated_items, actualizează ULTIMA_MOD
        if updated_items and item in updated_items:
            row_dict["ULTIMA_MOD"] = current_timestamp
        else:
            # Păstrează ULTIMA_MOD vechia dacă nu e actualizat
            discord_val = row_dict.get("DISCORD", "")
            if discord_val in existing_rows:
                row_dict["ULTIMA_MOD"] = existing_rows[discord_val].get("ULTIMA_MOD", "")
        
        data["rows"].append(row_dict)
    
    file_path = institution_path(city, institution)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    # Auto-commit și push la Git
    git_commit_and_push(file_path, f"Update {city}/{institution}")


def delete_institution(city, institution):
    path = institution_path(city, institution)
    if os.path.exists(path):
        os.remove(path)
        # Commit delete-ul la Git
        if GIT_ENABLED and GIT_REPO:
            try:
                GIT_REPO.index.remove([path])
                GIT_REPO.index.commit(f"Delete {city}/{institution}")
                print(f"✓ Git: Ștergere {path}")
            except:
                pass


def delete_city(city):
    path = city_dir(city)
    if os.path.exists(path):
        shutil.rmtree(path)

# ================== UI ==================
root = tk.Tk()
root.title("Manager punctaj - orase / institutii / angajati")
root.geometry("1200x700")

style = ttk.Style()
style.theme_use("default")
style.configure("Treeview", rowheight=28)
style.configure("Treeview.Heading", anchor="center")

# ================== LAYOUT ==================
main = tk.Frame(root)
main.pack(fill="both", expand=True)

# -------- SIDEBAR --------
sidebar = tk.Frame(main, width=200, bg="#f0f0f0")
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

tk.Label(sidebar, text="Orașe", font=("Segoe UI", 12, "bold"), bg="#f0f0f0").pack(pady=20)

btn_add_tab = tk.Button(sidebar, text="➕ Adaugă oraș", width=18)
btn_add_tab.pack(pady=8)

btn_edit_tab = tk.Button(sidebar, text="✏️ Editează oraș", width=18)
btn_edit_tab.pack(pady=8)

btn_del_tab = tk.Button(sidebar, text="❌ Șterge oraș", width=18)
btn_del_tab.pack(pady=8)

# -------- CONTENT --------
content = tk.Frame(main)
content.pack(side="right", fill="both", expand=True)

city_notebook = ttk.Notebook(content)
city_notebook.pack(fill="both", expand=True)


# ================== GIT PERIODIC SYNC ==================
def git_periodic_sync():
    """Sincronizează datele locale cu Git la fiecare 5 minute"""
    def sync():
        try:
            # Încearcă pull pentru a lua modificările de pe Git
            if git_pull_and_sync():
                # Dacă pull-ul a reușit și sunt conflicte, reload-ează interfața
                print("[Git] Datele au fost sincronizate cu serverul")
                # Ar putea triggera reload de tab-uri dacă necesare
        except Exception as e:
            print(f"[Git] Eroare la sync: {str(e)}")
    
    # Rulează sync la fiecare 5 minute
    schedule.every(5).minutes.do(sync)


# Inițializează Git sync
git_periodic_sync()


# ================== AUTO-RESET SCHEDULER ==================
def auto_reset_all_institutions():
    """Face reset automat la toate instituțiile din toate orașele"""
    print(f"[{datetime.now()}] Inițiez reset automat pentru prima zi a lunii...")
    
    # Iterează prin toate orașele
    for city_dir_name in os.listdir(DATA_DIR):
        city_path = os.path.join(DATA_DIR, city_dir_name)
        if not os.path.isdir(city_path):
            continue
        
        # Iterează prin toate instituțiile din oraș
        for json_file in os.listdir(city_path):
            if not json_file.endswith('.json'):
                continue
            
            institution = json_file[:-5]
            
            try:
                inst_data = load_institution(city_dir_name, institution)
                columns = inst_data.get("columns", [])
                rows = inst_data.get("rows", [])
                
                if "PUNCTAJ" not in columns:
                    continue
                
                # Creează folder de arhivă și salvează raport
                archive_city_dir = os.path.join(ARCHIVE_DIR, city_dir_name)
                os.makedirs(archive_city_dir, exist_ok=True)
                
                csv_filename = f"{institution}.csv"
                csv_path = os.path.join(archive_city_dir, csv_filename)
                
                reset_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Verifică dacă CSV-ul există
                file_exists = os.path.exists(csv_path)
                
                # Salvează datele vechi în CSV
                with open(csv_path, "a", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile)
                    
                    if not file_exists:
                        header = ["RESET_DATA"] + columns
                        writer.writerow(header)
                    
                    for row in rows:
                        if isinstance(row, dict):
                            values = [row.get(col, "") for col in columns]
                        else:
                            values = list(row) if isinstance(row, (list, tuple)) else [row]
                        
                        writer.writerow([reset_timestamp] + values)
                    
                    writer.writerow([])
                
                # Resetează PUNCTAJ la 0
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for row in rows:
                    if isinstance(row, dict):
                        row["PUNCTAJ"] = 0
                        row["ULTIMA_MOD"] = current_timestamp
                    else:
                        row_dict = {}
                        for i, col in enumerate(columns):
                            row_dict[col] = row[i] if i < len(row) else ""
                        row_dict["PUNCTAJ"] = 0
                        row_dict["ULTIMA_MOD"] = current_timestamp
                        rows[rows.index(row)] = row_dict
                
                # Asigură ULTIMA_MOD în coloane
                if "ULTIMA_MOD" not in columns:
                    columns.append("ULTIMA_MOD")
                
                # Salvează în JSON
                inst_data["columns"] = columns
                inst_data["rows"] = rows
                inst_data["last_punctaj_update"] = reset_timestamp
                
                with open(institution_path(city_dir_name, institution), "w", encoding="utf-8") as f:
                    json.dump(inst_data, f, indent=4, ensure_ascii=False)
                
                print(f"  ✓ Reset: {city_dir_name}/{institution}")
            
            except Exception as e:
                print(f"  ✗ Eroare la reset {city_dir_name}/{institution}: {str(e)}")
    
    print(f"[{datetime.now()}] Reset automat finalizat!")


def schedule_daily_check():
    """Scheduler care verifica daca e prima zi a lunii la 00:00"""
    def check_and_reset():
        now = datetime.now()
        if now.day == 1 and now.hour == 0:
            auto_reset_all_institutions()
    
    schedule.every(1).minutes.do(check_and_reset)
    
    while True:
        schedule.run_pending()
        time.sleep(30)  # Verifica la fiecare 30 de secunde


# Lansează scheduler-ul în background thread
scheduler_thread = threading.Thread(target=schedule_daily_check, daemon=True)
scheduler_thread.start()
tabs = {}  # oras -> {"nb": notebook institutii, "trees": {institutie: tree}}

# ================== FUNCȚII ==================
def create_city_ui(city):
    """Creează UI pentru un oraș și încarcă instituțiile existente."""
    ensure_city(city)

    city_frame = tk.Frame(city_notebook)
    city_notebook.add(city_frame, text=city)

    inst_nb = ttk.Notebook(city_frame)
    inst_nb.pack(fill="both", expand=True)

    controls = tk.Frame(city_frame)
    controls.pack(fill="x", pady=8)

    tk.Button(controls, text="➕ Adaugă instituție", width=18, command=lambda c=city: add_institution(c)).pack(side="left", padx=5)
    tk.Button(controls, text="✏️ Editează instituție", width=18, command=lambda c=city: edit_institution(c)).pack(side="left", padx=5)
    tk.Button(controls, text="❌ Șterge instituții", width=18, command=lambda c=city: delete_institution_ui(c)).pack(side="left", padx=5)

    tabs[city] = {"nb": inst_nb, "trees": {}, "info_frames": {}}

    # Încarcă instituțiile existente din folderul orașului
    for json_file in sorted([f for f in os.listdir(city_dir(city)) if f.endswith('.json')]):
        inst = json_file[:-5]
        create_institution_tab(city, inst)

    return city_frame


def add_tab():
    city = simpledialog.askstring("Nume oraș", "Introdu numele orașului:")
    if not city:
        return

    city = city.strip().replace(" ", "_")

    if city in tabs:
        messagebox.showerror("Eroare", "Există deja un oraș cu acest nume!")
        return

    frame = create_city_ui(city)
    city_notebook.select(frame)

def edit_tab():
    current = city_notebook.select()
    if not current:
        messagebox.showinfo("Info", "Selectează un oraș mai întâi!")
        return

    old_city = city_notebook.tab(current, "text")
    new_city = simpledialog.askstring("Editează oraș", "Nume nou:", initialvalue=old_city)
    if not new_city:
        return
    new_city = new_city.strip().replace(" ", "_")

    if new_city == old_city:
        return
    if new_city in tabs:
        messagebox.showerror("Eroare", "Există deja un oraș cu acest nume!")
        return

    try:
        os.rename(city_dir(old_city), city_dir(new_city))
    except Exception as e:
        messagebox.showerror("Eroare", f"Nu pot redenumi orașul: {e}")
        return

    # Elimină tab-ul vechi și reconstruiește orașul cu numele nou
    for tab_id in city_notebook.tabs():
        if city_notebook.tab(tab_id, "text") == old_city:
            city_notebook.forget(tab_id)
            break
    tabs.pop(old_city, None)

    frame = create_city_ui(new_city)
    city_notebook.select(frame)


def delete_tab():
    # Șterge orașe (tabele principale)
    if not tabs:
        messagebox.showinfo("Info", "Nu există orașe de șters!")
        return

    win = tk.Toplevel(root)
    win.title("Șterge orașe")
    win.geometry("400x450")
    win.grab_set()

    frame_top = tk.Frame(win, bg="#ffe8e8", pady=10)
    frame_top.pack(fill="x")

    tk.Label(
        frame_top,
        text="Selectează orașele pe care vrei să le ștergi",
        font=("Segoe UI", 10, "bold"),
        bg="#ffe8e8"
    ).pack(pady=5)

    tk.Label(
        frame_top,
        text="⚠️ Se vor șterge toate instituțiile și angajații din orașele selectate",
        font=("Segoe UI", 9),
        fg="#d32f2f",
        bg="#ffe8e8"
    ).pack(pady=2)

    frame_list = tk.Frame(win)
    frame_list.pack(fill="both", expand=True, pady=10)

    canvas = tk.Canvas(frame_list)
    scrollbar = tk.Scrollbar(frame_list, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    vars_cities = []
    for city in sorted(tabs.keys()):
        var = tk.BooleanVar(value=False)
        inst_count = len(tabs[city]["trees"])
        chk = tk.Checkbutton(
            scroll_frame,
            text=f"🏙️ {city} ({inst_count} instituții)",
            variable=var,
            anchor="w",
            font=("Segoe UI", 10)
        )
        chk.pack(fill="x", padx=10, pady=3)
        vars_cities.append((city, var))

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=5)

    def select_all():
        for _, var in vars_cities:
            var.set(True)

    tk.Button(btn_frame, text="✓ Selectează toate", command=select_all, width=18).pack(side="left", padx=5)

    def deselect_all():
        for _, var in vars_cities:
            var.set(False)

    tk.Button(btn_frame, text="✗ Deselectează toate", command=deselect_all, width=18).pack(side="left", padx=5)

    def aplica():
        selectate = [city for city, var in vars_cities if var.get()]
        if not selectate:
            messagebox.showwarning("Nicio selecție", "Nu ai selectat niciun oraș!")
            return

        if not messagebox.askyesno(
            "Confirmare ștergere",
            f"Ștergi {len(selectate)} oraș(e) și toate datele aferente?"
        ):
            return

        for city in selectate:
            # șterge tab din notebook
            for tab_id in city_notebook.tabs():
                if city_notebook.tab(tab_id, "text") == city:
                    city_notebook.forget(tab_id)
                    break
            delete_city(city)
            tabs.pop(city, None)

        win.destroy()
        messagebox.showinfo("Succes", "Orașele selectate au fost șterse.")

    tk.Button(
        win,
        text="🗑️ ȘTERGE ORAȘE",
        bg="#F44336",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        width=25,
        height=2,
        command=aplica
    ).pack(pady=15)
 
# ================== INSTITUȚII ==================
def sort_tree_by_punctaj(tree):
    """Sortează treeview-ul descrescător după coloana PUNCTAJ"""
    columns = tree.columns
    if "PUNCTAJ" not in columns:
        return
    
    punctaj_idx = columns.index("PUNCTAJ")
    
    # Extrage toate rândurile cu valorile lor
    items = []
    for item in tree.get_children():
        values = tree.item(item, "values")
        try:
            punctaj = int(values[punctaj_idx]) if punctaj_idx < len(values) else 0
        except (ValueError, IndexError):
            punctaj = 0
        items.append((item, values, punctaj))
    
    # Sortează descrescător după punctaj
    items.sort(key=lambda x: x[2], reverse=True)
    
    # Rearanjează rândurile în treeview
    for index, (item, values, _) in enumerate(items):
        tree.move(item, "", index)


def sync_roles_with_ranks(tree, ranks_map):
    """Sincronizează rolurile din ROLE coloană cu definiția rankurilor curente"""
    columns = tree.columns
    if "RANK" not in columns or "ROLE" not in columns:
        return
    
    rank_idx = columns.index("RANK")
    role_idx = columns.index("ROLE")
    
    needs_save = False
    for item in tree.get_children():
        values = list(tree.item(item, "values"))
        rank = str(values[rank_idx]).strip()
        old_role = str(values[role_idx]).strip()
        
        # Dacă rankul are o definiție în ranks_map și rolul nu se potrivește, actualizează
        if rank in ranks_map:
            new_role = ranks_map[rank]
            if old_role != new_role:
                values[role_idx] = new_role
                tree.item(item, values=tuple(values))
                needs_save = True
    
    return needs_save


def reset_punctaj(tree, city, institution):
    """Resetează PUNCTAJ-ul la 0, arhivează datele vechi în CSV (actualizeaza CSV existent)"""
    
    if not messagebox.askyesno(
        "Confirmare resetare",
        f"Sigur vrei să resetezi punctajul pentru toți angajații?\n\nDatele vechi vor fi salvate în arhiva."
    ):
        return
    
    # Încarcă datele instituției
    inst_data = load_institution(city, institution)
    columns = inst_data.get("columns", [])
    rows = inst_data.get("rows", [])
    
    if "PUNCTAJ" not in columns:
        messagebox.showwarning("Eroare", "Nu există coloana PUNCTAJ!")
        return
    
    punctaj_idx = columns.index("PUNCTAJ")
    
    # Creează folder de arhivă pentru oraș
    archive_city_dir = os.path.join(ARCHIVE_DIR, city)
    os.makedirs(archive_city_dir, exist_ok=True)
    
    # CSV-ul nu are timestamp, doar numele instituției
    csv_filename = f"{institution}.csv"
    csv_path = os.path.join(archive_city_dir, csv_filename)
    
    # Timestamp pentru reset
    reset_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Verifică dacă CSV-ul există deja
    file_exists = os.path.exists(csv_path)
    
    # Salvează datele vechi în CSV (append dacă există)
    with open(csv_path, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        
        # Dacă fișierul nu exista, adaug header
        if not file_exists:
            header = ["RESET_DATA"] + columns
            writer.writerow(header)
        
        # Scriu rândurile cu timestamp-ul reset-ului
        for row in rows:
            if isinstance(row, dict):
                values = [row.get(col, "") for col in columns]
            else:
                values = list(row) if isinstance(row, (list, tuple)) else [row]
            
            # Adaug timestamp la început
            writer.writerow([reset_timestamp] + values)
        
        # Adaug o linie goală pentru separator vizual
        writer.writerow([])
    
    # Resetează PUNCTAJ-ul la 0 și adaug ULTIMA_MOD
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for row in rows:
        if isinstance(row, dict):
            row["PUNCTAJ"] = 0
            row["ULTIMA_MOD"] = current_timestamp
        else:
            # Convertește la dict dacă e list
            row_dict = {}
            for i, col in enumerate(columns):
                row_dict[col] = row[i] if i < len(row) else ""
            row_dict["PUNCTAJ"] = 0
            row_dict["ULTIMA_MOD"] = current_timestamp
            rows[rows.index(row)] = row_dict
    
    # Asigură că ULTIMA_MOD este în coloane
    if "ULTIMA_MOD" not in columns:
        columns.append("ULTIMA_MOD")
    
    # Salvează datele resetate în JSON cu timestamp
    inst_data["columns"] = columns
    inst_data["rows"] = rows
    inst_data["last_punctaj_update"] = reset_timestamp
    with open(institution_path(city, institution), "w", encoding="utf-8") as f:
        json.dump(inst_data, f, indent=4, ensure_ascii=False)
    
    # Reîncarcă treeview-ul cu noua coloană
    if "ULTIMA_MOD" not in tree.columns:
        tree.columns = list(tree.columns) + ["ULTIMA_MOD"]
        tree.heading("ULTIMA_MOD", text="ULTIMA_MOD", anchor="center")
        tree.column("ULTIMA_MOD", anchor="center", width=200)
    
    tree.delete(*tree.get_children())
    for row in rows:
        if isinstance(row, dict):
            values = tuple(row.get(col, "") for col in tree.columns)
        else:
            values = tuple(row) if isinstance(row, (list, tuple)) else (row,)
        tree.insert("", tk.END, values=values)
    
    update_info_label(city, institution)
    sort_tree_by_punctaj(tree)
    
    messagebox.showinfo("Succes", f"Punctaj resetat! Datele vechi salvate în:\n{csv_path}")


def update_info_label(city, institution):
    """Actualizează label-ul cu timestamp-ul ultimei modificări"""
    if city not in tabs or institution not in tabs[city]["info_frames"]:
        return
    
    inst_data = load_institution(city, institution)
    last_update = inst_data.get("last_punctaj_update", "N/A")
    info_label = tabs[city]["info_frames"][institution]
    info_label.config(text=f"⏱️ Ultima modificare: {last_update}")


def apply_search_filter(tree, search_column, search_text, all_rows, columns):
    """Filtrează treeview-ul pe baza coloanei și textului de căutare"""
    tree.delete(*tree.get_children())
    
    if not search_column or not search_text:
        # Dacă nu e specificată căutare, arată toate rândurile
        for row in all_rows:
            if isinstance(row, dict):
                values = tuple(row.get(col, "") for col in columns)
            else:
                values = tuple(row) if isinstance(row, (list, tuple)) else (row,)
            tree.insert("", tk.END, values=values)
    else:
        # Filtrează rândurile care conțin textul de căutare în coloana specificată
        col_index = columns.index(search_column) if search_column in columns else 0
        search_lower = search_text.lower()
        
        for row in all_rows:
            if isinstance(row, dict):
                values = tuple(row.get(col, "") for col in columns)
            else:
                values = tuple(row) if isinstance(row, (list, tuple)) else (row,)
            
            # Compară valoarea din coloana specificată
            if col_index < len(values):
                cell_value = str(values[col_index]).lower()
                if search_lower in cell_value:
                    tree.insert("", tk.END, values=values)
    
    sort_tree_by_punctaj(tree)


def create_institution_tab(city, institution):
    ensure_institution(city, institution)

    inst_nb = tabs[city]["nb"]
    frame = tk.Frame(inst_nb)
    inst_nb.add(frame, text=institution)

    inst_data = load_institution(city, institution)
    columns = inst_data.get("columns", ["Discord", "Nume", "Punctaj"])
    rows = inst_data.get("rows", [])
    ranks_map = inst_data.get("ranks", {})

    tree = ttk.Treeview(
        frame,
        columns=columns,
        show="headings",
        selectmode="extended"
    )
    
    # Salvează coloanele pe tree pentru a le folosi în save_institution
    tree.columns = columns

    for col in columns:
        tree.heading(col, text=col.upper(), anchor="center")
        tree.column(col, anchor="center", width=200)

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # Încarcă rândurile din date
    for row in rows:
        if isinstance(row, dict):
            values = tuple(row.get(col, "") for col in columns)
        else:
            values = tuple(row) if isinstance(row, (list, tuple)) else (row,)
        tree.insert("", tk.END, values=values)
    
    # Sincronizează rolurile cu rankurile curente
    if sync_roles_with_ranks(tree, ranks_map):
        save_institution(city, institution, tree)
    
    # Sortează angajații descrescător după PUNCTAJ
    sort_tree_by_punctaj(tree)

    # ===== INFO FRAME CU TIMESTAMP ULTIMEI MODIFICARI =====
    last_update = inst_data.get("last_punctaj_update", "N/A")
    info_frame = tk.Frame(frame, bg="#e3f2fd", relief="solid", borderwidth=1)
    info_frame.pack(fill="x", padx=10, pady=5)
    
    info_label = tk.Label(
        info_frame, 
        text=f"⏱️ Ultima modificare: {last_update}", 
        font=("Segoe UI", 9), 
        bg="#e3f2fd",
        fg="#1565c0"
    )
    info_label.pack(side="left", padx=10, pady=5)
    
    # Salvează referința la info_label pentru actualizare dinamică
    tabs[city]["info_frames"][institution] = info_label

    # ===== SEARCH FRAME =====
    search_frame = tk.Frame(frame, bg="#f0f0f0", relief="solid", borderwidth=1)
    search_frame.pack(fill="x", padx=10, pady=10)
    
    tk.Label(search_frame, text="🔍 Cauta:", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(side="left", padx=10, pady=8)
    
    # Dropdown pentru selectarea coloanei (excluzând ROLE)
    searchable_columns = [col for col in columns if col != "ROLE"]
    cb_column = ttk.Combobox(search_frame, values=searchable_columns, state="readonly", width=15, font=("Segoe UI", 9))
    cb_column.pack(side="left", padx=5)
    if searchable_columns:
        cb_column.current(0)
    
    # Entry pentru textul de căutare
    search_entry = tk.Entry(search_frame, font=("Segoe UI", 9), width=20)
    search_entry.pack(side="left", padx=5)
    
    # Funcție de căutare
    def do_search():
        search_col = cb_column.get()
        search_txt = search_entry.get().strip()
        apply_search_filter(tree, search_col, search_txt, rows, columns)
    
    # Funcție de reset
    def reset_search():
        search_entry.delete(0, tk.END)
        cb_column.current(0)
        apply_search_filter(tree, "", "", rows, columns)
    
    tk.Button(search_frame, text="🔎 Cauta", command=do_search, font=("Segoe UI", 9), bg="#2196F3", fg="white").pack(side="left", padx=5)
    tk.Button(search_frame, text="✕ Reset", command=reset_search, font=("Segoe UI", 9), bg="#757575", fg="white").pack(side="left", padx=5)
    
    # Bind Enter pe search_entry pentru căutare rapidă
    search_entry.bind("<Return>", lambda e: do_search())

    btn_frame = tk.Frame(frame)
    btn_frame.pack(pady=10)

    tk.Button(
        btn_frame, text="Adaugă angajat", width=18,
        command=lambda t=tree, c=city, inst=institution: add_member(t, c, inst)
    ).grid(row=0, column=0, padx=8, pady=5)

    tk.Button(
        btn_frame, text="Șterge angajat", width=18,
        command=lambda t=tree, c=city, inst=institution: delete_members(t, c, inst)
    ).grid(row=0, column=1, padx=8, pady=5)

    tk.Button(
        btn_frame, text="✏️ Editează angajat", width=18,
        command=lambda t=tree, c=city, inst=institution: edit_member(t, c, inst)
    ).grid(row=0, column=2, padx=8, pady=5)

    tk.Button(
        btn_frame, text="➕ Adaugă punctaj", width=18,
        command=lambda t=tree, c=city, inst=institution: punctaj_cu_selectie(t, c, inst, "add")
    ).grid(row=1, column=0, padx=8, pady=5)

    tk.Button(
        btn_frame, text="➖ Scade punctaj", width=18,
        command=lambda t=tree, c=city, inst=institution: punctaj_cu_selectie(t, c, inst, "remove")
    ).grid(row=1, column=1, padx=8, pady=5)

    tk.Button(
        btn_frame, text="🔄 Reset punctaj", width=18, bg="#FF9800", fg="white",
        command=lambda t=tree, c=city, inst=institution: reset_punctaj(t, c, inst)
    ).grid(row=1, column=2, padx=8, pady=5)

    tabs[city]["trees"][institution] = tree
    inst_nb.select(frame)




def add_institution(city):
    name = simpledialog.askstring("Instituție", f"Instituție nouă în {city}:")
    if not name:
        return
    name = name.strip().replace(" ", "_")
    if name in tabs[city]["trees"]:
        messagebox.showerror("Eroare", "Există deja o instituție cu acest nume în oraș!")
        return
    
    # Fereastră pentru definire variabile suplimentare
    win = tk.Toplevel(root)
    win.title(f"Adaugă variabile - {name} ({city})")
    win.geometry("550x500")
    win.grab_set()
    
    tk.Label(win, text="Adaugă variabile personalizate pentru instituție", font=("Segoe UI", 10, "bold")).pack(pady=10)
    tk.Label(win, text="Variabilele RANK, ROLE și PUNCTAJ sunt deja incluse!", font=("Segoe UI", 9), fg="#2196F3").pack(pady=5)
    
    # ===== RANKURI - PRIMA ALEGERE =====
    tk.Label(win, text="Configurare RANK", font=("Segoe UI", 10, "bold"), fg="#FF9800").pack(pady=10)
    
    rank_frame = tk.Frame(win, relief="solid", borderwidth=1, bg="#fff3e0")
    rank_frame.pack(fill="x", padx=10, pady=5)
    
    tk.Label(rank_frame, text="Câte rankuri ai? (ex: 3 pentru rankuri 1, 2, 3)", font=("Segoe UI", 9), bg="#fff3e0").pack(anchor="w", padx=10, pady=5)
    e_num_ranks = tk.Entry(rank_frame, width=10, font=("Segoe UI", 10))
    e_num_ranks.insert(0, "2")
    e_num_ranks.pack(anchor="w", padx=10, pady=5)
    
    # Frame pentru definire rankuri (inițial gol, se completează după input)
    ranks_defs = tk.Frame(win)
    ranks_defs.pack(fill="both", expand=True, padx=10, pady=5)
    
    canvas_defs = tk.Canvas(ranks_defs)
    scrollbar_defs = tk.Scrollbar(ranks_defs, orient="vertical", command=canvas_defs.yview)
    scroll_defs = tk.Frame(canvas_defs)
    
    scroll_defs.bind("<Configure>", lambda e: canvas_defs.configure(scrollregion=canvas_defs.bbox("all")))
    canvas_defs.create_window((0, 0), window=scroll_defs, anchor="nw")
    canvas_defs.configure(yscrollcommand=scrollbar_defs.set)
    
    canvas_defs.pack(side="left", fill="both", expand=True)
    scrollbar_defs.pack(side="right", fill="y")
    
    rank_entries = {}
    
    def update_rank_fields(*args):
        """Actualizează câmpurile de rank când se schimbă numărul"""
        try:
            num = int(e_num_ranks.get())
            if num < 1:
                num = 1
        except ValueError:
            return
        
        # Curăță frame-urile anterioare
        for widget in scroll_defs.winfo_children():
            widget.destroy()
        rank_entries.clear()
        
        tk.Label(scroll_defs, text="Definește rolul pentru fiecare rank:", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=5, pady=(5, 10))
        
        for rank_num in range(1, num + 1):
            rank_row = tk.Frame(scroll_defs, relief="solid", borderwidth=1)
            rank_row.pack(fill="x", pady=5, padx=5)
            
            tk.Label(rank_row, text=f"Rank {rank_num} →", font=("Segoe UI", 9, "bold")).pack(side="left", padx=5, pady=5)
            e_rol = tk.Entry(rank_row, width=30, font=("Segoe UI", 10))
            e_rol.pack(side="left", padx=5, pady=5, fill="x", expand=True)
            
            # Setează roluri implicite
            if rank_num == 1:
                e_rol.insert(0, "User")
            elif rank_num == 2:
                e_rol.insert(0, "Admin")
            
            rank_entries[rank_num] = e_rol
    
    e_num_ranks.bind("<KeyRelease>", update_rank_fields)
    update_rank_fields()  # Inițializează cu 2 rankuri
    
    # ===== VARIABILE PERSONALIZATE =====
    tk.Label(win, text="Variabile personalizate", font=("Segoe UI", 10, "bold"), fg="#FF9800").pack(pady=10)
    
    frame_list = tk.Frame(win)
    frame_list.pack(fill="both", expand=True, padx=10, pady=5)
    
    canvas = tk.Canvas(frame_list)
    scrollbar = tk.Scrollbar(frame_list, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)
    
    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    extra_columns = []
    
    def add_column():
        col_frame = tk.Frame(scroll_frame, relief="solid", borderwidth=1)
        col_frame.pack(fill="x", pady=5, padx=5)
        
        tk.Label(col_frame, text="Variabilă:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        e_col = tk.Entry(col_frame, width=30, font=("Segoe UI", 10))
        e_col.grid(row=0, column=1, padx=5, pady=5)
        
        def remove_col():
            col_frame.destroy()
            if e_col in extra_columns:
                extra_columns.remove(e_col)
        
        tk.Button(col_frame, text="✕ Șterge", command=remove_col, width=8, bg="#F44336", fg="white").grid(row=0, column=2, padx=5, pady=5)
        
        extra_columns.append(e_col)
    
    btn_frame = tk.Frame(win)
    btn_frame.pack(fill="x", pady=10)
    
    tk.Button(btn_frame, text="➕ Adaugă variabilă", command=add_column, width=30, bg="#2196F3", fg="white").pack(side="left", padx=5)
    
    def save_structure():
        # Validează numărul de rankuri
        try:
            num_ranks = int(e_num_ranks.get())
            if num_ranks < 1:
                messagebox.showerror("Eroare", "Trebuie să ai cel puțin 1 rank!")
                return
        except ValueError:
            messagebox.showerror("Eroare", "Introduceți un număr valid pentru rankuri!")
            return
        
        # Validează roluri pentru fiecare rank
        ranks_data = {}
        for rank_num in range(1, num_ranks + 1):
            rol = rank_entries[rank_num].get().strip()
            if not rol:
                messagebox.showerror("Eroare", f"Introduceți un rol pentru rank {rank_num}!")
                return
            ranks_data[str(rank_num)] = rol
        
        # Variabile custom
        col_names = [e.get().strip().upper() for e in extra_columns]
        col_names = [c for c in col_names if c]
        
        # Verifică duplicate
        if len(col_names) != len(set(col_names)):
            messagebox.showerror("Eroare", "Nu pot exista două variabile cu același nume!")
            return
        
        # Structura finală: Variabile custom + RANK + ROLE + PUNCTAJ
        final_cols = col_names + ["RANK", "ROLE", "PUNCTAJ"]
        
        ensure_institution(city, name)
        
        # Crea o descriere ușor de citit a rankurilor
        ranks_description = "\n".join([f"Rank {rank_num}: {ranks_data[str(rank_num)]}" for rank_num in sorted([int(k) for k in ranks_data.keys()])])
        
        data = {
            "columns": final_cols,
            "ranks": ranks_data,
            "rankuri_desc": ranks_description,
            "rows": []
        }
        with open(institution_path(city, name), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        win.destroy()
        create_institution_tab(city, name)
    
    tk.Button(btn_frame, text="✓ Creează tabel", command=save_structure, bg="#4CAF50", fg="white", width=30, font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)


def edit_institution(city):
    inst_nb = tabs.get(city, {}).get("nb")
    if not inst_nb:
        messagebox.showinfo("Info", "Nu există instituții de editat!")
        return

    current = inst_nb.select()
    if not current:
        messagebox.showinfo("Info", "Selectează o instituție din tab-urile orașului!")
        return

    old_inst = inst_nb.tab(current, "text")
    new_inst = simpledialog.askstring("Editează instituție", "Nume nou:", initialvalue=old_inst)
    if not new_inst:
        return
    new_inst = new_inst.strip().replace(" ", "_")

    if new_inst == old_inst:
        return
    if new_inst in tabs[city]["trees"]:
        messagebox.showerror("Eroare", "Există deja o instituție cu acest nume!")
        return

    try:
        os.rename(institution_path(city, old_inst), institution_path(city, new_inst))
    except Exception as e:
        messagebox.showerror("Eroare", f"Nu pot redenumi instituția: {e}")
        return

    # reconstruieste tab-ul instituției
    inst_nb.forget(current)
    tabs[city]["trees"].pop(old_inst, None)
    create_institution_tab(city, new_inst)


def delete_institution_ui(city):
    trees = tabs.get(city, {}).get("trees", {})
    if not trees:
        messagebox.showinfo("Info", "Nu există instituții de șters în acest oraș!")
        return

    win = tk.Toplevel(root)
    win.title(f"Șterge instituții - {city}")
    win.geometry("400x450")
    win.grab_set()

    frame_top = tk.Frame(win, bg="#ffe8e8", pady=10)
    frame_top.pack(fill="x")
    tk.Label(frame_top, text="Selectează instituțiile de șters", font=("Segoe UI", 10, "bold"), bg="#ffe8e8").pack(pady=5)

    frame_list = tk.Frame(win)
    frame_list.pack(fill="both", expand=True, pady=10)

    canvas = tk.Canvas(frame_list)
    scrollbar = tk.Scrollbar(frame_list, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)
    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    vars_inst = []
    for inst in sorted(trees.keys()):
        var = tk.BooleanVar(value=False)
        chk = tk.Checkbutton(scroll_frame, text=inst, variable=var, anchor="w", font=("Segoe UI", 10))
        chk.pack(fill="x", padx=10, pady=3)
        vars_inst.append((inst, var))

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=5)

    def select_all():
        for _, var in vars_inst:
            var.set(True)

    tk.Button(btn_frame, text="✓ Selectează toate", command=select_all, width=18).pack(side="left", padx=5)

    def deselect_all():
        for _, var in vars_inst:
            var.set(False)

    tk.Button(btn_frame, text="✗ Deselectează toate", command=deselect_all, width=18).pack(side="left", padx=5)

    def aplica():
        selectate = [inst for inst, var in vars_inst if var.get()]
        if not selectate:
            messagebox.showwarning("Nicio selecție", "Nu ai selectat nicio instituție!")
            return
        if not messagebox.askyesno("Confirmare", f"Ștergi {len(selectate)} instituție(i) din {city}?"):
            return

        inst_nb = tabs[city]["nb"]
        for inst in selectate:
            # șterge tab-ul
            for tab_id in inst_nb.tabs():
                if inst_nb.tab(tab_id, "text") == inst:
                    inst_nb.forget(tab_id)
                    break
            delete_institution(city, inst)
            tabs[city]["trees"].pop(inst, None)

        win.destroy()
        messagebox.showinfo("Succes", "Instituțiile au fost șterse.")

    tk.Button(win, text="🗑️ ȘTERGE INSTITUȚII", bg="#F44336", fg="white", font=("Segoe UI", 10, "bold"), width=25, height=2, command=aplica).pack(pady=15)


def add_member(tree, city, institution):
    data = load_institution(city, institution)
    ranks_map = data.get("ranks", {})
    
    win = tk.Toplevel(root)
    win.title(f"Adaugă angajat - {institution} ({city})")
    win.geometry("400x350")
    win.resizable(False, False)
    win.grab_set()

    columns = tree.columns
    entries = {}
    
    # Creează mai întâi toate entry-urile
    for i, col in enumerate(columns):
        tk.Label(win, text=f"{col}:").pack(pady=5)
        
        if col == "RANK":
            # Entry pentru RANK (user intră manual numărul)
            e_rank = tk.Entry(win, justify="center", width=30)
            e_rank.pack()
            entries[col] = e_rank
        
        elif col == "ROLE":
            # ROLE este read-only, se completează automat
            e = tk.Entry(win, justify="center", width=30, state="readonly")
            e.pack()
            entries[col] = e
        
        elif col == "PUNCTAJ":
            # PUNCTAJ defaultează la 0
            e = tk.Entry(win, justify="center", width=30)
            e.insert(0, "0")
            e.pack()
            entries[col] = e
        
        else:
            e = tk.Entry(win, justify="center", width=30)
            e.pack()
            entries[col] = e
    
    # Acum configură bind-urile și completările
    if "RANK" in entries:
        def on_rank_change(event=None):
            if "ROLE" in entries:
                rank_val = entries["RANK"].get().strip()
                if rank_val in ranks_map:
                    entries["ROLE"].config(state="normal")
                    entries["ROLE"].delete(0, tk.END)
                    entries["ROLE"].insert(0, ranks_map[rank_val])
                    entries["ROLE"].config(state="readonly")
        
        entries["RANK"].bind("<KeyRelease>", on_rank_change)
        # Apelează la început în caz că RANK are deja valoare (edit)
        on_rank_change()

    def save():
        # Asigură că ROLE este completat înainte de a salva
        if "RANK" in entries and "ROLE" in entries:
            rank_val = entries["RANK"].get().strip()
            if rank_val in ranks_map:
                entries["ROLE"].config(state="normal")
                entries["ROLE"].delete(0, tk.END)
                entries["ROLE"].insert(0, ranks_map[rank_val])
                entries["ROLE"].config(state="readonly")
        
        values = []
        for col in columns:
            if col == "ROLE":
                rank_val = str(entries["RANK"].get())
                values.append(ranks_map.get(rank_val, ""))
            else:
                values.append(entries[col].get().strip())
        
        if not any(values):
            messagebox.showwarning("Eroare", "Adaugă cel puțin o valoare!")
            return
        new_item = tree.insert("", tk.END, values=tuple(values))
        # Actualizează timestamp dacă se schimbă PUNCTAJ
        has_punctaj = "PUNCTAJ" in columns
        # Marchează rândul nou ca updatat
        save_institution(city, institution, tree, update_timestamp=has_punctaj, updated_items=[new_item])
        
        # Adaug ULTIMA_MOD la treeview dacă nu e acolo
        if "ULTIMA_MOD" not in tree.columns:
            tree.columns = list(tree.columns) + ["ULTIMA_MOD"]
            tree.heading("ULTIMA_MOD", text="ULTIMA_MOD", anchor="center")
            tree.column("ULTIMA_MOD", anchor="center", width=200)
            # Reîncarcă datele cu coloana nouă
            tree.delete(*tree.get_children())
            inst_data = load_institution(city, institution)
            rows = inst_data.get("rows", [])
            for row in rows:
                if isinstance(row, dict):
                    values = tuple(row.get(col, "") for col in tree.columns)
                else:
                    values = tuple(row) if isinstance(row, (list, tuple)) else (row,)
                tree.insert("", tk.END, values=values)
        
        update_info_label(city, institution)
        sort_tree_by_punctaj(tree)
        win.destroy()

    tk.Button(win, text="Salvează", command=save).pack(pady=15)

def delete_members(tree, city, institution):
    win = tk.Toplevel(root)
    win.title("Șterge angajat")
    win.geometry("500x550")
    win.grab_set()

    # ---------- HEADER ----------
    frame_top = tk.Frame(win, bg="#ffe8e8", pady=10)
    frame_top.pack(fill="x")

    tk.Label(
        frame_top, 
        text="Selectează angajații pe care vrei să-i ștergi", 
        font=("Segoe UI", 10, "bold"),
        bg="#ffe8e8"
    ).pack(pady=5)

    # ---------- LISTĂ CU CHECKBOX ----------
    frame_list = tk.Frame(win)
    frame_list.pack(fill="both", expand=True, pady=10)

    canvas = tk.Canvas(frame_list)
    scrollbar = tk.Scrollbar(frame_list, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    vars_items = []

    for item in tree.get_children():
        values = tree.item(item, "values")
        # Arată primele 3 coloane pentru identificare (sau mai puține dacă sunt mai puține)
        display = " | ".join(str(v) for v in values[:3])
        var = tk.BooleanVar(value=False)
        chk = tk.Checkbutton(
            scroll_frame,
            text=display,
            variable=var,
            anchor="w"
        )
        chk.pack(fill="x", padx=10, pady=2)
        vars_items.append((item, var))

    # ---------- BUTOANE CONTROL ----------
    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=5)

    def select_all():
        for _, var in vars_items:
            var.set(True)

    tk.Button(btn_frame, text="✓ Selectează toți", command=select_all, width=18).pack(side="left", padx=5)

    def deselect_all():
        for _, var in vars_items:
            var.set(False)

    tk.Button(btn_frame, text="✗ Deselectează toți", command=deselect_all, width=18).pack(side="left", padx=5)

    # ---------- CONFIRMARE ----------
    def aplica():
        selectati = [item for item, var in vars_items if var.get()]

        if not selectati:
            messagebox.showwarning(
                "Nicio selecție",
                "Nu ai selectat niciun angajat pentru ștergere!"
            )
            return

        if not messagebox.askyesno(
            "Confirmare ștergere",
            f"Sigur vrei să ștergi {len(selectati)} angajat/angajați?"
        ):
            return

        for item in selectati:
            tree.delete(item)

        save_institution(city, institution, tree)
        update_info_label(city, institution)
        sort_tree_by_punctaj(tree)
        win.destroy()

    tk.Button(
        win,
        text="🗑️ ȘTERGE SELECTAȚI",
        bg="#F44336",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        width=25,
        height=2,
        command=aplica
    ).pack(pady=15)


def edit_member(tree, city, institution):
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Eroare", "Selectează un angajat!")
        return
    if len(sel) > 1:
        messagebox.showwarning("Eroare", "Selectează un singur angajat pentru editare!")
        return

    item = sel[0]
    old_values = tree.item(item, "values")
    columns = tree.columns
    
    data = load_institution(city, institution)
    ranks_map = data.get("ranks", {})

    win = tk.Toplevel(root)
    win.title(f"Editează angajat - {institution} ({city})")
    win.geometry("400x350")
    win.resizable(False, False)
    win.grab_set()

    entries = {}
    
    # Creează mai întâi toate entry-urile
    for i, col in enumerate(columns):
        tk.Label(win, text=f"{col}:").pack(pady=5)
        
        if col == "RANK":
            # Entry pentru RANK (user intră manual numărul)
            e_rank = tk.Entry(win, justify="center", width=30)
            e_rank.insert(0, old_values[i] if i < len(old_values) else "")
            e_rank.pack()
            entries[col] = e_rank
        
        elif col == "ROLE":
            # ROLE este read-only, se completează automat
            e = tk.Entry(win, justify="center", width=30, state="readonly")
            e.insert(0, old_values[i] if i < len(old_values) else "")
            e.pack()
            entries[col] = e
        
        else:
            e = tk.Entry(win, justify="center", width=30)
            e.insert(0, old_values[i] if i < len(old_values) else "")
            e.pack()
            entries[col] = e
    
    # Acum configură bind-urile și completările
    if "RANK" in entries:
        def on_rank_change(event=None):
            if "ROLE" in entries:
                rank_val = entries["RANK"].get().strip()
                if rank_val in ranks_map:
                    entries["ROLE"].config(state="normal")
                    entries["ROLE"].delete(0, tk.END)
                    entries["ROLE"].insert(0, ranks_map[rank_val])
                    entries["ROLE"].config(state="readonly")
        
        entries["RANK"].bind("<KeyRelease>", on_rank_change)
        # Apelează la început în caz că RANK are deja valoare (edit)
        on_rank_change()

    def save():
        # Asigură că ROLE este completat înainte de a salva
        if "RANK" in entries and "ROLE" in entries:
            rank_val = entries["RANK"].get().strip()
            if rank_val in ranks_map:
                entries["ROLE"].config(state="normal")
                entries["ROLE"].delete(0, tk.END)
                entries["ROLE"].insert(0, ranks_map[rank_val])
                entries["ROLE"].config(state="readonly")
        
        values = []
        for col in columns:
            if col == "ROLE":
                rank_val = str(entries["RANK"].get())
                values.append(ranks_map.get(rank_val, ""))
            else:
                values.append(entries[col].get().strip())
        
        if not any(values):
            messagebox.showwarning("Eroare", "Adaugă cel puțin o valoare!")
            return
        
        # Verifică dacă PUNCTAJ s-a modificat
        punctaj_changed = False
        if "PUNCTAJ" in columns:
            punctaj_idx = columns.index("PUNCTAJ")
            old_punctaj = str(old_values[punctaj_idx]) if punctaj_idx < len(old_values) else ""
            new_punctaj = str(values[punctaj_idx])
            punctaj_changed = old_punctaj != new_punctaj
        
        tree.item(item, values=tuple(values))
        # Marchează rândul ca updatat dacă PUNCTAJ s-a modificat
        save_institution(city, institution, tree, update_timestamp=punctaj_changed, updated_items=[item] if punctaj_changed else None)
        update_info_label(city, institution)
        sort_tree_by_punctaj(tree)
        win.destroy()

    tk.Button(win, text="Salvează", command=save).pack(pady=15)

def add_points(tree, city, institution):
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Eroare", "Selectează cel puțin o persoană!")
        return

    value = simpledialog.askinteger("Adaugă punctaj", "Număr puncte:", minvalue=1)
    if value is None:
        return

    for item in sel:
        d, i, p = tree.item(item, "values")
        tree.item(item, values=(d, i, int(p) + value))

    save_institution(city, institution, tree)

def remove_points(tree, city, institution):
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Eroare", "Selectează cel puțin o persoană!")
        return

    value = simpledialog.askinteger("Șterge punctaj", "Număr puncte:", minvalue=1)
    if value is None:
        return

    for item in sel:
        d, i, p = tree.item(item, "values")
        tree.item(item, values=(d, i, max(0, int(p) - value)))

    save_institution(city, institution, tree)

# ================== LEGARE BUTOANE ==================
btn_add_tab.config(command=add_tab)
btn_edit_tab.config(command=edit_tab)
btn_del_tab.config(command=delete_tab)

# ================== AUTO-ÎNCĂRCARE ORAȘE / INSTITUȚII ==================
def load_existing_tables():
    """Încarcă automat toate orașele (foldere) și instituțiile (fișiere JSON)"""
    if not os.path.exists(DATA_DIR):
        return

    for city in sorted([d for d in os.listdir(DATA_DIR) if os.path.isdir(city_dir(d))]):
        frame = create_city_ui(city)
        city_notebook.select(frame)


# Încarcă tabelele existente la pornire
load_existing_tables()

def punctaj_cu_selectie(tree, city, institution, mode="add"):
    win = tk.Toplevel(root)
    win.title("Adaugă/Șterge valori" if mode == "add" else "Șterge valori")
    win.geometry("400x500")
    win.grab_set()

    # Detectează coloana PUNCTAJ (obligatorie)
    numeric_col = None
    columns = tree.columns
    
    # Caută exact "PUNCTAJ"
    if "PUNCTAJ" in columns:
        numeric_col = "PUNCTAJ"
    else:
        # Fallback pe alte coloane numerice
        for col in columns:
            if col.upper() in ["PUNCTAJ", "VALOARE", "SCOR"]:
                numeric_col = col
                break
    
    if not numeric_col:
        messagebox.showwarning("Eroare", "Nu găsesc coloana PUNCTAJ!")
        return

    frame_top = tk.Frame(win, bg="#e8f4f8" if mode == "add" else "#ffe8e8", pady=10)
    frame_top.pack(fill="x")

    tk.Label(
        frame_top, 
        text=f"PASUL 1: Introdu valoarea pentru {numeric_col}", 
        font=("Segoe UI", 10, "bold"),
        bg="#e8f4f8" if mode == "add" else "#ffe8e8"
    ).pack(pady=5)

    entry = tk.Entry(frame_top, justify="center", font=("Segoe UI", 12), width=15)
    entry.pack(pady=5)
    entry.focus()

    tk.Label(
        win, 
        text="PASUL 2: Selectează rândurile din lista de mai jos", 
        font=("Segoe UI", 9),
        fg="#555"
    ).pack(pady=10)

    frame_list = tk.Frame(win)
    frame_list.pack(fill="both", expand=True, pady=5)

    canvas = tk.Canvas(frame_list)
    scrollbar = tk.Scrollbar(frame_list, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    vars_items = []

    for item in tree.get_children():
        values = tree.item(item, "values")
        var = tk.BooleanVar(value=False)
        chk = tk.Checkbutton(
            scroll_frame,
            text=" | ".join(str(v) for v in values[:3]),
            variable=var,
            anchor="w"
        )
        chk.pack(fill="x", padx=10, pady=2)
        vars_items.append((item, var))

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=5)

    def select_all():
        for _, var in vars_items:
            var.set(True)

    tk.Button(btn_frame, text="✓ Selectează toate", command=select_all, width=18).pack(side="left", padx=5)

    def deselect_all():
        for _, var in vars_items:
            var.set(False)

    tk.Button(btn_frame, text="✗ Deselectează toate", command=deselect_all, width=18).pack(side="left", padx=5)

    def aplica():
        try:
            valoare = int(entry.get())
            if valoare <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Eroare", "Introdu un număr valid!")
            return

        selectati = [item for item, var in vars_items if var.get()]

        if not selectati:
            messagebox.showwarning(
                "Nicio selecție",
                "Nu ai selectat niciun rând!"
            )
            return

        col_idx = columns.index(numeric_col)
        for item in selectati:
            values = list(tree.item(item, "values"))
            try:
                current = int(values[col_idx]) if col_idx < len(values) else 0
            except (ValueError, IndexError):
                current = 0
            
            if mode == "add":
                nou = current + valoare
            else:
                nou = max(0, current - valoare)

            values[col_idx] = str(nou)
            tree.item(item, values=tuple(values))

        save_institution(city, institution, tree, update_timestamp=True, updated_items=selectati)
        update_info_label(city, institution)
        sort_tree_by_punctaj(tree)
        
        tree.selection_set(selectati)
        if selectati:
            tree.see(selectati[0])
        
        win.destroy()

    tk.Button(
        win,
        text="✓ CONFIRMĂ ȘI APLICĂ",
        bg="#4CAF50" if mode == "add" else "#F44336",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        width=25,
        height=2,
        command=aplica
    ).pack(pady=15)


root.mainloop()
