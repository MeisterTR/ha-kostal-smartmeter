from __future__ import annotations


def bearer_header(access_token: str) -> dict:
    """Erzeugt Header für Bearer-Token-Authentifizierung"""
    return {"Authorization": f"Bearer {access_token}"}


def first_evse_from_coordinator(coord) -> dict | None:
    """Gib die erste (bevorzugt verfügbare) Wallbox aus coord.data zurück."""
    if not coord or not getattr(coord, "data", None):
        return None
    evses = coord.data.get("evse") or []
    if not evses:
        return None
    for wb in evses:
        if wb.get("available"):
            return wb
    return evses[0]  # Fallback: erste, auch wenn offline
