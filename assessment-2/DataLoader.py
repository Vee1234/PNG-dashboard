import pandas as pd
import json
from dataclasses import asdict
from bs4 import BeautifulSoup
import requests
import hashlib
from pathlib import Path
import time
from Result import Result
from requests.exceptions import ReadTimeout, RequestException
class DataLoader:
    def __init__(self):
        self.confidence_score_dict = {'source_category': {'primary': 0.9, 'secondary': 0.7, 'tertiary': 0.4 }, 
                                      'source_type': {'expert-curated': 0.1, 'community-curated': 0.05}, 
                                      'access_route': {'direct': 0, 'indirect': -0.1} }
        self.headers =  {
                        "User-Agent": (
                        "PapuanLanguagesResearchBot/1.0 "
                        "(academic research, non-commercial; "
                        "contact: ec25777@qmul.ac.uk)"
                        ),
                        "Accept-Language": "en",
                        "Accept": "text/html"
                        }

    def load_data_from_json(self, data_address: str) -> dict:
        # Simulate loading data
        with open(data_address, 'r') as file:
            data = json.load(file)
        return data
    
    def cache_path(self, url:str):
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        cache_file = Path("cache") / f"{url_hash}.html"
        return cache_file
    
    def write_df_to_csv(self, df: pd.DataFrame, file_path: str):
        df.to_csv(file_path, index=False)
    
    def get_page(self, url, retries: int = 3, timeout: int = 30) -> str:
        '''Retrieves HTML content from a URL, using
         caching to avoid redundant network requests.
         If the page has been accessed before,
         the cached version is used. If it is the first
         time, the page is cached and then used.'''
        cached_file = self.cache_path(url)
        if cached_file.exists():
            with open(cached_file, 'r', encoding='utf-8') as file:
                html_content = file.read()
            return html_content
        for attempt in range(retries):
            try:
                response = requests.get(url, headers = self.headers, timeout = timeout)
                response.raise_for_status()
                html_content = response.text
                with open(cached_file, 'w', encoding='utf-8') as file:
                    file.write(html_content)
                return html_content
            except ReadTimeout:
                print(f"Timeout occurred for {url}. Retrying {attempt + 1}/{retries}...")
                time.sleep(2)  # brief pause before retrying
            except RequestException as e:
                print(f"Request failed for {url}: {e}")
                time.sleep(2)
        print(f"Failed to retrieve {url} after {retries} attempts.")
        return None
          
    def orchestrate_data_scraping(self, df: pd.DataFrame) -> pd.DataFrame:
        list_of_languages_without_speaker_number = df['language'].tolist()
        results_list = []
        for row in df.itertuples():
            result = Result()
            result = asdict(result)
            result["language"] = row.language
            print(f'Scraping speaker number for language: {row.language}')    
            for link in row.links:
                url = link['url']         
                if 'endangeredlanguages.com' in url:
                    result["source_urls"].append(url)
                    result["speaker_number_raw"] = self.scrape_data_in_class_field_from_website(url, html_class_field = "speaker-number-value") 
                    result["speaker_source"] = 'endangeredlanguages.com'
                    result["source_category"] = 'secondary' 
                    result["source_type"] = 'expert-curated'
                    result["access_route"] = 'direct'
                    result["source_confidence"] = round(self.confidence_score_dict['source_category'][result["source_category"]] + self.confidence_score_dict['source_type'][result["source_type"]] + self.confidence_score_dict['access_route'][result["access_route"]],2)
                    break
                elif 'apics-online' in url:
                    result["source_urls"].append(url)
                    result["speaker_number_raw"] = self.scrape_data_in_class_field_from_website(url, html_class_field= "key", string_expression = "Number of speakers", attribute1 = "td", method_called_after_label_identified="find_next_sibling")
                    result["speaker_source"] = 'apics-online.info'
                    result["source_category"] = 'secondary' 
                    result["source_type"] = 'expert-curated'
                    result["access_route"] = 'direct'
                    result["source_confidence"] = round(self.confidence_score_dict['source_category'][result["source_category"]] + self.confidence_score_dict['source_type'][result["source_type"]] + self.confidence_score_dict['access_route'][result["access_route"]], 2)
                    break
                elif 'wikipedia.org' in url:
                    result["source_urls"].append(url)
                    result["speaker_number_raw"] = self.scrape_data_in_class_field_from_website(url, html_class_field= "infobox-label", string_expression = "Native speakers", attribute1 = "th", attribute2 = "td", method_called_after_label_identified="find_next_sibling")
                    result["speaker_source"] = 'wikipedia.org'
                    result["source_category"] = 'tertiary' 
                    result["source_type"] = 'community-curated'
                    result["access_route"] = 'direct'
                    result["source_confidence"] = round(self.confidence_score_dict['source_category'][result["source_category"]] + self.confidence_score_dict['source_type'][result["source_type"]] + self.confidence_score_dict['access_route'][result["access_route"]], 2)
                    break
            if result["speaker_number_raw"]: 
                list_of_languages_without_speaker_number.remove(row.language) 
            if result["speaker_number_raw"] == "Extinct":
                result = self.fill_columns_based_on_language_vitality("extinct", result)
            elif result["speaker_number_raw"] == "Dormant":
                result = self.fill_columns_based_on_language_vitality("dormant", result)
            results_list.append(result)
            speaker_data_df = pd.DataFrame(results_list)
            final_df = self.left_merge_data_frames(df, speaker_data_df)
        return final_df, list_of_languages_without_speaker_number
    
    def fill_columns_based_on_language_vitality(self, vitality_label:str, result_dict: dict) -> dict:
        result_dict["vitality_status"] = vitality_label.lower()
        result_dict["speaker_number_raw"] = None
        result_dict["speaker_number_numeric"] = None
        return result_dict
    
    def left_merge_data_frames(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        merged_df = pd.merge(df1, df2, how='left')
        return merged_df #write to file
        
    def scrape_data_in_class_field_from_website(self, url: str, html_class_field: str = None, string_expression: str= None, attribute1: str = "div", attribute2: str = None, method_called_after_label_identified: str= None) -> dict:
        # Simulate web scraping (placeholder)
        CACHE_DIR = Path("cache")
        CACHE_DIR.mkdir(exist_ok=True)
        self.cache_path(url)
        try:
            html = self.get_page(url)
            soup = BeautifulSoup(html, 'html.parser')    
            if self.check_for_word_in_text('extinct', soup):
                return "Extinct"
            elif self.check_for_word_in_text('dormant', soup):
                return "Dormant"
            if string_expression is None:
                label = soup.find(attribute1, class_ = html_class_field)
            elif method_called_after_label_identified == "find_next_sibling":
                label = None
                if attribute2 is None:
                    attribute2 = attribute1
                for attr in soup.find_all(attribute1, class_=html_class_field):
                    print(attr.get_text())
                    if string_expression in attr.get_text():
                        label = attr
                        next_sibling_html = label.find_next_sibling(attribute2)
                        speaker_number_raw = next_sibling_html.text.strip()
                        return speaker_number_raw
            if not label:
                return None
            speaker_number_raw = label.text.strip()
            return speaker_number_raw
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def check_for_word_in_text(self, word:str, soup: str) -> bool:
        word = word.lower()
        word_present = soup.find(string=lambda text: word in text.lower())
        if word_present:
            return True
        return False
    
        
        