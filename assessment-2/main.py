from Visualiser import Visualiser
from DataLoader import DataLoader
from Analyser import Analyser
from Processor import Processor

def main():
    visualiser = Visualiser()
    data_loader = DataLoader()
    analyser = Analyser(None)
    processor = Processor()
    # """ 
    # language_location_data = data_loader.load_data_from_json("data/PNG_all_languages_coordinate_data.geojson")
    # df = processor.convert_json_to_df(language_location_data, 'features')
  
    # columns_mapping = {
    #     'properties.language.id': 'language_ID',
    #     'properties.language.name': 'language',
    #     'properties.language.latitude': 'latitude',
    #     'properties.language.longitude': 'longitude',
    #     'properties.language.jsondata.links': 'links',
    # }
    # df = processor.rename_columns(df, columns_mapping)
    # selected_columns = ['language_ID', 'language', 'latitude', 'longitude', 'links']
    # df = processor.create_new_dataframe_with_selected_columns(df, selected_columns)
    # df = processor.remove_data(df, 'language', 'Bilua')
    # df = processor.remove_data(df, 'language', 'Touo')
    # df = processor.replace_expression_in_values_in_column(df,'language', ' (Papua New Guinea)')
    # df = processor.replace_url_in_values_in_column(df, 'https://endangeredlanguages.com/lang/', 'https://www.endangeredlanguages.com/elp-language/')
   
    # final_df, languages_without_speaker_number = data_loader.orchestrate_data_scraping_per_domain_name(
    #     df, 
    #     'endangeredlanguages.com',
    #     'speaker-number-value',
    #     'secondary',
    #     'expert-curated',
    #     'direct',
    #     vitality_status_html_field= 'vitality',
    #     vitality_certainty_html_field= 'certainty') #placeholders
    # final_df, languages_without_speaker_number = data_loader.orchestrate_data_scraping_per_domain_name(
    #     final_df, 
    #     'wikipedia.org',
    #     "infobox-label", 
    #     'tertiary',
    #     'community-curated',
    #     'direct',
    #     string_expression = "Native speakers", 
    #     attribute1 = "th", 
    #     attribute2 = "td", 
    #     method_called_after_label_identified="find_next_sibling")
    # final_df, languages_without_speaker_number = data_loader.orchestrate_data_scraping_per_domain_name(
    #     final_df,
    #     'apics-online.info',
    #     'key',
    #     'secondary',
    #     'expert-curated',
    #     'direct',
    #     string_expression = "Number of speakers", 
    #     attribute1 = "td", 
    #     method_called_after_label_identified="find_next_sibling"

    # )
    
    
    # data_loader.write_df_to_csv(final_df, 'data/language_speaker_data__.csv') #code required to create the original dataframe (collecting data from websites)
    # """

    #DATA CLEANING
    language_speaker_data = data_loader.load_data_from_csv('assessment-2/data/language_speaker_data_clean.csv')   
    #language_speaker_data = processor.replace_regex_character(language_speaker_data, '[\u2012\u2013\u2014]', '-')
    #language_speaker_data = processor.replace_regex_character(language_speaker_data, '[\u00A0\u202F\u2007]', ' ')
    language_speaker_data = language_speaker_data.apply(processor.clean_speaker_number, axis=1)
    language_speaker_data = language_speaker_data.apply(analyser.calculate_source_confidence, axis=1)
    language_speaker_data = language_speaker_data.apply(analyser.calculate_min_and_max_for_not_ranges, axis=1)
    data_loader.write_df_to_csv(language_speaker_data, 'assessment-2/data/language_speaker_data_clean.csv')
    
    language_speaker_data = processor.create_plotting_data_column(language_speaker_data)
    #language_speaker_data = processor.create_tooltip_column_for_barchart(language_speaker_data)
    data_loader.write_df_to_csv(language_speaker_data, 'assessment-2/data/language_speaker_data_clean.csv')
    
#in some cases, wiki data not loading
#andai and meakambut do not have figures n the df even though there is a figure on the endangered languages website- why?

    visualiser.show_title("Language Speaker Data Visualisation for Papua New Guinea")
    map = visualiser.create_map(language_speaker_data, location= analyser.midpoint_coordinates(language_speaker_data), zoom_start=6.5)
    cluster = visualiser.show_cluster(map, language_speaker_data)
    
    visualiser.display_filtered_map(language_speaker_data, cluster)

    visualiser.display_map(map)
    visualiser.show_logarithmic_bar_graph(language_speaker_data)
   
    

    


if __name__ == "__main__":
    main()
   


 
