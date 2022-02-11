# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from curses.ascii import isdigit
import dash
from dash import dcc
from dash import html
from numpy.core.fromnumeric import nonzero
from numpy.lib.utils import info
import plotly.express as px
import pandas as pd
import requests
import dash_table
from dash.dependencies import Input, Output
import numpy as np
import plotly.graph_objects as go
df4 = pd.DataFrame(dict(
    r=[1, 5, 2, 2, 3],
    theta=['processing cost','mechanical properties','chemical stability',
           'thermal stability', 'device integration']))
# fig = px.line_polar(df, r='r', theta='theta', line_close=True)

app = dash.Dash(__name__)

API_URL = "http://127.0.0.1:5000/api/"


def getClientInformation(identifiant):
    url_client_info = API_URL + "clients/{}/".format(identifiant)
    response = requests.get(url_client_info)
    return response.json()['data'][0]

def getEtoileData(attribut):
    response = requests.get(API_URL + "stats/etoile/{}/".format(attribut) )
    json = response.json()
    return json['data']

def transformEtoileRowToDf(etoile_row):
    df4 = pd.DataFrame(etoile_row)
    df4['r'] = df4['r'].apply(abs)
    df4['r'] = np.log( 1 * df4['r'].values)
    return df4


def getClientsIdentifiants() -> dict:
    """

    :return: {success: true, data: []}
    """
    response = requests.get(API_URL + "clients/?fields=SK_ID_CURR")
    json = response.json()
    return json

def getStatsGroup(attribut):
    response = requests.get(API_URL + "stats/{}/".format(attribut) )
    json = response.json()
    return json['data']

def getOptionsClientsIdentifiants():
    """
        Transforme les identifiants clients dans le format attendu de la liste déroulante
    :return:
    """
    json = getClientsIdentifiants()
    clients_output = []
    for index, client in enumerate(json['data']):
        clients_output.append({
            "label": client["SK_ID_CURR"],
            "value": client["SK_ID_CURR"],
        })
    return clients_output


def getTitreGrapheSelonValeur(valeur):
    if valeur == "ORGANIZATION_TYPE":
        return "Graphique de remboursement selon le secteur d'activité"
    elif valeur == "CODE_GENDER":
        return "Graphique de remboursement selon le genre"
    elif valeur == "NAME_EDUCATION_TYPE":
        return "Graphique de remboursement selon le niveau d'éducation"
    elif valeur == "HOUSETYPE_MODE":
        return "Graphique de remboursement selon le type de maison"
    elif valeur == "NAME_INCOME_TYPE":
        return "Graphique de remboursement selon le type de revenu"
    else: 
        return "Titre non défini"
        

def ajoutFigureEtoileRemboursement(fig, df):
    fig.add_trace(go.Scatterpolar(
      r=df['r'].values,
      theta=df['theta'].values,
      fill='toself',
      name='Clients qui ont pas remboursés leur prêt'
    ))
    
def ajoutFigureEtoileNonRembourse(fig, df):
      fig.add_trace(go.Scatterpolar(
      r=df['r'].values,
      theta=df['theta'].values,
      fill='toself',
      name='Clients qui n\'ont pas remboursés leur prêt'
    ))
      
def ajoutFigureEtoileNotreClient(fig, df):
      fig.add_trace(go.Scatterpolar(
      r=df['r'].values,
      theta=df['theta'].values,
      fill='toself',
      name='Notre client'
    ))


def getDataFrameClientsIdentifiants():
    json = getClientsIdentifiants()
    return pd.DataFrame(json['data'])


options_identifiants = getOptionsClientsIdentifiants()
client_actuel = options_identifiants[0]
info_client = getClientInformation(client_actuel['value'])
stats_gender = getStatsGroup("CODE_GENDER")
stats_gender = pd.DataFrame(stats_gender)
etoile_data = getEtoileData(100002)

df_etoile1 = transformEtoileRowToDf(etoile_data[0])
df_etoile2 = transformEtoileRowToDf(etoile_data[1])
df_etoile3 = transformEtoileRowToDf(etoile_data[2])

etoile_figure = go.Figure()
ajoutFigureEtoileRemboursement(etoile_figure, df_etoile1)
ajoutFigureEtoileNonRembourse(etoile_figure, df_etoile2)
ajoutFigureEtoileNotreClient(etoile_figure, df_etoile3)


      
# print(info_client)
print("donnée chargé")
# df_clients_identifiants = getDataFrameClientsIdentifiants()

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options


columns_datable = [
    {
     "name": "Sexe",
     "id":  "CODE_GENDER"
    },
     {
     "name": "Status",
     "id":  "NAME_FAMILY_STATUS"
    },
      {
     "name": "Education",
     "id":  "NAME_EDUCATION_TYPE"
    },
    {
        "name": "Annuité",
        "id": "AMT_ANNUITY",
    },
    {
        "name": "Crédit",
        "id": "AMT_CREDIT",
    },
      {
        "name": "Revenus",
        "id": "AMT_INCOME_TOTAL",
    },
    {
        "name": "Type de revenu",
        "id": "NAME_INCOME_TYPE"
    },
    {
        "name": "Type de maison",
        "id": "HOUSETYPE_MODE"
    },

]

# print(info_client)

app.layout = html.Div(children=[
    
    html.Div(
        className='n-header',
        children= [
            html.H1(children='Tableau de bord - Accord crédit '),
            html.Div(children=[
                dcc.Dropdown(
                    id='demo-dropdown',
                    options=options_identifiants,
                    value=options_identifiants[0]['value']
                ),
            ]),
        ]
    ),
   
    html.Div(
        className = 'n-global-stats',
        children = [
            dcc.Store(id='second-value'),
            dcc.Store(id='intermediate-value'),
            html.Div(className='n-card', children = 
            [
                html.Div(className= 'n-card-wrapper', children = 
                [
                    html.Div(
                        className='n-card-title',
                        children=
                        '''
                        Probabilité d'impayé
                        ''',
                    ),
                    html.Div(
                        id="n-proba",
                        className= 'n-card-value',
                        children=
                        '''
                        
                        ''' + str(info_client['score'])
                    ),
                ]),
            ]),
            html.Div(className='n-card', children = 
            [
                html.Div(className= 'n-card-wrapper', children = 
                [
                    html.Div(
                        className='n-card-title',
                        children=
                        '''
                        Annuités
                        ''',
                    ),
                    html.Div(
                        id="n-annuite",
                        className= 'n-card-value',
                        children=
                        '''
                        ''' + str(info_client['AMT_ANNUITY'])
                    ),
                ]),
            ]),
            html.Div(className='n-card', children = 
            [
                html.Div(className= 'n-card-wrapper', children = 
                [
                    html.Div(
                        className='n-card-title',
                        children=
                        '''
                        Revenus
                        ''',
                    ),
                    html.Div(
                        id="n-income",
                        className= 'n-card-value',
                        children=
                        '''
                        ''' + str(info_client['AMT_INCOME_TOTAL'])
                    ),
                ]),
            ]),
        ]
    ),
    html.Div(
      className="n-card n-container-info-clients",
      children = [
        html.Div(
            className='n-card-title',
            children='''
            Informations clients
        '''),
        dash_table.DataTable(
            id='table',
            columns=columns_datable,
            data=[info_client],
        ),
      ]   
    ),
    dcc.Tabs(
        className= "n-tabs",
        children=[
            dcc.Tab(
                label='Comparaison autre clients',
                children = [
                         dcc.Dropdown(
                            id='test-dropdown',
                            options=[
                                {
                                    "label": "Secteur d'activité",
                                    "value": "ORGANIZATION_TYPE",
                                },
                                {
                                    "label": "Genre",
                                    "value": "CODE_GENDER",
                                },
                                {
                                    "label": "Type de revenu",
                                    "value": "NAME_INCOME_TYPE",
                                },
                                {
                                    "label": "Niveau d'éducation",
                                    "value": "NAME_EDUCATION_TYPE",
                                },
                                {
                                    "label": "Type de maison",
                                    "value": "HOUSETYPE_MODE",
                                } 
                                # # {
                                #     "label": "Niveau de revenu",
                                #     "value": "revenu",
                                # }
                            ],
                            value='CODE_GENDER'
                        ),
                        html.Div(
                            className="n-secteur",
                            children = [
                                dcc.Graph(id="etoile_chart", figure=etoile_figure),
                                dcc.Graph(
                                    id="fig_chart",
                                    figure= px.bar(stats_gender, x="CODE_GENDER", y="value", color="TARGET", title=getTitreGrapheSelonValeur("CODE_GENDER"), text = "percentage")
                                )
                            ]
                        ),
                ]
            ),
            dcc.Tab(
                label='Interpretabilité',
                children = [
                     html.H3(
                      children = '''
                               Explications du modéle
                            '''
                    ),
                    html.Div(
                        className="n-explication-model"
                    )
                ]
            )
        ]
    ),
])
import json

@app.callback(
    Output('intermediate-value', 'data'),
    Input('demo-dropdown', 'value'))
def clean_data(value):
    info_client = getClientInformation(value)
    return json.dumps(info_client)

# n-income n-annuite
@app.callback(
    Output('n-annuite', 'children'),
    Input('intermediate-value', 'data'))
def update_card_annuite(my_json):
    data = json.loads(my_json)
    return data['AMT_ANNUITY']

@app.callback(
    Output('n-income', 'children'),
    Input('intermediate-value', 'data'))
def update_card_annuite(my_json):
    data = json.loads(my_json)
    return data['AMT_INCOME_TOTAL']

@app.callback(
    Output('n-proba', 'children'),
    Input('intermediate-value', 'data'))
def update_card_annuite(my_json):
    data = json.loads(my_json)
    score = data['score']
    return "{:.2f}".format(score)

@app.callback(
    Output('table', 'data'), 
    Input('intermediate-value', 'data')
    )
def update_table(my_json):
    data = json.loads(my_json)
    return [data]
    
    
@app.callback(
    Output('fig_chart', 'figure'),
    Input('test-dropdown', 'value')
)
def update_barchart(attribut):
    data = getStatsGroup(attribut)
    df_temp = pd.DataFrame(data)
    return px.bar(df_temp, x=attribut, y="value", color="TARGET", title=getTitreGrapheSelonValeur(attribut), text = "percentage")


@app.callback(
    Output('etoile_chart', 'figure'), 
    Input('demo-dropdown', 'value')
)   
def update_etoile_char(id_client):
    etoile_data = getEtoileData(id_client)

    df_etoile1 = transformEtoileRowToDf(etoile_data[0])
    df_etoile2 = transformEtoileRowToDf(etoile_data[1])
    df_etoile3 = transformEtoileRowToDf(etoile_data[2])

    etoile_figure = go.Figure()
    ajoutFigureEtoileRemboursement(etoile_figure, df_etoile1)
    ajoutFigureEtoileNonRembourse(etoile_figure, df_etoile2)
    ajoutFigureEtoileNotreClient(etoile_figure, df_etoile3)
    return etoile_figure
if __name__ == '__main__':
    app.run_server(debug=True)
