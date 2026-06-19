from __future__ import annotations

import os
from dataclasses import dataclass

import streamlit as st

from database import ensure_staff


@dataclass
class UserContext:
    email: str
    name: str
    role: str
    authenticated: bool
    clinical_mode: bool


ROLE_PERMISSIONS = {
    "admin": {"read", "write", "sign", "admin", "archive"},
    "consultant": {"read", "write", "sign", "archive"},
    "resident": {"read", "write"},
    "nurse": {"read", "vitals", "ward", "files"},
    "viewer": {"read"},
}


def _secret(name: str, default=None):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return os.getenv(name, default)


def auth_configured() -> bool:
    try:
        return "auth" in st.secrets
    except Exception:
        return False


def get_user_context() -> UserContext:
    mode = str(_secret("APP_MODE", "demo")).lower()
    clinical_mode = mode == "clinical"

    if clinical_mode and auth_configured():
        if not st.user.is_logged_in:
            st.markdown("## 🔐 النظام خاص بالقسم الجراحي")
            st.write("يلزم تسجيل الدخول قبل الوصول إلى بيانات المرضى.")
            st.button("تسجيل الدخول / Log in", on_click=st.login, type="primary")
            st.stop()
        email = str(getattr(st.user, "email", "") or st.user.get("email", "")).strip().lower()
        name = str(getattr(st.user, "name", "") or st.user.get("name", email)).strip()
        staff = ensure_staff(email=email, display_name=name, default_role="viewer")
        if not staff.active:
            st.error("هذا الحساب غير مفعل. راجع مسؤول النظام.")
            st.stop()
        return UserContext(email=email, name=name, role=staff.role, authenticated=True, clinical_mode=True)

    # Demo mode intentionally avoids claiming production security.
    email = "demo.user@surgiscore.local"
    name = "Demo User"
    staff = ensure_staff(email=email, display_name=name, default_role="admin")
    return UserContext(email=email, name=name, role=staff.role, authenticated=False, clinical_mode=False)


def can(user: UserContext, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(user.role, {"read"})


def require(user: UserContext, permission: str) -> None:
    if not can(user, permission):
        st.error("ليست لديك صلاحية تنفيذ هذا الإجراء.")
        st.stop()


def render_user_sidebar(user: UserContext) -> None:
    st.sidebar.markdown(f"**{user.name}**")
    st.sidebar.caption(f"{user.email} · {user.role}")
    if user.clinical_mode and user.authenticated:
        st.sidebar.button("Log out", on_click=st.logout)
    else:
        st.sidebar.warning("Demo mode — لا تُدخل معلومات مرضى حقيقية")
