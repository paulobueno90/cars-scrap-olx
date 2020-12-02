from fipe import *
from spider import *
from clean_data import *
#from regression import *


# Take Fipe brand Keys and Model Keys
#get_models()

# Olx Links Crawler
get_links('mitsubishi', 'pajero', '')

# Olx Ads Crawler
search_ads()

# Clean Data
clean_data()

# Get Fipe Prices for each model and year
get_models_price()

# Add fipe prices in Ads csv
add_fipe2csv()

# Variables Adjustment
variables_adjustment()
df_adjust()


