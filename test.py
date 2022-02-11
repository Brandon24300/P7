import requests
import pandas as pd
API_URL = "http://127.0.0.1:5000/api/"
test = "clients/?fields=SK_ID_CURR"
response = requests.get(API_URL + test)
json = response.json()

# print(pd.DataFrame(json['data']))
# print(json['data'])

clients_output = []
for index, client in enumerate(json['data']):
    clients_output.append({
        "label": client["SK_ID_CURR"],
        "value": client["SK_ID_CURR"],
    })

print(clients_output)