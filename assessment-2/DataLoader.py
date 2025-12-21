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

    def orchestrate_data_scraping(self, df: pd.DataFrame) -> pd.DataFrame:
        list_of_languages_without_speaker_number = df['language'].tolist()
        results_list = []
        for row in df.itertuples():
            result = {"language": None, #from df
            "speaker_number_raw": None, #from scraping, though some languages are yet to be scraped
            "speaker_number_numeric": None, #will need to process raw to get numeric
            "speaker_number_type": None,
            "vitality_status": None,
            "vitality_confidence": None, #will need to scrape by running through possible options and checking if they are in the html
            "speaker_year": None,
            "speaker_source": None,
            "speaker_method": None,
            "source_url": []}
            result["language"] = row.language
        
            for link in row.links:
                url = link['url']         
                if 'endangeredlanguages.com' in url:
                    result["source_url"].append(url)
                    result["speaker_number_raw"] = self.scrape_data_from_class_field_from_website(url, html_class_field = "speaker-number-value")
                
                elif 'apics-online' in url:
                    result["source_url"].append(url)
                    result["speaker_number_raw"] = self.scrape_data_in_class_field_from_website(url, html_class_field= "key", string_expression = "Number of speakers", attribute = "td", method_called_after_label_identified="find_next_sibling")
                if result["speaker_number_raw"]: 
                    list_of_languages_without_speaker_number.remove(row.language)
                   
            results_list.append(result)
            speaker_data_df = pd.DataFrame(results_list)
            final_df = self.left_merge_data_frames(df, speaker_data_df)
        return final_df
                    
    def left_merge_data_frames(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        merged_df = pd.merge(df1, df2, how='left')
        return merged_df #write to file
        
    def scrape_data_in_class_field_from_website(self, url: str, html_class_field: str = None, string_expression: str= None, attribute: str = "div", method_called_after_label_identified: str= None) -> dict:
        # Simulate web scraping (placeholder)
        
        CACHE_DIR = Path("cache")
        CACHE_DIR.mkdir(exist_ok=True)
        self.cache_path(url)


        html = self.get_page(url)
        soup = BeautifulSoup(html, 'html.parser')
        label = soup.find(attribute, class_ = html_class_field , string =  string_expression)
        if method_called_after_label_identified == "find_next_sibling":
            next_sibling_html = label.find_next_sibling(attribute)
            speaker_number_raw = next_sibling_html.text.strip()
            return speaker_number_raw
        if not label:
            return None
        speaker_number_raw = label.text.strip()
        return speaker_number_raw

        