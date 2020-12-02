from tkinter import *
from tkinter import Button, Checkbutton
from tkinter import ttk
from spider import *
from data_view import get_images
import webbrowser

from functools import partial

estados = ['TODOS', 'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
estados = {i:i.lower() for i in estados}


def frame_pesquisa_simples():
    def unpack_frame():
        frame_pesq_simples.destroy()



    frame_pesq_simples = LabelFrame(tab_control, text="PESQUISA SIMPLES", padx=150, pady=100)
    frame_pesq_simples.grid(row=1, column=0)
    frame_pesq_simples_buttons = Frame(frame_pesq_simples, pady=25)

    uf = ttk.Combobox(frame_pesq_simples, width=50, value=sorted(list(estados.keys())))
    uf.current((len(list(estados.keys())) - 1))

    car_brand = ttk.Combobox(frame_pesq_simples, width=50, value=get_brand())
    car_brand.current(0)

    def callback(eventObject):
        car = car_brand.get()
        car_model.config(values=get_model(car.lower()))




    car_model = ttk.Combobox(frame_pesq_simples, width=50, values=['MODELO'])
    car_model.bind('<Button-1>', callback)
    car_model.current(0)

    def search_btn():
        brand = car_brand.get().lower()
        model = car_model.get().lower()
        estate = uf.get().lower()

        get_links(brand, model, estate,frame_pesq_simples)
        search_ads(frame_pesq_simples, modelo=model)

    btn_pesquisar = Button(frame_pesq_simples_buttons,
                           text="Pesquisar",
                           command=search_btn,
                           bg='dark green',
                           fg='white',
                           height=2, width=15)
    btn_frame_cont_sair = Button(frame_pesq_simples_buttons, text="Fechar", command=unpack_frame, bg='dark red', fg='white', height = 2, width = 15)

    uf.grid(row=2, column=0)
    car_brand.grid(row=3, column=0)
    car_model.grid(row=4, column=0)
    frame_pesq_simples_buttons.grid(row=5, column=0)
    btn_pesquisar.grid(row=0, column=0)
    btn_frame_cont_sair.grid(row=0, column=1)

    tab_control.add(frame_pesq_simples, text="Pesquisa")

def frame_atualizar_pesquisa():
    def unpack_frame():
        frame_att_pesquisa.destroy()


    df = pd.read_csv('consulta_olx.csv', sep=';')

    df_brands = [i.upper() for i in set(df['brand'])]
    def callback_base_model(eventObject):
        box1_item = box1.get().lower()
        filt = df['brand'] == box1_item
        df_base_model = df.loc[filt]
        box2.config(values= [i.upper() for i in set(df_base_model['base_model'])])

    def callback_model(eventObject):
        box2_item = box2.get().lower()
        filt = df['base_model'] == box2_item
        df_base_model = df.loc[filt]
        box3.config(values=[i.upper() for i in set(df_base_model['model'])])

    def callback_year(eventObject):
        box1_item = box1.get().lower()
        box2_item = box2.get().lower()
        box3_item = box3.get().lower()
        filt = df['brand'] == box1_item
        df_base_model = df.loc[filt]
        filt = df_base_model['base_model'] == box2_item
        df_base_model = df_base_model.loc[filt]
        filt = df_base_model['model'] == box3_item
        df_base_model = df_base_model.loc[filt]
        box4_values = ['ANO'] + [i for i in set(df_base_model['year'])]

        box4.config(values=box4_values)

    def window_data():

        data = Toplevel(frame_att_pesquisa, pady=30)
        data.title("Anuncios OLX")
        data.iconbitmap("./icons/report.ico")
        data.geometry("850x800")

        # Create A Main Frame
        mf = Frame(data)
        mf.pack(fill=BOTH, expand=1)

        # Create A Canvas
        mc = Canvas(mf)
        mc.pack(side=LEFT, fill=BOTH, expand=1)

        # Add A Scrollbar To The Canvas
        window_scrollbar = ttk.Scrollbar(mf, orient=VERTICAL, command=mc.yview)
        window_scrollbar.pack(side=RIGHT, fill=Y)

        # Configure The Canvas
        mc.configure(yscrollcommand=window_scrollbar.set)
        mc.bind('<Configure>', lambda e: mc.configure(scrollregion=mc.bbox("all")))

        # Create ANOTHER Frame INSIDE the Canvas
        window_frame = Frame(mc)

        # Add that New frame To a Window In The Canvas
        mc.create_window((0, 0), window=window_frame, anchor="nw")


        box1_item = box1.get().lower()
        filt = df['brand'] == box1_item
        df_base_model = df.loc[filt]

        box2_item = box2.get().lower()
        filt = df_base_model['base_model'] == box2_item
        df_base_model = df_base_model.loc[filt]


        box3_item = box3.get().lower()

        if box3_item == "versão":
            pass
        else:
            filt = df_base_model['model'] == box3_item
            df_base_model = df_base_model.loc[filt]


        box4_item = box4.get()

        if box4_item == "ANO":
            pass
        else:
            box4_item = int(box4_item)
            filt = df_base_model['year'] == box4_item
            df_base_model = df_base_model.loc[filt]

        num = 1
        print(df_base_model.iloc[1])
        for i, row in df_base_model.iterrows():

            def open_link(link):
                webbrowser.open(link)

            def window_images(item):

                root_img = Toplevel(frame_att_pesquisa)

                root_img.title("Visualizar Fotos")
                root_img.iconbitmap("./icons/report.ico")
                root_img.geometry("750x750")
                root_img.maxsize(750, 1200)

                images = get_images(link=item.link)
                size = len(images) - 1
                current_img = 0

                # Create A Main Frame
                mf2 = Frame(root_img)
                mf2.pack(fill=BOTH, expand=1)

                # Create A Canvas
                mc2 = Canvas(mf2)
                mc2.pack(side=LEFT, fill=BOTH, expand=1)

                # Add A Scrollbar To The Canvas
                window_scrollbar2 = ttk.Scrollbar(mf2, orient=VERTICAL, command=mc2.yview)
                window_scrollbar2.pack(side=RIGHT, fill=Y)

                # Configure The Canvas
                mc2.configure(yscrollcommand=window_scrollbar2.set)
                mc2.bind('<Configure>', lambda e: mc2.configure(scrollregion=mc2.bbox("all")))

                # Create ANOTHER Frame INSIDE the Canvas
                window_frame2 = Frame(mc2)

                # Add that New frame To a Window In The Canvas
                mc2.create_window((0, 0), window=window_frame2, anchor="nw")


                def foward():
                    nonlocal current_img
                    if current_img == size:
                        current_img = 0
                    else:
                        current_img += 1

                    label1['image'] = images[current_img]
                    label1.update_idletasks()

                def backward():
                    nonlocal current_img
                    if current_img == 0:
                        current_img = size
                    else:
                        current_img -= 1

                    label1['image'] = images[current_img]
                    label1.update_idletasks()

                def quit_img():
                    root_img.destroy()

                def open_link():
                    webbrowser.open(item.link)
                frame1 = Frame(window_frame2)
                frame2 = Frame(window_frame2)
                frame3 = Frame(window_frame2, pady=25)
                label1 = Label(frame1, image=images[current_img])

                btn_link = Button(frame2,
                                  text="Abrir no Site",
                                  command=open_link,
                                  bg='dark green',
                                  fg='white',
                                  height=2, width=15)
                btn_fwd = Button(frame2, text=">>", command=foward,height=2, width=15)
                btn_bck = Button(frame2, text="<<", command=backward,height=2, width=15)
                btn_sair = Button(frame2, text="Sair", command=quit_img,height=2, width=15)
                frame1.grid(row=0, column=0)
                frame2.grid(row=1, column=0)
                frame3.grid(row=2, column=0)

                label1.grid(row=0, column=0)
                btn_bck.grid(row=0, column=1)
                btn_fwd.grid(row=0, column=2)
                btn_sair.grid(row=0, column=3)
                btn_link.grid(row=0,column=0)


                ad2 = LabelFrame(frame3,
                                text=f"{item.brand.upper()} {item.base_model.upper()}",
                                pady=5, height=200, width=500,
                                font=("Helvetica", 16, 'bold'),
                                )

                ad2_descript = LabelFrame(frame3,
                                 text=f"- Descrição -",
                                 pady=5,
                                 font=("Helvetica", 16, 'bold'),
                                 )
                description = item.description
                description = description.replace('$ENTER$', '\n')

                Label(ad2_descript, text=f"{description}", wraplengt=200).grid(row=0,column=0)



                Label(ad2, text=f"VERSÃO:", font=("Helvetica", 12, 'bold')).grid(row=0, column=0)
                Label(ad2, text=f"{item.model.upper()}", font=("Helvetica", 10)).grid(row=0, column=1)

                Label(ad2, text=f"ANO:", font=("Helvetica", 12, 'bold')).grid(row=1, column=0)
                Label(ad2, text=f"{item.year}", font=("Helvetica", 10)).grid(row=1, column=1)

                Label(ad2, text=f"PREÇO:", font=("Helvetica", 12, 'bold')).grid(row=0, column=2)
                Label(ad2, text=f"R$ {item.preco}", font=("Helvetica", 10)).grid(row=0, column=3)

                Label(ad2, text=f"Kilometragem:", font=("Helvetica", 12, 'bold')).grid(row=1, column=2)
                Label(ad2, text=f"{item.km} km", font=("Helvetica", 10)).grid(row=1, column=3)

                Label(ad2, text=f"Transmissão:", font=("Helvetica", 12, 'bold')).grid(row=2, column=2)
                Label(ad2, text=f"{item.transmission}", font=("Helvetica", 10)).grid(row=2, column=3)

                Label(ad2, text=f"Cor:", font=("Helvetica", 12, 'bold')).grid(row=3, column=2)
                Label(ad2, text=f"{item.color.title()}", font=("Helvetica", 10)).grid(row=3, column=3)

                ad2.grid(row=0, column=0)
                ad2_descript.grid(row=1, column=0)

            window_images_object = partial(window_images, row)
            open_link_object = partial(open_link, row.link)

            ad = LabelFrame(window_frame,
                            text=f"{row.brand.upper()} {row.base_model.upper()}",
                            pady=5, height=170, width=550,
                            font=("Helvetica", 16, 'bold'),
                            )

            button_frame = Frame(window_frame,padx=15)

            btn_link = Button(button_frame,
                                   text="Abrir no Site",
                                   command=open_link_object,
                                   bg='dark green',
                                   fg='white',
                                   height=2, width=15)

            btn_images = Button(button_frame,
                              text="Ver Anuncio Local",
                              command= window_images_object,
                              bg='dark blue',
                              fg='white',
                              height=2, width=15)





            btn_link.grid(row=0, column=0)
            btn_images.grid(row=1, column=0)
            button_frame.grid(row=num, column=0)
            ad.grid_propagate(0)
            ad.grid(row=num, column=1)

            Label(ad, text=f"VERSÃO:", font=("Helvetica", 12, 'bold')).grid(row=0, column=0)
            Label(ad, text=f"{row.model.upper()}", font=("Helvetica", 10)).grid(row=0, column=1)

            Label(ad, text=f"ANO:", font=("Helvetica", 12, 'bold')).grid(row=1, column=0)
            Label(ad, text=f"{row.year}", font=("Helvetica", 10)).grid(row=1, column=1)

            Label(ad, text=f"PREÇO:", font=("Helvetica", 12, 'bold')).grid(row=0, column=2)
            Label(ad, text=f"R$ {row.preco}", font=("Helvetica", 10)).grid(row=0, column=3)

            Label(ad, text=f"Kilometragem:", font=("Helvetica", 12, 'bold')).grid(row=1, column=2)
            Label(ad, text=f"{row.km} km", font=("Helvetica", 10)).grid(row=1, column=3)

            Label(ad, text=f"Transmissão:", font=("Helvetica", 12, 'bold')).grid(row=2, column=2)
            Label(ad, text=f"{row.transmission}", font=("Helvetica", 10)).grid(row=2, column=3)

            Label(ad, text=f"Cor:", font=("Helvetica", 12, 'bold')).grid(row=3, column=2)
            Label(ad, text=f"{row.color.title()}", font=("Helvetica", 10)).grid(row=3, column=3)


            num += 1

        title = Label(window_frame, text=f"ANUNCIOS")

        title.grid(row=0, column=0)




    #df_base_model = [i.upper() for i in set(df['base_model'])]
    #df_model = [i.upper() for i in set(df['model'])]

    frame_att_pesquisa = LabelFrame(tab_control, text="Visualizar", padx=20)
    frame_att_pesquisa.grid(row=2, column=0)
    frame_att_pesquisa_buttons = Frame(frame_att_pesquisa, pady=25)
    frame_att_pesquisa_buttons.grid(row=7, column=0)


    label1 = Label(frame_att_pesquisa, text=f"Mostrar Anuncios:", anchor='w')
    check_normal = Checkbutton(frame_att_pesquisa, text="Anuncios Normais")
    check_agio = Checkbutton(frame_att_pesquisa, text="Ágio")
    check_carta = Checkbutton(frame_att_pesquisa, text="Consórcio")
    check_realidade = Checkbutton(frame_att_pesquisa, text="Informação Duvidosa")
    check_normal.select()
    btn_pesquisar = Button(frame_att_pesquisa_buttons, text="Pesquisar", command=window_data, bg='dark green',
                           fg='white', height=2, width=15)
    btn_frame_cont_sair = Button(frame_att_pesquisa_buttons, text="Fechar", command=unpack_frame, bg='dark red',
                                 fg='white', height=2, width=15)



    box1 = ttk.Combobox(frame_att_pesquisa, width=50, value=df_brands)
    box1.current(0)
    box2 = ttk.Combobox(frame_att_pesquisa, width=50, values=['MODELO'])
    box2.bind('<Button-1>', callback_base_model)
    box2.current(0)
    box3 = ttk.Combobox(frame_att_pesquisa, width=50, values=['VERSÃO'])
    box3.bind('<Button-1>', callback_model)
    box3.current(0)
    box4 = ttk.Combobox(frame_att_pesquisa, width=50, values=['ANO'])
    box4.bind('<Button-1>', callback_year)
    box4.current(0)


    label1.config(font=("Courier", 22))

    check_normal.select()

    label1.grid(row=0, column=0)
    check_normal.grid(row=1, column=0)
    check_agio.grid(row=1, column=2)
    check_carta.grid(row=1, column=3)
    check_realidade.grid(row=1, column=4)

    btn_pesquisar.grid(row=0, column=0)
    btn_frame_cont_sair.grid(row=0, column=1)

    box1.grid(row=3, column=0)
    box2.grid(row=4, column=0)
    box3.grid(row=5, column=0)
    box4.grid(row=6, column=0)

    tab_control.add(frame_att_pesquisa, text="Visualizar")

def frame_pesquisa_completa():
    def unpack_frame():
        frame_pesq_completa.destroy()

    frame_pesq_completa = LabelFrame(tab_control, text="PESQUISA COMPLETA", padx=200, pady=200)
    frame_pesq_completa.grid(row=3, column=0)

    uf = ttk.Combobox(frame_pesq_completa, width=37, value=sorted(list(estados.keys())))
    btn_frame_cont_sair = Button(frame_pesq_completa, text="Sair", command=unpack_frame, height = 2, width = 15)

    uf.grid(row=0, column=0)
    btn_frame_cont_sair.grid(row=2, column=0)

    tab_control.add(frame_pesq_completa, text="Pesquisa Avançada")

def frame_precificador():
    def unpack_frame():
        frame_prec.destroy()

    frame_prec = LabelFrame(tab_control, text="PRECIFICAÇÃO", padx=250, pady=200)
    frame_prec.grid(row=4, column=0)


    btn_frame_cont_sair = Button(frame_prec, text="Sair", command=unpack_frame, height = 2, width = 15)
    btn_frame_cont_sair.grid(row=2, column=0)

    tab_control.add(frame_prec, text="Análise de Preços")



root = Tk()
root.title('Scraper Olx - 2020')
root.iconphoto(False, PhotoImage(file='./icons/olx.png'))
root.geometry("675x500")
#root.minsize(675, 500)

# Create A Main Frame
main_frame = Frame(root)
main_frame.pack(fill=BOTH, expand=1)

# Create A Canvas
my_canvas = Canvas(main_frame)
my_canvas.pack(side=LEFT, fill=BOTH, expand=1)

# Add A Scrollbar To The Canvas
my_scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL, command=my_canvas.yview)
my_scrollbar.pack(side=RIGHT, fill=Y)

# Configure The Canvas
my_canvas.configure(yscrollcommand=my_scrollbar.set)
my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

# Create ANOTHER Frame INSIDE the Canvas
second_frame = Frame(my_canvas)

# Add that New frame To a Window In The Canvas
my_canvas.create_window((0, 0), window=second_frame, anchor="nw")



def Quit(): root.destroy()


frame_buttons = LabelFrame(second_frame, text="MENU")
frame_buttons.grid(row=0, column=0, sticky='w')


# Create Buttons
btn1 = Button(frame_buttons, text="Pesquisa Simples", command=frame_pesquisa_simples, height = 3, width = 17)
btn2 = Button(frame_buttons, text="Atualizar Pesquisa", command=frame_atualizar_pesquisa, height = 3, width = 17)
btn3 = Button(frame_buttons, text="Pesquisa Completa", command=frame_pesquisa_completa, height = 3, width = 17)
btn4 = Button(frame_buttons, text="Precificador", command=frame_precificador, height = 3, width = 17)
btn5 = Button(frame_buttons, text="Sair", command=Quit, height = 3, width = 17)


# Placing Buttons
btn1.grid(row=0, column=0)
btn2.grid(row=0, column=1)
btn3.grid(row=0, column=2)
btn4.grid(row=0, column=3)
btn5.grid(row=0, column=4)




frame_cont = LabelFrame(second_frame)
frame_cont.grid(row=2, column=0)

tab_control = ttk.Notebook(frame_cont)#1


tab_control.grid(column=0, row=0, sticky='w')

root.mainloop()