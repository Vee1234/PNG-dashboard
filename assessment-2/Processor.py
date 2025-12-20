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
                print(link['url'])
                link['url'] = link['url'].replace(expression, to_be_replaced)
                print(link['url'])
            
       

    def replace_expression_in_values_in_column(self, df: pd.DataFrame, column, expression: str, to_be_replaced: str = '') -> pd.DataFrame:
        '''This function removes a specific expression from all values in a specified column of the dataframe.'''
        df[column]= df[column].str.replace(expression, to_be_replaced)     
        return df

        

       



    
 

      

 

    