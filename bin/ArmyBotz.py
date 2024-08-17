


import requests as req
from urllib.parse import urljoin as ujoin, urlparse as uparse
from bs4 import BeautifulSoup as BS
import time as t
import random as rnd
import json as js
import os as os

class A:
    _ = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:61.0) Gecko/20100101 Firefox/61.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:71.0) Gecko/20100101 Firefox/71.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0"
    ]

    def __init__(self):
        self._b = ""
        self._d = 1.0
        self._e = 3
        self._f = set()
        self._g = set()
        self._h = []
        self._i = 0
        self._j = "10.0.0.0"
        self._k = "0.0.0.0/0"
        self._l = f"state_{t.strftime('%Y%m%d_%H%M%S')}.json"

    def _m(self):
        if os.path.exists(self._l):
            with open(self._l, "r") as f:
                s = js.load(f)
                self._f = set(s.get("visited", []))
                self._h = s.get("links_to_visit", [])
                print("Loaded state from file.")
        else:
            print("No state file found.")

    def _n(self):
        s = {
            "visited": list(self._f),
            "links_to_visit": self._h
        }
        with open(self._l, "w") as f:
            js.dump(s, f)
        print("State saved to file.")

    def _o(self):
        r = ujoin(self._b, "/robots.txt")
        try:
            res = req.get(r, headers={"User-Agent": rnd.choice(self._)})
            if res.status_code == 200:
                self._p(res.text)
            else:
                print(f"No robots.txt found or error fetching it. Status code: {res.status_code}")
        except req.RequestException as e:
            print(f"Error fetching robots.txt: {e}")

    def _p(self, txt):
        ua = None
        for l in txt.splitlines():
            l = l.strip()
            if l.startswith("User-agent:"):
                ua = l.split(":", 1)[1].strip()
            elif ua == "*" and l.startswith("Disallow:"):
                p = l.split(":", 1)[1].strip()
                self._g.add(p)

    def _q(self, url):
        p = uparse(url)
        path = p.path
        return not any(path.startswith(d) for d in self._g)

    def _r(self, url, d):
        if url in self._f or d > self._e:
            return
        if not self._q(url):
            print(f"Skipping {url} due to robots.txt rules.")
            return
        print(f"Visiting {url} at depth {d}")
        try:
            res = req.get(url, headers={"User-Agent": rnd.choice(self._)})
            if res.status_code == 200:
                self._f.add(url)
                self._s(res.text, url, d)
            else:
                print(f"Failed to retrieve {url}. Status code: {res.status_code}")
        except req.RequestException as e:
            print(f"Error fetching {url}: {e}")
        t.sleep(self._d)

    def _s(self, html, base_url, d):
        s = BS(html, "html.parser")
        for l in s.find_all("a", href=True):
            href = l["href"]
            full_url = ujoin(base_url, href)
            if full_url not in self._f:
                self._h.append((full_url, d + 1))

    def _t(self, start_ip, cidr):
        ip_range = []
        ip_parts = list(map(int, start_ip.split('.')))
        return [f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.{i}" for i in range(1, 256)]

    def _u(self):
        self._m()
        if not self._b:
            self._b = input("Enter base URL: ")
        self._o()
        
        m = input("Start in manual mode? (y/n): ").strip().lower()
        if m == 'y':
            ip_start = input("Enter starting IP (e.g., 10.0.0.1): ")
            ip_range = input("Enter IP range (CIDR): ")
            self._j = ip_start
            self._k = ip_range
            self._h.append((self._b, 0))

        while self._h:
            url, d = self._h.pop(0)
            self._r(url, d)
            self._n()

        print("Crawling completed.")

if __name__ == "__main__":
    bot = A()
    bot._u()
