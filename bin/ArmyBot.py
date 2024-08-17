import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time
import re
import random
import json
import os

class AdvancedBot:
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:61.0) Gecko/20100101 Firefox/61.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:71.0) Gecko/20100101 Firefox/71.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0"
    ]

    def __init__(self):
        self.base_url = ""
        self.delay = 1.0
        self.max_depth = 3
        self.visited = set()
        self.disallowed = set()
        self.links_to_visit = []
        self.depth = 0
        self.start_ip = "10.0.0.0"
        self.ip_range = "0.0.0.0/0"
        self.state_file = f"bot_state_{time.strftime('%Y%m%d_%H%M%S')}.json"

    def load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as file:
                state = json.load(file)
                self.visited = set(state.get("visited", []))
                self.links_to_visit = state.get("links_to_visit", [])
                print("Estado cargado desde el archivo.")
        else:
            print("No hay estado guardado.")

    def save_state(self):
        state = {
            "visited": list(self.visited),
            "links_to_visit": self.links_to_visit
        }
        with open(self.state_file, "w") as file:
            json.dump(state, file)
        print("Estado guardado en el archivo.")

    def fetch_robots_txt(self):
        robots_url = urljoin(self.base_url, "/robots.txt")
        try:
            response = requests.get(robots_url, headers={"User-Agent": random.choice(self.USER_AGENTS)})
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
            response = requests.get(url, headers={"User-Agent": random.choice(self.USER_AGENTS)})
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

    def generate_ip_range(self, start_ip, cidr):
        # Función simplificada para generar un rango de IPs basadas en CIDR
        ip_range = []
        ip_parts = list(map(int, start_ip.split('.')))
        # Aquí podrías implementar lógica más compleja para CIDR, por simplicidad se omite.
        return [f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.{i}" for i in range(1, 256)]

    def crawl(self):
        self.load_state()
        if not self.base_url:
            self.base_url = input("Ingrese la URL base: ")
        self.fetch_robots_txt()
        
        # Modo Manual
        mode = input("¿Deseas iniciar en modo manual? (s/n): ").strip().lower()
        if mode == 's':
            ip_start = input("Ingresa la IP inicial (ej. 10.0.0.1): ")
            ip_range = input("Ingresa el rango de IPs (CIDR): ")
            self.start_ip = ip_start
            self.ip_range = ip_range
            self.links_to_visit.append((self.base_url, 0))  # Comenzar desde la URL base con profundidad 0

        # Proceso de crawling
        while self.links_to_visit:
            url, depth = self.links_to_visit.pop(0)
            self.fetch_page(url, depth)
            self.save_state()

        print("Crawling completado.")

# Uso del bot
if __name__ == "__main__":
    bot = AdvancedBot()
    bot.crawl()
