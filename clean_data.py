import pandas as pd
import numpy as np
import datetime
pd.options.display.max_columns = None
#df = pd.read_csv("consulta_olx.csv", encoding="utf-8", sep=";")


def clean_data():

    def description_clean(string):

        item = string.lower()
        item = item.replace('á', 'a')
        item = item.replace('é', 'e')

        if 'agio' in item:
            return np.nan
        elif "entrada a vista" in item:
            return np.nan
        elif "contemplada" in item:
            return np.nan
        else:
            return item


    df = pd.read_csv('consulta_olx.csv', encoding='latin-1', sep=';')

    # Filtering Year Data (Incorrect Data)
    filt = df['year'] == '1950 ou anterior'
    df.loc[filt] = np.nan
    df.dropna(inplace=True)

    # Filtering description expressions that can be false ads
    df['description'] = df['description'].apply(lambda x: description_clean(x))

    # Creating Age Column
    current_year = datetime.date.today().year
    df['age'] = df['year'].apply(lambda x: current_year - int(x))
    df['km_ano'] = df['km'] / df['age']
    df['km_ano'] = df['km_ano'].values
    df['km_ano'] = df['km_ano'].apply(lambda x: x ** 2.5)

    filt = df['age'] >= 0
    df = df.loc[filt]

    filt = df['km'] <= 400000
    df = df.loc[filt]


    df.to_csv('consulta_olx2.csv', encoding='utf-8', sep=';', index=False)


def variables_adjustment():

    df = pd.read_csv('consulta_olx2.csv', encoding='utf-8', sep=';')

    # Creating 'dif_fipe': price proportion to price national index(fipe)
    df['dif_fipe'] = df['preco'] / df['fipe']

    # Filtering price outliers
    mask = (df['dif_fipe'] < 2) & (df['dif_fipe'] > 0.6)
    df = df.loc[mask]

    models = df.groupby(['brand_id', 'model_id', 'age']).count()
    models = list(models.index)
    df['price_std'] = 0

    for i in models:
        filt = (df['brand_id'] == i[0]) & (df['model_id'] == i[1]) & (df['age'] == i[2])
        _ = df.loc[filt]

        pricestd = _['preco'].std()

        df.loc[filt, 'price_std'] = _['preco'].std()

        filt_outlier = ((df['brand_id'] == i[0]) & (df['model_id'] == i[1]) & (df['age'] == i[2])) & (
                    (df['preco'] >= (df['fipe'] + (pricestd * 2))) | (df['preco'] <= (df['fipe'] - (pricestd * 2))))
        df.loc[filt_outlier] = np.nan

    df.dropna(inplace=True)

        #df.loc[filt, 'preco_medio'] = _.preco.mean()
    filt = df['km'] < 1000
    df.loc[filt, ['preco', 'km', 'year','link']].to_csv('fraude.csv',sep=';')

    # Filtering Kilometers (droping outliers)

    filt = df['km'] > 1000
    df = df.loc[filt]

    filt = df['km'] <= df['km'].quantile(0.97)
    df = df.loc[filt]


    # Year: float -> int
    df['year'] = df['year'].apply(lambda x: int(x))



    # Creating new variable
    # df['fipe_km'] = df['fipe'] / df['km']

    df.to_csv('cleaned_consulta_olx.csv', encoding='utf-8', sep=';', index=False)

def df_adjust():
    df = pd.read_csv('consulta_olx2.csv', encoding='latin-1', sep=';')
    df_model = pd.read_csv('cleaned_consulta_olx.csv', encoding='latin-1', sep=';')

    # Adjust Color Differences Between Model vs Dataset
    base_colors = set(df.color.values)
    model_color = set(df_model.color.values)
    color_dif = base_colors - model_color

    if color_dif:
        for i in color_dif:
            if 'outra' in base_colors:
                filt = df['color'] == i
                df.loc[filt, 'color'] = 'outra'
            else:
                filt = df['color'] == i
                df.loc[filt, 'color'] = np.nan
                df.dropna(inplace=True)

    # Adjust Car-Model Differences Between Model vs Dataset
    base_model = set(df.model.values)
    model_model = set(df_model.model.values)
    model_dif = base_model - model_model

    if model_dif:
        for i in model_dif:
            filt = df['model'] == i
            df.loc[filt, 'model'] = np.nan
            df.dropna(inplace=True)

    # Adjust Transmission Differences Between Model vs Dataset
    base_transmission = set(df.transmission.values)
    model_transmisstion = set(df_model.transmission.values)
    transmission_dif = base_transmission - model_transmisstion

    if transmission_dif:
        for i in transmission_dif:
            filt = df['transmission'] == i
            df.loc[filt, 'transmission'] = np.nan
            df.dropna(inplace=True)

    df.to_csv('consulta_olx2.csv', encoding='utf-8', sep=';', index=False)



