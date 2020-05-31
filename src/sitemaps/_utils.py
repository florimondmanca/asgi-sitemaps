from urllib.parse import urljoin, urlsplit


def replace_root(url: str, root_url: str) -> str:
    return urljoin(root_url, urlsplit(url).path)
