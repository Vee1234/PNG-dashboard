import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import altair as alt
class Visualiser:
    def __init__(self):
        pass

    def create_map(self, df, location: tuple = (-5, 149), zoom_start: int = 6) -> folium.Map:
        # Create a folium map object
        map = folium.Map(location=location, zoom_start=zoom_start, scrollWheelZoom=False, tiles='OpenStreetMap')
        return map
    
    def structure_popup(self, row) -> str:
        lines = []

        if pd.notna(row["language"]):
            lines.append(f"<b>Language:</b> {row['language']}")

        if pd.notna(row["speaker_number_numeric"]) and row["speaker_number_type"] == 'exact':
            lines.append(f"<b>Speakers:</b> {int(row['speaker_number_numeric'])}")
        
        if row["speaker_number_type"] == 'range' or row["speaker_number_type"] == 'estimate' or row["speaker_number_type"] == 'qualitative range' or row["speaker_number_type"] == 'qualitative estimate':
            lines.append(f"<b>Speakers:</b> {row['speaker_number_raw']}")

        if pd.notna(row["speaker_number_year"]):
            lines.append(f"<b>Year Cited:</b> {row['speaker_number_year']}")
        
        if pd.notna(row['vitality_status']):
            lines.append(f"<b>Vitality Status:</b> {row['vitality_status']}")
        
        if pd.notna(row['source_confidence']):
            lines.append(f"<b>Confidence Score:</b> {row['source_confidence']}")

        if pd.notna(row['speaker_number_type']):
            lines.append(f"<b>Speaker Number Type:</b> {row['speaker_number_type']}")
        
        if pd.notna(row['speaker_source']):
            lines.append(f"<b>Source:</b> {row['speaker_source']}")
    
        return "<br>".join(lines)
    
    def show_logarithmic_bar_graph(self, df: pd.DataFrame):
        df_plot = df[df["plotting_data"].notna()]
        
        chart = (
            alt.Chart(df_plot)
            .mark_bar()
            .encode(
                y=alt.Y("language:N", sort="-x", title="Language"),
                x=alt.X(
                    "plotting_data:Q",
                    scale=alt.Scale(type="log"),
                    title="Number of speakers (log scale)"
                ),
                color=alt.condition(
                    alt.datum.speaker_status == "extinct",
                    alt.value("lightgray"),
                    alt.value("steelblue")
                ),
                tooltip=[
                    alt.Tooltip("language:N", title="Language"),
                    alt.Tooltip("bar_chart_tooltip_value:N", title="Actual speakers"),
                ]
            )
        )



        st.altair_chart(chart, use_container_width=True)

    def add_points_to_map(self, df: pd.DataFrame, map: folium.Map) -> folium.Map:
        for idx, row in df.iterrows():
            folium.Circle(
                location=[row['latitude'], row['longitude']],
                color="black",
                tooltip= folium.Tooltip(self.structure_popup(row), max_width=300), #what is the correct syntax to have multple pieces of info in the popup?
                radius=6000,
                stroke = False,
                fill = True,
                opacity = 1,

            ).add_to(map)

    def display_map(self, map: folium.Map):
        # Save the map to an HTML file
        map.save("map.html")
        # Display the map in Streamlit
        st.components.v1.html(open("map.html", "r").read(), width=1500, height=1200)

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
        
    
        
            
        

  
    
