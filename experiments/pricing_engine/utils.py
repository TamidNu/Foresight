import hashlib
import json
import os
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from typing import Any, Dict, Iterable, List, Tuple

from dotenv import load_dotenv


def load_env(env_path: str | None = None) -> None:
    """
    Load environment variables from a .env file if present.
    Defaults to experiments/.env when run from repo root context.
    """
    if env_path and os.path.exists(env_path):
        load_dotenv(env_path)
        return
    # Try experiments/.env relative to this file
    here = os.path.dirname(os.path.abspath(__file__))
    exp_root = os.path.abspath(os.path.join(here, ".."))
    default_env = os.path.join(exp_root, ".env")
    if os.path.exists(default_env):
        load_dotenv(default_env)
    else:
        load_dotenv()  # fallback to current working dir


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def daterange(start: date, end: date) -> Iterable[date]:
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def to_iso(d: date | datetime) -> str:
    if isinstance(d, datetime):
        return d.date().isoformat()
    return d.isoformat()


def sha1_of_obj(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha1(payload).hexdigest()


def cache_path(base_dir: str, key: Dict[str, Any]) -> str:
    ensure_dir(base_dir)
    return os.path.join(base_dir, f"{sha1_of_obj(key)}.json")


def read_json(path: str) -> Dict[str, Any] | None:
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str, data: Dict[str, Any]) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


