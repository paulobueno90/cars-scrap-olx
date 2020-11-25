import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import lxml.html as lh
import locale
import fake_useragent
import concurrent.futures
import datetime as dt
import threading
from tkinter import *
from tkinter import Button
#from tkinter import ttk
from tkinter.ttk import Progressbar
import time



locale.setlocale(locale.LC_NUMERIC, '')


pd.set_option('display.max_rows', 200)
pd.set_option('display.max_columns', 200)

headers = {
        'User-Agent': fake_useragent.UserAgent().chrome,
}

def get_brand():


    url = f'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios'

    page = requests.get(url, headers=headers)

    doc = lh.fromstring(page.content)

    # Parse data that are stored between <select>..</select> of HTML
    select_elements = doc.xpath("//select")

    brands = [i.text.replace(' - ', '-').replace(' ', '-').upper() for i in select_elements[0]]

    return brands




def get_model(brand):

    if brand == 'marca':
        models = ['modelo']
        return models

    else:
        url = f'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/{brand}'
        page = requests.get(url, headers=headers)

        doc = lh.fromstring(page.content)

        # Parse data that are stored between <select>..</select> of HTML
        select_elements = doc.xpath("//select")

        models = [i.text.replace(' - ', '-').replace(' ', '-').upper() for i in select_elements[1]]

        return models


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
        select_date = doc.xpath('//li/a/div/div[2]/div[1]/div[2]/div[4]/div/span[1]')
        select_time = doc.xpath('//li/a/div/div[2]/div[1]/div[2]/div[4]/div/span[2]')


        with open('links.csv', 'a') as f:
            for ind, i in enumerate(select_elements[3:]):
                f.write(f"{i},{select_date[ind].text},{select_time[ind].text}\n")


        print(f"{dt.datetime.now()} | PAGE: {page_index} | ADDED: {len(select_elements[3:])} links ")

    for state in estados:
        url_state = f'{state}.'
        scrap(url_state)


def search_ads(frame=False):
    global ad_list
    global links_len
    ad_list = 0


    links = pd.read_csv('links.csv')
    links_len = links.shape[0]
    links = (i for i in list(links['links']))


    df2 = pd.read_csv("modelos.csv")
    df2['id'] = df2['id'].apply(lambda x: x.lower())

    df3 = pd.read_csv("marcas.csv")


    with open("consulta_olx.csv", 'w', encoding='utf-8') as arq:
        arq.write(f"model;brand;color;transmission;year;km;preco;link;postal_code;description;brand_id;model_id\n")


    def scrap_ad(link):

        global ad_list

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

        labels = set(['postal_code', 'link','description', 'brand', 'model', 'category', 'year', 'km', 'eng', 'fuel', 'transmission', 'steering', 'color', 'doors', 'last_num_plate', 'preco', 'brand_id', 'model_id'])
        missing = labels - set(ad.keys())
        if missing:
            for i in missing:
                ad[i] = "nao-preenchido"
        with open("consulta_olx.csv", 'a', encoding='utf-8') as arq:
            arq.write(f"{ad['model']};{ad['brand']};{ad['color']};{ad['transmission']};{ad['year']};{ad['km']};{ad['preco']};{ad['link']};{ad['postal_code']};{ad['description']};{ad['brand_id']};{ad['model_id']}\n")
        ad_list += 1
        print(f"[{dt.datetime.now()}] ITEM: {ad_list}  | MARCA: {ad['brand']} | MODELO:{ad['model']} | ANO: {ad['year']} | PREÇO: {ad['preco']} | KM: {ad['km']}")

    """with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(scrap_ad, links)"""

    # creating tkinter window

    if frame:
        # Progress bar widget
        progress = Progressbar(frame, orient=HORIZONTAL,
                               length=300, mode='determinate')

        def progressbar():


            def bar():
                global ad_list



                while ad_list < links_len - 1:
                    time.sleep(2)
                    progress['value'] = ((ad_list / links_len) * 100)
                    frame.update_idletasks()
                else:
                    print(f"Scraping Ended - Total {ad_list} ads")
                    progress.destroy()


            def thread_scraper():

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    executor.map(scrap_ad, links)


            func1 = threading.Thread(target=bar)
            func2 = threading.Thread(target=thread_scraper)

            func1.start()
            func2.start()

        progress.grid(row=6, column=0)

        # This button will initialize
        # the progress bar
        Button(frame, text='Start', command=progressbar).grid(row=7, column=0)

        # infinite loop
        mainloop()

    else:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(scrap_ad, links)





def get_links(brand, model, state):

    estados = ['ac', 'al', 'ap', 'am', 'ba', 'ce', 'df', 'es', 'go', 'ma', 'mt',
               'ms', 'mg', 'pa', 'pb', 'pr', 'pe', 'pi', 'rj', 'rn', 'rs',
               'ro', 'rr', 'sc', 'sp', 'se', 'to']

    with open('links.csv', 'w') as f:
        f.write("links,data,horario\n")

    if state:
        if state.lower() == 'todos':
            for uf in estados:
                search_links(brand, model, uf)
        else:
            search_links(brand, model, state)
    else:
        for uf in estados:
            search_links(brand, model, uf)




if __name__ == '__main__':
    search_ads()


