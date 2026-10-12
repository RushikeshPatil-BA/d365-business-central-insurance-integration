"""INT-03 · Bank statement auto-matching against Business Central ledger entries.

Matching rules (FR-BR-02):
  Rule 1 - same amount AND the BC reference appears in the bank narrative
  Rule 2 - same amount AND posting date within +/- DATE_WINDOW_DAYS, with exactly one candidate
Anything else goes to the exceptions queue with a reason (FR-BR-03).

Each BC entry can be matched at most once.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import config


@dataclass
class ReconResult:
    matches: list[dict] = field(default_factory=list)
    exceptions: list[dict] = field(default_factory=list)
    unmatched_bc: list[dict] = field(default_factory=list)

    @property
    def match_rate(self) -> float:
        total = len(self.matches) + len(self.exceptions)
        return len(self.matches) / total if total else 0.0

    def summary(self) -> str:
        by_rule = {r: sum(1 for m in self.matches if m["rule"] == r) for r in (1, 2)}
        return (
            f"{len(self.matches)} matched ({self.match_rate:.0%}; rule 1: {by_rule[1]}, rule 2: {by_rule[2]}), "
            f"{len(self.exceptions)} exceptions, {len(self.unmatched_bc)} BC entries not yet on statement"
        )


def _base_ref(reference: str) -> str:
    """'CLM-20431/1' -> 'CLM-20431'; 'POL-1001-T55' stays as is."""
    return reference.split("/")[0].strip().upper()


def reconcile(statement: list[dict], bc_entries: list[dict]) -> ReconResult:
    """statement rows: {line_id, date, amount, narrative}
    bc_entries:     {entry_id, posting_date, amount, reference}
    Amounts are signed from the bank's point of view (payments out negative).
    """
    result = ReconResult()
    open_entries = list(bc_entries)

    for line in statement:
        amount = round(float(line["amount"]), 2)
        narrative = line["narrative"].upper()
        same_amount = [e for e in open_entries if round(float(e["amount"]), 2) == amount]

        # Rule 1: amount + reference
        by_ref = [e for e in same_amount if _base_ref(e["reference"]) in narrative]
        if by_ref:
            entry = by_ref[0]
            open_entries.remove(entry)
            result.matches.append({"line_id": line["line_id"], "entry_id": entry["entry_id"], "rule": 1})
            continue

        # Rule 2: amount + date window, single candidate only
        line_date = date.fromisoformat(line["date"])
        in_window = [
            e for e in same_amount
            if abs((date.fromisoformat(e["posting_date"]) - line_date).days) <= config.DATE_WINDOW_DAYS
        ]
        if len(in_window) == 1:
            entry = in_window[0]
            open_entries.remove(entry)
            result.matches.append({"line_id": line["line_id"], "entry_id": entry["entry_id"], "rule": 2})
            continue

        reason = "Multiple candidates" if len(in_window) > 1 else "No matching BC entry"
        result.exceptions.append({**line, "reason": reason})

    result.unmatched_bc = open_entries
    return result
