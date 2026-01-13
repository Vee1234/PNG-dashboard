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
        self.HEADERS =  {
                        "User-Agent": (
                        "PapuanLanguagesResearchBot/1.0 "
                        "(academic research, non-commercial; "
                        "contact: ec25777@qmul.ac.uk)"
                        ),
                        "Accept-Language": "en",
                        "Accept": "text/html"
                        }

    def load_data_from_json(self, data_address: str) -> dict:
        '''Loads data in dictionary form from a JSON file located at data_address.'''
        with open(data_address, 'r') as file:
            data = json.load(file)
        return data

    def load_data_from_csv(self, data_address: str) -> pd.DataFrame:
        df = pd.read_csv(data_address)
        return df
    
    def add_new_row_to_dataframe(self, df: pd.DataFrame, new_row: dict) -> pd.DataFrame:
        '''Adds a new row to the DataFrame and writes the updated DataFrame to a CSV file.'''
        new_row_df = pd.DataFrame([new_row])
        updated_df = pd.concat([df, new_row_df], ignore_index=True)
        self.write_df_to_csv(updated_df, 'data/language_speaker_data.csv')
        return updated_df
    
    def cache_path(self, url:str):
        '''Generates a cache file path based on the MD5 hash of the URL.'''
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
                response = requests.get(url, headers = self.HEADERS, timeout = timeout)
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
          
    def orchestrate_data_scraping_per_domain_name(self, df: pd.DataFrame, domain_name: str, speaker_number_html_field: str, source_category: str, source_type: str, access_route: str, attribute1: str = None, attribute2: str = None, string_expression: str = None, method_called_after_label_identified: str= None, preference_list: list = ['endangeredlanguages.com', 'apics-online.info', 'wikipedia.org']) -> pd.DataFrame:
        """
        Orchestrates the scraping of speaker number data for a specific domain name from a DataFrame of languages.

        Args:
            df (pd.DataFrame): DataFrame containing language data, including 'language' and 'links' columns.
            domain_name (str): The domain name to prioritize for scraping.
            speaker_number_html_field (str): HTML class field to locate speaker number data.
            source_category (str): Category of the data source.
            source_type (str): Type of the data source.
            access_route (str): Route used to access the data source.
            attribute1 (str, optional): Primary HTML tag for filtering. Defaults to None.
            attribute2 (str, optional): Secondary HTML attribute for filtering. Defaults to None.
            string_expression (str, optional): String expression to refine the search. Defaults to None.
            method_called_after_label_identified (str, optional): Method to call on the identified label. Defaults to None.
            preference_list (list, optional): Ordered list of preferred domains for scraping. Defaults to ['endangeredlanguages.com', 'apics-online.info', 'wikipedia.org'].

        Processes:
            - Iterates through each row in the DataFrame.
            - Checks if the domain name is present in the links for each language.
            - Scrapes speaker number data from the specified domain if it is higher in the preference list or no source is set.
            - Updates the result dictionary with scraped data, source URLs, and the domain name."""

        list_of_languages_without_speaker_number = df['language'].tolist()
        results_list = []

        for row in df.itertuples():
            result = Result()
            result = asdict(result)
            result["language"] = row.language  

            for link in row.links:
                url = link['url']         
                if domain_name in url and (preference_list.index(result["speaker_source"])>preference_list.index(domain_name) or result["speaker_source"] == None):
                    result["speaker_number_raw"] = self.scrape_data_in_class_field_from_website(url, html_class_field = speaker_number_html_field, string_expression= string_expression, attribute1 = attribute1, attribute2 = attribute2, method_called_after_label_identified= method_called_after_label_identified)
                    result["source_urls"].clear()
                    result["source_urls"].append(url)
                    result["speaker_source"] = domain_name
                    result["source_category"] = source_category
                    result["source_type"] = source_type
                    result["access_route"] = access_route
                    
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
        '''Fills the result dictionary with specific values based on the language vitality status.'''
        result_dict["vitality_status"] = vitality_label.lower()
        result_dict["speaker_number_raw"] = None
        result_dict["speaker_number_numeric"] = None
        return result_dict
    
    def left_merge_data_frames(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        merged_df = pd.merge(df1, df2, how='left')
        return merged_df #write to file
        
    def scrape_data_in_class_field_from_website(self, url: str, html_class_field: str = None, string_expression: str= None, attribute1: str = "div", attribute2: str = None, method_called_after_label_identified: str= None) -> dict:
        """
        Scrapes data from a webpage based on specified HTML attributes and class fields.

        Args:
            url (str): The URL of the webpage to scrape.
            html_class_field (str, optional): The HTML class to locate the target element. Defaults to None.
            string_expression (str, optional): A string expression to refine the search. Defaults to None.
            attribute1 (str, optional): The primary HTML tag to search for. Defaults to "div".
            attribute2 (str, optional): A secondary HTML attribute for further filtering. Defaults to None.
            method_called_after_label_identified (str, optional): A method to call on the identified label (e.g., "find_next_sibling"). Defaults to None.

        Returns:
            dict: A dictionary containing the scraped data or a status string ("Extinct" or "Dormant") if specific keywords are found.
        """

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
    
        
        