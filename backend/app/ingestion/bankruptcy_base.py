from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass
class BankruptcyCaseRecord:
    external_case_id: str
    debtor_name: str
    chapter: str
    court_name: str
    filed_date: date
    source_url: str
    source_metadata: dict[str, Any]


@dataclass
class BankruptcyDocketRecord:
    external_docket_id: str
    external_case_id: str
    entry_date: date
    title: str
    content: str
    source_url: str
    source_metadata: dict[str, Any]


@dataclass
class BankruptcyIngestionStats:
    fetched_cases: int = 0
    fetched_dockets: int = 0
    parsed_cases: int = 0
    parsed_dockets: int = 0
    upserted_cases: int = 0
    upserted_dockets: int = 0
    parse_failures: int = 0
    partial_failures: int = 0
