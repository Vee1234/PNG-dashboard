import pandas as pd
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
       



    
 

      

 

    