from datetime import timezone

def to_utc_iso(dt):
    if dt is None:
        return None
    # ensure it's timezone-aware, then force UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")