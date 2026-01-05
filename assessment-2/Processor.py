import pandas as pd
import geopandas as gpd
import math
import re
class Processor:
    def __init__(self):
        self.multipliers = {'million': 1000000, 'thousand': 1000}
        pass
       
    def convert_json_to_df(self, json_data:dict, highest_field_name: str) -> pd.DataFrame:
        '''This function creates a pandas dataframe from the json data.'''
        df = pd.json_normalize(
        json_data[highest_field_name],
        record_path=None,
        meta=None,
        )
        return df
    def round_sf(x, sig=4):
        if x == 0:
            return 0
        else:
            return round(x, sig - int(math.floor(math.log10(abs(x)))) - 1)
    
    def rename_columns(self, df: pd.DataFrame, columns_mapping: dict) -> pd.DataFrame:
        '''This function renames the columns of the dataframe.'''
        renamed_df = df.rename(columns=columns_mapping)
        return renamed_df
    
    def create_new_dataframe_with_selected_columns(self, df: pd.DataFrame, selected_columns: list) -> pd.DataFrame:
        new_df = df[selected_columns].copy()
        return new_df
    
    def remove_data(self, df: pd.DataFrame, column_name, condition) -> pd.DataFrame:
        try:
            df = df.drop(df[df[column_name] == condition].index)
            return df
        except KeyError:
            print(f"Column '{column_name}' does not exist in the DataFrame.")
            return df
    def replace_regex_character(self, df: pd.DataFrame, original_regex: str, replacement_character: str) -> pd.DataFrame:
        df = df.replace(
        {rf'{original_regex}': replacement_character},
        regex=True
        )
        return df
  
    def convert_geojson_to_gpd(self, df: pd.DataFrame):
        gdf = gpd.read_file("PNG_all_languages_coordinate_data.geojson")
        print(gdf)
    
    def replace_url_in_values_in_column(self, df: pd.DataFrame, expression: str, to_be_replaced: str = '') -> pd.DataFrame:
        for link_list in df['links']:
            for link in link_list:              
                link['url'] = link['url'].replace(expression, to_be_replaced)
        return df           

    def replace_expression_in_values_in_column(self, df: pd.DataFrame, column, expression: str, to_be_replaced: str = '') -> pd.DataFrame:
        '''This function removes a specific expression from all values in a specified column of the dataframe.'''
        df[column]= df[column].str.replace(expression, to_be_replaced)     
        return df
    
    def extract_numeric_speaker_number(self, df: pd.DataFrame) -> int:
        df['speaker_number_raw'] = self.remove_commas(df, 'speaker_number_raw')
        mask_before_cited = (
        df['speaker_number_raw']
        .str.lower()
        .str.split('cited', n=1)
        .str[0]
        .str.contains(r'(\d{1,5})', na=False)
        )

        mask_after_cited = (
        df['speaker_number_raw']
        .str.lower()
        .str.split('cited', n=1)
        .str[1]
        .str.contains(r'(\d{1,5})', na=False)
        )

        
        # Extract numeric values before 'cited'
        df.loc[mask_before_cited, 'speaker_number_numeric'] = (
        df.loc[mask_before_cited, 'speaker_number_raw']
        .str.lower()
        .str.split('cited', n=1)
        .str[0]
        .str.extract(r'(\d{1,5})')[0]
        .astype('Int64')
        )

        # Extract numeric values after 'cited'
        df.loc[mask_after_cited, 'speaker_number_year'] = (
        df.loc[mask_after_cited, 'speaker_number_raw']
        .str.lower()
        .str.split('cited', n=1)
        .str[1]
        .str.extract(r'(\d{1,5})')[0]
        .astype('Int64')
        )       

            #number_of_speakers = int(re.search(r'(\d{2,})', raw_value).group()) #first value in the expression is the number of speakers
            #row['speaker_number_numeric'] =  number_of_speakers
                #df.at[index, 'speaker_number_numeric'] = self.remove_commas(raw_value)
            
            
        return df
        
    def remove_commas(self, df: pd.DataFrame, column_name: str) -> str:
        return df[column_name].astype(str).str.replace(',', '')

        

       



    
 

      

 

    