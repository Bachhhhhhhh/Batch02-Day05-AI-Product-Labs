import json
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "data" / "drug_urls.txt"
OUTPUT_FILE = ROOT / "data" / "drugs_clean.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (student-project; LongChau crawler demo)"
}

FIELDS = {
    "drug_name": "",
    "ingredients": "",
    "uses": "",
    "dosage": "",
    "side_effects": "",
    "warnings": "",
    "contraindications": "",
    "storage": "",
    "source_url": "",
}

SECTION_MAP = {
    "thành phần": "ingredients",
    "công dụng": "uses",
    "chỉ định": "uses",
    "cách dùng": "dosage",
    "liều dùng": "dosage",
    "tác dụng phụ": "side_effects",
    "lưu ý": "warnings",
    "thận trọng": "warnings",
    "tương tác thuốc": "warnings",
    "chống chỉ định": "contraindications",
    "bảo quản": "storage",
}

def clean_text(text):
    return re.sub(r"\s+", " ", text or "").strip()

def get_title(soup):
    h1 = soup.find("h1")
    if h1:
        return clean_text(h1.get_text(" "))
    title = soup.find("title")
    return clean_text(title.get_text(" ")) if title else ""

def match_section(text):
    text = text.lower()
    for key, field in SECTION_MAP.items():
        if key in text:
            return field
    return None

def extract_sections(soup):
    data = {k: "" for k in FIELDS if k not in ["drug_name", "source_url"]}

    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()

    headings = soup.find_all(["h2", "h3", "h4"])

    for heading in headings:
        field = match_section(clean_text(heading.get_text(" ")))
        if not field:
            continue

        parts = []
        for sib in heading.find_next_siblings():
            if sib.name in ["h2", "h3", "h4"]:
                break
            text = clean_text(sib.get_text(" "))
            if text:
                parts.append(text)

        content = clean_text(" ".join(parts))
        if content:
            data[field] = clean_text(data[field] + " " + content)

    return data

def scrape_drug(url):
    res = requests.get(url, headers=HEADERS, timeout=25)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "lxml")

    drug = dict(FIELDS)
    drug["drug_name"] = get_title(soup)
    drug["source_url"] = url
    drug.update(extract_sections(soup))

    return drug

def main():
    urls = [
        line.strip()
        for line in INPUT_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and line.startswith("http")
    ]

    results = []

    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Crawl: {url}")
        try:
            drug = scrape_drug(url)
            results.append(drug)
        except Exception as e:
            print("ERROR:", url, e)

        time.sleep(1.5)

    OUTPUT_FILE.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"Saved {len(results)} drugs to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()