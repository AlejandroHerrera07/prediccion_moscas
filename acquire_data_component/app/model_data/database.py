from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "").strip()


class SupabaseExecuteResult:
    def __init__(self, data: list[dict[str, Any]]):
        self.data = data


class SupabaseTableQuery:
    def __init__(self, client: "SupabaseRestClient", table_name: str):
        self._client = client
        self._table_name = table_name
        self._columns = "*"

    def select(self, columns: str = "*") -> "SupabaseTableQuery":
        self._columns = columns or "*"
        return self

    def execute(self) -> SupabaseExecuteResult:
        data = self._client._select(self._table_name, self._columns)
        return SupabaseExecuteResult(data)


class SupabaseRestClient:
    def __init__(self, supabase_url: str, supabase_key: str):
        if not supabase_url:
            raise RuntimeError("Falta SUPABASE_URL en .env.")
        if not supabase_key:
            raise RuntimeError("Falta SUPABASE_ANON_KEY en .env.")
        self._supabase_url = supabase_url.rstrip("/")
        self._supabase_key = supabase_key

    def table(self, table_name: str) -> SupabaseTableQuery:
        return SupabaseTableQuery(self, table_name)

    def _select(self, table_name: str, columns: str) -> list[dict[str, Any]]:
        endpoint = urljoin(f"{self._supabase_url}/", f"rest/v1/{table_name}")
        query_string = urlencode({"select": columns})
        url = f"{endpoint}?{query_string}"
        request = Request(
            url,
            headers={
                "apikey": self._supabase_key,
                "Authorization": f"Bearer {self._supabase_key}",
                "Accept": "application/json",
            },
        )

        try:
            with urlopen(request) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Error consultando Supabase en '{table_name}': HTTP {exc.code} {exc.reason}. {body}"
            ) from exc

        parsed = json.loads(raw) if raw else []
        if not isinstance(parsed, list):
            raise RuntimeError(f"Respuesta inesperada de Supabase para '{table_name}'.")
        return parsed


def get_supabase_client() -> SupabaseRestClient:
    return SupabaseRestClient(SUPABASE_URL, SUPABASE_ANON_KEY)
