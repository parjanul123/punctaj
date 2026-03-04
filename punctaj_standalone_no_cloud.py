"""
Launcher variantă standalone (fără baza de date cloud / Supabase).

Utilizare:
    python punctaj_standalone_no_cloud.py
"""

import os

os.environ["PUNCTAJ_NO_CLOUD_DB"] = "1"
os.environ["PUNCTAJ_FORCE_ALL_SUPERUSERS"] = "1"

import punctaj  # noqa: F401
