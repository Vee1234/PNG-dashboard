import pandas as pd
import shapel

class Analyser:
    def __init__(self):
        self.SOURCE_CONFIDENCE_DICT = {'source_category': {'primary': 1, 'secondary': 0.75, 'tertiary': 0.5}, 
                                      'source_type': {'expert-curated': 1, 'community-curated': 0.75}, 
                                      'speaker_number_type': {'exact': 1, 'estimate': 0.75, 'range': 0.5, 'qualitative estimate': 0.25, 'qualitative range': 0.25},
                                      'access_route': {'direct': 1, 'indirect': 0.5} }
        
    def midpoint_coordinates(self, df: pd.DataFrame) -> tuple:
        '''This function calculates the midpoint of the latitude and longitude from the dataframe.'''
        mid_latitude = ((df['latitude'].max() + df['latitude'].min())) / 2
        mid_longitude = ((df['longitude']).max() + df['longitude'].min()) / 2
        return (mid_latitude, mid_longitude)
    
    def calculate_source_confidence(self,row):
        """
        Calculates the source confidence score based on predefined weights for various attributes.

        Args:
            row (pd.Series): A row of data containing source-related attributes.

        Returns:
            pd.Series: Updated row with the 'source_confidence' value.
        """

        if pd.notna(row["source_category"]) and pd.notna(row["source_type"]) and pd.notna(row["access_route"]) and pd.notna(row['speaker_number_type']):
            row["source_confidence"] = round(self.SOURCE_CONFIDENCE_DICT['source_category'][row["source_category"]] * self.source_confidence_dict['source_type'][row["source_type"]] * self.source_confidence_dict['access_route'][row["access_route"]] * self.source_confidence_dict['speaker_number_type'][row['speaker_number_type']],2)
        else:
            row["source_confidence"] = None
        return row
    
    def calculate_min_and_max_for_not_ranges(self, row):
        '''-Calculates min and max speaker numbers for non-range types.
        - If vitality status is extinct or dormant, sets min and max to 0.
        -Estimates min and max bounds for estimates and qualitative estimates using source confidence.
        - '''
        one_minus_confidence = 1 - row["source_confidence"]
        if row['speaker_number_type'] == 'exact':
            row['speaker_number_min'] = row['speaker_number_numeric']
            row['speaker_number_max'] = row['speaker_number_numeric']

        elif row['speaker_number_type'] == 'estimate' or row['speaker_number_type'] == 'qualitative estimate':
            row['speaker_number_min'] = row['speaker_number_numeric'] *  row["source_confidence"]
            row['speaker_number_max'] = row['speaker_number_numeric'] * (1+ one_minus_confidence)

        elif  row['speaker_number_type'] == 'qualitative range':
            row['speaker_number_max'] = row['speaker_number_max'] * (1+ one_minus_confidence)

        elif row['vitality_status'] == 'extinct' or row['vitality_status'] == 'dormant':
            row['speaker_number_min'] = 0
            row['speaker_number_max'] = 0

        return row

    def build_province_language_mapping(self, boundaries_data: dict, language_df: pd.DataFrame) -> pd.DataFrame:
        '''This function builds a mapping of provinces to the number of languages spoken in each province.
        -OUTPUT: DataFrame with columns 'Province', 'Number of Languages', 'Languages List'''

        df = pd.DataFrame(columns=['Province', 'Number of Languages', 'Languages List'])
        for feature in boundaries_data['features']:
                polygon = shape(feature['geometry'])
                for index, row in language_df.iterrows():
                    language = row['language']
                    longitude = row['longitude']
                    latitude = row['latitude']
                    point = Point(longitude, latitude) 
                    if polygon.contains(point):
                        if feature['properties']['shapeName'] not in df['Province'].values:
                            new_row =pd.DataFrame([{
                                'Province': feature['properties']['shapeName'],
                                'Number of Languages': 0,
                                'Languages List': []
                            }])
                            df = pd.concat([df, new_row], ignore_index=True)
                        province_index = df.index[df['Province'] == feature['properties']['shapeName']][0]
                        df.at[province_index, "Number of Languages"] += 1
                        df.at[province_index, "Languages List"].append(language)    
                            
                    else:
                        continue
        return df
    
    def create_plotting_data_column(self, df: pd.DataFrame) -> pd.DataFrame:
        '''Creates a plotting data column for the dataframe. 
        Used for visualisations where a single numerical value is required for each language, e.g., bar charts'''
        df = df.apply(self.calculate_min_and_max_for_not_ranges, axis=1)
        df["plotting_data"] = None 
        df["speaker_number_min"] = pd.to_numeric(df["speaker_number_min"], errors="coerce")
        df["speaker_number_max"] = pd.to_numeric(df["speaker_number_max"], errors="coerce")
        df["speaker_number_numeric"] = pd.to_numeric(df["speaker_number_numeric"], errors="coerce")

        # Case 1: range → midpoint

        df.loc[df["speaker_number_type"] == "range", "plotting_data"] = (
            (df["speaker_number_min"] + df["speaker_number_max"]) / 2
        )

        # Case 2: extinct or dormant → value below minimum
        df.loc[df["vitality_status"].isin(["extinct", "dormant"]), "plotting_data"] = df["speaker_number_numeric"].min()-0.5
        

        # Case 3: exact → numeric
        df.loc[df["speaker_number_type"] == "estimate", "plotting_data"] = df["speaker_number_numeric"]
        df.loc[df["speaker_number_type"] == "exact", "plotting_data"] = df["speaker_number_numeric"]
        df.loc[df["speaker_number_type"] == "qualitative estimate", "plotting_data"] = df["speaker_number_numeric"]
        df.loc[df["speaker_number_type"] == "qualitative range", "plotting_data"] = (
            (df["speaker_number_min"] + df["speaker_number_max"])/ 2)
    
        return df

            
    def create_tooltip_column_for_barchart(self, df) -> pd.DataFrame:
        '''This function creates a tooltip column for the dataframe.'''

        df["bar_chart_tooltip_value"] = pd.NA  # start with empty column

        df.loc[df["speaker_number_type"] == "range", "bar_chart_tooltip_value"] = (
            df["speaker_number_raw"]
        )
        df.loc[df["speaker_number_type"] == "estimate", "bar_chart_tooltip_value"] = (
            df["speaker_number_raw"]
        )
        df.loc[df["speaker_number_type"] == "qualitative range", "bar_chart_tooltip_value"] = (
            df["speaker_number_raw"]
        )
        df.loc[df["speaker_number_type"] == "qualitative estimate", "bar_chart_tooltip_value"] = (
            df["speaker_number_raw"]
        )
        df.loc[df["speaker_number_type"] == "exact", "bar_chart_tooltip_value"] = (
            df["speaker_number_numeric"]
        )
        df.loc[df["vitality_status"].isin(["extinct", "dormant"]), "bar_chart_tooltip_value"] = (
            df["vitality_status"]
        )
        return df 

        
        
        


        

       



    
 

      

 

    
    
