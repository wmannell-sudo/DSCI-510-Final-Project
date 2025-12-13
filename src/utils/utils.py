import requests
import pandas as pd

def safe_get_json(url, params=None, timeout=20):
    try:
        r = requests.get(url, params=params, timeout=timeout)
        status = r.status_code
        text_head = (r.text or "")[:200]
        try:
            return r.json(), status, text_head
        except Exception:
            return None, status, text_head
    except Exception as e:
        return None, None, str(e)[:200]


def ensure_float_series(s):
    return pd.to_numeric(s, errors="coerce")
