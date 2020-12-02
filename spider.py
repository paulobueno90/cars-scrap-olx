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
import datetime
from fipe import fipe_id_brand_model



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

        monthvalue_dict = {
            "jan":"01",
            "fev":"02",
            "mar":"03",
            "abr":"04",
            "mai":"05",
            "jun":"06",
            "jul":"07",
            "ago":"08",
            "set":"09",
            "out":"10",
            "nov":"11",
            "dez":"12"
        }

        delta_0day = datetime.datetime.today().date()
        delta_1day = delta_0day - datetime.timedelta(days=1)
        year_now = datetime.datetime.today().year

        with open('links.csv', 'a') as f:
            for ind, i in enumerate(select_elements[3:]):
                ad_date = select_date[ind].text
                ad_date = ad_date.lower()

                if ad_date == "hoje":
                    ad_date = delta_0day

                elif ad_date == "ontem":
                    ad_date = delta_1day

                else:
                    ad_date = ad_date.split()
                    ad_date = f"{year_now}-{monthvalue_dict[ad_date[1]]}-{ad_date[0]}"

                ad_date = f"{ad_date} {select_time[ind].text}"
                ad_date = datetime.datetime.strptime(ad_date, '%Y-%m-%d %H:%M')

                f.write(f"{i} & {ad_date}\n")


        print(f"{dt.datetime.now()} | PAGE: {page_index} | ADDED: {len(select_elements[3:])} links ")

    for state in estados:
        url_state = f'{state}.'
        scrap(url_state)


def search_ads(frame=False, modelo=None):
    global ad_list
    global links_len
    ad_list = 0


    links = pd.read_csv('links.csv')
    links_len = links.shape[0]
    links = (i for i in list(links['links']))


    with open("consulta_olx.csv", 'w', encoding='utf-8') as arq:
        arq.write(f"data;base_model;model;brand;color;transmission;year;km;preco;link;postal_code;description\n")


    def scrap_ad(link, data=None):

        global ad_list

        entry = link.split(" & ")
        url, data = entry[0], entry[1]

        page = requests.get(url, headers=headers)

        doc = page.content

        soup = BeautifulSoup(doc, 'html.parser')

        ad = {}

        for item in soup.select('.cIfjkh'):
            ad['preco'] = item.get_text().lstrip('R$ ').replace('.', '')

        for item in soup.select('.eNZSNe'):

            if 'Modelo' in item.get_text():
                ad['model'] = item.get_text().replace('Modelo', '')
                ad['model'] = ad['model'].replace(']','')

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
        desc = desc.replace('\n','$ENTER$')
        desc = desc.replace(';',':')
        ad['description'] = desc
        ad['model'] = ad['model'].replace(ad['brand'], '').lstrip().lower()
        ad['model'] = ad['model'].replace(modelo, '').lstrip()
        ad['base_model'] = modelo
        ad['brand'] = ad['brand'].lower()

        """if ad['base_model'] in ad['model']:
            pass
        else:
            ad['model'] = f"{modelo} {ad['model']}"""

        labels = {'postal_code', 'link', 'description', 'brand', 'model', 'category', 'year', 'km', 'eng', 'fuel',
                  'transmission', 'steering', 'color', 'doors', 'last_num_plate', 'preco', 'base_model'}
        missing = labels - set(ad.keys())

        if ad['model'] == '':
            ad['model'] = "nao-preenchido"

        if missing:
            for i in missing:
                ad[i] = "nao-preenchido"

        with open("consulta_olx.csv", 'a', encoding='utf-8') as arq:
            arq.write(
                f"{data};{ad['base_model']};{ad['model']};{ad['brand']};{ad['color']};{ad['transmission']};{ad['year']};{ad['km']};{ad['preco']};{ad['link']};{ad['postal_code']};{ad['description']}\n")
        ad_list += 1

        print(f"[{dt.datetime.now()}] ITEM: {ad_list}  | MARCA: {ad['brand']} | MODELO: {ad['base_model']} | VERSÃO: {ad['model']} | ANO: {ad['year']} | PREÇO: {ad['preco']} | KM: {ad['km']}")


    # creating tkinter window

    if frame:
        # Progress bar widget

        download = Toplevel(frame, pady=30)
        download.title("Download Anuncios")
        download.iconbitmap("./gear2.ico")


        progress = Progressbar(download, orient=HORIZONTAL,
                               length=300, mode='determinate')

        perc = Label(download, text=f"Aguardando Inicio")
        quant = Label(download, text=f"")

        def progressbar():

            def bar():
                global ad_list

                last2 = None
                last1 = None


                while ad_list < links_len - 1:

                    last2 = last1
                    last1 = ad_list

                    if ad_list == last2:
                        break

                    time.sleep(2)
                    perc_complete = round(((ad_list / links_len) * 100), 2)
                    progress['value'] = perc_complete
                    perc['text'] = f"{perc_complete}%"
                    quant['text'] = f"Download: {ad_list} itens de um total de {links_len} itens."
                    download.update_idletasks()
                else:
                    print(f"Scraping Ended - Total {ad_list} ads")
                    quant.destroy()
                    perc['text'] = f"Procedimento Completo."
                    download.update_idletasks()
                    time.sleep(3)
                    download.destroy()


            def thread_scraper():

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    executor.map(scrap_ad, links)

            time.sleep(2)

            func1 = threading.Thread(target=bar)
            func2 = threading.Thread(target=thread_scraper)

            func1.start()
            func2.start()


        # This button will initialize
        # the progress bar
        #btn_str = Button(download, text='Start', command=progressbar)

        quant.grid(row=0, column=0)
        progress.grid(row=1, column=0)
        perc.grid(row=2, column=0)
        #btn_str.grid(row=3, column=0)
        progressbar()

    else:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(scrap_ad, links)


    fipe_id_brand_model()


def get_links(brand, model, state, frame=None):

    estados = ['ac', 'al', 'ap', 'am', 'ba', 'ce', 'df', 'es', 'go', 'ma', 'mt',
               'ms', 'mg', 'pa', 'pb', 'pr', 'pe', 'pi', 'rj', 'rn', 'rs',
               'ro', 'rr', 'sc', 'sp', 'se', 'to']

    with open('links.csv', 'w') as f:
        f.write("links\n")


    estados_qt = len(estados)



    est = Label(frame, text=f"Estado: N/A")
    tot_est = Label(frame, text=f"Total: 0 / {estados_qt} estados")

    est.grid(row=0, column=0)
    tot_est.grid(row=1, column=0)



    if state:
        if state.lower() == 'todos':
            for i,uf in enumerate(estados):
                est['text'] = f"Estado: {uf.upper()}"
                tot_est['text'] = f"Total: {i + 1} / {estados_qt} estados"
                frame.update_idletasks()
                search_links(brand, model, uf)
            est.destroy()
            tot_est.destroy()
        else:
            search_links(brand, model, state)


def ad_images(link):
    url = link
    page = requests.get(url, headers=headers)

    soup = BeautifulSoup(page.content, 'html.parser')

    return [item.img.get('src') for item in soup.select('.bQbWAr')]


