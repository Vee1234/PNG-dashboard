import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon
import numpy as np
import scipy as sp
class Analyser:
    def __init__(self, data_address):
        pass
    def mean_coordinates(self, df: pd.DataFrame) -> tuple:
        '''This function calculates the mean latitude and longitude from the dataframe.'''
        mean_latitude = df['Latitude'].mean()
        mean_longitude = df['Longitude'].mean()
        return (mean_latitude, mean_longitude)
    
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
