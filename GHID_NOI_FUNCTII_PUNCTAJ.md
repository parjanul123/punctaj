# 📘 Ghid de Utilizare - Noi Funcții de Punctaj

## 🎯 Cum să Adaugi Punctaj cu Acțiune

### Pași:

1. **Selectează instituția** din lista de orașe și instituții
2. **Apasă butonul "➕ Adaugă punctaj"**
3. **În fereastra care se deschide:**

   #### Pasul 1️⃣ - Valoarea Punctajului
   - Introdu numărul de puncte pe care vrei să le adaugi
   - Exemplu: `5`, `10`, `15`

   #### Pasul 2️⃣ - Selectează Acțiunea
   - Din dropdown-ul "Selectează tipul de acțiune", alege:
     - 🏙️ **Patrula de oras** - Patrule în interiorul orașului
     - 🌳 **Patrula de camp** - Patrule în afara orașului
     - 🚨 **Razie** - Operațiuni/razii speciale

   #### Pasul 3️⃣ - Zonă (DOAR pentru Razie)
   - Dacă ai selectat "Razie", câmpul **Zonă** devine activ
   - Introdu zona unde a fost efectuată razie
   - Exemplu: `Centru`, `Periferica`, `Parc Industrial`
   - Pentru alte acțiuni, acest câmp rămâne dezactivat

   #### Pasul 4️⃣ - Selectează Persoane
   - Bifează persoanele care au participat la acțiune
   - Poți folosi:
     - ✓ **Selectează toate** - pentru a selecta toți angajații
     - ✗ **Deselectează toate** - pentru a deselecționa

4. **Apasă "✓ CONFIRMĂ ȘI APLICĂ"**

---

## 📊 Ce Se Salvează

Aplicația salvează automat:

| Coloană | Descriere | Exemplu |
|---------|-----------|---------|
| **PUNCTAJ** | Punctele adăugate | 5, 10 |
| **ACTIUNE** | Tipul acțiunii | Patrula de oras |
| **ZONA** | Zona (doar pentru razie) | Centru |
| **NR_ACTIUNI** | Numărul total de acțiuni în care a participat | 1, 2, 3... |

---

## 🔍 Coloane Noi în Aplicație

La deschiderea instituției, vei vedea noi coloane:

- **ACTIUNE** (150px) - Tipul ultimei acțiuni
- **ZONA** (100px) - Zona (dacă razie)
- **NR_ACTIUNI** (80px) - Contor de acțiuni

---

## 💡 Exemple de Utilizare

### Exemplu 1: Patrula de Oras
```
1. Punctaj: 3
2. Acțiune: Patrula de oras
3. Zona: (goală - nu e necesară)
4. Selectează: Ion, Maria, Andrei
5. Confirma
```
**Rezultat**: Fiecare dintre ei va primi 3 puncte, NR_ACTIUNI se incrementează cu 1

### Exemplu 2: Razie
```
1. Punctaj: 8
2. Acțiune: Razie
3. Zona: Parc Industrial
4. Selectează: Cosmin, George, Vasile
5. Confirma
```
**Rezultat**: Fiecare dintre ei va primi 8 puncte, NR_ACTIUNI se incrementează cu 1, zona "Parc Industrial" se salvează

---

## ⚠️ Validări

Aplicația va afișa erori dacă:
- ❌ Nu introduci o valoare de punctaj validă
- ❌ Nu selectezi nicio acțiune (pentru instituții de poliție)
- ❌ Selectezi "Razie" dar nu introduci zona
- ❌ Nu selectezi niciun angajat

---

## 📝 Note Importante

- **NR_ACTIUNI** crește DOAR când se adaugă punctaj (nu se scade la ștergere)
- **ZONA** este salvată în baza de date și va fi vizibilă în rapoarte
- Datele se sincronizează automat cu cloud (Supabase)
- Modificările sunt loggate în sistemul de audit

---

## 🆘 Troubleshooting

**Problema**: Zona nu apare
- ✓ Asigură-te că ai selectat "Razie" din dropdown

**Problema**: NR_ACTIUNI nu se incrementează
- ✓ Acesta se incrementează doar când ADAUGI punctaj, nu când ștergi

**Problema**: Acțiunile nu se salvează
- ✓ Verifică că apasă "✓ CONFIRMĂ ȘI APLICĂ" complet

---

**Versiunea**: 1.0
**Data**: Martie 1, 2026
**Status**: ✅ Activ
