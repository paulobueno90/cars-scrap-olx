import pandas as pd
import datetime
import scipy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import locale

locale.setlocale(locale.LC_NUMERIC, '')

pd.set_option('display.max_columns', 200)

df = pd.read_csv("consulta_olx.csv", encoding='utf-8', sep=';')

# ser = df.groupby(['brand','year', 'model']).preco.median()

current_year = datetime.date.today().year
df['age'] = df['year'].apply(lambda x: current_year - int(x))

filt = df['km'] > 500
df = df.loc[filt]
filt = df['km'] <= df['km'].quantile(0.97)
df = df.loc[filt]

"""print(df['km'].quantile(0.05))
print(df['km'].quantile(0.97))
print(df['km'].skew())"""


# print(df['km'].describe())

# plt.boxplot(df['km'])


def description_clean(string):
    item = string.lower()
    item = item.replace('á', 'a')

    if 'agio' in item:
        return np.nan
    else:
        return item


# df.set_index('year', inplace=True)
# df.sort_index(inplace=True)
df['description'] = df['description'].apply(lambda x: description_clean(x))
# filt = df['preco'] < (df['preco'].median() - df['preco'].std())
# df.loc[filt] = np.nan
df.dropna(inplace=True)

df['fipe'] = df['fipe'].apply(lambda x: locale.atof(x.lstrip('R$ ')))
df['dif_fipe'] = df['preco'] / df['fipe']
# df['year'] = df['year'].apply(lambda x: str(int(x))
df['year'] = df['year'].apply(lambda x: datetime.datetime.strptime(str(int(x)), '%Y'))

df['year'].astype('datetime64[ns]')
df.set_index('year', inplace=True)

std_price = df['preco'].std()
mask = (df['preco'] < (df['fipe'] + 1.5 * std_price)) & (df['preco'] > (df['fipe'] - 1 * std_price))
df = df.loc[mask]

plt.boxplot(df['preco'])
import seaborn as sns

dados = df[['preco', 'km', 'age']]
# sns.jointplot(x='km',y='age',data=dados, kind='reg')
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

y = list(dados.preco)

x = [list(dados.km), list(dados.age)]

corr = dados.corr()
# sns.heatmap(corr, xticklabels = corr.columns, yticklabels= corr.columns, cmap="RdBu")

dados_before = dados

X1 = sm.tools.add_constant(dados_before)

series_before = pd.Series([variance_inflation_factor(X1.values, i) for i in range(X1.shape[1])], index=X1.columns)

# pd.plotting.scatter_matrix(dados, alpha=1, figsize=(18,6))
# plt.show()

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from statsmodels.stats import diagnostic as diag

# define input variable and our output variable
X = dados.drop('preco', axis=1)
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

print("The intercept for our model is {:.4}".format(intercept))
print("-" * 100)

# Loop through the dictionary and print the data
for cf in zip(X.columns, coef):
    print("The Coefficient for {} is {:.2}".format(cf[0], cf[1]))

print("-" * 100)

# get multiple predictions
y_predict = regression_model.predict(X_test)

# show the first five
# print(y_predict[:5])
# print(y_test[:5])


# define our input
X2 = sm.add_constant(X)

# create an OLS model
model = sm.OLS(Y, X2)

# fit the data
est = model.fit()

# Running the white's test
_, pval, __, f_pval, = diag.het_white(est.resid, est.model.exog)
print(pval, f_pval)
print('_' * 100)

_, pval, __, f_pval, = diag.het_breuschpagan(est.resid, est.model.exog)
print(pval, f_pval)
print('_' * 100)

# print the results of the test
if pval > 0.05:
    print("For the Breusch-Pagan's Test")
    print("The p-value was {:.4}".format(pval))
    print("We Fail to reject the null hypthoesis, so there is no heterosecdasticity.")
else:
    print("For the Breusch-Paga's Test")
    print("The p-value was {:.4}".format(pval))
    print("We reject the null hypthoesis, so there is heterosecdasticity")
print('')
print('')
print('')
print('')
lag = min(10, len(X) // 5)

# Perform ljungbox
test_results = diag.acorr_ljungbox(est.resid, lags=lag)

ibvalue, p_val = test_results

# print the results of the test
if min(p_val) > 0.05:
    print("The Lowest p-value found was {:.4}".format(min(p_val)))
    print("We fail to reject the null hyphoesis, so there is no autocorrelation")
    print("-" * 100)
else:
    print("The Lowest p-value found was {:.4}".format(min(p_val)))
    print("We reject the null hypthoesis, so there is autocorrelation.")
    print("-" * 100)
print('')
print('')
print('')
print('')
# sm.graphics.tsa.plot_acf(est.resid)

# check for the normality of the residuals
import pylab

# sm.qqplot(est.resid, line = 's')
# pylab.show()

# check that the mean of the residuals is approx. 0
mean_residuals = sum(est.resid) / len(est.resid)
# print(mean_residuals)

import math

model_mse = mean_squared_error(y_test, y_predict)

model_mae = mean_absolute_error(y_test, y_predict)

model_rmse = math.sqrt(model_mse)
"""print('-'*50)
print("MSE {:.3}".format(model_mse))
print("MAE {:.3}".format(model_mae))
print("RMSE {:.3}".format(model_rmse))"""

model_r2 = r2_score(y_test, y_predict)
# print(model_r2)

import pickle

# pickle the model
# with open('my_multilinear_regression.sav', 'wb') as f:
# pickle.dump(regression_model, f)

# with open('my_multilinear_regression.sav', 'rb') as pickle_file:
# regression_model_2 = pickle.load(pickle_file)

# make new_prediction
pred = regression_model.predict(X)
lista = [j for i in pred for j in i]

df['predicted_price'] = lista
print(df[['preco', 'predicted_price']])
std_price = df['preco'].std()

mask = df['preco'] < (df['fipe'] + 1.5 * std_price)
df = df.loc[mask]
mask = df['preco'] > (df['fipe'] - 1 * std_price)
df = df.loc[mask]

# filt = df['preco'] < df['predicted_price']
# print(df[filt])


pred_prec = df[['predicted_price', 'fipe', 'preco']].resample('Y').mean()

pred_prec.plot()

plt.show()

# print(df[['fipe','predicted_price','preco']])

"""fig1, ax1 = plt.subplots()
ax1.scatter(age, fipe, color='g')
ax1.scatter(age, pred_prec, color='b')
ax1.scatter(age, precos, color='r')



plt.show()"""

"""#dados = pd.DataFrame(dados_dicionario)
X = dados.iloc[:, 0].values

y = dados.iloc[:, 1].values




correlacao = np.corrcoef(X, y)
print(correlacao)

X = X.reshape(-1, 1)

regressor = LinearRegression()
regressor.fit(X,y)

regressor.coef_

regressor.intercept_

plt.scatter(X,y)
plt.plot(X, regressor.predict(X), color = 'red')
plt.title('TESTE REGRESSÃO LINEAR')
plt.xlabel('Quilometragem')
plt.ylabel('Preco R$')
#plt.show()








#df['preco'].plot(kind='scatter')

#plt.plot(df['preco'])"""

"""fig = plt.figure(constrained_layout=False)

spec2 = gridspec.GridSpec(ncols=2, nrows=2, figure=fig)
ax1 = fig.add_subplot(spec2[0, 0])
ax2 = fig.add_subplot(spec2[0, 1])
ax3 = fig.add_subplot(spec2[1, 0])
ax4 = fig.add_subplot(spec2[1, 1])

df.boxplot(column='km', by='age', ax=ax1)
df.boxplot(column='preco', by='age', ax=ax2)
df.groupby(['year']).preco.mean().plot(kind='bar', ax=ax3, legend=True)
df.groupby(['year']).km.mean().plot(kind='bar', ax=ax4, legend=True)"""

# plt.show()
