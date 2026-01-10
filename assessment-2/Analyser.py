import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, shape
import numpy as np
import scipy as sp
class Analyser:
    def __init__(self):
        self.source_confidence_dict = {'source_category': {'primary': 1, 'secondary': 0.75, 'tertiary': 0.5}, 
                                      'source_type': {'expert-curated': 1, 'community-curated': 0.75}, 
                                      'speaker_number_type': {'exact': 1, 'estimate': 0.75, 'range': 0.5, 'qualitative estimate': 0.25, 'qualitative range': 0.25},
                                      'access_route': {'direct': 1, 'indirect': 0.5} }
    def midpoint_coordinates(self, df: pd.DataFrame) -> tuple:
        '''This function calculates the mean latitude and longitude from the dataframe.'''
        mid_latitude = ((df['latitude'].max() + df['latitude'].min())) / 2
        mid_longitude = ((df['longitude']).max() + df['longitude'].min()) / 2
        return (mid_latitude, mid_longitude)
    def calculate_source_confidence(self,row):
        if pd.notna(row["source_category"]) and pd.notna(row["source_type"]) and pd.notna(row["access_route"]) and pd.notna(row['speaker_number_type']):
            row["source_confidence"] = round(self.source_confidence_dict['source_category'][row["source_category"]] * self.source_confidence_dict['source_type'][row["source_type"]] * self.source_confidence_dict['access_route'][row["access_route"]] * self.source_confidence_dict['speaker_number_type'][row['speaker_number_type']],2)
        else:
            row["source_confidence"] = None
        return row
    def calculate_min_and_max_for_not_ranges(self, row):
        if row['speaker_number_type'] == 'exact':
            row['speaker_number_min'] = row['speaker_number_numeric']
            row['speaker_number_max'] = row['speaker_number_numeric']
        if row['speaker_number_type'] == 'estimate' or row['speaker_number_type'] == 'qualitative estimate':
            row['speaker_number_min'] = row['speaker_number_numeric'] * (1-(1- row["source_confidence"]))
            row['speaker_number_max'] = row['speaker_number_numeric'] * (1+ (1- row["source_confidence"]))
        if  row['speaker_number_type'] == 'qualitative range':
            row['speaker_number_max'] = row['speaker_number_max'] * (1+ (1- row["source_confidence"]))
        if row['vitality_status'] == 'extinct' or row['vitality_status'] == 'dormant':
            row['speaker_number_min'] = 0
            row['speaker_number_max'] = 0

        return row
   
    def create_geometry(self, df):
        geometry = [Point(xy) for xy in zip(df['Longitude'], df['Latitude'])]
        return geometry
    
    def convert_df_to_gdf(self, df: pd.DataFrame, geometry: list) -> gpd.GeoDataFrame:
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs= "EPSG:4326")
        return gdf
    def project_gdf(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:   
        gdf_proj = gdf.to_crs(epsg=32754)
        return gdf_proj

    def generate_voronoi_diagram(self, projected_gdf: gpd.GeoDataFrame, geometry: list) -> gpd.GeoDataFrame:
        points = np.array([[point.x, point.y] for point in geometry])
        vor = sp.spatial.Voronoi(points)
        polygons = []
        for region in vor.regions:
            if not -1 in region and len(region) > 0:
                polygon = Polygon([vor.vertices[i] for i in region])
                polygons.append(polygon)
        print(f'length of polygons: {len(polygons)}')
        print(f'length of projected_gdf: {len(projected_gdf)}')
        voronoi_gdf = gpd.GeoDataFrame(data= projected_gdf, geometry=polygons, crs=projected_gdf.crs)
        voronoi_gdf = voronoi_gdf[voronoi_gdf.geometry.notnull()]
        return voronoi_gdf
    
    def fit_cells_in_country_boundary(self, voronoi_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        region = gpd.read_file("geoBoundaries-PNG-ADM2_simplified.geojson").to_crs(voronoi_gdf.crs)
        vor_clipped = gpd.clip(voronoi_gdf, region)
        return vor_clipped
    
    def reproject_gdf_to_wgs84(self, vor_clipped: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        vor_web = vor_clipped.to_crs(epsg=4326)
        return vor_web
   
    def create_voronoi_chloropleth(self, df):
        geometry = self.create_geometry(df)
        gdf = self.convert_df_to_gdf(df, geometry)
        projected_gdf = self.project_gdf(gdf)
        voronoi_gdf = self.generate_voronoi_diagram(projected_gdf, geometry)
        vor_clipped = self.fit_cells_in_country_boundary(voronoi_gdf)
        print(f'vor_clipped{vor_clipped}')
        vor_web = self.reproject_gdf_to_wgs84(vor_clipped)
        print(f'vor_web{vor_web}')
        return vor_web
    
    def build_province_language_mapping(self, boundaries_data, language_df):
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