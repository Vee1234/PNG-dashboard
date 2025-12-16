import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
class Visualiser:
    def __init__(self):
        pass
    def create_map(self, df, location: tuple = (-5, 149), zoom_start: int = 4) -> folium.Map:
        # Create a folium map object
        map = folium.Map(location=location, zoom_start=zoom_start, scrollWheelZoom=False, tiles='OpenStreetMap')
        return map
    
    def add_points_to_map(self, df: pd.DataFrame, map: folium.Map) -> folium.Map:
        for idx, row in df.iterrows():
            folium.Circle(
                location=[row['Latitude'], row['Longitude']],
                popup=row['Language Name'],
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(map)

    def display_map(self, map: folium.Map):
        # Save the map to an HTML file
        map.save("map.html")
        # Display the map in Streamlit
        st.components.v1.html(open("map.html", "r").read(), width=700, height=450)
        
    
        
            
        

  
    
