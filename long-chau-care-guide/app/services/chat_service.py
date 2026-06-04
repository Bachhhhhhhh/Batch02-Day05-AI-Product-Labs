import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

from thefuzz import fuzz
from google import genai
from openai import OpenAI

from app.core.config import GEMINI_API_KEY, OPENAI_API_KEY, MODEL_TEMPERATURE, MAX_TOKENS
from app.core.logger import system_logger
from app.core.model_settings import model_settings
from vector_db.retriever import search_drugs

DISCLAIMER = (
    "Thông tin dưới đây chỉ để bạn hiểu đơn thuốc, không thay thế chỉ định "
    "của bác sĩ hoặc tư vấn trực tiếp từ dược sĩ."
)
OUT_OF_SCOPE_MESSAGE = "Không hỗ trợ chủ đề này. Mình chỉ hỗ trợ giải thích đơn thuốc hoặc tên thuốc."
NOT_SOLD_MESSAGE = "Long Châu không có bán."

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

SYMPTOM_WORDS = {
    "dau",
    "rat",
    "hong",
    "ho",
    "sot",
    "so",
    "mui",
    "nghet",
    "met",
    "moi",
    "ngua",
    "man",
    "do",
    "non",
    "oi",
    "tieu",
    "chay",
    "bung",
    "dau bung",
    "dau dau",
    "cam",
    "cum",
    "viem",
    "kho",
    "tho",
    "chong",
    "mat",
}

DRUG_CONTEXT_WORDS = {
    "thuoc",
    "don thuoc",
    "toa thuoc",
    "bac si ke",
    "bs ke",
    "giai thich",
    "luu y",
    "cach dung",
    "tac dung",
}

DRUG_FORM_PREFIXES = (
    "Thuốc nhỏ mắt",
    "Dung dịch uống",
    "Dung dịch",
    "Viên nén",
    "Viên nang",
    "Siro",
    "Kem bôi",
    "Gel bôi",
    "Thuốc",
)

DESCRIPTION_STARTERS = (
    " điều trị ",
    " hỗ trợ ",
    " bổ sung ",
    " phòng và điều trị ",
    " phòng ngừa ",
    " giảm ",
    " dùng ",
    " chứa ",
    " trị ",
)


def _normalize(text: str) -> str:
    text = (text or "").replace("Đ", "D").replace("đ", "d")
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text.lower()


def _tokens(text: str) -> list[str]:
    normalized = _normalize(text)
    normalized = re.sub(r"\d+(?:[,.]\d+)?\s*(mg|mcg|g|ml|vien|viên|lan|lần)", " ", normalized)
    found = []
    for token in re.findall(r"[a-z0-9]+", normalized):
        if len(token) < 4 or token.isdigit() or token in STOPWORDS:
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


def _has_drug_context(text: str) -> bool:
    normalized = _normalize(text)
    return any(keyword in normalized for keyword in DRUG_CONTEXT_WORDS)


def _has_dosage_marker(text: str) -> bool:
    normalized = _normalize(text)
    return bool(re.search(r"\b\d+(?:[,.]\d+)?\s*(mg|mcg|g|ml)\b", normalized))


def _looks_like_symptom_only(text: str) -> bool:
    normalized = _normalize(text)
    has_first_person_symptom = bool(re.search(r"\b(toi|minh|em|con|me|bo|ba)\s+(bi|dang bi|thay|cam thay)\b", normalized))
    symptom_hits = sum(1 for symptom in SYMPTOM_WORDS if re.search(rf"\b{re.escape(symptom)}\b", normalized))
    return has_first_person_symptom and symptom_hits > 0 and not _has_drug_context(text)


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


def _model_unavailable_response(provider: str, reason: str) -> dict:
    return _base_response(
        f"Không gọi được model AI {provider}. Vui lòng kiểm tra API key/kết nối mạng rồi thử lại.\n\nChi tiết: {reason}",
        confidence="low",
    )


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


def _display_drug_name(drug_name: str) -> str:
    name = re.sub(r"\([^()]*\)", " ", drug_name or "")
    for prefix in DRUG_FORM_PREFIXES:
        name = re.sub(rf"^{re.escape(prefix)}\s+", "", name, flags=re.IGNORECASE)
        break_match = re.match(rf"^{re.escape(prefix)}\s+", drug_name or "", flags=re.IGNORECASE)
        if break_match:
            break

    lowered = _normalize(name)
    cut_positions = []
    for starter in DESCRIPTION_STARTERS:
        idx = lowered.find(_normalize(starter))
        if idx > 0:
            cut_positions.append(idx)
    if cut_positions:
        name = name[: min(cut_positions)]

    name = re.sub(r"\s+-\s+.*$", "", name)
    name = re.sub(r"\b\d+\s*(vỉ|vi|viên|vien|ống|ong|lọ|lo|gói|goi)\b.*$", "", name, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", name).strip(" .:-;,")


@lru_cache(maxsize=1)
def _drug_index() -> list[dict]:
    indexed = []
    for drug in _load_drugs():
        raw_name = drug.get("drug_name", "")
        display_name = _display_drug_name(raw_name)
        indexed.append(
            {
                "drug": drug,
                "raw_name": raw_name,
                "display_name": display_name,
                "raw_norm": _normalize(raw_name),
                "display_norm": _normalize(display_name),
                "display_tokens": _tokens(display_name),
            }
        )
    return indexed


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


def _score_drug(query: str, drug_name: str) -> int:
    query_norm = _normalize(query)
    name_norm = _normalize(drug_name)
    query_tokens = _tokens(query)
    if not query_tokens:
        return 0

    token_hits = sum(1 for token in query_tokens if token in name_norm)
    if token_hits == len(query_tokens):
        return 100 + token_hits
    if query_norm in name_norm:
        return 95
    fuzzy = fuzz.token_set_ratio(query_norm, name_norm)
    coverage = int((token_hits / len(query_tokens)) * 100)
    return max(fuzzy, coverage)


def _find_drug(query: str) -> dict | None:
    query_norm = _normalize(_clean_candidate(query))
    query_tokens = _tokens(query)
    if not query_norm or not query_tokens:
        return None

    best_item = None
    best_score = 0
    for item in _drug_index():
        display_norm = item["display_norm"]
        raw_norm = item["raw_norm"]
        display_tokens = item["display_tokens"]
        token_hits = sum(1 for token in query_tokens if token in display_tokens or token in display_norm)

        exactish = (
            query_norm == display_norm
            or re.search(rf"\b{re.escape(query_norm)}\b", display_norm)
            or all(token in display_norm for token in query_tokens)
        )
        if not exactish:
            continue

        # Do not let generic symptom words retrieve medicines from indication text.
        if token_hits == 0 or all(token in SYMPTOM_WORDS for token in query_tokens):
            continue

        score = 120 + token_hits if query_norm in display_norm else 100 + token_hits
        if query_norm in raw_norm and score < 110:
            score = 110 + token_hits
        if score > best_score:
            best_score = score
            best_item = item

    if not best_item:
        return None

    drug = dict(best_item["drug"])
    drug["_display_name"] = best_item["display_name"]
    return drug


def _has_medicine_intent(message: str, requested_items: list[dict]) -> bool:
    if _has_drug_context(message) or _has_dosage_marker(message) or _parse_numbered_prescription(message):
        return True
    if len(requested_items) == 1 and _find_drug(requested_items[0]["name"]):
        return True
    return False


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


def _row_from_drug(drug: dict, schedule: str = "") -> dict:
    dosage = schedule or _summary(drug.get("dosage", ""))
    return {
        "name": drug.get("_display_name") or _display_drug_name(drug.get("drug_name", "")),
        "matched_name": drug.get("drug_name", ""),
        "use": _summary(drug.get("uses", "")),
        "dosage": dosage,
        "source_dosage": _summary(drug.get("dosage", "")),
        "safety": _summary(drug.get("warnings", "")),
        "side_effects": _summary(drug.get("side_effects", "")),
        "source": drug.get("source_url", ""),
    }


def _explain_item(requested: dict) -> tuple[dict, dict | None]:
    drug = _find_drug(requested["name"])
    if not drug:
        return ({}, None)

    return (_row_from_drug(drug, requested.get("schedule", "")), drug)


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


def _retrieve_context_for_drug(drug: dict, user_message: str, top_k: int = 12) -> list[dict]:
    raw_name = drug.get("drug_name", "")
    display_name = drug.get("_display_name") or _display_drug_name(raw_name)
    query = f"{display_name} {raw_name} {user_message}"
    retrieved = search_drugs(query, top_k=top_k)
    exact = [item for item in retrieved if item.get("drug_name") == raw_name]

    if exact:
        return exact

    fallback = []
    section_map = {
        "uses": "uses",
        "dosage": "dosage",
        "warnings": "warnings",
        "side_effects": "side_effects",
        "contraindications": "contraindications",
    }
    for section, key in section_map.items():
        content = drug.get(key, "")
        if content:
            fallback.append(
                {
                    "drug_name": raw_name,
                    "section": section,
                    "content": content,
                    "source_url": drug.get("source_url", ""),
                }
            )
    return fallback


def _build_rag_context(rows: list[dict], drugs: list[dict], user_message: str) -> tuple[str, list[dict]]:
    blocks = []
    references = []
    for row, drug in zip(rows, drugs):
        raw_name = drug.get("drug_name", "")
        display_name = row.get("name", _display_drug_name(raw_name))
        contexts = _retrieve_context_for_drug(drug, user_message)
        if drug.get("source_url"):
            references.append({"name": raw_name, "url": drug.get("source_url")})

        section_lines = []
        for item in contexts:
            section_lines.append(
                f"- section={item.get('section', '')}; source={item.get('source_url', '')}; content={item.get('content', '')}"
            )
        blocks.append(
            "\n".join(
                [
                    f"DRUG_DISPLAY_NAME: {display_name}",
                    f"DRUG_NAME_FULL: {raw_name}",
                    "CONTEXT:",
                    *section_lines,
                ]
            )
        )
    return "\n\n---\n\n".join(blocks), references


def _build_llm_prompt(user_message: str, rows: list[dict], context: str) -> str:
    requested_names = ", ".join(row["name"] for row in rows)
    return f"""
Bạn là AI giải thích đơn thuốc bằng tiếng Việt cho người dùng phổ thông.

Nhiệm vụ:
- Chỉ giải thích các thuốc đã match chính xác: {requested_names}.
- Chỉ dùng CONTEXT được cung cấp. Không dùng kiến thức ngoài context.
- Không kê đơn, không chẩn đoán, không đề xuất thuốc mới, không thay thuốc tương tự.
- Nếu user hỏi tương tác thuốc-thức ăn/cà phê/rượu/sữa nhưng CONTEXT không có thông tin tương tác đó, hãy ghi rõ: "Nguồn Long Châu trong demo chưa có dữ liệu tương tác thuốc-thức ăn cụ thể cho thuốc này." Không được bịa.
- Nếu user hỏi đổi liều/tăng liều/ngừng thuốc, từ chối chỉnh liều và khuyên hỏi bác sĩ/dược sĩ.
- Trả lời bằng Markdown table duy nhất với đúng các cột:
| Thuốc | Dùng để làm gì | Cách dùng theo nguồn | Lưu ý an toàn | Tác dụng phụ cần chú ý | Nguồn |
- Cột "Thuốc" dùng đúng DRUG_DISPLAY_NAME, không dùng lại nguyên input của user.
- Cột "Nguồn" đặt link Markdown [Long Châu](source_url) nếu có.

USER_MESSAGE:
{user_message}

CONTEXT:
{context}
""".strip()


def _call_gemini(prompt: str, api_key: str | None = None) -> str:
    key = api_key or GEMINI_API_KEY
    if not key:
        raise RuntimeError("GEMINI_API_KEY chưa được cấu hình")
    client = genai.Client(api_key=key)
    response = client.models.generate_content(
        model=model_settings.GEMINI_MODEL_NAME,
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            temperature=min(MODEL_TEMPERATURE, 0.2),
            max_output_tokens=MAX_TOKENS,
        ),
    )
    return (response.text or "").strip()


def _call_openai(prompt: str, api_key: str | None = None) -> str:
    key = api_key or OPENAI_API_KEY
    if not key:
        raise RuntimeError("OPENAI_API_KEY chưa được cấu hình")
    client = OpenAI(api_key=key)
    response = client.chat.completions.create(
        model=model_settings.OPENAI_MODEL_NAME,
        messages=[
            {"role": "system", "content": "Bạn chỉ trả lời dựa trên context được cung cấp và tuân thủ guardrail y tế."},
            {"role": "user", "content": prompt},
        ],
        temperature=min(MODEL_TEMPERATURE, 0.2),
        max_tokens=MAX_TOKENS,
    )
    return (response.choices[0].message.content or "").strip()


def _generate_ai_table(provider: str, user_message: str, rows: list[dict], drugs: list[dict], api_key: str | None = None) -> tuple[str, list[dict]]:
    context, references = _build_rag_context(rows, drugs, user_message)
    prompt = _build_llm_prompt(user_message, rows, context)
    if provider == "gemini":
        return _call_gemini(prompt, api_key), references
    if provider == "openai":
        return _call_openai(prompt, api_key), references
    raise RuntimeError(f"Provider không hỗ trợ AI RAG: {provider}")


def _explain_drugs(message: str, provider: str = "mock", api_key: str | None = None) -> dict:
    if _looks_like_symptom_only(message):
        return _base_response(
            f"{DISCLAIMER}\n\nMình không kê đơn, không chẩn đoán và không đề xuất thuốc mới từ triệu chứng. "
            "Nếu bạn đã có đơn thuốc hoặc tên thuốc cụ thể, hãy nhập đúng tên thuốc để mình giải thích.",
            confidence="low",
        )

    requested_items = _extract_requested_drugs(message)
    if not _has_medicine_intent(message, requested_items):
        return _base_response(OUT_OF_SCOPE_MESSAGE, confidence="low")

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
    matched_drugs = []
    missing_count = 0
    for item in requested_items:
        row, drug = _explain_item(item)
        if drug:
            rows.append(row)
            matched_drugs.append(drug)
            matched.append(drug.get("drug_name", item["name"]))
            source_url = drug.get("source_url", "")
            if source_url:
                references.append({"name": drug.get("drug_name", item["name"]), "url": source_url})
        else:
            missing_count += 1

    if not matched:
        return _base_response(NOT_SOLD_MESSAGE, confidence="low")

    if provider in {"gemini", "openai"}:
        try:
            ai_table, ai_references = _generate_ai_table(provider, message, rows, matched_drugs, api_key)
        except Exception as exc:
            system_logger.error("AI RAG generation failed with %s: %s", provider, exc)
            return _model_unavailable_response(provider, str(exc))

        response = _base_response(
            f"{DISCLAIMER}\n\nĐã dùng RAG: truy xuất context từ vector database Long Châu và gọi model AI {provider} để giải thích.",
            confidence="high",
        )
        response["prescription_explanation"] = ai_table or _markdown_table(rows)
        response["references"] = ai_references or references
        response["side_effects"] = [row["side_effects"] for row in rows if row.get("side_effects")]
        return response

    response = _base_response(
        f"{DISCLAIMER}\n\nĐang chạy local fallback: đối chiếu rule-based từ database demo Long Châu, chưa gọi model AI. "
        f"Mình đã đối chiếu đúng {len(rows)} thuốc."
        + (f" {missing_count} thuốc còn lại: {NOT_SOLD_MESSAGE}" if missing_count else ""),
        confidence="high",
    )
    response["prescription_explanation"] = _markdown_table(rows)
    response["references"] = references
    response["side_effects"] = [row["side_effects"] for row in rows if row.get("side_effects")]
    return response


def _process_prescription_flow(message: str, chat_history: list = None, provider: str = "mock", api_key: str | None = None) -> dict:
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
    return _explain_drugs(message, provider, api_key)


def process_mock_ai(message: str, chat_history: list = None) -> dict:
    return _process_prescription_flow(message, chat_history, "mock")


def process_gemini_ai(message: str, chat_history: list = None, api_key: str | None = None) -> dict:
    system_logger.info("Using Gemini RAG prescription explainer.")
    return _process_prescription_flow(message, chat_history, "gemini", api_key)


def process_openai_ai(message: str, chat_history: list = None, api_key: str | None = None) -> dict:
    system_logger.info("Using OpenAI RAG prescription explainer.")
    return _process_prescription_flow(message, chat_history, "openai", api_key)
