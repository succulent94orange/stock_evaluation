from pandas_datareader import data as wb
from datetime import date, timedelta
import pandas as pd
import requests
import numpy as np
from bs4 import BeautifulSoup

#Set the company to evaluate
company = input("ticker\n").upper()
## Estimate the Cost of capital using CAPM

#Twenty years of trading days i.e. 5000 = 250 * 20
dt = date.today() - timedelta(5000)

## 10-year US Treasury Yield
url = requests.get(f'https://finance.yahoo.com/quote/%5ETNX?p=^TNX&.tsrc=fin-srch').text
soup = BeautifulSoup(url, 'lxml')

Rf = soup.find("fin-streamer", {'class': 'Fw(b) Fz(36px) Mb(-4px) D(ib)'}).text
Rf = float(Rf)

## Get Beta (5Y Monthly)
url = requests.get(f'https://finance.yahoo.com/quote/{company}/').text
soup = BeautifulSoup(url, 'lxml')

beta = soup.find('td', {'data-test': 'BETA_5Y-value'}).text
beta = float(beta)

## Get the Market Rate
# Ticker and data source
SPY = wb.DataReader('SPY', data_source='yahoo', start=dt)

# Calculate total log returns
SPY['log_returns'] = np.log(SPY['Adj Close'] / SPY['Adj Close'].shift(1))

log_returns_a = SPY['log_returns'].mean() * 250
Rm = log_returns_a * 100

## Equity Risk Premium
ERP = Rm - Rf
ERP = round(ERP, 4)

## Estimating the Cost of Capital using CAPM
CAPM = Rf + beta * (Rm - Rf)
CAPM = round(CAPM, 4)

ke = CAPM/100

## Get the Five-Year EBITDA Growth Rate

url = 'https://www.macrotrends.net/stocks/charts/' + company + '/' + company + '/ebitda'
r = requests.get(url)
df_ebitda = pd.read_html(r.text)
df_e = pd.DataFrame(df_ebitda[0])

# Remove Column Names
df_e.columns = range(df_e.shape[1])

# Remove "$" form data
array_grwth_ebitda = pd.DataFrame(df_e[1], index=[0, 1, 2, 3, 4, 5]).replace('[\$,]', '', regex=True).astype(float)

# Get the log growth rate

array_grwth_ebitda = np.log(array_grwth_ebitda / array_grwth_ebitda.shift(-1))

# Get the five-year average revenue growth rate

avg_ebitda_growth = array_grwth_ebitda.mean()
avg_ebitda_growth = float(avg_ebitda_growth)


## Get the Five-year Revenue Growth Rate
url = 'https://www.macrotrends.net/stocks/charts/' + company + '/' + company + '/revenue'
r = requests.get(url)
df_rev = pd.read_html(r.text)
df_r = pd.DataFrame(df_rev[0])

# Remove Column Names
df_r.columns = range(df_r.shape[1])

# Remove "$" form data
array_grwth_rev = pd.DataFrame(df_r[1], index=[0, 1, 2, 3, 4, 5]).replace('[\$,]', '', regex=True).astype(float)

# Get the log growth rate
array_grwth_rev = np.log((array_grwth_rev) / array_grwth_rev.shift(-1))

# Get the five-year average revenue growth rate

avg_rev_growth = array_grwth_rev.mean()
avg_rev_growth = float(avg_rev_growth)


# Average Revenue and EBITDA Growth Rate

avg_growth_rate  = (avg_ebitda_growth + avg_rev_growth)/2


## Get projected EPS
url = 'https://www.marketwatch.com/investing/stock/' + company +'/analystestimates'
r = requests.get(url)
df_projected_eps = pd.read_html(r.text)
df_future_eps = pd.DataFrame(df_projected_eps[4], index=[9])

pro_eps = df_future_eps.iloc[0][1]
pro_eps = float(pro_eps)

#### DCF Valuation

# Value in the first three years

## Year One

    #Cash Flows
CF_Y_One = pro_eps * 0.9

    #Present Value
PV_Y_One = CF_Y_One / (1 + ke)

##Year Two

    # Cash Flow
CF_Y_Two = CF_Y_One * (1 + avg_growth_rate)

    # Present Value
PV_Y_Two = CF_Y_Two / (1 + ke)**2

##  Year Three

    # Cash Flow
CF_Y_Three = CF_Y_Two * (1 + avg_growth_rate)

    # Present Value
PV_Y_Three = CF_Y_Three / (1 + ke)**3

## Value of first Three Years

Value_First_Three_Years = PV_Y_One + PV_Y_Two + PV_Y_Three

# Stage 1
# Stage one Growth Rate is avg_growth_rate * .85
##Year Four

Stage_One_Growth_Rate = avg_growth_rate * .85

    # Cash Flow
CF_Y_Four = CF_Y_Three * (1 + Stage_One_Growth_Rate)

    # Present Value
PV_Y_Four = CF_Y_Four / (1 + ke)**4

##Year Five

    # Cash Flow
CF_Y_Five = CF_Y_Four * (1 + Stage_One_Growth_Rate)

    # Present Value
PV_Y_Five = CF_Y_Five / (1 + ke)**5

##Year Six

    # Cash Flow
CF_Y_Six = CF_Y_Five * (1 + Stage_One_Growth_Rate)

    # Present Value
PV_Y_Six = CF_Y_Six / (1 + ke)**6

# Value at Stage 1
Value_Stage_One = PV_Y_Four + PV_Y_Five + PV_Y_Six

# Stage 2
# Stage two Growth Rate is avg_growth_rate * .65

##Year Seven
Stage_Two_Growth_Rate = avg_growth_rate * .65

    # Cash Flow
CF_Y_Seven = CF_Y_Six * (1 + Stage_Two_Growth_Rate)

    # Present Value
PV_Y_Seven = CF_Y_Seven / (1 + ke)**7

##Year Eight

    # Cash Flow
CF_Y_Eight = CF_Y_Seven * (1 + Stage_Two_Growth_Rate)

    # Present Value
PV_Y_Eight = CF_Y_Eight / (1 + ke)**8

##Year Nine

    # Cash Flow
CF_Y_Nine = CF_Y_Eight * (1 + Stage_Two_Growth_Rate)

    # Present Value
PV_Y_Nine = CF_Y_Nine / (1 + ke)**9

# Value at Stage 2
Value_Stage_Two = PV_Y_Seven + PV_Y_Eight + PV_Y_Nine

# Stage 3
# Stage two Growth Rate is avg_growth_rate * .35

##Year 10
Stage_Three_Growth_Rate = avg_growth_rate * .35

    # Cash Flow
CF_Y_Ten = CF_Y_Nine * (1 + Stage_Three_Growth_Rate)

    # Present Value
PV_Y_Ten = CF_Y_Ten / (1 + ke)**10

##Year 11

    # Cash Flow
CF_Y_Eleven = CF_Y_Ten * (1 + Stage_Three_Growth_Rate)

    # Present Value
PV_Y_Eleven = CF_Y_Eleven / (1 + ke)**11

##Year 12

    # Cash Flow
CF_Y_Twelve = CF_Y_Eleven * (1 + Stage_Three_Growth_Rate)

    # Present Value
PV_Y_Twelve = CF_Y_Twelve / (1 + ke)**12

# Value at Stage 2
Value_Stage_Three = PV_Y_Ten + PV_Y_Eleven + PV_Y_Twelve

# Terminal Value

T_Val = ((CF_Y_Twelve * ( 1 + Stage_Three_Growth_Rate)) / (ke - Stage_Three_Growth_Rate))/4

# Display DCF Calculation
print(T_Val + Value_Stage_One + Value_Stage_Two + Value_Stage_Three + Value_First_Three_Years)
