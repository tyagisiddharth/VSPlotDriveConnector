import requests
import json
import pandas as pd 

pd.options.display.max_columns = None

tpg_config = {
    'case': "TSLA/MPN5P/2024-12-01/20241201 VSPlotDriveConnector_predictions_plots_TSLA_MPN5P_200001-202203_711_DM-20230103-20230227",
    'predicted_targets': [5.3, 4.3, 6.4, 7.5], 
    'actual_targets': [4.4, 5.5, 8.1, 10.4],
    'dates': ["2024-05-01","2024-05-02","2024-05-07","2024-05-08"],
}

for key in tpg_config.keys():
    tpg_config[key] = json.dumps(tpg_config[key])

query = f'''
    query {{
        PlotsGenerator(
            case: {tpg_config["case"]}
            predicted_targets: {tpg_config["predicted_targets"]}
            actual_targets: {tpg_config["actual_targets"]}
            dates: {tpg_config["dates"]}
        ) {{
            success,
            error,
            file_web_link,
            folder_web_link
        }}
    }}
'''

headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Connection': 'keep-alive',
        'DNT': '1'
    }

response = requests.post('http://192.168.41.216:3999/graphql',json={"query":query},headers=headers).json()
File_Web_link = response['data']['PlotsGenerator']['file_web_link']
Folder_web_link = response['data']['PlotsGenerator']['folder_web_link']
print('File_Web_Link', File_Web_link)
print('Folder_Web_link:', Folder_web_link)