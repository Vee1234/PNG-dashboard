import pandas as pd
import geopandas as gpd
import math
import re
class Processor:
    def __init__(self):
        self.MULTIPLIERS = {'million': 1000000, 'thousand': 1000, 'hundred': 100, 'dozen': 12}
        self.QUANTIFIERS = {'a few': 3, 'a couple': 2}
        self.RE_NUM = re.compile(r"\d+")
        self.RE_RANGE = re.compile(r"(\d+)-(\d+)")
        self.RE_APPROX = re.compile(r"~(\d+)")
        self.RE_LESS_SYMBOL = re.compile(r"<(\d+)")
        self.RE_YEAR = re.compile(r"\d{4}(?:\s*-\s*\d{4})?")
        self.RE_QUANTIFIERANDMULTIPLIER = re.compile(r"(?i)\b(?P<quantifier>a couple|a few|several|\d+)\b\s*(?P<multiplier>dozen|hundred|thousand|million)\b")
        pass
       
    def convert_json_to_df(self, json_data:dict, highest_field_name: str) -> pd.DataFrame:
        '''This function creates a pandas dataframe from the json data.'''
        df = pd.json_normalize(
        json_data[highest_field_name],
        record_path=None,
        meta=None,
        )
        return df
    def round_sf(x, sig=4):
        if x == 0:
            return 0
        else:
            return round(x, sig - int(math.floor(math.log10(abs(x)))) - 1)
    
    def rename_columns(self, df: pd.DataFrame, columns_mapping: dict) -> pd.DataFrame:
        '''This function renames the columns of the dataframe.'''
        renamed_df = df.rename(columns=columns_mapping)
        return renamed_df
    
    def create_new_dataframe_with_selected_columns(self, df: pd.DataFrame, selected_columns: list) -> pd.DataFrame:
        new_df = df[selected_columns].copy()
        return new_df 
    
    def remove_data(self, df: pd.DataFrame, column_name, condition) -> pd.DataFrame:
        try:
            df = df.drop(df[df[column_name] == condition].index)
            return df
        except KeyError:
            print(f"Column '{column_name}' does not exist in the DataFrame.")
            return df
    def replace_regex_character(self, df: pd.DataFrame, original_regex: str, replacement_character: str) -> pd.DataFrame:
        df = df.replace(
        {rf'{original_regex}': replacement_character},
        regex=True
        )
        return df
  
    def convert_geojson_to_gpd(self, df: pd.DataFrame):
        gdf = gpd.read_file("PNG_all_languages_coordinate_data.geojson")
        print(gdf)
    
    def replace_url_in_values_in_column(self, df: pd.DataFrame, expression: str, to_be_replaced: str = '') -> pd.DataFrame:
        for link_list in df['links']:
            for link in link_list:              
                link['url'] = link['url'].replace(expression, to_be_replaced)
        return df           

    def replace_expression_in_values_in_column(self, df: pd.DataFrame, column, expression: str, to_be_replaced: str = '') -> pd.DataFrame:
        '''This function removes a specific expression from all values in a specified column of the dataframe.'''
        df[column]= df[column].str.replace(expression, to_be_replaced)     
        return df
    
    def clean_speaker_number(self, row) -> int:
        
        try:
            raw = row["speaker_number_raw"]
            # ---------- Possibility 1: Missing data ----------
            if pd.isna(raw):
                row["speaker_number_numeric"] = None
                return row

            raw = str(raw).lower().replace(",", "").strip() #1000 cited 2000-2003

            # ---------- Possibility 2: Speaker number raw contains only 1 number ----------
            if raw.isdigit():
                row["speaker_number_numeric"] = int(raw)
                row["speaker_number_type"] = "exact"
                return row
            # ---------- Possibility 3: Cited ----------
            if "cited" in raw:
                nums = self.RE_NUM.findall(raw)
                try:
                    if nums:
                        row["speaker_number_numeric"] = int(nums[0])
                except ValueError:
                    row["speaker_number_numeric"] = None
                split_raw = raw.split("cited", 1)
                year = self.RE_YEAR.search(split_raw[1])
                if year:
                    row["speaker_number_year"] = year.group()
                row["speaker_number_type"] = "exact"
                return row

            # ---------- Possibility 4: Approx ----------
            m = self.RE_APPROX.match(raw)
            if m:
                row["speaker_number_numeric"] =int(m.group(1))
                row["speaker_number_type"] = "estimate"
                return row

            # ---------- Possibility 5: Less than ----------
            m = self.RE_LESS_SYMBOL.match(raw)
            if m:
                row["speaker_number_min"] = 0
                row["speaker_number_max"] = int(m.group(1))
                row["speaker_number_type"] = "range"
                return row

            # ---------- Possibility 6: Fewer than ----------
            if raw.startswith("fewer than"):
                num = self.RE_NUM.search(raw)
                if num:
                    row["speaker_number_min"] = 0
                    row["speaker_number_max"] = int(num.group())
                    row["speaker_number_type"] = "range"
                return row

            # ---------- Possibility 7: Explicit range ----------
            m = self.RE_RANGE.fullmatch(raw)
            if m:
                row["speaker_number_min"] = int(m.group(1))
                row["speaker_number_max"] = int(m.group(2))
                row["speaker_number_type"] = "range"
                return row

            # ---------- 8: Multipliers and Quantifiers ----------
            for word, mult in self.MULTIPLIERS.items():
                if word in raw:
                    nums = self.RE_NUM.findall(raw)
                    try:
                        if len(nums) == 1:
                            row["speaker_number_numeric"] = int(int(nums[0]) * mult)
                            row["speaker_number_type"] = "exact"
                        elif len(nums) == 2:
                            row["speaker_number_min"] = int(int(nums[0]) * mult)
                            row["speaker_number_max"] =int(int(nums[1]) * mult)
                            row["speaker_number_type"] = "range"
                            return row
                        elif len(nums) == 0:
                                match = self.RE_QUANTIFIERANDMULTIPLIER.search(raw)
                                if match:
                                    q = match.group("quantifier")
                                    m = match.group("multiplier")

                                    # convert quantifier
                                    q_val = self.QUANTIFIERS.get(q, None)
                                    if q_val is None:
                                        try:
                                            q_val = float(q) 
                                        except:
                                            q_val = 1
                                    if "fewer than" in raw or "less than" in raw or "or less" in raw or "or fewer" in raw:
                                        row["speaker_number_min"] = "0"
                                        row["speaker_number_max"] = int(q_val * self.MULTIPLIERS.get(m, 1))
                                        row["speaker_number_type"] = "qualitative range"
                                        return row
                                    else:
                                        row["speaker_number_type"] = "qualitative estimate"
                                        row['speaker_number_numeric'] = int(q_val * self.MULTIPLIERS.get(m, 1))
                                    return row
                    except ValueError:
                        row["speaker_number_type"] = "error"
                        return row
            # ---------- 10: Wide catch for other formats  ----------
            nums = self.RE_NUM.findall(raw)
            if nums:
                try:
                    row["speaker_number_numeric"] = int(nums[0])
                    row["speaker_number_type"] = "exact"
                except ValueError:
                    row["speaker_number_numeric"] = None

                if len(nums) > 1 and self.RE_YEAR.match(nums[1]):
                    row["speaker_number_year"] = nums[1]
                

            return row

        except Exception:
            # Absolute safety net
            row["speaker_number_numeric"] = None
            return row

    def create_plotting_data_column(self, df: pd.DataFrame) -> pd.DataFrame:
        df["plotting_data"] = pd.NA  # start with empty column
        df["speaker_number_min"] = pd.to_numeric(df["speaker_number_min"], errors="coerce")
        df["speaker_number_max"] = pd.to_numeric(df["speaker_number_max"], errors="coerce")
        df["speaker_number_numeric"] = pd.to_numeric(df["speaker_number_numeric"], errors="coerce")

        # Case 1: range → midpoint

        df.loc[df["speaker_number_type"] == "range", "plotting_data"] = (
            (df["speaker_number_min"] + df["speaker_number_max"]) / 2
        )

        # Case 2: extinct or dormant → 1
        df.loc[df["vitality_status"].isin(["extinct", "dormant"]), "plotting_data"] = df["speaker_number_numeric"].min()-0.5

        # Case 3: exact → numeric
        df.loc[df["speaker_number_type"] == "estimate", "plotting_data"] = df["speaker_number_numeric"]
        df.loc[df["speaker_number_type"] == "exact", "plotting_data"] = df["speaker_number_numeric"]
        df.loc[df["speaker_number_type"] == "qualitative estimate", "plotting_data"] = df["speaker_number_numeric"]
        df.loc[df["speaker_number_type"] == "qualitative range", "plotting_data"] = (
            (df["speaker_number_min"] + df["speaker_number_max"])/ 2
        )
        # Case 4: optional - NA handled automatically
        return df
            #number_of_speakers = int(re.search(r'(\d{2,})', raw_value).group()) #first value in the expression is the number of speakers
            #row['speaker_number_numeric'] =  number_of_speakers
                #df.at[index, 'speaker_number_numeric'] = self.remove_commas(raw_value)
            
    def create_tooltip_column_for_barchart(self, df) -> pd.DataFrame:
        '''This function creates a tooltip column for the dataframe.'''
        df["bar_chart_tooltip_value"] = pd.NA  # start with empty column

        df.loc[df["speaker_number_type"] == "range", "bar_chart_tooltip_value"] = (
            df["speaker_number_raw"]
        )
        df.loc[df["speaker_number_type"] == "estimate", "bar_chart_tooltip_value"] = (
            df["speaker_number_raw"]
        )
        df.loc[df["speaker_number_type"] == "qualitative range", "bar_chart_tooltip_value"] = (
            df["speaker_number_raw"]
        )
        df.loc[df["speaker_number_type"] == "qualitative estimate", "bar_chart_tooltip_value"] = (
            df["speaker_number_raw"]
        )
        df.loc[df["speaker_number_type"] == "exact", "bar_chart_tooltip_value"] = (
            int(df["speaker_number_numeric"])
        )
        df.loc[df["vitality_status"].isin(["extinct", "dormant"]), "bar_chart_tooltip_value"] = (
            df["vitality_status"]
        )

        return df   
    
        
        


        

       



    
 

      

 

    