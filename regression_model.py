import pandas as pd
import numpy as np
import locale
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import pickle



locale.setlocale(locale.LC_NUMERIC, '')

pd.set_option('display.max_columns', 200)


def km_ano(dataframe):
    df_copy = dataframe
    filt = df_copy['age'] == 0
    df_copy.loc[filt, 'age'] = 1

    filt = df_copy['age'] == 0
    df_copy['km_ano'] = df_copy['km'] / df_copy['age']
    dataframe['km_ano'] = df_copy['km_ano'].values
    dataframe['km_ano'] = dataframe['km_ano'].apply(lambda x: x**2.5)

    return dataframe

def linear_reg():
    # Reading Cleaned Data Extracted From OLX
    dados = pd.read_csv("cleaned_consulta_olx.csv", encoding='utf-8', sep=';')

    dados.set_index('year', inplace=True)
    dados = km_ano(dados)
    df = dados.copy()


    #dados['km'] = dados['km'].apply(lambda x: np.log(x))

    dados.drop(['description', 'brand_id', 'model_id', 'postal_code', 'link', 'brand','price_std'], axis=1, inplace=True)


    # define input variable and our output variable
    X = dados.drop('preco', axis=1)
    X = pd.get_dummies(X)
    X['km'] = X['km'].apply(lambda km2: (km2 ** 0.80))
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


    #print(regression_model.score(X, Y))

    # make new_prediction
    pred = regression_model.predict(pd.get_dummies(dados.drop('preco', axis=1)))
    lista = [round(j, 2) for i in pred for j in i]

    # Add a column with Predicted Prices
    columns = list(pd.get_dummies(dados.drop('preco', axis=1)))
    df['predicted_price'] = lista
    #df = df.loc[2015]
    #print(df[['preco','predicted_price','km','fipe','color']])
    # pickle the model
    with open('my_multilinear_regression.sav', 'wb') as f:
        pickle.dump(regression_model, f)

    return regression_model, columns





regression_model, lista = linear_reg()

df = pd.read_csv('consulta_olx2.csv', encoding='utf-8', sep=';')

for i, row in df.iterrows():
        if row['age'] > 1:
            if row['km'] < 400 and row['km'] != 0:
                df.at[i, 'km'] = row.km * 1000
            elif row['km'] == 0:
                df.at[i, 'km'] = np.nan

df.dropna(inplace=True)

df['dif_fipe'] = df['preco'] / df['fipe']


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

df = km_ano(df)
df.set_index('year', inplace=True)
df.drop(['description', 'brand_id', 'model_id', 'postal_code', 'link', 'brand','price_std'], axis=1, inplace=True)
df.dropna(inplace=True)

# define input variable and our output variable
X = df.drop('preco', axis=1)
X = pd.get_dummies(X)
Y = df[['preco']]

# make new_prediction
pred = regression_model.predict(pd.get_dummies(df.drop('preco', axis=1)))
lista = [round(j, 2) for i in pred for j in i]
df['predicted_price'] = lista


df['dist'] = df['predicted_price'] / df['preco']
print(df['dist'].min())
#df.sort_values(by=['km'], inplace=True, ascending=False)
print(df[['fipe','predicted_price','preco','km','dist']])
print(regression_model.score(X, Y))

def search_car_price():
    df = pd.read_csv('cleaned_consulta_olx.csv', encoding='utf-8', sep=';')

    car_brand = list(set(df.brand.values))
    car_models = list(set(df.model.values))
    car_transmission = list(set(df.transmission.values))
    car_color = list(set(df.color.values))

    print('__' * 20)
    print('MARCAS')
    print('__' * 20)
    for i, v in enumerate(car_brand):
        print(f"[{i}] - {v}")
    print('__' * 20)
    print('\n'*3)

    print('__' * 20)
    print('MODELOS')
    print('__' * 20)
    for i, v in enumerate(car_models):
        print(f"[{i}] - {v}")
    print('__' * 20)
    print('\n' * 3)

    print('__' * 20)
    print('COR')
    print('__' * 20)
    for i, v in enumerate(car_color):
        print(f"[{i}] - {v}")
    print('__' * 20)
    print('\n' * 3)

    print('__' * 20)
    print('TRANSMISSÃO')
    print('__' * 20)
    for i, v in enumerate(car_transmission):
        print(f"[{i}] - {v}")
    print('__' * 20)
    print('\n' * 3)


    #brand = input('Brand: ')
    #model = input('\nModel: ')
    #transmission = input('\n')




#print(df.loc[2013][['preco','predicted_price','km','fipe','color']])




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
