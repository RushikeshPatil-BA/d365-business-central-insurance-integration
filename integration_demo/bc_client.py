"""Business Central API v2.0 client - real and mock implementations.

Both classes expose the same small interface, so the integration jobs
(claims_to_gl, premiums_to_ar) run unchanged against either:

    exists(entity, external_document_number) -> bool
    create_journal_line(journal_code, line) -> dict
    create_sales_document(entity, header, lines) -> dict   # salesInvoices | salesCreditMemos
    customer_exists(number) -> bool

`BusinessCentralClient` talks to a real BC SaaS environment using OAuth 2.0
client credentials (Microsoft Entra ID). `MockBusinessCentral` keeps records
in memory so the demo and tests run with no tenant or credentials.
"""
from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass, field
from typing import Callable

import config


class BCApiError(Exception):
    """Non-retryable error returned by Business Central (4xx)."""

    def __init__(self, status: int, message: str):
        super().__init__(f"HTTP {status}: {message}")
        self.status = status


def with_retry(send: Callable[[], tuple[int, dict]], sleep: Callable[[float], None] = time.sleep) -> dict:
    """Call `send` and retry on throttling / server errors with exponential backoff (NFR-05).

    `send` returns (status_code, json_body). Backoff: 1s, 2s, 4s, 8s ...
    """
    for attempt in range(1, config.MAX_ATTEMPTS + 1):
        status, body = send()
        if status < 400:
            return body
        if status in config.RETRY_STATUS_CODES and attempt < config.MAX_ATTEMPTS:
            sleep(2 ** (attempt - 1))
            continue
        message = body.get("error", {}).get("message", "") if isinstance(body, dict) else str(body)
        raise BCApiError(status, message)
    raise AssertionError("unreachable")


# --------------------------------------------------------------------------- real client
class BusinessCentralClient:
    """Minimal client for the BC standard API v2.0.

    Configure with environment variables:
        BC_TENANT_ID, BC_ENVIRONMENT, BC_COMPANY_ID, BC_CLIENT_ID, BC_CLIENT_SECRET
    """

    TOKEN_URL = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
    SCOPE = "https://api.businesscentral.dynamics.com/.default"

    def __init__(self) -> None:
        import requests  # imported here so the mock needs no third-party packages

        self._requests = requests
        self.tenant = os.environ["BC_TENANT_ID"]
        env = os.environ.get("BC_ENVIRONMENT", "production")
        company = os.environ["BC_COMPANY_ID"]
        self.base = (
            f"https://api.businesscentral.dynamics.com/v2.0/{self.tenant}/{env}"
            f"/api/v2.0/companies({company})"
        )
        self._token: str | None = None
        self._journal_ids: dict[str, str] = {}

    # -- auth
    def _get_token(self) -> str:
        if self._token is None:
            r = self._requests.post(
                self.TOKEN_URL.format(tenant=self.tenant),
                data={
                    "grant_type": "client_credentials",
                    "client_id": os.environ["BC_CLIENT_ID"],
                    "client_secret": os.environ["BC_CLIENT_SECRET"],
                    "scope": self.SCOPE,
                },
                timeout=30,
            )
            r.raise_for_status()
            self._token = r.json()["access_token"]
        return self._token

    def _call(self, method: str, path: str, **kwargs) -> dict:
        def send() -> tuple[int, dict]:
            r = self._requests.request(
                method,
                f"{self.base}/{path}",
                headers={"Authorization": f"Bearer {self._get_token()}"},
                timeout=60,
                **kwargs,
            )
            body = r.json() if r.content else {}
            return r.status_code, body

        return with_retry(send)

    # -- helpers
    def _journal_id(self, code: str) -> str:
        if code not in self._journal_ids:
            res = self._call("GET", f"journals?$filter=code eq '{code}'")
            self._journal_ids[code] = res["value"][0]["id"]
        return self._journal_ids[code]

    # -- interface
    def exists(self, entity: str, external_document_number: str) -> bool:
        flt = f"externalDocumentNumber eq '{external_document_number}'"
        if entity == "journalLines":
            path = f"journals({self._journal_id(config.CLAIMS_JOURNAL_CODE)})/journalLines?$filter={flt}"
        else:
            path = f"{entity}?$filter={flt}"
        return bool(self._call("GET", path)["value"])

    def customer_exists(self, number: str) -> bool:
        return bool(self._call("GET", f"customers?$filter=number eq '{number}'")["value"])

    def create_journal_line(self, journal_code: str, line: dict) -> dict:
        dims = line.pop("dimensions", {})
        created = self._call("POST", f"journals({self._journal_id(journal_code)})/journalLines", json=line)
        for code, value in dims.items():
            self._call(
                "POST",
                f"journals({self._journal_id(journal_code)})/journalLines({created['id']})/dimensionSetLines",
                json={"code": code, "valueCode": value},
            )
        return created

    def create_sales_document(self, entity: str, header: dict, lines: list[dict]) -> dict:
        line_entity = {"salesInvoices": "salesInvoiceLines", "salesCreditMemos": "salesCreditMemoLines"}[entity]
        doc = self._call("POST", entity, json=header)
        for line in lines:
            dims = line.pop("dimensions", {})
            created = self._call("POST", f"{entity}({doc['id']})/{line_entity}", json=line)
            for code, value in dims.items():
                self._call(
                    "POST",
                    f"{entity}({doc['id']})/{line_entity}({created['id']})/dimensionSetLines",
                    json={"code": code, "valueCode": value},
                )
        self._call("POST", f"{entity}({doc['id']})/Microsoft.NAV.post")
        return doc


# --------------------------------------------------------------------------- mock
@dataclass
class MockBusinessCentral:
    """In-memory stand-in for Business Central, used by the demo and tests."""

    customers: set[str] = field(default_factory=set)
    journal_lines: list[dict] = field(default_factory=list)
    sales_invoices: list[dict] = field(default_factory=list)
    sales_credit_memos: list[dict] = field(default_factory=list)

    def _store(self, entity: str) -> list[dict]:
        return {"journalLines": self.journal_lines, "salesInvoices": self.sales_invoices,
                "salesCreditMemos": self.sales_credit_memos}[entity]

    def exists(self, entity: str, external_document_number: str) -> bool:
        return any(r["externalDocumentNumber"] == external_document_number for r in self._store(entity))

    def customer_exists(self, number: str) -> bool:
        return number in self.customers

    def create_journal_line(self, journal_code: str, line: dict) -> dict:
        record = {"id": str(uuid.uuid4()), "journalCode": journal_code,
                  "lineNumber": 10_000 * (len(self.journal_lines) + 1), **line}
        self.journal_lines.append(record)
        return record

    def create_sales_document(self, entity: str, header: dict, lines: list[dict]) -> dict:
        store = self._store(entity)
        prefix = "PSI" if entity == "salesInvoices" else "PSCM"
        record = {
            "id": str(uuid.uuid4()),
            "number": f"{prefix}{len(store) + 100001}",
            "status": "Open",
            **header,
            "lines": lines,
            "totalAmountIncludingTax": round(sum(l["unitPrice"] * l["quantity"] for l in lines), 2),
        }
        store.append(record)
        return record
