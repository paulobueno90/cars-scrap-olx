import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import lxml.html as lh
import locale
import fake_useragent
import concurrent.futures
import datetime as dt



locale.setlocale(locale.LC_NUMERIC, '')


pd.set_option('display.max_rows', 200)
pd.set_option('display.max_columns', 200)

headers = {
        'User-Agent': fake_useragent.UserAgent().chrome,
}

def get_brand_and_model():
    url = f'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios'

    page = requests.get(url, headers=headers)

    doc = lh.fromstring(page.content)

    # Parse data that are stored between <select>..</select> of HTML
    select_elements = doc.xpath("//select")

    brands = [i.text.replace(' - ', '-').replace(' ', '-').lower() for i in select_elements[0]]

    def get_model(brand):

        if brand == 'marca':
            brand = ''

        url = f'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/{brand}'
        page = requests.get(url, headers=headers)

        doc = lh.fromstring(page.content)

        # Parse data that are stored between <select>..</select> of HTML
        select_elements = doc.xpath("//select")

        model = [i.text.replace(' - ', '-').replace(' ', '-').lower() for i in select_elements[1]]
        print(f'[{brand} - ok]')
        return model


    return { brand : get_model(brand)[1:] for i, brand in enumerate(brands) if i > 0}


def search_links(marca=None, modelo=None, estado=None):


    url_estado = estado
    url_marca = marca
    if marca:
        url_marca = f'{marca}/'
    if estado:
        url_estado = f'{estado}.'
        estados = [estado]


    def scrap(state):
        url = f"https://{state}olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/{url_marca}{modelo}?o=1"
        page = requests.get(url, headers=headers)

        doc = lh.fromstring(page.content)

        # Parse data that are stored between <select>..</select> of HTML
        select_qtd = doc.xpath('//*[@id="column-main-content"]/div[8]/div/span')
        qtd_items = int(select_qtd[0].text.replace(' - ', '-').replace('.', '').split(' ')[2])
        if qtd_items > 50:
            paginas = int(qtd_items / 50) + 1
        elif qtd_items == 0:
            paginas = 0
        else:
            paginas = 1
        print(f"\nESTADO: {state[:2].upper()} | TOTAL PAGES: {paginas}  | TOTAL LINKS: {qtd_items}")
        lista = (i for i in range(1, paginas + 1))


        if paginas > 0:

            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(scrap_links, lista)

        else:
            print('Não há resultados')

    def scrap_links(page_index):

        url = f"https://{url_estado}olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/{marca}/{modelo}?o={page_index}"
        page = requests.get(url, headers=headers)

        doc = lh.fromstring(page.content)

        select_elements = doc.xpath('//li/a/@href')
        with open('links.csv', 'a') as f:
            for i in select_elements[3:]:
                f.write(f"{i}\n")

        print(f"{dt.datetime.now()} | PAGE: {page_index} | ADDED: {len(select_elements[3:])} links ")

    for state in estados:
        url_state = f'{state}.'
        scrap(url_state)


def search_ads():

    ad_list = []

    links = pd.read_csv('links.csv')
    links = (i for i in list(links['links']))

    df2 = pd.read_csv("modelos.csv")
    df2['id'] = df2['id'].apply(lambda x: x.lower())

    df3 = pd.read_csv("marcas.csv")


    with open("consulta_olx.csv", 'w', encoding='utf-8') as arq:
        arq.write(f"model;brand;color;transmission;year;km;preco;link;postal_code;description;brand_id;model_id\n")


    def scrap_ad(link):
        url = link

        page = requests.get(url, headers=headers)

        doc = page.content

        soup = BeautifulSoup(doc, 'html.parser')

        ad = {}



        for item in soup.select('.cIfjkh'):
            ad['preco'] = item.get_text().lstrip('R$ ').replace('.', '')

        for item in soup.select('.eNZSNe'):

            if 'Modelo' in item.get_text():
                ad['model'] = item.get_text().replace('Modelo', '')

            elif 'Marca' in item.get_text():
                ad['brand'] = item.get_text().replace('Marca', '')

            elif 'Tipo' in item.get_text():
                ad['category'] = item.get_text().replace('Tipo de veículo', '')

            elif 'Ano' in item.get_text():
                ad['year'] = item.get_text().replace('Ano','')

            elif 'Quilometragem' in item.get_text():
                ad['km'] = item.get_text().replace('Quilometragem', '')

            elif 'Potência' in item.get_text():
                ad['eng'] = item.get_text().replace('Potência do motor', '')

            elif 'Combustível' in item.get_text():
                ad['fuel'] = item.get_text().replace('Combustível', '')

            elif 'Câmbio' in item.get_text():
                ad['transmission'] = item.get_text().replace('Câmbio', '').replace('á', 'a')

            elif 'Direção' in item.get_text():
                ad['steering'] = item.get_text().replace('Direção', '')

            elif 'Cor' in item.get_text():
                ad['color'] = item.get_text().replace('Cor', '').lower()

            elif 'Portas' in item.get_text():
                ad['doors'] = item.get_text().replace('Portas', '')

            elif 'Final' in item.get_text():
                ad['last_num_plate'] = item.get_text().replace('Final de placa', '')


        ad['link'] = url
        ad['postal_code'] = soup.select('.kaNiaQ')[0].get_text()

        desc = soup.select('.eOSweo')[0].get_text()
        desc = desc.replace('\n',' ')
        desc = desc.replace(';',':')
        ad['description'] = desc

        ad['model'] = ad['model'].replace(ad['brand'], '').lstrip().lower()

        # MODEL - FIPE ID
        filt = df2['id'] == ad['model']
        items = df2.loc[filt]
        item = items['key'].to_list()
        if item:
            ad['model_id'] = item[0]

        else:
            ad['model_id'] = np.nan

        # BRAND - FIPE ID
        filt = df3['name'] == ad['brand']
        items = df3.loc[filt]
        item = items['id'].to_list()

        if item:
            ad['brand_id'] = item[0]

        else:
            ad['brand_id'] = np.nan

        with open("consulta_olx.csv", 'a', encoding='utf-8') as arq:
            arq.write(f"{ad['model']};{ad['brand']};{ad['color']};{ad['transmission']};{ad['year']};{ad['km']};{ad['preco']};{ad['link']};{ad['postal_code']};{ad['description']};{ad['brand_id']};{ad['model_id']}\n")
        ad_list.append(ad)
        print(f"[{dt.datetime.now()}] ITEM: {len(ad_list)}  | MARCA: {ad['brand']} | MODELO:{ad['model']} | ANO: {ad['year']} | PREÇO: {ad['preco']} | KM: {ad['km']}")


    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(scrap_ad, links)

def get_links(brand, model, state):

    estados = ['ac', 'al', 'ap', 'am', 'ba', 'ce', 'df', 'es', 'go', 'ma', 'mt',
               'ms', 'mg', 'pa', 'pb', 'pr', 'pe', 'pi', 'rj', 'rn', 'rs',
               'ro', 'rr', 'sc', 'sp', 'se', 'to']

    with open('links.csv', 'w') as f:
        f.write("links\n")

    if state:
        search_links(brand, model, state)
    else:
        for uf in estados:
            search_links(brand, model, uf)




