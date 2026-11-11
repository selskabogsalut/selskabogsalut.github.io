#!/usr/bin/env python3
"""Crawl test for the Selskab & Salut site.

Starts at the front page, follows every <a href> link on the same host
(breadth-first, standard library only) and reports what it finds. Afterwards it
compares the result with sitemap.xml, so pages that no link points to show up.

Usage:
    python3 tools/crawl_test.py https://selskabogsalut.github.io/
    python3 tools/crawl_test.py http://localhost:4000/

Exit code 0 means every page answered 200 and every sitemap URL was reachable via links.
"""
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import deque
from html.parser import HTMLParser

USER_AGENT = "selskab-crawl-test/1.0"


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.tables = 0
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)
        elif tag == "table":
            self.tables += 1
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, resp.headers.get("Content-Type", ""), body
    except urllib.error.HTTPError as err:
        return err.code, err.headers.get("Content-Type", ""), ""


def normalise(url):
    url, _fragment = urllib.parse.urldefrag(url)
    return url


def crawl(start):
    host = urllib.parse.urlparse(start).netloc
    queue = deque([(normalise(start), 0)])
    seen = {normalise(start)}
    results = {}
    while queue:
        url, depth = queue.popleft()
        status, ctype, body = fetch(url)
        info = {"status": status, "depth": depth, "title": "", "tables": 0, "html": "text/html" in ctype}
        if status == 200 and info["html"]:
            parser = PageParser()
            parser.feed(body)
            info["title"] = " ".join(parser.title.split())
            info["tables"] = parser.tables
            for href in parser.links:
                target = normalise(urllib.parse.urljoin(url, href))
                parsed = urllib.parse.urlparse(target)
                if parsed.scheme in ("http", "https") and parsed.netloc == host and target not in seen:
                    seen.add(target)
                    queue.append((target, depth + 1))
        results[url] = info
    return results


def sitemap_paths(start):
    status, _ctype, body = fetch(urllib.parse.urljoin(start, "/sitemap.xml"))
    if status != 200:
        return None
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    root = ET.fromstring(body)
    return {urllib.parse.urlparse(loc.text.strip()).path for loc in root.findall("sm:url/sm:loc", ns)}


def main():
    start = sys.argv[1] if len(sys.argv) > 1 else "https://selskabogsalut.github.io/"
    results = crawl(start)

    print(f"{'Status':<7}{'Dybde':<7}{'Tabeller':<10}Adresse")
    for url, info in sorted(results.items(), key=lambda kv: (kv[1]["depth"], kv[0])):
        path = urllib.parse.urlparse(url).path
        print(f"{info['status']:<7}{info['depth']:<7}{info['tables']:<10}{path}")

    pages = {u: i for u, i in results.items() if i["html"]}
    broken = {u: i for u, i in results.items() if i["status"] != 200}
    print(f"\nSider fundet via links: {len(pages)}")
    print(f"Tabeller i alt: {sum(i['tables'] for i in pages.values())}")

    ok = not broken
    if broken:
        print("\nAdresser der ikke svarede 200:")
        for url, info in broken.items():
            print(f"  {info['status']}  {url}")

    in_sitemap = sitemap_paths(start)
    if in_sitemap is None:
        print("\nsitemap.xml blev ikke fundet.")
        ok = False
    else:
        reached = {urllib.parse.urlparse(u).path for u in pages}
        orphans = sorted(in_sitemap - reached)
        print(f"Sider i sitemap.xml: {len(in_sitemap)}")
        if orphans:
            ok = False
            print("Sider i sitemap.xml, som intet link fører til:")
            for path in orphans:
                print(f"  {path}")
        else:
            print("Alle sider i sitemap.xml kan nås via links.")

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
