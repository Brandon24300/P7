from flask import Flask, jsonify
from flask import request
from sklearn.preprocessing import MinMaxScaler
from sklearn.impute import SimpleImputer
import os
import pandas as pd
import joblib


def transform(app_train):
    # Drop the target from the training data
    columnsSupp = []

    # if 'SK_ID_CURR' in app_train:
    #     columnsSupp.append('SK_ID_CURR')

    if 'TARGET' in app_train:
        columnsSupp.append('TARGET')

    if len(columnsSupp) > 0:
        train = app_train.drop(columns=columnsSupp)
    else:
        train = app_train

    # train = app_train.drop(columns = columnsSupp)

    features_training = train.columns.values

    # Feature names
    features = list(train.columns)

    # Copy of the testing data

    # Median imputation of missing values
    imputer = SimpleImputer(strategy='median')

    # Scale each feature to 0-1
    scaler = MinMaxScaler(feature_range=(0, 1))

    # Fit on the training data
    imputer.fit(train)

    # Transform both training and testing data
    train = imputer.transform(train)
    # Repeat with the scaler
    scaler.fit(train)
    # X = scaler.transform(train)
    # y = app_train['TARGET'].values
    X = scaler.transform(train)
    y = app_train['TARGET']

    X = pd.DataFrame(data=X, columns=features_training)

    return X, y, features_training


# Chargemnt des données
input_data_dir = os.path.dirname(os.path.realpath(__file__)) + "/../data/"
input_data_cleaned_dir = os.path.dirname(os.path.realpath(__file__)) + "/../data_cleaned/"
df = pd.read_csv(input_data_dir + 'application_train.csv', nrows=5000)
df_cleaned = pd.read_csv(input_data_cleaned_dir + 'app_train_cleaned.csv', nrows=5000)
# df = df.sample(n=10000)

# Chargement du modéle
filename = input_data_cleaned_dir + "random_forest_model.sav"
model = joblib.load(filename)

# Prediction des classes
X_test, y, _ = transform(df_cleaned)
scores = model.predict_proba(X_test)
df['score'] = scores[:, 1]

del df_cleaned

df = df[df['DAYS_EMPLOYED'] < 100000]

# print(df)
# Lancement du serveur 
app = Flask(__name__)


@app.route('/api/clients/')
def clients():
    """

    Exemple 1:
    Récupérer tous les clients avec une partie des attributs
        URL: /api/clients/?fields=SK_CURR ID
        Output [{SK_CURR_ID=10}]

    Exemple 2:
    Récupérer tous les clients
        URL: /api/clients/
        Output [{attribut1=10, attribut2= 20 ...}]

    :param fields la liste des champs souhaités par le separateur suivant ,
    :return: la liste de tous les clients avec les attributs sélectionnées
    """
    args = request.args
    fields = args.get('fields')

    # Si l'utilisateur demande des champs en particulier alors on lui renvoie que cela
    if fields is not None:
        fields = fields.split(",")
    else:
        fields = df.columns.values
    return jsonify({
        'status': 'ok',
        'data': df[fields].to_dict(orient='records')
    })


def safe_cast(val, to_type, default=None):
    """
    Exemple 1:
    Caster une strint en int
        safe_cast("10", int, default=0)
        Output = 10

    Exemple 2 :
    Caster un int en objet
        safe_cast(10, object, default=None)
        Output = None

    :param val: la valeur a caster
    :param to_type: le type a caster int, str, object..
    :param default: la valeur de retour souhaiter si le cast a échoué
    :return:
    """
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


@app.route('/api/clients/<client_id>/')
def client_info(client_id):
    result = df[df['SK_ID_CURR'] == safe_cast(client_id, int, 0)]
    my_cols = [
        "score", "TARGET", "ORGANIZATION_TYPE", "OCCUPATION_TYPE", "NAME_HOUSING_TYPE", "NAME_INCOME_TYPE", "NAME_EDUCATION_TYPE",
        "NAME_CONTRACT_TYPE", "NAME_FAMILY_STATUS", "HOUSETYPE_MODE", "CODE_GENDER", "AMT_ANNUITY", "AMT_CREDIT", "AMT_INCOME_TOTAL"
    ]

    result = result[my_cols]
    return jsonify({
        'status': 'ok',
        'data': result.to_dict(orient='records')
    })


@app.route('/api/stats/<attribut>/')
def client_stat_group(attribut):
    cols = []
    if (attribut == "CODE_GENDER"):
        cols = ["CODE_GENDER", 'TARGET']
    elif attribut == "ORGANIZATION_TYPE":
        cols = ["ORGANIZATION_TYPE", 'TARGET']
    elif attribut == "NAME_EDUCATION_TYPE":
        cols = ["NAME_EDUCATION_TYPE", 'TARGET']
    elif attribut == "HOUSETYPE_MODE":
        cols = ["HOUSETYPE_MODE", 'TARGET']
    elif attribut == "NAME_INCOME_TYPE":
        cols = ["NAME_INCOME_TYPE", 'TARGET']
    else:
        cols = ["CODE_GENDER", 'TARGET']

    result = df.value_counts(cols).to_frame().rename({0: "value"}, axis=1).reset_index()
    records = result.to_dict(orient='records')
    records = calcul_pourcentage(attribut, records)
    # print(result)()
    return jsonify({
        'status': 'ok',
        'data': records
    })


def rename_target_values(df):
    df['TARGET'] = df['TARGET'].replace([0, 1, 2], ["Renboursé", "Non-renboursé", "Notre client"])
    return df


@app.route('/api/stats/etoile/<id_client>/')
def client_etoile(id_client):
    cols = [
        "DAYS_BIRTH", "DAYS_EMPLOYED", "AMT_ANNUITY", "AMT_CREDIT"
    ]

    # df_filtered = df[df['SK_ID_CURR'] != id_client]
    # result = df_filtered.groupby("TARGET")[cols].mean().reset_index()
    id_client = int(id_client)
    df_filtered = df.copy()
    df_filtered.loc[df_filtered["SK_ID_CURR"] == id_client, "TARGET"] = 2
    print(df_filtered["TARGET"].unique())
    result = df_filtered.groupby("TARGET")[cols].mean().reset_index()
    # result = rename_target_values(result)
    result = result.drop("TARGET", axis=1)
    records = result.to_dict(orient='records')
    records = changeFormatOutput(records)

    return jsonify({
        'status': 'ok',
        'data': records
    })


def sum_column(colonne, data):
    compteur = {}
    for row in data:
        cle = row[colonne]
        value = compteur.get(cle, 0)
        value = value + row["value"]
        compteur[cle] = value
    return compteur


def calcul_pourcentage(colonne, data):
    compteur = sum_column(colonne, data)
    for row in data:
        cle = row[colonne]
        value = compteur[cle]
        result = round(100 * (row["value"] / value), 2)
        row['percentage'] = result
    return data


# @app.route('/api/clients/score/',  methods = ['POST'])
# def all_client_score():
#     return None


# @app.route('/api/clients/<client_id>/score/')
# def client_score(client_id):
#     """
#     Exemple 1:
#         /api/clients/10002/score/

#     :param client_id: Id du client
#     :return: list content le score du client ainsi que son id
#     """
#     result = df_score[df_score['SK_ID_CURR'] == safe_cast(client_id, int, 0)]

#     return jsonify({
#         'status': 'ok',
#         'data': result.to_dict(orient='records')
#     })


def changeFormatOutput(data):
    output = []
    for row in data:
        rowOutput = {
            "theta": list(row.keys()),
            "r": list(row.values())
        }
        output.append(rowOutput)
    return output


if __name__ == "__main__":
    print("avant lancement serveur api")
    app.run(debug=False)
