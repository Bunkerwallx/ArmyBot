



import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time
import re

class AdvancedBot:
    def __init__(self, base_url, delay=1.0, max_depth=3):
        self.base_url = base_url
        self.delay = delay
        self.max_depth = max_depth
        self.visited = set()
        self.disallowed = set()
        self.links_to_visit = []
        self.depth = 0

    def fetch_robots_txt(self):
        robots_url = urljoin(self.base_url, "/robots.txt")
        try:
            response = requests.get(robots_url)
            if response.status_code == 200:
                self.parse_robots_txt(response.text)
            else:
                print(f"No robots.txt found or error fetching it. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error fetching robots.txt: {e}")

    def parse_robots_txt(self, text):
        user_agent = None
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("User-agent:"):
                user_agent = line.split(":", 1)[1].strip()
            elif user_agent == "*" and line.startswith("Disallow:"):
                path = line.split(":", 1)[1].strip()
                self.disallowed.add(path)

    def should_visit(self, url):
        parsed_url = urlparse(url)
        path = parsed_url.path
        return not any(path.startswith(disallowed) for disallowed in self.disallowed)

    def fetch_page(self, url, depth):
        if url in self.visited or depth > self.max_depth:
            return
        if not self.should_visit(url):
            print(f"Skipping {url} due to robots.txt rules.")
            return
        print(f"Visiting {url} at depth {depth}")
        try:
            response = requests.get(url)
            if response.status_code == 200:
                self.visited.add(url)
                self.parse_page(response.text, url, depth)
            else:
                print(f"Failed to retrieve {url}. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
        time.sleep(self.delay)  # Control de velocidad

    def parse_page(self, html, base_url, depth):
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link["href"]
            full_url = urljoin(base_url, href)
            if full_url not in self.visited:
                self.links_to_visit.append((full_url, depth + 1))

    def crawl(self):
        self.fetch_robots_txt()
        self.links_to_visit.append((self.base_url, 0))  # Comenzar desde la URL base con profundidad 0

        while self.links_to_visit:
            url, depth = self.links_to_visit.pop(0)
            self.fetch_page(url, depth)

# Uso del bot
if __name__ == "__main__":
    base_url = "http://example.com"  # Reemplazar con la URL que deseas rastrear
    bot = AdvancedBot(base_url, delay=2.0, max_depth=3)
    bot.crawl()
