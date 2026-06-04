import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

from thefuzz import fuzz

from app.core.logger import system_logger

DISCLAIMER = (
    "Thông tin dưới đây chỉ để bạn hiểu đơn thuốc, không thay thế chỉ định "
    "của bác sĩ hoặc tư vấn trực tiếp từ dược sĩ."
)

EMERGENCY_KEYWORDS = [
    "qua lieu",
    "uong nham",
    "ngo doc",
    "kho tho",
    "sung moi",
    "sung mat",
    "phat ban lan nhanh",
    "choang",
    "dau nguc",
    "ngat",
    "co giat",
    "hon me",
]

DOSE_CHANGE_KEYWORDS = [
    "tang lieu",
    "giam lieu",
    "doi lieu",
    "gap doi lieu",
    "uong nhieu hon",
    "ngung thuoc",
    "bo thuoc",
]

PRESCRIBE_KEYWORDS = [
    "ke don cho toi",
    "ke don thuoc cho toi",
    "cho toi don thuoc",
    "nen uong thuoc gi",
    "toi bi benh gi",
    "chan doan",
    "chuan doan",
]

STOPWORDS = {
    "thuoc",
    "vien",
    "sang",
    "chieu",
    "toi",
    "ngay",
    "uong",
    "ngam",
    "lan",
    "moi",
    "sau",
    "an",
    "dieu",
    "tri",
    "giam",
    "tang",
    "benh",
    "mau",
    "than",
    "soi",
    "acid",
    "uric",
    "domesco",
    "stella",
    "pharm",
    "euvipharm",
    "alcon",
    "mg",
    "ml",
}


def _normalize(text: str) -> str:
    text = (text or "").replace("Đ", "D").replace("đ", "d")
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text.lower()


def _tokens(text: str) -> list[str]:
    raw = text or ""
    # Split camelCase BEFORE normalizing so uppercase boundaries are visible
    raw = re.sub(r"([a-z])([A-Z])", r"\1 \2", raw)
    normalized = _normalize(raw)
    # Strip dosage quantities (e.g. 500mg, 10ml)
    normalized = re.sub(r"\d+(?:[,.]\d+)?\s*(mg|mcg|g|ml|vien|viẻn|lan|lần)", " ", normalized)
    # Also expand hyphens to spaces
    normalized = normalized.replace("-", " ")
    found = []
    for token in re.findall(r"[a-z0-9]+", normalized):
        if len(token) < 3 or token.isdigit() or token in STOPWORDS:
            continue
        found.append(token)
    return list(dict.fromkeys(found))


def check_emergency_rules(text: str) -> bool:
    normalized = _normalize(text)
    return any(keyword in normalized for keyword in EMERGENCY_KEYWORDS)


def _is_ambiguous(text: str) -> bool:
    normalized = _normalize(text)
    return "..." in text or bool(re.search(r"\b[a-z]{2,6}\.\.\.", normalized))


def _is_dose_change_request(text: str) -> bool:
    normalized = _normalize(text)
    return any(keyword in normalized for keyword in DOSE_CHANGE_KEYWORDS)


def _is_new_prescription_request(text: str) -> bool:
    normalized = _normalize(text)
    has_prescribed_drug_context = bool(
        re.search(r"\b(bac si|bs|doctor)\s+(da\s+)?ke\s+don\s+thuoc\s+.+", normalized)
        or re.search(r"\b(don thuoc|thuoc)\s+.+\b(luu y|cach dung|tac dung|canh bao|giai thich)\b", normalized)
    )
    if has_prescribed_drug_context:
        return False
    return any(keyword in normalized for keyword in PRESCRIBE_KEYWORDS)


def _base_response(message: str, confidence: str = "low", is_emergency: bool = False) -> dict:
    return {
        "symptoms": [],
        "confidence": confidence,
        "message": message,
        "combined_effect": "",
        "prescription_explanation": "",
        "side_effects": [],
        "categories": [],
        "recommendations": [],
        "warnings": [DISCLAIMER],
        "is_emergency": is_emergency,
        "clarifying_questions": [],
        "references": [],
        "products": [],
    }


@lru_cache(maxsize=1)
def _load_drugs() -> list[dict]:
    data_path = Path(__file__).resolve().parents[2] / "data" / "drugs_clean.json"
    with data_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _clean_name(text: str) -> str:
    text = re.sub(r"\([^()]*\)", " ", text or "")
    text = re.sub(r"\s+-\s+.*$", " ", text)
    text = re.sub(r"\b\d+[,.]\d+\s*(viên|vien|ống|ong|lọ|lo|gói|goi)\b", " ", text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", text).strip(" .:-;,")


def _clean_candidate(text: str) -> str:
    text = re.sub(r"[\n;]+", " ", text or "")
    text = re.sub(
        r"(?i)\b(giải thích|giai thich|thông tin|thong tin|đơn thuốc|don thuoc|thuốc|thuoc|của tôi|cua toi|cho tôi|cho toi)\b",
        " ",
        text,
    )
    text = re.sub(r"(?i)\b(bác sĩ|bac si|bs)\s*(đã\s*)?(kê|ke)\s*(đơn|don)?\b", " ", text)
    text = re.split(
        r"(?i)\b(thì|thi|nên|nen|cần|can|lưu ý|luu y|dùng để|dung de|cách dùng|cach dung|tác dụng|tac dung|cảnh báo|canh bao|những|nhung|điều|dieu|gì|gi|không|khong)\b",
        text,
        maxsplit=1,
    )[0]
    return _clean_name(text)


def _parse_numbered_prescription(message: str) -> list[dict]:
    normalized_message = message.replace("\r\n", "\n")
    matches = list(
        re.finditer(
            r"(?<!\d)(\d+)\.\s+(.*?)(?=(?<!\d)\d+\.\s+|\Z)",
            normalized_message,
            flags=re.DOTALL,
        )
    )
    items = []
    for match in matches:
        raw = match.group(2).strip()
        schedule_match = re.search(r"\b(Ngày|NGÀY|Ngay|NGAY)\b.*", raw, flags=re.DOTALL)
        med_part = raw[: schedule_match.start()].strip() if schedule_match else raw
        schedule = " ".join(schedule_match.group(0).split()) if schedule_match else ""
        name = _clean_name(med_part)
        if name:
            items.append({"name": name, "schedule": schedule})
    return items


def _extract_requested_drugs(message: str) -> list[dict]:
    numbered = _parse_numbered_prescription(message)
    if numbered:
        return numbered

    parts = re.split(r",|;|\n|\bvà\b|\band\b", message, flags=re.IGNORECASE)
    candidates = []
    for part in parts:
        candidate = _clean_candidate(part)
        if len(candidate) >= 3 and _tokens(candidate):
            candidates.append({"name": candidate, "schedule": ""})
    return candidates[:8]


def _get_short_name(text: str) -> str:
    name = re.sub(r"\([^()]*\)", " ", text or "")
    name = re.split(r"(?i)\b(điều trị|trị|bổ sung|phòng|cải thiện|dự phòng|tiêu|giảm|hỗ trợ|giúp|chống|cung cấp|ngăn ngừa|long đờm|làm dịu)\b", name, maxsplit=1)[0]
    return re.sub(r"\s+", " ", name).strip(" .:-;,")


def _score_drug(query: str, drug_name: str) -> int:
    short_drug_name = _get_short_name(drug_name)
    name_norm = _normalize(short_drug_name)
    # Build a set of whole words in the drug name for exact word matching
    name_words = set(re.findall(r"[a-z0-9]+", name_norm))

    query_tokens = _tokens(query)
    if not query_tokens:
        return 0

    # Count how many query tokens appear as WHOLE WORDS in the drug name
    token_hits = sum(1 for token in query_tokens if token in name_words)
    if token_hits == len(query_tokens):
        # All tokens matched as whole words -> strong match
        return 100 + token_hits

    query_norm = _normalize(query)
    if query_norm in name_norm:
        return 95

    # Fuzzy only when there are token hits; purely fuzzy alone is too noisy
    if token_hits > 0:
        fuzzy = fuzz.token_set_ratio(query_norm, name_norm)
        coverage = int((token_hits / len(query_tokens)) * 100)
        return max(fuzzy, coverage)

    # No token overlap at all: fall back to partial ratio but cap it
    fuzzy = fuzz.partial_ratio(query_norm, name_norm)
    return min(fuzzy, 74)  # cap below threshold so it never auto-matches


def _find_drug(query: str) -> dict | None:
    best_drug = None
    best_score = 0
    for drug in _load_drugs():
        score = _score_drug(query, drug.get("drug_name", ""))
        if score > best_score:
            best_score = score
            best_drug = drug
    return best_drug if best_score >= 80 else None


def _sentences(text: str) -> list[str]:
    clean = " ".join((text or "").split())
    if not clean:
        return []
    parts = re.split(r"(?<=[.!?])\s+|;\s+", clean)
    if len(parts) == 1:
        parts = re.split(r"\s+(?=(?:Chống chỉ định|Thận trọng|Liều dùng|Cách dùng|Tác dụng|Dược lực học)\b)", clean)
    return [part.strip(" -") for part in parts if part.strip(" -")]


def _summary(text: str, max_sentences: int = 2) -> str:
    parts = _sentences(text)
    return " ".join(parts[:max_sentences]) if parts else "Chưa có dữ liệu trong database demo"


def _escape_md(text: str) -> str:
    return (text or "").replace("|", "/").replace("\n", " ").strip()


def _explain_item(requested: dict) -> tuple[dict, dict | None]:
    drug = _find_drug(requested["name"])
    if not drug:
        return (
            {
                "name": requested["name"],
                "use": "Chưa tìm thấy dữ liệu về thuốc này trong database demo",
                "dosage": requested.get("schedule") or "Theo đúng đơn bác sĩ đã kê; chatbot không tự chỉnh liều",
                "safety": "Không tự thay bằng thuốc tương tự. Hãy hỏi bác sĩ/dược sĩ nếu nhà thuốc không có đúng thuốc trong đơn.",
                "side_effects": "Chưa có dữ liệu trong database demo",
                "source": "Chưa tìm thấy dữ liệu về thuốc này trong database demo",
            },
            None,
        )

    dosage = requested.get("schedule") or _summary(drug.get("dosage", ""))
    return (
        {
            "name": requested["name"],
            "matched_name": drug.get("drug_name", ""),
            "use": _summary(drug.get("uses", "")),
            "dosage": dosage,
            "source_dosage": _summary(drug.get("dosage", "")),
            "safety": _summary(drug.get("warnings", "")),
            "side_effects": _summary(drug.get("side_effects", "")),
            "source": drug.get("source_url", ""),
        },
        drug,
    )


def _markdown_table(rows: list[dict]) -> str:
    header = "| Thuốc | Dùng để làm gì | Cách dùng theo nguồn | Lưu ý an toàn | Tác dụng phụ cần chú ý | Nguồn |"
    sep = "|---|---|---|---|---|---|"
    body = []
    for row in rows:
        source = row["source"]
        if source.startswith("http"):
            source = f"[Long Châu]({source})"
        body.append(
            "| "
            + " | ".join(
                _escape_md(row.get(key, ""))
                for key in ["name", "use", "dosage", "safety", "side_effects"]
            )
            + f" | {_escape_md(source)} |"
        )
    return "\n".join([header, sep, *body])


def _explain_drugs(message: str) -> dict:
    requested_items = _extract_requested_drugs(message)
    if not requested_items:
        response = _base_response(
            f"{DISCLAIMER}\n\nBạn hãy nhập tên thuốc hoặc paste đơn thuốc để mình giải thích. "
            "Mình không hỏi thêm triệu chứng và không kê đơn mới.",
            confidence="low",
        )
        response["clarifying_questions"] = [
            "Bạn có thể nhập tên thuốc đầy đủ hơn không?",
            "Nếu có đơn thuốc, bạn có thể paste từng dòng thuốc trong đơn không?",
        ]
        return response

    rows = []
    references = []
    matched = []
    for item in requested_items:
        row, drug = _explain_item(item)
        rows.append(row)
        if drug:
            matched.append(drug.get("drug_name", item["name"]))
            source_url = drug.get("source_url", "")
            if source_url:
                references.append({"name": drug.get("drug_name", item["name"]), "url": source_url})

    response = _base_response(
        f"{DISCLAIMER}\n\nMình đã tách được {len(rows)} thuốc/tên thuốc và chỉ đối chiếu đúng tên thuốc trong database demo Long Châu. "
        "Nếu không tìm thấy đúng thuốc, mình ghi rõ là chưa có dữ liệu và không thay bằng thuốc tương tự.",
        confidence="high" if matched else "low",
    )
    response["prescription_explanation"] = _markdown_table(rows)
    response["references"] = references
    response["side_effects"] = [row["side_effects"] for row in rows if row.get("side_effects")]
    return response


def process_mock_ai(message: str, chat_history: list = None) -> dict:
    if check_emergency_rules(message):
        return _base_response(
            f"{DISCLAIMER}\n\nNội dung có dấu hiệu rủi ro cao. Vui lòng liên hệ bác sĩ/dược sĩ hoặc cơ sở y tế ngay.",
            confidence="emergency",
            is_emergency=True,
        )
    if _is_ambiguous(message):
        response = _base_response(
            f"{DISCLAIMER}\n\nTên thuốc đang bị viết tắt hoặc chưa rõ. Mình không nên đoán tên thuốc vì có thể giải thích sai.",
            confidence="low",
        )
        response["clarifying_questions"] = ["Bạn vui lòng nhập lại tên thuốc đầy đủ và hàm lượng nếu có không?"]
        return response
    if _is_dose_change_request(message):
        return _base_response(
            f"{DISCLAIMER}\n\nMình không thể hướng dẫn tự tăng, giảm, ngừng hoặc đổi liều thuốc. "
            "Bạn nên làm theo đơn gốc và hỏi bác sĩ/dược sĩ nếu cần thay đổi.",
            confidence="low",
        )
    if _is_new_prescription_request(message):
        return _base_response(
            f"{DISCLAIMER}\n\nMình không kê đơn, không chẩn đoán và không đề xuất thuốc mới từ triệu chứng. "
            "Nếu bạn đã có đơn thuốc, hãy nhập tên thuốc trong đơn để mình giải thích.",
            confidence="low",
        )
    return _explain_drugs(message)


def process_gemini_ai(message: str, chat_history: list = None) -> dict:
    system_logger.info("Using deterministic prescription explainer instead of free-form Gemini prescribing flow.")
    return process_mock_ai(message, chat_history)


def process_openai_ai(message: str, chat_history: list = None) -> dict:
    system_logger.info("Using deterministic prescription explainer instead of free-form OpenAI prescribing flow.")
    return process_mock_ai(message, chat_history)
