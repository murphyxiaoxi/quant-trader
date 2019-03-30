import requests
from requests.cookies import RequestsCookieJar


def get_cookies() -> RequestsCookieJar:
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Origin": "https://xueqiu.com",
        "Accept-Encoding": "br, gzip, deflate",
        "Host": "xueqiu.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15",
        "Accept-Language": "en-us",
        "Referer": "https://xueqiu.com/",
        "Connection": "keep-alive"
    }

    return requests.get(url="https://xueqiu.com", headers=headers, timeout=30).cookies
