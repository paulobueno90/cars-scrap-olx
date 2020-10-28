import requests
import fake_useragent
import json
import pandas as pd
from time import sleep
import numpy as np
import os
from urllib.error import HTTPError

# SITE_API = "http://fipeapi.appspot.com/"

#pd.set_option('display.max_rows', 200)
pd.set_option('display.max_columns', 200)


headers = {
        'User-Agent': fake_useragent.UserAgent().chrome,
    }

def get_models():
    try:
        modelos = pd.read_csv('modelos.csv')

    except:


        try:
            marcas = pd.read_csv('marcas.csv')

        except:

            url_marcas = "http://fipeapi.appspot.com/api/1/carros/marcas.json"
            marcas = pd.read_json(url_marcas)
            marcas.to_csv('marcas.csv', index=False)

        with open('modelos.csv', 'w', encoding='utf-8') as f:
            f.write("fipe_marca,name,marca,key,id,fipe_name\n")

        for index, row in marcas.iterrows():


            sleep(1)
            url_modelos = f"http://fipeapi.appspot.com/api/1/carros/veiculos/{row.id}.json"
            modelos = pd.read_json(url_modelos)
            for i, r in modelos.iterrows():
                with open('modelos.csv', 'a', encoding='utf-8') as f:
                    f.write(f"{row.fipe_name},{r.name},{r.key},{r.id},{r.fipe_name}\n")


            print(f"[id: {row.id} | {row.fipe_name}] - Ok !")



def get_fipe_price(marca, modelo, ano):



    url_md = f"http://fipeapi.appspot.com/api/1/carros/veiculo/{marca}/{modelo}.json"




    year = pd.read_json(url_md)
    year['ano'] = year['key'].apply(lambda x: x[0:4])


    filt = year['ano'] == ano
    year = year.loc[filt]

    if year.empty:

        return 'missing'

    else:
        year_key = year['id'].values[0]


        url_final = f"http://fipeapi.appspot.com/api/1/carros/veiculo/{marca}/{modelo}/{year_key}.json"

        response = requests.get(url_final)

        price_json = json.loads(response.content)

        try:

            price = price_json['preco']

            return price

        except KeyError:
            print("[REQUEST LIMIT] - Will retry in 60 seconds")
            sleep(60)

            try:
                response = requests.get(url_final)
                price_json = json.loads(response.content)
                price = price_json['preco']
                return price

            except:
                return 'error'


def get_models_price():

    df = pd.read_csv("consulta_olx.csv", encoding='latin-1', sep=';')
    df.dropna(inplace=True)
    df['brand_id'] = df['brand_id'].apply(lambda x: int(x))
    df['model_id'] = df['model_id'].apply(lambda x: int(x))
    df = df.groupby(['brand_id', 'model_id', 'year']).count()

    models = list(df.index)

    with open('consulta_fipe.csv', 'w', encoding='utf-8') as arq:
        arq.write(f"brand_id;model_id;year;price\n")


    for i in iter(models):

        try:
            item = get_fipe_price(i[0], i[1], i[2])
            with open('consulta_fipe.csv', 'a', encoding='utf-8') as arq:
                arq.write(f"{i[0]};{i[1]};{i[2]};{item}\n")
            print(f"[ADD ITEM] - Brand ID: {i[0]} | Model ID: {i[1]} | Year: {i[2]} | Price: {item}")

        except HTTPError:
            print(f"[FAIL TO ADD] - Brand ID: {i[0]} | Model ID: {i[1]} | Year: {i[2]}")
            print("Will retry in 60 seconds - First Attempt")
            try:
                sleep(60)
                item = get_fipe_price(i[0], i[1], i[2])
                with open('consulta_fipe.csv', 'a', encoding='utf-8') as arq:
                    arq.write(f"{i[0]};{i[1]};{i[2]};{item}\n")
                print(f"[ADD ITEM] - Brand ID: {i[0]} | Model ID: {i[1]} | Year: {i[2]} | Price: {item}")


            except HTTPError:

                print(f"[FAIL TO ADD] - Brand ID: {i[0]} | Model ID: {i[1]} | Year: {i[2]}")

                print("Will retry in 30 seconds - Second Attempt")

                try:
                    sleep(30)

                    item = get_fipe_price(i[0], i[1], i[2])


                    with open('consulta_fipe.csv', 'a', encoding='utf-8') as arq:
                        arq.write(f"{i[0]};{i[1]};{i[2]};{item}\n")

                    print(f"[ADD ITEM] - Brand ID: {i[0]} | Model ID: {i[1]} | Year: {i[2]} | Price: {item}")

                except HTTPError:
                    print(f"[FAIL TO ADD] - Brand ID: {i[0]} | Model ID: {i[1]} | Year: {i[2]}")
                    print("Will retry in 30 seconds - Third Attempt")
                    try:
                        sleep(30)
                        item = get_fipe_price(i[0], i[1], i[2])

                        with open('consulta_fipe.csv', 'a', encoding='utf-8') as arq:
                            arq.write(f"{i[0]};{i[1]};{i[2]};{item}\n")
                        print(f"[ADD ITEM] - Brand ID: {i[0]} | Model ID: {i[1]} | Year: {i[2]} | Price: {item}")

                    except:
                        item = np.nan
                        with open('consulta_fipe.csv', 'a', encoding='utf-8') as arq:
                            arq.write(f"{i[0]};{i[1]};{i[2]};{item}\n")
                        print(f"[FAILED ITEM] - Brand ID: {i[0]} | Model ID: {i[1]} | Year: {i[2]} | Price: {item}")


def add_fipe2csv():

    df = pd.read_csv("consulta_olx.csv", encoding="latin-1", sep=";")
    df.dropna(inplace=True)



    fipe = pd.read_csv("consulta_fipe.csv", encoding="utf-8", sep=";")

    df['model_id'] = df['model_id'].apply(lambda x: int(x))
    df['brand_id'] = df['brand_id'].apply(lambda x: int(x))
    df['year'] = df['year'].apply(lambda x: str(x))
    fipe['model_id'] = fipe['model_id'].apply(lambda x: int(x))
    fipe['brand_id'] = fipe['brand_id'].apply(lambda x: int(x))
    fipe['year'] = fipe['year'].apply(lambda x: str(x))

    lista = []
    for i, row in df.iterrows():

        filt = (fipe['brand_id'] == row.brand_id) & (fipe['model_id'] == row.model_id) & (fipe['year'] == row.year)

        for _, p in fipe.loc[filt].iterrows():
            item = p.price

        lista.append(item)



    df['fipe'] = lista
    df.replace('missing', np.nan, inplace=True)
    df.dropna(inplace=True)
    df.to_csv("consulta_olx.csv", encoding='utf-8', sep=';', index=False)

