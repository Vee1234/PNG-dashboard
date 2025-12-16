import pandas as pd
import json
class DataLoader:
    def __init__(self):
        pass

    def load_data_from_json(self, data_address: str) -> dict:
        # Simulate loading data
        with open(data_address, 'r') as file:
            data = json.load(file)
        return data