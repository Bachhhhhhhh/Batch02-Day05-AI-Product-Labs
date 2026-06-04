import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "data" / "drug_urls.txt"

START_URLS = [
    "https://nhathuoclongchau.com.vn/thuoc/forlen-600mg-3716.html"
]

SITEMAP_URLS = [
    "https://nhathuoclongchau.com.vn/sitemap.xml",
    "https://nhathuoclongchau.com.vn/sitemap-products.xml",
    "https://nhathuoclongchau.com.vn/product-sitemap.xml",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (student-project; collect drug urls)"
}


def get_html(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text


def is_drug_product_url(url):
    return (
        url.startswith("https://nhathuoclongchau.com.vn/thuoc/")
        and url.endswith(".html")
        and "/tim-kiem" not in url
        and "?" not in url
    )


def extract_links_from_page(url):
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser")

    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if href.startswith("/"):
            href = "https://nhathuoclongchau.com.vn" + href

        href = href.split("?")[0]

        if is_drug_product_url(href):
            links.add(href)

    return links


def extract_links_from_sitemap(url):
    xml = get_html(url)
    soup = BeautifulSoup(xml, "xml")

    links = set()

    for loc in soup.find_all("loc"):
        link = loc.get_text(strip=True)

        if link.endswith(".xml"):
            try:
                print("Reading nested sitemap:", link)
                links.update(extract_links_from_sitemap(link))
                time.sleep(0.2)
            except Exception as e:
                print("Skip nested sitemap:", link, e)

        else:
            link = link.split("?")[0]
            if is_drug_product_url(link):
                links.add(link)

    return links


def read_existing_urls():
    if not OUT_FILE.exists():
        return set()

    return set(
        line.strip()
        for line in OUT_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def save_urls(urls):
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text("\n".join(sorted(urls)), encoding="utf-8")


def main():
    try:
        limit = int(input("Bạn muốn gen bao nhiêu link? "))
    except ValueError:
        print("Giá trị không hợp lệ, mặc định lấy 100 link.")
        limit = 100

    existing_urls = read_existing_urls()

    all_links = set()

    for url in START_URLS:
        all_links.add(url)

    for sitemap in SITEMAP_URLS:
        try:
            print("Reading sitemap:", sitemap)
            links = extract_links_from_sitemap(sitemap)
            all_links.update(links)
        except Exception as e:
            print("Skip sitemap:", sitemap, e)

    for url in START_URLS:
        try:
            links = extract_links_from_page(url)
            all_links.update(links)
        except Exception as e:
            print("Skip page:", url, e)

    new_urls = []

    for url in sorted(all_links):
        if url not in existing_urls:
            new_urls.append(url)

        if len(new_urls) >= limit:
            break

    final_urls = existing_urls.union(new_urls)
    save_urls(final_urls)

    print("================================")
    print(f"Existing URLs: {len(existing_urls)}")
    print(f"Found URLs total: {len(all_links)}")
    print(f"New URLs added: {len(new_urls)}")
    print(f"Total saved: {len(final_urls)}")
    print(f"Saved to: {OUT_FILE}")
    print("================================")

    print("New links:")
    for url in new_urls:
        print(url)


if __name__ == "__main__":
    main()