QUICK START - PERMISIUNI INSTITUTII
===================================

## CEA MAI RAPIDA CALE SA SETEZI PERMISIUNI

### 1. DESCHIDE ADMIN PANEL
```
Apasa butonul "⚙️ Admin" din sidebar (dupa login cu Discord)
```

### 2. CAUTA UTILIZATORUL
```
Admin Panel → Cauta utilizator
```

### 3. SETEAZA PERMISIUNILE

Pentru ADAUGARE ANGAJAT:
```
BlackWater / Politie / can_add_employee = ✓ (BIFAT)
```

Pentru STERGERE ANGAJAT:
```
BlackWater / Politie / can_delete_employee = ✓ (BIFAT)
```

Pentru EDITARE ANGAJAT:
```
BlackWater / Politie / can_edit_employee = ✓ (BIFAT)
```

Pentru ADAUGARE PUNCTAJ:
```
BlackWater / Politie / can_add_score = ✓ (BIFAT)
```

### 4. SALVEAZA
```
Click "Salvează Permisiuni"
```

### GATA! ✅
User-ul va vedea butoanele ACTIVE pentru actiunile cu permisiuni.


## EXEMPLE RAPIDE

### User "Alex" poate adauga dar NU sterge angajati la Politie
```
BlackWater/Politie:
✓ can_add_employee = BIFAT
✗ can_delete_employee = NEBIFAT
✓ can_edit_employee = BIFAT
```

### User "Maria" can vede dar NU modifica nimic (Viewer)
```
Toate permisiunile:
✗ NEBIFATE
```

### User "Admin" - acces total (Admin)
```
Toate permisiunile:
✓ BIFATE
```


## BUTOANE CARE SE DEZACTIVEAZA

| Buton | Permisiune | Oras | Institutie |
|-------|-----------|------|-----------|
| ➕ Adaugă angajat | can_add_employee | Orice | Specifica |
| ✏️ Editează angajat | can_edit_employee | Orice | Specifica |
| ❌ Șterge angajat | can_delete_employee | Orice | Specifica |
| ➕ Adaugă punctaj | can_add_score | Orice | Specifica |
| ➕ Adaugă oraș | can_add_city | GLOBAL | N/A |
| ✏️ Editează oraș | can_edit_city | GLOBAL | N/A |
| ❌ Șterge oraș | can_delete_city | GLOBAL | N/A |


## TESTARE RAPIDA

1. Seteaza un user cu `can_add_employee = true`
2. User-ul deschide institutia
3. Vede butonul "➕ Adaugă angajat" ACTIV (nu gri)
4. Apasa butonul - se deschide dialog

1. Seteaza `can_delete_employee = false`
2. User-ul deschide institutia
3. Vede butonul "❌ Șterge angajat" DEZACTIVAT (gri)
4. Nu poate sa nici daca incearca alt mod


## ROLURI AUTOMATE

| Rol | Permisiuni |
|-----|-----------|
| SUPERUSER (👑) | TOATE = ✓ |
| ADMIN (🛡️) | TOATE = ✓ |
| USER (👤) | Doar ce bifezi |
| VIEWER (👁️) | TOATE = ✗ |


## ERORI COMUNE

❌ User nu vede butonul:
   → Inchide/deschide aplicatia
   → Verifica daca are `can_view = true` pentru institutie

❌ Butonul este activ dar nu functioneaza:
   → Verifica daca Discord-ul lui e autentificat
   → Verifica log-urile pentru erori

❌ Permisiunile nu se salveaza:
   → Verifica daca esti SUPERUSER
   → Verifica conexiunea la Supabase
   → Incearca din nou


## SUPORTA RAPIDA

Permisiuni per institutie:
```
{
  "BlackWater": {
    "Politie": {
      "can_add_employee": true,    ← Poate adauga
      "can_delete_employee": false, ← NU poate sterge
      "can_edit_employee": true,    ← Poate edita
      "can_add_score": true         ← Poate adauga punctaje
    }
  }
}
```

Permisiuni globale:
```
{
  "can_add_city": true,     ← Poate adauga orase
  "can_edit_city": true,    ← Poate edita orase
  "can_delete_city": false  ← NU poate sterge orase
}
```

