from Visualiser import Visualiser
from DataLoader import DataLoader
from Analyser import Analyser
from Processor import Processor

def main():
    visualiser = Visualiser()
    data_loader = DataLoader()
    analyser = Analyser(None)
    processor = Processor()
    
    language_location_data = data_loader.load_data_from_json("PNG_all_languages_coordinate_data.geojson")
    df = processor.convert_json_to_df(language_location_data, 'features')
    columns_mapping = {
        'properties.language.id': 'Language ID',
        'properties.language.name': 'Language Name',
        'properties.language.latitude': 'Latitude',
        'properties.language.longitude': 'Longitude'
    }
    df = processor.rename_columns(df, columns_mapping)
    selected_columns = ['Language ID', 'Language Name', 'Latitude', 'Longitude']
    df = processor.create_new_dataframe_with_selected_columns(df, selected_columns)
    map = visualiser.create_map(df, location= analyser.mean_coordinates(df), zoom_start=6)
    visualiser.add_points_to_map(df, map)
    visualiser.display_map(map)
    

    


if __name__ == "__main__":
    main()
   


 
