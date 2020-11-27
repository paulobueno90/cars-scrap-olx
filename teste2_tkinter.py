from tkinter import *
from tkinter import Button
from tkinter import ttk
from spider import *
from data_view import *

estados = ['TODOS', 'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
estados = {i:i.lower() for i in estados}


def frame_pesquisa_simples():
    def unpack_frame():
        frame_pesq_simples.destroy()



    frame_pesq_simples = LabelFrame(tab_control, text="PESQUISA SIMPLES", padx=150, pady=100)
    frame_pesq_simples.grid(row=1, column=0)

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

    btn_pesquisar = Button(frame_pesq_simples, text="Pesquisar", command=search_btn, height=2, width=15)
    btn_frame_cont_sair = Button(frame_pesq_simples, text="Fechar", command=unpack_frame, height = 2, width = 15)

    uf.grid(row=2, column=0)
    car_brand.grid(row=3, column=0)
    car_model.grid(row=4, column=0)
    btn_pesquisar.grid(row=5, column=0)
    btn_frame_cont_sair.grid(row=6, column=0)

    tab_control.add(frame_pesq_simples, text="Pesquisa")

def frame_atualizar_pesquisa():
    def unpack_frame():
        frame_att_pesquisa.destroy()



    frame_att_pesquisa = LabelFrame(tab_control, text="Visualizar", padx=20)
    frame_att_pesquisa.grid(row=2, column=0)
    window_data(frame_att_pesquisa)

    label1 = Label(frame_att_pesquisa, text=f"Mostrar Anuncios:", anchor='w')
    check_normal = Checkbutton(frame_att_pesquisa, text="Anuncios Normais")
    check_agio = Checkbutton(frame_att_pesquisa, text="Ágio")
    check_carta = Checkbutton(frame_att_pesquisa, text="Consórcio")
    check_realidade = Checkbutton(frame_att_pesquisa, text="Informação Duvidosa")
    btn_frame_cont_sair = Button(frame_att_pesquisa, text="Sair", command=unpack_frame, height = 2, width = 15)

    label1.config(font=("Courier", 22))

    label1.grid(row=0, column=0)
    check_normal.grid(row=1, column=0)
    check_agio.grid(row=1, column=2)
    check_carta.grid(row=1, column=3)
    check_realidade.grid(row=1, column=4)
    btn_frame_cont_sair.grid(row=2, column=0)

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
root.iconphoto(False, PhotoImage(file='./olx.png'))
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