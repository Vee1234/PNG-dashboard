from Visualiser import Visualiser
from DataLoader import DataLoader
from Analyser import Analyser
from Processor import Processor

def main():
    visualiser = Visualiser()
    data_loader = DataLoader()
    analyser = Analyser(None)
    processor = Processor()
    
    '''language_location_data = data_loader.load_data_from_json("data/PNG_all_languages_coordinate_data.geojson")
    df = processor.convert_json_to_df(language_location_data, 'features')
  
    columns_mapping = {
        'properties.language.id': 'language_ID',
        'properties.language.name': 'language',
        'properties.language.latitude': 'latitude',
        'properties.language.longitude': 'longitude',
        'properties.language.jsondata.links': 'links',
    }
    df = processor.rename_columns(df, columns_mapping)
    selected_columns = ['language_ID', 'language', 'latitude', 'longitude', 'links']
    df = processor.create_new_dataframe_with_selected_columns(df, selected_columns)
    df = processor.remove_data(df, 'language', 'Bilua')
    df = processor.remove_data(df, 'language', 'Touo')
    df = processor.replace_expression_in_values_in_column(df,'language', ' (Papua New Guinea)')
    df = processor.replace_url_in_values_in_column(df, 'https://endangeredlanguages.com/lang/', 'https://www.endangeredlanguages.com/elp-language/')
   
    final_df, languages_without_speaker_number = data_loader.orchestrate_data_scraping(df)
    
    data_loader.write_df_to_csv(final_df, 'data/language_speaker_data.csv')''' #code required to create the original dataframe (collecting data from websites)
    
    #DATA CLEANING
    language_speaker_data = data_loader.load_data_from_csv('assessment-2/data/language_speaker_data.csv')   
    language_speaker_data = processor.replace_regex_character(language_speaker_data, '[\u2012\u2013\u2014]', '-')
    language_speaker_data = processor.replace_regex_character(language_speaker_data, '[\u00A0\u202F\u2007]', ' ')
    language_speaker_data = processor.extract_numeric_speaker_number(language_speaker_data)
    data_loader.write_df_to_csv(language_speaker_data, 'assessment-2/data/language_speaker_data_.csv')
    
   
#in some cases, wiki data not loading
#andai and meakambut do not have figures n the df even though there is a figure on the endangered languages website- why?

    
    '''map = visualiser.create_map(df, location= analyser.mean_coordinates(df), zoom_start=6)
    visualiser.add_points_to_map(df, map)
    vor_web = analyser.create_voronoi_chloropleth(df)
    visualiser.add_voronoi_to_map(vor_web, map)
    visualiser.add_hover(vor_web, map)
    visualiser.trial_chloropleth(df, map)
    visualiser.display_map(map)'''
    

    


if __name__ == "__main__":
    main()
   


 
