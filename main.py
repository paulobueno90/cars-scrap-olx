from fipe import *
from spider import *
from regression import *


# Take Fipe brand Keys and Model Keys
get_models()

# Olx Crawler
#search_ads(marca='honda', modelo='fit', estado='')

# Get Fipe Prices for each model and year
#get_models_price()

# Add fipe prices in Ads csv
add_fipe2csv()

