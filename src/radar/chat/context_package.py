"""Chat-assisted context package + import validation.

`build_chat_package` produces a deterministic, content-addressed, byte-stable set
of files for a human to hand to ChatGPT. It never contains secrets, full articles,
duplicate content or model-invented conclusions. `validate_chat_import` verifies a
human-produced report against that context.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

from radar.contracts.report import RadarReportV2, radar_report_json_schema
from radar.contracts.runtime import RuntimeContract
from radar.domain.models import Event
from radar.reporting.contracts import validate_report_contract

PACKAGE_VERSION = "chat/v1"
_MAX_EXCERPT_CHARS = 280


def _canonical(payload: object) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


@dataclass(frozen=True)
class ChatContext:
    date: str
    profile: str
    run_id: str
    context_hash: str
    allowed_event_ids: frozenset[str]
    allowed_document_ids: frozenset[str]
    allowed_source_ids: frozenset[str]
    allowed_urls: frozenset[str]
    allowed_numeric_facts: frozenset[str]
    domains: frozenset[str]
    retail_keys: frozenset[str]
    crypto_keys: frozenset[str]
    indicator_ids: frozenset[str]
    taiwan_sources: frozenset[str]


@dataclass(frozen=True)
class ChatPackage:
    files: dict[str, bytes]
    context: ChatContext

    @property
    def relative_dir(self) -> str:
        return f"artifacts/chat/v1/{self.context.date}/{self.context.context_hash}"


def build_chat_package(report: RadarReportV2, events: list[Event], contract: RuntimeContract) -> ChatPackage:
    event_ids: set[str] = set()
    document_ids: set[str] = set()
    source_ids: set[str] = set()
    urls: set[str] = set()
    numeric_facts: set[str] = set()
    taiwan_sources: set[str] = set()

    events_payload = []
    evidence_payload = []
    prior_state_payload = []
    for event in sorted(events, key=lambda event: event.event_id):
        event_ids.add(event.event_id)
        prior_state_payload.append(
            {"event_id": event.event_id, "delta_types": sorted({delta.delta_type for delta in event.deltas})}
        )
        event_docs = []
        for document in event.documents:
            document_ids.add(document.document_id)
            source_ids.add(document.source_id)
            urls.add(document.url)
            for metric in document.facts:
                if metric != "source_roles":
                    numeric_facts.add(metric)
            if document.macro_region == "Taiwan":
                taiwan_sources.add(document.source_id)
            event_docs.append(
                {
                    "document_id": document.document_id,
                    "source_id": document.source_id,
                    "url": document.url,
                    "title": document.title,
                    "language": document.language,
                    "excerpt": (document.summary or document.title)[:_MAX_EXCERPT_CHARS],
                    "metrics": sorted(m for m in document.facts if m != "source_roles"),
                }
            )
            evidence_payload.append(
                {"document_id": document.document_id, "source_id": document.source_id, "url": document.url}
            )
        events_payload.append({"event_id": event.event_id, "documents": event_docs})

    context_json = {
        "package_version": PACKAGE_VERSION,
        "date": report.date,
        "profile": report.profile,
        "run_id": report.run_id,
        "output_language": "zh-Hant-TW",
        "domains": sorted(contract.report_domains),
        "retail_matrix_keys": sorted(contract.retail_matrix_keys),
        "crypto_matrix_keys": sorted(contract.crypto_matrix_keys),
        "structural_indicator_ids": sorted(contract.structural_indicator_ids),
        "taiwan_direct_sources": sorted(taiwan_sources),
    }
    deterministic_eval = json.loads(report.canonical_json_bytes().decode("utf-8"))
    report_schema = radar_report_json_schema()

    content_files: dict[str, bytes] = {
        "context.json": _canonical(context_json),
        "events.json": _canonical(events_payload),
        "evidence.json": _canonical(evidence_payload),
        "prior-state.json": _canonical(prior_state_payload),
        "deterministic-evaluation.json": _canonical(deterministic_eval),
        "runtime-contract.json": _canonical(
            {
                "report_domains": contract.report_domains,
                "retail_matrix_keys": contract.retail_matrix_keys,
                "crypto_matrix_keys": contract.crypto_matrix_keys,
                "structural_indicator_ids": contract.structural_indicator_ids,
            }
        ),
        "report-schema.json": _canonical(report_schema),
        "expected-output.schema.json": _canonical(report_schema),
        "INSTRUCTIONS.md": _INSTRUCTIONS.encode("utf-8"),
    }
    context_hash = hashlib.sha256(
        b"".join(content_files[name] for name in sorted(content_files))
    ).hexdigest()[:16]

    manifest = {
        "package_version": PACKAGE_VERSION,
        "date": report.date,
        "profile": report.profile,
        "run_id": report.run_id,
        "context_hash": context_hash,
        "files": sorted(content_files),
    }
    files = dict(content_files)
    files["manifest.json"] = _canonical(manifest)

    context = ChatContext(
        date=report.date,
        profile=report.profile,
        run_id=report.run_id,
        context_hash=context_hash,
        allowed_event_ids=frozenset(event_ids),
        allowed_document_ids=frozenset(document_ids),
        allowed_source_ids=frozenset(source_ids),
        allowed_urls=frozenset(urls),
        allowed_numeric_facts=frozenset(numeric_facts),
        domains=frozenset(contract.report_domains),
        retail_keys=frozenset(contract.retail_matrix_keys),
        crypto_keys=frozenset(contract.crypto_matrix_keys),
        indicator_ids=frozenset(contract.structural_indicator_ids),
        taiwan_sources=frozenset(taiwan_sources),
    )
    return ChatPackage(files=files, context=context)


def load_chat_context(files: dict[str, bytes]) -> ChatContext:
    """Reconstruct the allowed-fact context from a written package (for import)."""

    manifest = json.loads(files["manifest.json"].decode("utf-8"))
    context_meta = json.loads(files["context.json"].decode("utf-8"))
    events = json.loads(files["events.json"].decode("utf-8"))

    event_ids: set[str] = set()
    document_ids: set[str] = set()
    source_ids: set[str] = set()
    urls: set[str] = set()
    numeric_facts: set[str] = set()
    for event in events:
        event_ids.add(event["event_id"])
        for document in event["documents"]:
            document_ids.add(document["document_id"])
            source_ids.add(document["source_id"])
            urls.add(document["url"])
            numeric_facts.update(document.get("metrics", []))

    return ChatContext(
        date=manifest["date"],
        profile=manifest["profile"],
        run_id=manifest["run_id"],
        context_hash=manifest["context_hash"],
        allowed_event_ids=frozenset(event_ids),
        allowed_document_ids=frozenset(document_ids),
        allowed_source_ids=frozenset(source_ids),
        allowed_urls=frozenset(urls),
        allowed_numeric_facts=frozenset(numeric_facts),
        domains=frozenset(context_meta["domains"]),
        retail_keys=frozenset(context_meta["retail_matrix_keys"]),
        crypto_keys=frozenset(context_meta["crypto_matrix_keys"]),
        indicator_ids=frozenset(context_meta["structural_indicator_ids"]),
        taiwan_sources=frozenset(context_meta["taiwan_direct_sources"]),
    )


@dataclass(frozen=True)
class ChatImportReceipt:
    valid: bool
    reasons: tuple[str, ...] = ()
    effective_mode: str = "chat-assisted"
    evaluator: str = "human_initiated_chat"

    def as_dict(self) -> dict[str, object]:
        return {
            "valid": self.valid,
            "reasons": list(self.reasons),
            "effective_mode": self.effective_mode if self.valid else "unchanged",
            "evaluator": self.evaluator if self.valid else "none",
        }


def validate_chat_import(
    submitted: dict[str, object],
    context: ChatContext,
    contract: RuntimeContract,
    *,
    claimed_context_hash: str,
    claimed_package_version: str = PACKAGE_VERSION,
) -> ChatImportReceipt:
    reasons: list[str] = []

    if claimed_package_version != PACKAGE_VERSION:
        reasons.append(f"package_version_mismatch:{claimed_package_version}")
    if claimed_context_hash != context.context_hash:
        reasons.append("context_hash_mismatch")

    try:
        validate_report_contract(submitted, contract=contract)
    except Exception as exc:  # noqa: BLE001 - convert to a validation reason
        reasons.append(f"report_contract_invalid:{exc}")
        return ChatImportReceipt(valid=False, reasons=tuple(reasons))

    if submitted.get("date") != context.date:
        reasons.append("date_mismatch")
    if submitted.get("profile") != context.profile:
        reasons.append("profile_mismatch")
    if submitted.get("run_id") != context.run_id:
        reasons.append("run_id_mismatch")

    items = submitted.get("items", [])
    if not isinstance(items, list):
        return ChatImportReceipt(valid=False, reasons=tuple([*reasons, "items_not_a_list"]))

    for item in items:
        if item.get("event_id") not in context.allowed_event_ids:
            reasons.append(f"unknown_event_id:{item.get('event_id')}")
        for link in item.get("evidence_links", []) + item.get("direct_taiwan_evidence", []):
            if link.get("url") not in context.allowed_urls:
                reasons.append(f"invented_url:{link.get('url')}")
            if link.get("source_id") not in context.allowed_source_ids:
                reasons.append(f"invented_source_id:{link.get('source_id')}")
        for link in item.get("direct_taiwan_evidence", []):
            if link.get("source_id") not in context.taiwan_sources:
                reasons.append(f"non_taiwan_direct_evidence:{link.get('source_id')}")

    if set(submitted.get("retail_matrix", {})) != context.retail_keys:
        reasons.append("retail_matrix_keys_mismatch")
    if set(submitted.get("crypto_matrix", {})) != context.crypto_keys:
        reasons.append("crypto_matrix_keys_mismatch")
    indicator_ids = {row.get("indicator_id") for row in submitted.get("structural_indicators", [])}
    if indicator_ids != context.indicator_ids:
        reasons.append("indicator_ids_mismatch")

    major = {item["event_id"] for item in items if item.get("report_lane") == "major"}
    potential = {item["event_id"] for item in items if item.get("report_lane") == "potential"}
    if major & potential:
        reasons.append(f"major_potential_overlap:{sorted(major & potential)}")

    return ChatImportReceipt(valid=not reasons, reasons=tuple(reasons))


_INSTRUCTIONS = """# Chat-assisted evaluation instructions

你是情報雷達的語意與翻譯助手，不是事實判官。只能使用此封包中的 bounded context：

- 不得捏造 URL、event id、document id、source id 或數值事實。
- 所有自然語言輸出使用台灣繁體中文（zh-Hant-TW），公司名、產品名、數字與日期不得改寫。
- headline 若由外文翻成中文，必須在 uncertainties 加入 `原文標題：<原始標題>`，原文不得遺失。
- 保留每一個 evidence link；台灣直接證據只能使用封包列出的台灣來源。
- 必須完全遵守 expected-output.schema.json 與 runtime contract。
- Major 與 Potential 不得放入同一 event。
- 潛力候選不得因太小、證據弱或非主流而從資料層刪除；首頁精選是 projection，不是資料刪除。
- 回傳單一 RadarReportV2 JSON，沿用原本的 run_id、date 與 profile。

import 步驟會再次 deterministic 驗證，任何 drift 都會被拒絕。
"""
