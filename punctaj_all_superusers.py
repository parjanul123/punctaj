"""
Launcher variantă: toți utilizatorii autentificați sunt tratați ca SUPERUSER.

Utilizare:
    python punctaj_all_superusers.py
"""

import os

os.environ["PUNCTAJ_FORCE_ALL_SUPERUSERS"] = "1"

import punctaj  # noqa: F401
