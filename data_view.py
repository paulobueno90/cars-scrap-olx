import pandas as pd
from tkinter import *
from tkinter import Button
from tkinter import ttk

def window_data(frame):
    data = Toplevel(frame, pady=30)
    data.title("Anuncios OLX")
    data.iconbitmap("./report.ico")

    perc = Label(data, text=f"Aguardando Inicio")
    quant = Label(data, text=f"OLAAA")

    quant.grid(row=0, column=0)
    perc.grid(row=2, column=0)
