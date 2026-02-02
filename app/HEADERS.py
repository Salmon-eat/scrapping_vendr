import requests


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
}

SESSION = requests.Session()


def fetch_html(url: str) -> str:
    r = SESSION.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.text