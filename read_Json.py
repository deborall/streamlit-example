import json
import pandas as pd
with open('TME.US.json') as data_file:    
    #    data = json.load(data_file)
    data = json.loads(data_file.read())
    options_list = data['data']
    for expiry_item in options_list:
        item = expiry_item['options']['CALL']
        df = pd.json_normalize(item)

print(df)
