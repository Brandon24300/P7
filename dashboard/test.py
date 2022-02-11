import plotly.express as px
import pandas as pd
import requests
# long_df = px.data.medals_long()
# /api/stats/etoile/


# print(long_df)
API_URL = "http://127.0.0.1:5000/api/"
def getEtoileData(attribut):
    response = requests.get(API_URL + "stats/etoile/{}/".format(attribut) )
    json = response.json()
    return json['data']
#  ORGANIZATION_TYPE => Secteur d'activité
import numpy as np

etoile_data = getEtoileData(100002)

def transformEtoileRowToDf(etoile_row):
    df4 = pd.DataFrame(etoile_row)
    df4['r'] = df4['r'].apply(abs)
    df4['r'] = np.log( 1 * df4['r'].values)
    return df4

df1 = transformEtoileRowToDf(etoile_data[0])
df2 = transformEtoileRowToDf(etoile_data[1])
df3 = transformEtoileRowToDf(etoile_data[2])
# fig = px.line_polar(df4, r='r', theta='theta', line_close=True)
# fig.show()


import plotly.graph_objects as go

categories = ['processing cost','mechanical properties','chemical stability',
              'thermal stability', 'device integration']

fig = go.Figure()

fig.add_trace(go.Scatterpolar(
      r=df1['r'].values,
      theta=df1['theta'].values,
      fill='toself',
      name='Clients qui ont remboursés leur prêt'
))


print(
    df1['r'].values
)
print(df1.columns.values)
fig.add_trace(go.Scatterpolar(
      r=df2['r'].values,
      theta=df2['theta'].values,
      fill='toself',
    # line_close=True,
      name='Clients qui n\'ont pas remboursés leur prêt'
))

fig.add_trace(go.Scatterpolar(
      r=df3['r'].values,
      theta=df3['theta'].values,
      fill='toself',
    # line_close=True,
      name='Notre client'
))


fig.show()
