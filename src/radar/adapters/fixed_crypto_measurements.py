"""Fixed, bounded HTML measurements for remaining Crypto matrix cells.

These adapters parse one specialist table and one official Taiwan law record. They
store only the latest typed facts plus a short summary; no full page is persisted.
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from html.parser import HTMLParser

from radar.adapters.transport import HttpRequest, HttpTransport
from radar.domain.models import Document
from radar.schemas.measurement import MeasurementSource


class _TableAndTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[str]] = []
        self.text_parts: list[str] = []
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        if tag == "tr":
            self._row = []
        elif tag in {"td", "th"} and self._row is not None:
            self._cell = []

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self._row is not None and self._cell is not None:
            self._row.append(_normalize_text(" ".join(self._cell)))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            if any(self._row):
                self.rows.append(self._row)
            self._row = None
            self._cell = None

    def handle_data(self, data: str) -> None:
        value = data.strip()
        if not value:
            return
        self.text_parts.append(value)
        if self._cell is not None:
            self._cell.append(value)


def fetch_farside_etf_document(
    source: MeasurementSource,
    transport: HttpTransport,
    timeout_seconds: int,
) -> Document:
    body = _fetch_html(source.canonical_url, transport, timeout_seconds)
    observation_date, flow_usd_m = _parse_farside_latest(body)
    fetched_at = datetime.now(timezone.utc).isoformat()
    direction = "inflow" if flow_usd_m > 0 else "outflow" if flow_usd_m < 0 else "flat flow"
    signed = f"{flow_usd_m:+,.1f}"
    return Document.fixture(
        source_id=source.source_id,
        url=source.canonical_url,
        title=f"Farside US spot Bitcoin ETF latest net {direction} measurement",
        language=source.language,
        macro_region=source.macro_region,
        published_at=datetime(
            observation_date.year,
            observation_date.month,
            observation_date.day,
            tzinfo=timezone.utc,
        ).isoformat(),
        fetched_at=fetched_at,
        entities=["Farside Investors", "US spot Bitcoin ETF"],
        action="measures",
        object="bitcoin etf flow",
        location="United States",
        primary_domain=source.primary_domain,
        lane="indicator_only",
        facts={
            "source_roles": list(source.source_roles),
            "flow_usd_m_latest": flow_usd_m,
            "count_flow_observation_ordinal": float(observation_date.toordinal()),
        },
        summary=(
            f"Farside specialist Bitcoin ETF table latest observation "
            f"{observation_date.date().isoformat()}: aggregate daily flow US${signed}m."
        ),
    )


def fetch_fsc_vasp_document(
    source: MeasurementSource,
    transport: HttpTransport,
    timeout_seconds: int,
) -> Document:
    body = _fetch_html(source.canonical_url, transport, timeout_seconds)
    parser = _TableAndTextParser()
    parser.feed(body.decode("utf-8", errors="replace"))
    visible = _normalize_text(" ".join(parser.text_parts))
    for phrase in ("虛擬資產服務法", "金融監督管理委員會"):
        if phrase not in visible:
            raise ValueError(f"FSC VASP law page missing required phrase: {phrase}")

    published = _roc_date(visible)
    serial_match = re.search(r"華總一經字第\d+號", visible)
    serial = serial_match.group(0) if serial_match else "serial-unavailable"
    pending = "尚未施行" in visible
    status_code = 0.0 if pending else 1.0
    status_zh = "全部或部分尚未施行" if pending else "已發布，頁面未標示尚未施行"
    revision_fingerprint = int(
        hashlib.sha256(
            f"虛擬資產服務法|{published.date().isoformat()}|{serial}|{status_code}".encode("utf-8")
        ).hexdigest()[:12],
        16,
    )
    fetched_at = datetime.now(timezone.utc).isoformat()

    return Document.fixture(
        source_id=source.source_id,
        url=source.canonical_url,
        title="金管會 台灣 VASP 虛擬資產服務法 regulation policy snapshot",
        language=source.language,
        macro_region=source.macro_region,
        published_at=published.isoformat(),
        fetched_at=fetched_at,
        entities=["金融監督管理委員會", "台灣 VASP"],
        action="publishes",
        object="Taiwan VASP virtual asset regulation policy",
        location="Taiwan",
        primary_domain=source.primary_domain,
        lane="indicator_only",
        facts={
            "source_roles": list(source.source_roles),
            "count_policy_publication_yyyymmdd": float(int(published.strftime("%Y%m%d"))),
            "count_policy_effective_status_code": status_code,
            "count_policy_revision_fingerprint": revision_fingerprint,
        },
        summary=(
            f"金管會主管法規頁確認《虛擬資產服務法》於 "
            f"{published.date().isoformat()} 公布，狀態為「{status_zh}」；發文字號 {serial}。"
        ),
    )


def _fetch_html(url: str, transport: HttpTransport, timeout_seconds: int) -> bytes:
    response = transport.fetch(
        HttpRequest(
            url=url,
            headers={"Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.1"},
            timeout_seconds=timeout_seconds,
        )
    )
    if not 200 <= response.status < 300:
        raise ValueError(f"measurement HTTP {response.status}: {url}")
    if not response.body:
        raise ValueError(f"empty measurement page: {url}")
    return response.body


def _parse_farside_latest(body: bytes) -> tuple[datetime, float]:
    parser = _TableAndTextParser()
    parser.feed(body.decode("utf-8", errors="replace"))
    observations: list[tuple[datetime, float]] = []
    for row in parser.rows:
        if len(row) < 2:
            continue
        try:
            observed = datetime.strptime(row[0], "%d %b %Y").replace(tzinfo=timezone.utc)
            total = _parse_flow_value(row[-1])
        except ValueError:
            continue
        observations.append((observed, total))
    if not observations:
        raise ValueError("Farside Bitcoin ETF table contains no dated flow rows")
    return max(observations, key=lambda row: row[0])


def _parse_flow_value(value: str) -> float:
    normalized = value.replace("\u00a0", " ").replace(",", "").strip()
    if normalized in {"", "-", "—"}:
        return 0.0
    negative = normalized.startswith("(") and normalized.endswith(")")
    if negative:
        normalized = normalized[1:-1].strip()
    number = float(normalized)
    return -number if negative else number


def _roc_date(text: str) -> datetime:
    match = re.search(r"民國\s*(\d{2,3})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日", text)
    if match is None:
        raise ValueError("FSC VASP law page has no ROC publication date")
    year, month, day = (int(value) for value in match.groups())
    return datetime(year + 1911, month, day, tzinfo=timezone.utc)


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()
