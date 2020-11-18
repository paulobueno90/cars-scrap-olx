import pandas as pd

links = pd.read_csv('links.csv')
print(links)
links.drop_duplicates(inplace=True)
print(links)