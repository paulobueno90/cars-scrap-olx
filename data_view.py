from tkinter import *
import urllib.request
from PIL import ImageTk, Image
import io
from spider import ad_images


def get_images(link):

    links = ad_images(link)
    images = []
    for img in links:
        raw_data = urllib.request.urlopen(img).read()
        im = Image.open(io.BytesIO(raw_data))
        images.append(ImageTk.PhotoImage(im))
    return images
