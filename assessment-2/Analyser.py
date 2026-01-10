import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, shape
import numpy as np
import scipy as sp
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
    
