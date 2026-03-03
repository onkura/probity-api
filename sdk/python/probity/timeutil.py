import datetime


def utc_now_rfc3339() -> str:
    # RFC3339-like Zulu time without fractional seconds for determinism
    return datetime.datetime.utcnow().replace(microsecond=0, tzinfo=datetime.timezone.utc).isoformat().replace("+00:00", "Z")