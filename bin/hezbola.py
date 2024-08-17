import requests as req
from urllib.parse import urljoin as ujoin, urlparse as uparse
from bs4 import BeautifulSoup as BS
import time as t
import random as rnd
import json as js
import os
import ipaddress

class WebCrawler:
    _user_agents = [
        # Lista de User Agents
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
    ]

    def __init__(self):
        self.base_url = ""
        self.delay = 1.0
        self.max_depth = 3
        self.visited_urls = set()
        self.urls_to_visit = []
        self.state_file = f"state_{t.strftime('%Y%m%d_%H%M%S')}.json"
        self.robots_rules = set()
        self.ip_range = "10.0.0.0/24"
        self.current_ip = "10.0.0.1"

    def load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                state = js.load(f)
                self.visited_urls = set(state.get("visited", []))
                self.urls_to_visit = state.get("urls_to_visit", [])
                self.current_ip = state.get("current_ip", self.current_ip)
                print("Loaded state from file.")
        else:
            print("No state file found.")

    def save_state(self):
        state = {
            "visited": list(self.visited_urls),
            "urls_to_visit": self.urls_to_visit,
            "current_ip": self.current_ip
        }
        with open(self.state_file, "w") as f:
            js.dump(state, f)
        print("State saved to file.")

    def fetch_robots_txt(self):
        url = ujoin(self.base_url, "/robots.txt")
        try:
            response = req.get(url, headers={"User-Agent": rnd.choice(self._user_agents)})
            if response.status_code == 200:
                self.parse_robots_txt(response.text)
            else:
                print(f"No robots.txt found or error fetching it. Status code: {response.status_code}")
        except req.RequestException as e:
            print(f"Error fetching robots.txt: {e}")

    def parse_robots_txt(self, text):
        user_agent = None
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("User-agent:"):
                user_agent = line.split(":", 1)[1].strip()
            elif user_agent == "*" and line.startswith("Disallow:"):
                path = line.split(":", 1)[1].strip()
                self.robots_rules.add(path)

    def should_crawl(self, url):
        path = uparse(url).path
        return not any(path.startswith(rule) for rule in self.robots_rules)

    def crawl_url(self, url, depth):
        if url in self.visited_urls or depth > self.max_depth:
            return
        if not self.should_crawl(url):
            print(f"Skipping {url} due to robots.txt rules.")
            return
        print(f"Visiting {url} at depth {depth}")
        try:
            response = req.get(url, headers={"User-Agent": rnd.choice(self._user_agents)})
            if response.status_code == 200:
                self.visited_urls.add(url)
                self.extract_links(response.text, url, depth)
            else:
                print(f"Failed to retrieve {url}. Status code: {response.status_code}")
        except req.RequestException as e:
            print(f"Error fetching {url}: {e}")
        t.sleep(self.delay)

    def extract_links(self, html, base_url, depth):
        soup = BS(html, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link["href"]
            full_url = ujoin(base_url, href)
            if full_url not in self.visited_urls:
                self.urls_to_visit.append((full_url, depth + 1))

    def generate_ip_range(self):
        try:
            network = ipaddress.ip_network(self.ip_range, strict=False)
            return [str(ip) for ip in network.hosts()]
        except ValueError as e:
            print(f"Error with CIDR range: {e}")
            return []

    def start_crawling(self):
        self.load_state()
        if not self.base_url:
            self.base_url = input("Enter base URL: ")
        self.fetch_robots_txt()

        mode = input("Start in manual mode? (y/n): ").strip().lower()
        if mode == 'y':
            self.current_ip = input("Enter starting IP (e.g., 10.0.0.1): ")
            self.ip_range = input("Enter IP range (CIDR): ")
            self.urls_to_visit.append((self.base_url, 0))
        else:
            self.urls_to_visit.append((self.base_url, 0))

        while self.urls_to_visit:
            url, depth = self.urls_to_visit.pop(0)
            self.crawl_url(url, depth)
            self.save_state()

        print("Crawling completed.")

if __name__ == "__main__":
    crawler = WebCrawler()
    crawler.start_crawling()
