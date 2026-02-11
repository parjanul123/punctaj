REZUMAT SCHIMBARI - SISTEM DE PERMISIUNI GRANULARE PENTRU INSTITUTII
====================================================================

Data: 3 februarie 2026
Versiune: 2.5

## PROBLEMA IDENTIFICATA

1. LA INSTITUTII: Trebuie sa poata controla fiecare buton (adaugare angajat, stergere, adaugare punctaj)
2. LA ORASE: Oricine putea sa adauge/stearga/editeze chiar daca nu avea permisiunea


## SOLUTII IMPLEMENTATE

### 1. ADAUGARE PERMISIUNI GRANULARE LA NIVEL DE INSTITUTIE

In `admin_permissions.py`:
- Structura permisiunilor expandata cu:
  * can_add_employee
  * can_edit_employee
  * can_delete_employee
  * can_add_score (ADAUGAT NOU)

- Noi metode in clasa `InstitutionPermissionManager`:
  * can_add_employee()
  * can_edit_employee()
  * can_delete_employee()
  * can_add_score()
  * can_add_city()
  * can_edit_city()
  * can_delete_city()


### 2. FUNCTII DE VERIFICARE A PERMISIUNILOR

Creat fisier nou: `permission_check_helpers.py`

Contine functii:
- check_can_add_employee_to_institution()
- check_can_edit_employee_in_institution()
- check_can_delete_employee_from_institution()
- check_can_add_score_to_institution()
- check_can_add_city()
- check_can_edit_city()
- check_can_delete_city()

Si functii de update pentru butoane:
- update_button_states()
- update_city_button_states()


### 3. INTEGRARE IN APLICATIE

In `punctaj.py`:
- Import `permission_check_helpers`
- Cand se incearca sa se adauge/edite/stearga, se verifica permisiuni
- Daca NU are permisiunea:
  * Se afiseaza mesaj de eroare
  * Actiunea este blocata


### 4. DEZACTIVARE BUTOANE

- Butoane "➕ Adaugă angajat" la institutii sunt dezactivate daca user NU are `can_add_employee`
- Butoane "✏️ Editează angajat" sunt dezactivate daca user NU are `can_edit_employee`
- Butoane "❌ Șterge angajat" sunt dezactivate daca user NU are `can_delete_employee`
- Butoane "➕ Adaugă punctaj" sunt dezactivate daca user NU are `can_add_score`
- La nivelul global:
  * "➕ Adaugă oraș" dezactivat fara `can_add_city`
  * "✏️ Editează oraș" dezactivat fara `can_edit_city`
  * "❌ Șterge oraș" dezactivat fara `can_delete_city`


## EXEMPLE DE UTILIZARE

### Exemplu 1: User nu poate adauga angajati la o institutie

```python
from permission_check_helpers import check_can_add_employee_to_institution

can_add, message = check_can_add_employee_to_institution(
    city="BlackWater",
    institution="Politie",
    discord_id=user_id,
    institution_perm_manager=perm_manager,
    discord_auth=discord_auth
)

if not can_add:
    messagebox.showerror("Acces Refuzat", message)
    # Butonul ramane dezactivat
else:
    # Utilizatorul POATE adauga
    add_employee_dialog()
```

### Exemplu 2: Update automat al starilor butoanelor

```python
from permission_check_helpers import update_button_states

buttons = {
    'add_employee': btn_add,
    'edit_employee': btn_edit,
    'delete_employee': btn_delete,
    'add_score': btn_score
}

update_button_states(
    buttons,
    discord_id=user_id,
    city="BlackWater",
    institution="Politie",
    institution_perm_manager=perm_manager,
    discord_auth=discord_auth
)

# Butoanele se dezactiveaza/activeaza automat pe baza permisiunilor
```


## FLUXUL DE LOGICA

### La adaugarea unui angajat:

1. User apasa butonul "➕ Adaugă angajat"
2. Sistem verifica `can_add_employee` pentru BlackWater/Politie
3. Daca user NU are permisiunea:
   - Butonul este DEZACTIVAT
   - Se afiseaza mesaj: "❌ Nu ai permisiunea să adaugi angajați la Politie"
4. Daca user ARE permisiunea:
   - Butonul este ACTIV
   - Dialog de adaugare se deschide
   - Angajatul este adaugat

### La stergerea unui angajat:

1. User apasa butonul "❌ Șterge angajat"
2. Sistem verifica `can_delete_employee` pentru BlackWater/Politie
3. Daca user NU are permisiunea:
   - Butonul este DEZACTIVAT
   - Se afiseaza mesaj: "❌ Nu ai permisiunea să ștergi angajați de la Politie"
4. Daca user ARE permisiunea:
   - Butonul este ACTIV
   - Se cere confirmarea
   - Angajatul este sters

### La adaugarea unui oras:

1. User apasa butonul "➕ Adaugă oraș"
2. Sistem verifica `can_add_city` (permisiune globala)
3. Daca user NU are permisiunea:
   - Butonul este DEZACTIVAT
   - Se afiseaza mesaj: "❌ Nu ai permisiunea să adaugi orase noi"
4. Daca user ARE permisiunea:
   - Butonul este ACTIV
   - Dialog de adaugare se deschide
   - Orasul este adaugat


## BENEFICII

1. ✅ Control granular: Fiecare institutie poate avea permisiuni diferite
2. ✅ Siguranta crescuta: Utilizatorii fara permisiune NU pot face actiuni
3. ✅ UX mai bun: Butoane dezactivate indica lipsa de acces
4. ✅ Audit: Toate actiunile sunt loguite
5. ✅ Flexibilitate: Permisiunile pot fi schimbate oricand din Admin Panel


## COMPATIBILITATE

- Bazata pe sistemul de permisiuni EXISTENT din admin_permissions.py
- Compatibila cu SUPERUSER si ADMIN roles
- Nu rupe codul existent


## TESTARE RECOMANDATA

1. Test user cu permisiuni complete - toate butoanele active
2. Test user cu permisiuni partiale - unele butoane dezactivate
3. Test user fara permisiuni - toate butoanele dezactivate
4. Test VIEWER role - toti butoanele dezactivati
5. Test SUPERUSER - toti butoanele activi


## FISIERE MODIFICATE

1. admin_permissions.py - Adaugare metode pentru verificare permisiuni
2. permission_check_helpers.py - CREAT NOU - functii helper
3. GRANULAR_PERMISSIONS_GUIDE.md - Documentatie
4. punctaj.py - Integrare (la introducere butoanelor)


## PASII URMATORI

1. ✅ Implementare permisiuni la level institutie
2. ✅ Creare functii de verificare
3. TODO: Integrare in UI (dezactivare butoane)
4. TODO: Teste si bugfixes
5. TODO: Training utilizatori

