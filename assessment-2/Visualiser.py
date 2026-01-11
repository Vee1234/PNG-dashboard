import streamlit as st
import pandas as pd
import folium
from folium import Element
import numpy as np
import altair as alt
from folium.plugins import MarkerCluster
import math
from Analyser import Analyser
class Visualiser:
    def __init__(self):
        self.analyser = Analyser()
        self.MIN_POWER_OF_TEN = -1.0
        self.ICON_CREATE_FUNCTION =  """
        function(cluster) {
        var count = cluster.getChildCount();
        var color = count <10 ? 'yellow' :
                count <80 ? 'orange' :
                'red';
        var size = 20 + Math.log(count) * 15;

        return new L.DivIcon({
            html: '<div style="width:' + size + 'px; height:' + size +
                'px; line-height:' + size +
                'px; border-radius:50%; background-color:' + color + '; color:black; text-align:center;">' +
                '<span>' + count + '</span></div>',
            className: 'marker-cluster',
            iconSize: new L.Point(size, size)
        });
        }
        """
        self.LEGEND_HTML = """
        <div style="
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 9999;
            background-color: white;
            padding: 12px 16px;
            border-radius: 6px;
            box-shadow: 0 0 10px rgba(0,0,0,0.25);
            font-size: 14px;
            line-height: 1.4;
        ">
        <b>Number of speakers</b><br><br>

        <span style="display:inline-block;
                    width:14px;
                    height:14px;
                    background-color:black;
                    border-radius:50%;
                    margin-right:6px;"></span>
        Extinct/Dormant<br>

        <span style="display:inline-block;
                    width:14px;
                    height:14px;
                    background-color:green;
                    border-radius:50%;
                    margin-right:6px;"></span>
        Very Low (<100)<br>

        <span style="display:inline-block;
                    width:14px;
                    height:14px;
                    background-color:yellow;
                    border-radius:50%;
                    margin-right:6px;"></span>
        Low (100-999)<br>

        <span style="display:inline-block;
                    width:14px;
                    height:14px;
                    background-color:orange;
                    border-radius:50%;
                    margin-right:6px;"></span>
        Medium (1,000-9,999 )<br>

        <span style="display:inline-block;
                    width:14px;
                    height:14px;
                    background-color:red;
                    border-radius:50%;
                    margin-right:6px;"></span>
        High (10,000-99,999)<br>

        <span style="display:inline-block;
                    width:14px;
                    height:14px;
                    background-color:darkred;
                    border-radius:50%;
                    margin-right:6px;"></span>
        Very High (>= 100,00)<br>

        </div>
        """


    def show_title(self, title: str):
        st.title(title)

    def create_map(self, header, caption, location: tuple = (-5, 149), zoom_start: int = 6) -> folium.Map:
        '''Creates a folium map object with specified header, caption, location, and zoom level.'''
        st.header(header)
        st.subheader(caption)
        map = folium.Map(location=location, zoom_start=zoom_start, scrollWheelZoom=False, tiles='OpenStreetMap')
        return map
    
    def structure_popup(self, row) -> str:
        """
        Generates an HTML string for a popup tooltip based on the data in a given row.

        Args:
            row (pd.Series): A pandas Series object containing data for a specific language.

        Returns:
            str: An HTML-formatted string displaying language details, including:
                - Language name
                - Number of speakers (exact, range, or estimate)
                - Year cited
                - Vitality status
                - Confidence score
                - Speaker number type
                - Source of the data
        """

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
   
    def display_filtered_map(self, df, map) -> pd.DataFrame:
        """
        Displays a filtered map of languages based on speaker numbers.

        Args:
            df (pd.DataFrame): DataFrame containing language data.
            map (folium.Map): Folium map object to display the data.

        Returns:
            pd.DataFrame: Filtered DataFrame based on user-selected speaker number range.
        """
        map.get_root().html.add_child(Element(self.LEGEND_HTML))
        max_power_of_ten = float(math.ceil(math.log10(df['speaker_number_max'].max())))
        min_power_of_ten = self.MIN_POWER_OF_TEN

        try:
            with st.sidebar:
                st.header("Filter Languages by Speaker Number")
                user_min, user_max = st.slider(
                "Number of speakers",
                min_value=min_power_of_ten,
                max_value=max_power_of_ten,
                value=(min_power_of_ten, max_power_of_ten),
                label_visibility="hidden",
                help="Select the range of number of speakers to display on the map."
                )
                st.markdown("Logarithmic scale")

                if user_min == min_power_of_ten:
                    user_min = 0
                else: 
                    user_min = 10**user_min

                user_max = 10**user_max
                st.markdown(f"**Selected range:** {'{:,}'.format(int(user_min))} to {'{:,}'.format(int(user_max))} speakers")
          
            filtered_values = np.where((df['speaker_number_max']>=user_min) & (df['speaker_number_min']<=user_max))
            filtered_df = df.loc[filtered_values]
    
            cluster = folium.plugins.MarkerCluster(disableClusteringAtZoom=11, icon_create_function=self.ICON_CREATE_FUNCTION)
            self.add_points_to_cluster(filtered_df, cluster)
            cluster.add_to(map)
            return filtered_df

        except Exception as e:
            st.error(e)
        

    def show_logarithmic_bar_graph(self, df: pd.DataFrame):
        df_plot = df[df["plotting_data"].notna()]
        st.header("Number of Speakers per Language")
        st.write("Bar chart showing the number of speakers for each language on a logarithmic scale. Languages marked in red are classified as extinct.")
        
        chart = (
            alt.Chart(df_plot)
            .mark_bar()
            .encode(
                y=alt.Y("language:N", sort="-x", title="Language"),
                x=alt.X(
                    "plotting_data:Q",
                    scale=alt.Scale(type="log"),
                    title="Number of speakers (log scale)",
                    stack=None
                ),
                color=alt.condition(
                    alt.datum.vitality_status == "extinct",
                    alt.value("red"),
                    alt.value("steelblue")
                ),
                tooltip=[
                    alt.Tooltip("language:N", title="Language"),
                    alt.Tooltip("bar_chart_tooltip_value:N", title="Actual speakers"),
                ]
            )
        )

        st.altair_chart(chart, width= 'stretch')

    def assign_colour_based_on_speaker_number(self, df, idx) -> pd.DataFrame:
        speaker_number = df.at[idx, 'plotting_data'] 
        vitality_status = df.at[idx, 'vitality_status']
        
        if pd.isna(speaker_number) and pd.isna(vitality_status):
            return "gray"
        elif vitality_status == 'extinct' or vitality_status == 'dormant':
            return "black"
        elif speaker_number < 100: 
            return "green"
        elif 100 <= speaker_number < 1000: 
            return "yellow"
        elif 1000 <= speaker_number < 10000:
            return "orange"
        elif 10000<= speaker_number < 100000:
            return "red"
        else:
            return "darkred"

    def add_points_to_cluster(self, df: pd.DataFrame, cluster) -> folium.Map:
        for idx, row in df.iterrows():
            folium.Circle(
                location=[row['latitude'], row['longitude']],
                color=self.assign_colour_based_on_speaker_number(df, idx),
                tooltip= folium.Tooltip(self.structure_popup(row), max_width=800),
                radius=15000,
                stroke = False,
                fill = True,
                opacity = 1,
            ).add_to(cluster)
           
    def display_map(self, map: folium.Map, filename: str):
        '''Saves map html to a file and displays the folium map in Streamlit.'''
        map.save(filename)
        st.components.v1.html(open(filename, "r").read(), width=700, height=550)
         
    def create_choropleth(self, geo_data, frequency_data, map: folium.Map):
        folium.Choropleth(
            geo_data=geo_data,
            data=frequency_data,
            fill_opacity= 1.0,
            highlight=True,
            legend_name="Number of Languages",
            columns=["Province", "Number of Languages"],
            key_on="feature.properties.shapeName",
        ).add_to(map)

        self.add_geojson_tooltip(geo_data, frequency_data, map)
        
    def add_geojson_tooltip(self, geo_data: dict, df: pd.DataFrame, map: folium.Map):
        """
        Adds tooltips to a GeoJSON layer on the map, displaying the number of languages per province.

        Args:
            geo_data (dict): GeoJSON data defining the map regions.
            df (pd.DataFrame): DataFrame containing language counts by province.
            map (folium.Map): Folium map object to which the tooltips are added.
        """      
        for feature in geo_data["features"]:
            province = feature["properties"]["shapeName"]
            row = df[df["Province"] == province]
            if not row.empty:
                feature["properties"]["Number of Languages"] = int(
                    row["Number of Languages"].iloc[0]
                )
            else:
                feature["properties"]["Number of Languages"] = 0

        folium.GeoJson(
                geo_data,
                style_function=lambda feature: {
                    "fillColor": "transparent",
                    "color": "black",
                    "weight": 1
                },
                highlight_function=lambda feature: {
                    "weight": 3,
                    "color": "yellow"
                },
                tooltip=folium.GeoJsonTooltip(
                fields=["shapeName", "Number of Languages"],
                aliases=["Province:", "Number of Languages:"]
                )
        ).add_to(map)

    def search_for_language(self, df, map: folium.Map):
        """
        Searches for a specific language in the dataset by its name.

        Args:
            df (pd.DataFrame): The DataFrame containing language data.
            language_name (str): The name of the language to search for.

        Returns:
            pd.DataFrame: A filtered DataFrame containing rows that match the specified language name.
        """   
        
        options = ['All languages'] + df['language'].dropna().unique().tolist()
        with st.sidebar:
            st.header('Language Search')
            st.write('Use the dropdown menu to search for a specific language and highlight it on the map.')
            selected_language = st.sidebar.selectbox(
            "Search for a language",
            options,
            help = "Select a language to highlight it on the map."
            )
        if selected_language != "All languages":
            df_to_plot = df[df["language"] == selected_language]
        else:
            df_to_plot = df     
        for _, row in df.iterrows():
            is_selected = (
                selected_language != "All languages"
                and row["language"] == selected_language )

            color = "red" if is_selected else "white"
            radius = 10 if is_selected else 1

            cluster = MarkerCluster(
                name="Languages",
                disableClusteringAtZoom=9,
                icon_create_function=self.ICON_CREATE_FUNCTION
            ).add_to(map)

            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=radius,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=1.0,
                popup=row["language"]
            ).add_to(cluster)

            if selected_language != "All languages":
                bounds = df_to_plot[["latitude", "longitude"]].values.tolist()
                latitude = bounds[0][0]
                longitude = bounds[0][1]
                map.location = [latitude, longitude]

         
            else:
                    pass
        st.success(f'Showing {selected_language} on the map...')

        

            
        
            
                
            

    
        
