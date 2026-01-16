# auth.py – Simple password‑based authentication for Streamlit UI

import os
import hashlib
from typing import Optional
from dotenv import load_dotenv


# Load .env file (should contain ADMIN_PASSWORD_HASH and MEMBER_PASSWORD_HASH)
load_dotenv()

ADMIN_HASH = os.getenv("ADMIN_PASSWORD_HASH")
MEMBER_HASH = os.getenv("MEMBER_PASSWORD_HASH")

def _hash_password(pw: str) -> str:
    """Return a SHA‑256 hex digest of the password."""
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def check_credentials(username: str, password: str) -> Optional[str]:
    """Validate username/password.
    Returns the role string ("admin" or "member") if valid, otherwise ``None``.
    ``username`` is ignored for now – we only distinguish by password.
    """
    pw_hash = _hash_password(password)
    if ADMIN_HASH and pw_hash == ADMIN_HASH:
        return "admin"
    if MEMBER_HASH and pw_hash == MEMBER_HASH:
        return "member"
    return None

def get_user_role() -> Optional[str]:
    """Convenience wrapper – in Streamlit we store role in session state, so this is a stub.
    It can be expanded later to read from a DB or OAuth provider.
    """
    # Not used directly in the UI; kept for future extension.
    return None
