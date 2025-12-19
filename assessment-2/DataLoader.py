import pandas as pd
import json
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import hashlib
from pathlib import Path
class DataLoader:
    def __init__(self):
        pass

    def load_data_from_json(self, data_address: str) -> dict:
        # Simulate loading data
        with open(data_address, 'r') as file:
            data = json.load(file)
        return data
    def cache_path(self, url:str):
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        cache_file = Path("cache") / f"{url_hash}.html"
        return cache_file
    
    def get_page(self, url):
        '''Retrieves HTML content from a URL, using
         caching to avoid redundant network requests.
         If the page has been accessed before,
         the cached version is used. If it is the first
         time, the page is cached and then used.'''
        cache_file = self.cache_path(url)
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as file:
                html_content = file.read()
            return html_content
        response = requests.get(url, timeout = 10)
        html_content = response.text
        if response.status_code == 200:
            with open(cache_file, 'w', encoding='utf-8') as file:
                file.write(html_content)
            return html_content


      




    def scrape_data_from_website(self, url: str) -> dict:
        # Simulate web scraping (placeholder)
        
        CACHE_DIR = Path("cache")
        CACHE_DIR.mkdir(exist_ok=True)
        self.cache_path(url)

        html = self.get_page(url)
        soup = BeautifulSoup(html, 'html.parser')
        label = soup.find("div", class_="speaker-number-value")
        results = {"language_id": None,
            "speaker_number_raw": None,
            "speaker_number_numeric": None,
            "speaker_number_type": None,
            "vitality_status": None,
            "speaker_year": None,
            "speaker_source": None,
            "speaker_confidence": None,
            "speaker_method": None,
            "speaker_url": None,
        }
        if not label:
            return results
        speaker_number_raw = label.text.strip()
        results["speaker_number_raw"] = speaker_number_raw

        return results

        