import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
class Visualiser:
    def __init__(self):
        pass
    def add_hover(self, data, map):
        folium.GeoJson(
            data,
            tooltip=folium.GeoJsonTooltip(
                fields=["language", "Language ID"],
                aliases=["Language:", "Language ID"]
        )).add_to(map)
    def create_map(self, df, location: tuple = (-5, 149), zoom_start: int = 4) -> folium.Map:
        # Create a folium map object
        map = folium.Map(location=location, zoom_start=zoom_start, scrollWheelZoom=False, tiles='OpenStreetMap')
        return map
    
    def add_points_to_map(self, df: pd.DataFrame, map: folium.Map) -> folium.Map:
        for idx, row in df.iterrows():
            folium.Circle(
                location=[row['Latitude'], row['Longitude']],
                color="black",
                popup=row['Language'],
                radius=6000,
                stroke = False,
                fill = True,
                opacity = 1,

            ).add_to(map)

    def display_map(self, map: folium.Map):
        # Save the map to an HTML file
        map.save("map.html")
        # Display the map in Streamlit
        st.components.v1.html(open("map.html", "r").read(), width=700, height=450)

    def add_voronoi_to_map(self, vor_web, map: folium.Map) -> folium.Map:
        folium.Choropleth(
            geo_data=vor_web,
            data=vor_web,
            columns=["Language", "Language ID"],
            key_on="Language",
            fill_color="YlOrRd",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name="Number of Speakers"
        ).add_to(map)
        
    def trial_chloropleth(self, df, map):
        folium.Choropleth(
            geo_data='data/pg.json',
            data=df,
            columns=["Language", "Language ID"],
            key_on="Language",
            fill_color="YlOrRd",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name="Number of Speakers"
        ).add_to(map) 
    def trial_outline(self, map, coordinates):
        folium.Polygon(
            locations=coordinates,
            color="blue",
            fill=False
        ).add_to(map) 
        
    
        
            
        

  
    
