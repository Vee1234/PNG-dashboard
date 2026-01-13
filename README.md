## Island Dashboard
## Introduction, Scope and Context
### Introduction
With over 800 languages spoken by a population of just over 10 million people, Papua New Guinea is the most linguistically rich country in the world. I built a Streamlit-powered data dashboard to enable interactive exploration of language distribution and speaker populations across Papua New Guinea through three complementary visualisations. First, a geographic map displays the epicentres of individual languages, colour-coded by number of speakers. Interactive tooltips provide language-specific metadata, and users can filter by speaker population or search for individual languages. Second, a choropleth map shows the number of distinct languages spoken within each administrative province, with hover-based interaction revealing provincial counts. Third, a logarithmically scaled bar chart presents speaker populations for all languages, with extinct languages visually distinguished.

**The dashboard is deployed on StreamLit and can be accessed at this URL: https://vee1234-png-dashboard-assessment-2main-szkkgy.streamlit.app/**
 The underlying dataset was built on an established data set, wth significant supplementation from data scraping and derived data. The final dataset is stored in *language_speaker_number_clean.csv*. Single-responsibility classes encapsulate methods, with some classes having their own class variables.


### Gap Analysis
The problem addressed by this dashboard was defined through a review of existing linguistic visualisation tools and databases, focusing on their analytical scope, the combinations of data presented and the way that the data is presented. This analysis revealed a consistent emphasis on descriptive representation, with gaps in predictive insights, speaker number- geographical visualisations and national-regional language statistics offerings. The table below outlines a few of the different categories I analysed for gaps: 
| **Dimension**                      | **Current Practice**                                          | **Representative Systems**     | **Limitation**                                                               | **Contribution of This Work**                                                      |
| ---------------------------------- | ------------------------------------------------------------- | ------------------------------ | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **Analytical Orientation**         | Descriptive visualisation of observed linguistic data.        | D-Place, Glottolog, Ethnologue | Focuses on documentation rather than explanation or prediction.              | Introduces explanatory and predictive models of language evolution.                |
| **Geographical Representation**    | Point-based language markers.                                 | WALS, Glottolog                | Speaker populations and spatial extent are not represented. **No single map with overlayed language statistics.**  **Limited investigation of the distribution of languages at a national or regional level**         | Incorporates speaker counts, explicit legends, and inferred language areas.        |
| **Temporal Modelling**             | Static or historical representations.                         | Glottolog                      | No capacity for forward projection or counterfactual analysis.               | Enables simulation of future and alternative evolutionary trajectories.            |
| **Environmental Integration**      | Linguistic data visualised independently of physical context. | Glottolog                      | Environmental drivers of linguistic change remain unexamined.                | Integrates geospatial and environmental variables for correlation analysis.        |
| **Linguistic Feature Dynamics**    | Linguistic features listed per language.                      | WALS, Glottolog                | Feature evolution across families and regions is not analysed.               | Enables comparative analysis of typological trait evolution.                       |

This research informed my problem definition; I decided to target the gaps in **Geographical Representation**

Two existing projects in this area are Glottolog, an online bibliography and classification for the world's languages, and the Endangered Languages Project. Both projects offer map-based language visualisations, but do not allow the user to remain in the map context whilst viewing speaker number. Furthermore, these systems do not provide data or visualisations at administrative levels, limiting insight into language hotspots and the effects of geographic isolation on language density.

My dashboard combines geographical information with speaker and language numbers and presents how language distribution varies by region.


### Provenance
Provenance analysis aided me to determine which resources were most suitable for my project and optimise use of them to maximise both credibility and coverage. 
| **Source**                               | **Derived Data Used**                                                              | **Source Authority and Credibility**                                                                                                                                | **Data Collection and Generation Methods**                                                                                                                    | **Temporal Validity**                              | **Uncertainty and Bias**                                                                                       | **Fitness for Purpose**                                                                                                                                | **Licensing and Ethics**                                                        |
| ---------------------------------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| **Glottolog 5.2**                        | Language names, geographic centroids, source links                | Expert-curated and maintained by the Max Planck Institute for Evolutionary Anthropology. Widely referenced through use of Glottocodes by other linguistic datasets. | Compiled through expert-led review of handbooks, surveys, and existing bibliographies. Combines systematic collection with integration of existing resources. | Continually updated, with periodic major releases. | Automatic annotations have higher error rates than manual ones. Does not provide speaker population data.      | Provides a comprehensive list of all known languages, including extinct ones, and reliable geographic metadata required for mapping and data scraping. | Freely accessible and downloadable; appropriate for academic use.               |
| **Ethnologue** (not used directly)       | None                                                                               | Expert-curated and widely cited in academic literature.                                                                                                             | Compiled by specialists with extensive linguistic coverage.                                                                                                   | Regularly updated.                                 | Paywalled, preventing verification and reproducibility.                                                        | Would provide comprehensive speaker and vitality data, but access restrictions prevent direct use.                                                     | Restricted access limits transparency and reuse.                                |
| **Endangered Languages Project (ELCat)** | Speaker numbers and vitality status for endangered, dormant, and extinct languages | Maintained by the University of Hawaiʻi at Mānoa; academically curated secondary source.                                                                            | Aggregates vitality data from multiple expert sources and publications.                                                                                       | Actively updated.                                  | Coverage limited to endangered languages only; not a complete language catalogue.                              | Valuable for speaker numbers and vitality data, but insufficient as a standalone source.                                                               | Publicly accessible; data not provided in bulk downloadable form.               |
| **Wikipedia**                            | Speaker numbers and vitality status (fallback cases)                               | Community-curated tertiary source with low academic credibility.                                                                                                    | Aggregates information from secondary sources, often Ethnologue, without guaranteed traceability.                                                             | Update frequency is inconsistent.                  | High uncertainty due to indirect sourcing and lack of verification; error may propagate from upstream sources, resulting in an incorrect speaker number value. | Used only when no other data were available, improving completeness at the cost of increased uncertainty.                                              | Freely accessible; ethical use requires explicit acknowledgment of limitations. |
| **APiCS**                                | Speaker numbers for pidgin and creole languages                                    | Edited by academic linguists and supported by major research institutions.                                                                                          | Demographic and linguistic data compiled by domain experts; originally published as a peer-reviewed volume.                                                   | Continuously maintained.                           | Limited to pidgin and creole languages; not representative of all language types.                              | Provides reliable, expert-approved speaker estimates for a specific language class.                                                                    | Freely accessible and suitable for scholarly use.                               |

## Initial Data Cleaning 
The first resource I required was a comprehensive list of languages with their respective coordinates. I obtained this from GeoJSON which I copied from the Glottolog website. I retrieved the data using the *load_data_from_json* function in the *DataLoader* class shown below:
![alt text](<assets/Screenshot 2026-01-12 at 18.05.23.png>"load_data_from_json method, which takes in a path to a json file and returns the data retrieved.")
and converted the data from GeoJSON into a Pandas DataFrame called language_location_data using the *convert_json_to_df* function in *Processor*:
![alt text](<assets/Screenshot 2026-01-12 at 18.22.26.png>)
I decided to store the data in a Pandas DataFrame as it make the data cleaning, analysis and visualisation processes so much more efficient. It is easy to perform joins between DataFrames, perform statistical operations by row and column and DataFrames are compatible with many visualisation libraries. 

To reduce redundancy, I identified which columns would be the most relevant to this project. As well as language, latitude and longitude, I kept the Glottolog 'language_ID' (which could act as a primary key, given a single language could have multiple names) and the source 'links' column;  Ethnologue datasets are located behind a paywall so data scraping would be necessary to retrieve speaker number data and vitality status. These links are verified by the academics at Glottolog, increasing the credibility of the data from these websites.
I renamed these columns to improve readability and simplify referencing.  I did this by creating a dictionary called 'columns_mapping' which links the previous column name to a new one, and then calling the *rename_columns* function in *Processor*. 
![alt text](<assets/Screenshot 2026-01-12 at 18.50.33 1.png>)

![alt text](<assets/Screenshot 2026-01-12 at 19.17.40.png> "The rename_columns method takes a DataFrame and a columns mapping as arguments and returns the dataframe with modified column names." )

Following that, I created a list of the relevant columns and created a new DataFrame with only these columns using the *create_new_dataframe_with_selected_columns* I built in *Processor*. 

In preparation for data scraping, I tested a few of the links in  *language_location_data* to verify that they could  be accessed. When I navigated to any of the links to the Endangered Languages Project site, a 404 error occured. I discovered that URL schema changed from using the path /lang/<language-name> to /elp-language/<language-name>, replacing the original endpoint structure while retaining the language identifier as the terminal path segment. I wrote the *replace_url_in_values_in_column* method to rectify this.
 
![alt text](<assets/Screenshot 2026-01-12 at 19.47.03.png>"the replace_url_in_values_in_column method loops through each link in each row of 'links' columns, replacing an expression with another. The replacement expression defaults to '', in which case the expression will simply be removed." )
![alt text](<assets/Screenshot 2026-01-12 at 20.09.34.png>)


 ## Data Scraping
 ### Ethics
 In the *language_location_df* a list of links is listed for each language. As shown above, the three websites which consistently displayed speaker numbers were EndangeredLanguages.com, wikipedia.com and apics-online.info. To maximise data coverage, I could consider scraping data from all of these sources. I reviewed the Terms of Use and the robots.txt for each website to determine whether scraping was allowed and if so, under what conditions.

 With a strong focus on preserving and protecting indigenous cultures, EndangeredLanguages.com required its users to 'respect Indigenous Speakers' rights and decisions about their languages, cultures and knowledge' and 'approach all languages and materials with respect, responsibility, and care'. Furthermore, scraping for the purpose of training or fine tuning AI models is explicitly proibited. Wikipedia.com welcome friendly, low-speed bots welcome to view article pages, but not dynamically generated pages. I could not find any scraping guidance for apics-online.info, therefore I tried to keep my scraping algorithm as polite as possible. I cached each website I accessed (each website's cache can be found in the cache folder) to minimise request rate and set retries to occur every 2 seconds, putting the request rate at 0.5 seconds, well below Wikipedia's limit. Finally, I created a User Agent header to reveal my scraping bot as a custom, academic one and to prevent retrieval failures or being blocked by the website. 

 (self.HEADERS insert here)
### Algorithm Structure
I designed an algorithm to ethically and efficiently extract data from a specified website domain for each language, using the BeautifulSoup library.

This algorithm powers the code in the master function, *orchestrate_data_scraping_per_domain_name*, in *DataLoader*. 


(orchestrate_data_scraping_...)

The master function calls other methods with specific roles in the data scraping process. The *get_page* method hadnles retrieval and caching of website html, *scrape_data_in_class_field_from_website* retrieves the speaker number or vitality status from this html. Overall, *orchestrate_data_scraping* handles the execution of the algorithm, as well as populating rows in the dataframe with the correct values. 

The algorithm is extremely flexible; it successfully retrieves data from websites with a wide variety of html structures. The *speaker_number_html_field*, *attribute1*, *attribute2*, *string_expression* and *method_called_after_label_identified* arguments allow the user to describe the unique html structure of the desired website, which meant this algorithm was compatible with all three websites to be scraped. However, one downside of this algorithm is that it requires siginificant user knowledge of the underlying html structure. 

I created a dataclass called *Result* to provide a structure for what information needed to be stored in the final DatFrame and facilitate the storage of the scraping results. A new instance of the Result dataclass was created for each language and appended to a list of results once populated.

Users may provide a preference list (to the *preference_list* argument) to indicate the order in which websites should be scraped, with the default configuration placing wikipedia.org last. 

An essential part of the algorithm is defining when the scraping process is complete. To preserve the order of the preference list, the scraping process is coomplete when the contents of result fail to meet this condition, which is seen in *orchestrate_data_scraping_per_domain_name*:
```if domain_name in url and (preference_list.index(result["speaker_source"])>preference_list.index(domain_name) or result["speaker_source"] == None)```
This logic ensures that a website is only scraped if it appears in the user-defined preference list and has higher priority than any previously recorded source, or if no source has yet been recorded. It prioritizes more reliable sources and reduces redundant scraping.

The first column that is populated by the algorithm is 'speaker_number_raw'. This is an unclean, textual representation of the number of speakers. Where no speaker number was found, the value was set to None. The 'speaker_number_raw' field of a language which has been identified as extinct or dormant is temporarily set to this vitality status, before 'vitality_status' is filled by the *fill_columns_based_on_language_vitality* method.

'Extinct' and 'Dormant' are qualitative linguistic definitions that don't simply mean 'number of speakers = 0'. The Unesco Ad Hoc Group on Endangered Languages defines 'Extinct' as 'There is no one who can speak or remember the language.' whereas Endangered Languages defines a dormant language as one that 'does not have any living fluent speakers/signers'. Whilst sometimes these terms are equated to a zero speaker value in academia, there have been cases where a small, previously unknown, community of speakers has emerged. To show respect for the indigenous cultures and Endangered Language's Terms of Use, I set 'speaker_value_raw' to None for langauges reported as extinct or dormant. 

To keep a record of credibility and allow for quantification of confidence (which will be performed after the data is cleaned), the url which was accessed, the source category (primary, secondary or tertiary), the source type (expert-curated or community-curated) and access route (direct or indirect) for each source domain are collected and stored in individual columns in the DataFrame. 

The final step of the scraping algorithm was to combine geographical, speaker number, vitality status and source data into a single DataFrame. I converted the list of scraping results into a DataFrame and performed a left join with the language_location_data DataFrame, using 'language' as the primary key. The resulting dataFrame, called final_df in *orchestrate_data_scraping_per_domain_name* was written to *language_speaker_data.csv*

#### Key Modules and Techniques Used
I chose to use Beautiful Soup to extract data from the websites’ HTML because the three sources had markedly different HTML structures. The relevant information was embedded in different tags and at varying depths of nesting across the sites, so a flexible parsing tool was required. Beautiful Soup allows HTML to be navigated in multiple ways—by tag, attributes, hierarchy, and relationships between elements—making it well suited to handling this structural variability.
I used requests for its simple, robust interface, which streamlines HTTP requests, header handling, timeouts, and exceptions, making web scraping more reliable and concise than Python’s built-in urllib.

## Data Cleaning
The speaker_value_raw column contained a wide variety of formats and structures, including ranges (e.g., “3–5 million”), approximate values (e.g., “~200”), historical references (e.g., “2000 cited 1990”), and qualitative descriptions (e.g., “a few dozen speakers or less”). These inconsistencies required careful cleaning and standardisation in order to convert the raw entries into consistent numeric values suitable for analysis.


### Speaker Number Cleaning Function
The *clean_speaker_number* function is designed to standardise and convert raw speaker number data from heterogeneous formats into a numeric format suitable for analysis. It handles missing, approximate, range-based, qualitative, and cited speaker counts. The function populates several fields in the dataset, including speaker_number_numeric, speaker_number_min, speaker_number_max, speaker_number_type, and speaker_number_year, to capture the variety and uncertainty in the original data.
Firstly, the raw speaker number retrieved from the speaker_number_raw column is cleaned to remove commas, em-dashes and new-line characters which would interfere with numerical analysis. This is performed by the *replace_character* method inside of the *clean_speaker_function*. (insert image)

The following cases are then handled:
1. Missing data: If the speaker_number_raw value is missing (NaN), the function assigns None to indicate an absent or unknown speaker count.
2. Exact numeric values: Values containing only a single number are parsed as integers and marked as exact. Both the minimum and maximum speaker counts are set to this value.
3. Cited data: Entries that include the word "cited" are interpreted as historical references. The function extracts the numeric value before the citation and, if present, records the cited year separately.
4. Approximate numbers: Values indicated with symbols such as ~ are treated as estimates. The numeric component is extracted, and the type is marked as "estimate".
5. Upper-bound indicators: Phrases such as "less than X" or "fewer than X" are interpreted as ranges from 0 to the specified number, with the type "range" or "qualitative range" to reflect uncertainty.
6. Explicit ranges: Values formatted as "min–max" are parsed into speaker_number_min and speaker_number_max fields, with type "range".
7. Multipliers and quantifiers: Words like "thousand", "million", or qualitative quantifiers such as "dozen" are converted into numeric equivalents using predefined dictionaries, which are stored as class variables in the *Processor* class. This allows entries like "a few dozen" or "2–3 million" to be standardised. The type is marked as "qualitative estimate".
8. Fallback numeric extraction: For any remaining formats, the function attempts to extract the first numeric value as speaker_number_numeric and identifies additional numbers as potential years.
9. Error handling: Any unexpected formats trigger a safety net, assigning None to numeric fields to prevent crashing or misinterpretation.

This function returns a DataFrame with populated fields containing cleaned values, ready for data analysis. I wrote the cleaned DataFrame to *language_speaker_data_clean.csv*.

#### Key modules and techniques used:
The function uses pandas (pd.isna) for handling missing values, and regular expressions (re) for flexible pattern matching. These patterns, including numbers, ranges, years, approximate symbols, multipliers, and qualitative descriptors, are stored as class constants; as the pattern is only compiled once, the code is more efficient. 
The function converts human-readable estimates into numeric values using dictionaries for multipliers and quantifiers which are stored as class variables.

#### Statistical considerations
The function emphasises capturing uncertainty. Following the methodological guidance for self-selected interval data (Angelov et al., 2024), ranges were treated as interval-censored rather than collapsed into exact values. The function preserves ranges (min/max) and explicitly marks estimates or qualitative values. It also avoids misleading precision by not rounding or approximating values unnecessarily; if the raw data is approximate, the output retains that uncertainty in the type and min/max fields. Finally, the function ensures ethical representation of data: by distinguishing between exact counts, estimates, and ranges, it prevents misrepresentation of language vitality or speaker populations, which is particularly important for endangered or poorly documented languages.  This aligns with best practices in linguistics and demographic analysis, where speaker counts may be uncertain, approximate, or based on historical sources. 


## Methodology and Data Analysis (30%) 
You should talk about and demonstrate your analysis methods and approaches to visualisation here. While the quality of data available will depend on your project, you should be able to demonstrate statistics at the level of collections and subcollections. You should consider what types of visualisations will best convey your insights, and how these will be accessible to your audience. You should also ensure your work is reproducible and that algorithms or formulas used for calculations are documented. 

### Exploratory Visualisation

I created exploratory visualisations to guide analysis decisions, prioritising user experience and accurate representation of data and uncertainties.

I used the Folium library to create maps. In *Visualiser*, I built the *create_map* method which returns a Folium.Map object with an associated header and description. I extracted language_speaker_data from *language_speaker_data_clean.csv* and looped through the coordinates, adding each language as a point to the map. To display maps, Folium map HTML must be saved to a file and then read. To avoid repetitive code, I wrote the *display_map* method which accomplishes this.

I used Streamlit to build and display my web app. As I navigated this elementary visualisation, I considered a few ideas that would improve the value and credibility of the dashboard:
1. Adjusting the initial map coordinates to centre on Papua New Guinea;
2. Adding a tooltip to improve interactivity and readibility;
3. Calculation of source confidence and to reflect uncertainty in values, which can be applied to filtration functions.

This exploration helped me decided which data I wished to display and the visualisation I could use. Below is a list that I believe would bring value to my dashboard.
1. A map displaying each language as a point equipped with a tooltip feature, filtration and search capabilities. This would allow the user to explore the individual languages speaker numbers and locations and identify language hotspots.
2. A choropleth map displaying languages per administrative region. This would enable users to explore how the historically borderless linguistic landscape of Papua New Guinea fit into the country's modern-day political boundaries.
3. A bar chart displaying the number of speakers per language. This allows the user to directly compare the speaker numbers of all languages, at a macro level.

### Analysis
### Map Adjustment
I created the find_midpoint_coordinates function to find the geographical centre of all the coordinates in the dataset.
(find_midpoint_coordinates)
Because a large proportion of languages are concentrated in the north-west of Papua New Guinea, the mean coordinates were spatially skewed and unsuitable for map centring. Using the midpoints of the extrema provides a more balanced map centre.
### Deriving the Plotting Data and Bar Chart Tooltip Value columns
To display a bar chart, I needed to assign a single numerical speaker number to each language. This was a problem for languages whose speaker number was given as a numerical or qualitiative range- how could I derive a single numerical value while still preserving and presenting the uncertainty in speaker number? 

To simultaneously provide a clear visual representation of speaker number and not mislead the dashboard user, I decided to expose one value in a tooltip, called *bar_chart_tooltip_value*, while using a derived variable, called *plotting_data* in any underlying data analysis. The values were stored in separate columns in the DataFrame because the tooltip cannot dynamically compute the appropriate value for each language. The *create_plotting_data_column* is shown below: 
(plotting data function)
This function assigns a *plotting_data* value to each language using the following rules: 
| Case                     | How *plotting_data* is calculated                                                                 |
|---------------------------|--------------------------------------------------------------------------------------------------|
| Range                     | Midpoint of *speaker_number_min* and *speaker_number_max*                                         |
| Extinct / Dormant         | Value slightly below the dataset minimum to distinguish these languages visually. If the value were set to 0, the bar would not appear.                 |
| Exact counts              | Uses the numeric value directly                                                                 |
| Estimates                 | Uses the processed numeric estimate                                                             |
| Qualitative ranges        | Midpoint of inferred minimum and maximum values, consistent with numeric ranges                 |

The purpose of *bar_chart_tooltip_value* is to ensure that users see the most informative value for each language. For example, the raw speaker value for Tok Pisin '3-5 million (estimated)' is much easier to understand than a speaker_number_min of 3000000 and a speaker_number_max of 5000000. *create_tooltip_column_for_bar_chart* takes in a DataFrame and outputs a DataFrame with a populated *bar_chart_tooltip_value* column.

The function determines which value to display in the tooltip using the following rules:
| Value Type / Status                     | Conversion Method                                |
|----------------------------------------|-------------------------------------------------|
| Range, Estimate, Qualitative Range, Qualitative Estimate | Uses the raw speaker number (`speaker_number_raw`) |
| Exact                                  | Uses the numeric speaker count (`speaker_number_numeric`) |
| Extinct, Dormant                        | Uses the vitality status (`vitality_status`)    |
#### Key Modules and Techniques Used
I used the Pandas module to set the initial value of the columns to NaN.
### Calculating Source Confidence

Displaying source confidence is essential. It helps to inform the user's interpretation snf maintain transparency about the limitations of the dataset and the credibility of the underlying data.

The factors affecting the confidence of each source (access type, source category and source type) were recorded and stored in appropriate columns in the *language_speaker_data* DataFrame during data scraping. I created a dictionary wherein each descriptor was assigned a numerical multiplier, shown below.

Estimates are considered more credible than ranges and qualitative descriptions are heavily penalised. I assumed that confidence decreases through SOURCE_CONFIDENCE_DICTIONARY, with each level reducing the numerical score by 0.25. 

This is the formula I used to calculate source confidence, which I implemented in the *create_source_confidence* method:
```(T)*(C)*(N)*(A)```
where T, C, N and A are the confidences associated with source type, source category, speaker number type and access route respectively. 

### Applying Source Confidence to Filtration

Speaker numbers are inherently uncertain due to survey limitations; even for estimated counts, the true value is assumed to lie within a range surrounding the reported figure. Determining these bounds is essential to avoid misrepresenting speaker numbers when filtering by population. For example, if the map is filtered to show languages with more than 2,900 speakers, Manambu should be included, as its true speaker count is assumed to lie within a range around the reported raw value (~2,800). The size of the range is directly influenced by source confidence.

I created the *calculate_min_and_max_for_not_ranges* to calculate the upper and lower bounds and parse them into speaker_number_min and speaker_number_max.


Both bounds are set to 0 for extinct and dormant languages to separate them from the rest of the data which makes the process to access these languages more intuitive for the user.
Considering these bounds results in a more accurate filtering system.

### Mapping Languages to Province using shapely
A key insight derivable from the dataset is the distribution of languages across provinces. A choropleth map with a legend most effectively conveys this pattern, as the colour shading means relative language density is immediately apparent to the user. 

The GeoJSON file containing Papua New Guinea's provincial boundaries was downloaded from geoBoundaries.org. In the *build_province_language_mapping* method below, the contents of the GeoJSON were parsed as a parameter to boundaries_data while language_speaker_data was parsed to language_df.
(build_province_language_mapping)



This function demonstrates a clear analysis method by gathering point-level language data into province-level collections and subcollections using a point-in-polygon approach.
Because province membership is determined by an explicit, deterministic point-in-polygon rule, the collection process is fully reproducible: identical inputs will always yield the same province-level language counts, allowing the analysis to be independently replicated.

#### Key Modules and Techniques
I chose to use the shapely library as it handled all of the geometric operations required to use a point-in-polygon approach. Transforming coordinates to Point objects and converting each province to a Polygon was extremely simple, allowing me to focus on the overall logic of the function rather than the low-level geographical operations.

### Final Visualisation
#### Language Map
The first visualisation I created displays all of the languages from the DataFrame on the map as Circles, with the colour corresponding to the number of speakers.  To improve accessibility, a key shows each colour next to its corresponding speaker number range.Clusters reduce noise and offer visual cues indicating language density, improving readability. This visualisation offers insight into the distribution of languages across Papua New Guinea, allowing the user to identify language hotspots and cold zones. The visualisation allows the user to explore the details of each language in a geographical context, something that no other dashboard or visualisation is capable of. 

*add_points_to_cluster* in *Visualiser* is responsible for adding the languages in the DataFrame that fit the condition set by the user to a cluster which is then added to a map. *add_points_to_cluster* calls *assign_colour_based_on_speaker_number* which returns the colour the point should be depending on what range it falls in. The colour scale is designed to be intuitive, leveraging natural perceptual associations, with dark red representing extinct languages and green indicating languages with large speaker populations. To provide further clarification, I created a key, which I wrote in HTML and saved as the class variable *LEGEND_HTML*. To add the legend to the map I used:

`map.get_root().html.add_child(Element(self.LEGEND_HTML))`
which is located in the *display_filtered_map_ method.
`map.get_root()` accesses the map’s HTML structure, and `add_child(Element(self.LEGEND_HTML))` wraps the legend’s raw HTML as a Folium-compatible element and inserts it into the map.

Finally, to reduce noise on the map I implemented clusters. Cluster circles change in size and colour based on the number of children they have in an intuitive way, with large, red clusters having the most and small, yellow ones having the least. To make the size of clusters change continuously, I set the cluster radius to `size = 20 + Math.log(count) * 15`. In this way, cluster circle size is more representative of the number of children, making cluster size a more meaningful cue to the user. The function that determines the colour and size of a cluster is written in HTML and assigned to the class variable *ICON_CREATE_FUNCTION*. It is parsed as a parameter when a new cluster in instantiated in *display_filtered_map*.



#### Choropleth Map

For my second visualisation, I wanted to investigate the relationship between a given linguistic variable over political boundaries. I created a Folium.Chloropleth object, parsing the following parameters:  
- the dataset containing provincial boundaries (*boundaries_data*), 
- the DataFrame containing each Province and the number of languages spoken (*language_mapping*),
- a legend name,
- the columns in the DataFrame corresponding to the province and the  number of languages spoken there ('Province' and 'Number of Languages'),
- and the key in the boundaries dataset that contains the geographic boundaries('features.properties.shapeName'). 
This choropleth visualises the number of languages spoken per province. It links province geometries *geo_data* with frequency data *frequency_data* to colour each region according to its language count. The resulting map highlights regional patterns clearly, includes a legend for accessibility, and uses reproducible, documented Folium functionality. The method is shown below.

#### Bar Chart
Finally, I wanted to create a visualisation that would enable users to visually and numerically compare the speaker counts of all languages. I chose to display this data through a bar chart created with the Vega-Altair library, as bar length effectively conveys both the absolute number of speakers and the relative size of speaker populations across languages. 

The values in the *plotting_data* column are used as frequency values. I chose to place languages on the Y axis and number of speakers on the x axis as it means the user can continue to scroll downwards through the dashboard as they have been doing for the other visualisations, improving accessibility. Using a logarithmic scale allows languages with widely varying speaker numbers to be compared meaningfully- pattersn across languages become immediately visible. Extinct languages are highlighted in red to draw attention to them and remain consistent with the colour scheme used in the other visualisations. The benefit of setting the *plotting_data* value of extinct and dormant languages to 0 is evident: the bars can actually be seen.

why altair- compatible with df, declarative- focus on what rather than how, interactive capabilities

#### Key Modules and Techniques
I chose Folium for its versatile marker options, including circles, markers, and circle markers, which facilitated clear plotting of points on the map. Creating points and clusters was straightforward and fully reproducible. Additionally, the ability to convert raw HTML into Folium elements enabled customisation of the map to effectively display the data. Finally, Folium integrates seamlessly with Streamlit, meaning I could embed a Folium.Map object into Streamlit without any conversion.

I chose Altair to create the bar chart because it works seamlessly with DataFrames, allowing direct mapping of columns to visual elements and it supports built-in interactivity, such as tooltips and conditional formatting. Its declarative syntax focuses on what to display rather than how to draw it, which improves efficiency for simple graphs though it meant I had less control over the design. A more eye-catching visualisation could have been made using Plotly.


## Design and Implementation (30%) 

You should show how you constructed the dashboard, demonstrating both the visual and code design. A dashboard implies either interactivity or up-to-date data; ideally, you should include both. This means your dashboard should be interactive and responsive, accommodating different types of users. It should also be updatable, should new data be available. Version control should be used to track the development of new features against documented requirements. You should show knowledge of the classes and methods of libraries used, extending functionality where appropriate.
I displayed my visualisations using the Streamlit framework. 

### Interactivity
I have implemented interactivity into this dashboard in four ways.
#### 1. Tooltips
Each of the visualisations on the dashboard is equipped with a tooltip. The tooltips provide immediate, on-demand information without cluttering the map, allowing users to explore data dynamically. One limitation for tooltips is that are not as effective on touch-screen devices.

In the Languages Map, when the user hovers over a Circle marking a language, a small window appears with language name and any other metadata that would useful for a user, such as speaker number, speaker number type (eg. estimate, range, exact), source, year cited and confidence score. This approach enhances interactivity, accessibility, and transparency while allowing the dashboard to update dynamically as new data is added. To identify which of these fields are present for each language entry, I created the *structure_tooltip* function which is outlined below:

1. Initialise an empty list to store HTML lines.
2. Add the language name if available.
3. Add exact speaker numbers for entries marked as "exact".
4. Add raw speaker numbers for ranges, estimates, or qualitative types.
5. Add the year the speaker number was cited, if available.
6. Add the vitality status of the language.
7. Add the source confidence score.
8. Add the speaker number type.
9. Add the source of the data.
10. Join all lines with HTML <br> tags to produce a single tooltip string.

The tooltip string returned from this function is parsed as a parameter where the point for that language is created.
This function is reusable and reproducible.

For the choropleth map, the tooltip is combined with the highlight capability of Folium.choropleth. 
The tooltip enriches the map by adding the number of languages spoken per province as a property and visualises the provinces with borders and interactive tooltips using Folium. It enables users to see both the province name and the number of languages directly by hovering over each region. The highlighting on hover draws attention to the selected province, improving usability and helping users focus on areas of interest. Users can interactively compare provinces in a single visualisation, making spatial patterns in language distribution more understandable.

Finally, when the user hovers over each of the bars in the bar graph, the name of the language and *bar_chart_tooltip_value* appear. This provides the user with a more precise understanding of speaker population sizes, complementing the relative comparisons indicated by bar lengths. As no conditional logic was needed to assemble the contents of this tooltip, it could simply be written in the bar chart's 'Tooltip' field.

#### 2. Search Languages
The search functionality, in the *search_for_language* method, enables users to search for a specific language from the dataset using a dropdown menu in the Streamlit sidebar. Selected languages are highlighted on the Folium map with larger, red circle markers, while other languages remain smaller and white. The map automatically centres on the selected language, providing immediate spatial context.
This contributes to an interactive and responsive experience for the user in the following ways:
1. Users can focus on any language of interest, making the dashboard responsive to individual queries.
2. Highlighting selected languages with colour and size enhances clarity and reduces cognitive load.
3. Automatic recentering ensures the highlighted language is immediately visible, improving usability.
4. Marker clustering maintains readability in regions with dense language points, supporting exploration of large datasets. The user can click on these clusters to navigate to languages, allowing users to have more control over their experience.
5. The dropdown menu offers an interactive interface, dynamically filtering options as the user types to enable responsive language selection.

Currently, the circle representing the selected language is added to a cluster before being added to a map. This functionality could bring even more value if multiple languages could be selected at a time and added to a cluster, enabling comparative exploration across multiple languages simultaneously.

#### 3. Filtration

The filtration functionality in *display_filtered_map* enables interactive filtering of languages by speaker population using a logarithmic slider. I chose to use a logarithmic slider to accommodate the wide range of speaker counts and enable finer, more interactive control in the lower range, where the majority of languages are concentrated . The selected slider values are converted into absolute speaker thresholds by exponentiation, producing lower and upper bounds (user_min, user_max). Languages are retained if their estimated speaker range (bounded by speaker_value_min and speaker_value_max calculated in analysis) overlaps with the selected bounds, ensuring uncertainty-aware filtering. The filtered results are then displayed on the map using clustered markers.

This function demonstrates exemplary interactivity in the following ways:
1. The slider allows intuitive exploration across several orders of magnitude without overwhelming the user.
2. Slider inputs are transparently mapped to meaningful numeric bounds in real time.
3. The selected range displayed below the slider updates instantly as the slider moves, providing clear, real-time feedback that directly links user input to the data displayed.
4. The map updates instantly as filters change, reinforcing exploratory analysis.
5. Marker clustering preserves readability as the number of displayed languages changes.

### OOP Structure
There are a number of ways I have demonstrated exemplary OOP in this project:
1. **Separation of concerns**  
   `DataLoader`, `Processor`, `Analyser`, `Visualiser`, and `Result` each handle a single workflow stage, improving readability, testability, and maintainability.

2. **Low coupling**  
   Restricting instantiation (only `Visualiser` creates `Analyser`) limits dependencies, making components easier to replace, extend, or test independently. 

3. **Structured outputs via dataclass**  
   `Result` enforces explicit, typed data objects, avoiding shared mutable state and aligning with functional principles.

4. **Controlled execution**  
   `if __name__ == "__main__": main()` separates workflow control from class logic, supporting reuse, testing, and reproducible pipelines.

5. **Dependency injection**  
   Passing an `Analyser` to `Visualiser` instead of internal creation reduces coupling, increases testability, and allows flexible swapping of analysis logic.

### Updating Ease

### Version Control






## Recommendation, Reflection and Conclusions (10%) 
While this part alone is worth the least number of marks, this is critical for showing the learning that occurred during your work on the assignment, and effective completion of this section will allow you to get more marks in earlier sections. You should link your work to relevant knowledge, skills and behaviour from the apprenticeship, and ensure the marker has everything they need to use and evaluate your code.

For bar chart could have had a max speaker and min speaker bar for ranges.