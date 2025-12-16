import geopandas as gpd
import pandas as pd
class Analyser:
    def __init__(self, data_address):
        pass
    def mean_coordinates(self, df: pd.DataFrame) -> tuple:
        '''This function calculates the mean latitude and longitude from the dataframe.'''
        mean_latitude = df['Latitude'].mean()
        mean_longitude = df['Longitude'].mean()
        return (mean_latitude, mean_longitude)