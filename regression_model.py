import pandas as pd
import datetime
import scipy
import numpy as np
import locale
import pickle
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import statsmodels.api as sm
from statsmodels.stats import diagnostic as diag
from statsmodels.stats.outliers_influence import variance_inflation_factor

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error


locale.setlocale(locale.LC_NUMERIC, '')

pd.set_option('display.max_columns', 200)



def linear_reg():
    # Reading Cleaned Data Extracted From OLX
    dados = pd.read_csv("cleaned_consulta_olx.csv", encoding='utf-8', sep=';')

    dados.set_index('year', inplace=True)
    df = dados.copy()


    #dados['km'] = dados['km'].apply(lambda x: np.log(x))

    dados.drop(['description', 'brand_id', 'model_id', 'postal_code', 'link', 'brand'], axis=1, inplace=True)


    # define input variable and our output variable
    X = dados.drop('preco', axis=1)
    X = pd.get_dummies(X)
    X['km'] = X['km'].apply(lambda km2: (km2 ** 0.75))
    Y = dados[['preco']]

    # Split dataset into training and testing portion
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.20, random_state=1)

    # create an instance of our model
    regression_model = LinearRegression()

    # fit the model
    regression_model.fit(X_train, y_train)

    # grab the intercept and the coef
    intercept = regression_model.intercept_[0]
    coef = regression_model.coef_[0]


    print(regression_model.score(X, Y))

    # make new_prediction
    pred = regression_model.predict(pd.get_dummies(dados.drop('preco', axis=1)))
    lista = [round(j, 2) for i in pred for j in i]

    # Add a column with Predicted Prices
    print(list(pd.get_dummies(dados.drop('preco', axis=1))))
    df['predicted_price'] = lista
    #df = df.loc[2015]
    #print(df[['preco','predicted_price','km','fipe','color']])

    return regression_model





regression_model = linear_reg()



# Reading Extracted Data From OLX
df = pd.read_csv("consulta_olx.csv", encoding='utf-8', sep=';')
df.set_index('year', inplace=True)



models = df.groupby(['brand_id', 'model_id', 'age']).count()
models = list(models.index)
df['price_std'] = 0

for i in models:
    filt = (df['brand_id'] == i[0]) & (df['model_id'] == i[1]) & (df['age'] == i[2])
    _ = df.loc[filt]

    pricestd = _['preco'].std()

    df.loc[filt, 'price_std'] = _['preco'].std()

    filt_outlier = ((df['brand_id'] == i[0]) & (df['model_id'] == i[1]) & (df['age'] == i[2])) & (
                (df['preco'] >= (df['fipe'] + (pricestd * 2))) | (df['preco'] <= (df['fipe'] - (pricestd * 2))))
    df.loc[filt_outlier] = np.nan

df.dropna(inplace=True)


df.drop(['description', 'brand_id', 'model_id', 'postal_code', 'link', 'brand'], axis=1, inplace=True)

# define input variable and our output variable
X = df.drop('preco', axis=1)
X = pd.get_dummies(X)
X['km'] = X['km'].apply(lambda km2: (km2 ** 0.75))
Y = df[['preco']]


print(list(pd.get_dummies(df.drop('preco', axis=1))))

#print(regression_model.score(X, Y))

# make new_prediction
pred = regression_model.predict(pd.get_dummies(df.drop('preco', axis=1)))
lista = [round(j, 2) for i in pred for j in i]
df['predicted_price'] = lista
#df = df.loc[2015]
print(df[['preco','predicted_price','km','fipe','color']])


#print(df.shape)
#print(df.corr())
#print(df.loc[2012])



"""

fig = plt.figure(constrained_layout=False)

spec2 = gridspec.GridSpec(ncols=2, nrows=2, figure=fig)
ax1 = fig.add_subplot(spec2[0, 0])
ax2 = fig.add_subplot(spec2[0, 1])
ax3 = fig.add_subplot(spec2[1, 0])
ax4 = fig.add_subplot(spec2[1, 1])

df.boxplot(column='km', by='year', ax=ax1)
df.boxplot(column='preco', by='year', ax=ax2)
df.groupby(['year']).preco.mean().plot(kind='bar', ax=ax3, legend=True)
df.groupby(['year']).km.mean().plot(kind='bar', ax=ax4, legend=True)

plt.show()


models = df.groupby(['brand_id', 'model_id']).count()"""


"""

# pickle the model
# with open('my_multilinear_regression.sav', 'wb') as f:
# pickle.dump(regression_model, f)

# with open('my_multilinear_regression.sav', 'rb') as pickle_file:
# regression_model_2 = pickle.load(pickle_file)"""
