import pandas as pd
import geopandas as gpd
import re
class Processor:
    def __init__(self):
        pass
       
    def convert_json_to_df(self, json_data:dict, highest_field_name: str) -> pd.DataFrame:
        '''This function creates a pandas dataframe from the json data.'''
        df = pd.json_normalize(
        json_data[highest_field_name],
        record_path=None,
        meta=None,
        )
        return df
    
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
        for index, row in df.iterrows():
            raw_value = row['speaker_number_raw']
            if pd.isna(raw_value):
                continue
            raw_value = str(raw_value)
            if ',' in raw_value:
                df.at[index, 'speaker_number_numeric'] = self.remove_commas(raw_value)
            
        return df
        
    def remove_commas(self, number_str: str) -> str:
        return number_str.replace(',', '')

        

       



    
 

      

 

    