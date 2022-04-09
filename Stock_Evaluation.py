from pandas_datareader import data as wb
from datetime import date, timedelta
import pandas as pd
import requests
import numpy as np
from bs4 import BeautifulSoup
import re

# Enter Required Return
try:
    required_return = input("Enter your required returned as a decimal. \n")
    if required_return == 'exit':
        exit()
    else:
        required_return = float(required_return)
except ValueError:
    exit()
while True:
    try:
        # Enter the ticker to evaluate
        company = input("\nWhat company would you like to value?\n").upper()
        if company == 'exit':
            exit()
        else:
            ## Get external estimate for intrinstic value
            url = 'https://www.macroaxis.com/valuation/' + company +'/'
            r = requests.get(url)
            df_intrinsic_value = pd.read_html(r.text)
            df_i_v = pd.DataFrame(df_intrinsic_value[3])
            df_i_val = df_i_v.replace(r'[a-zA-Z]', '', regex=True)

            df_i_val = df_i_val.iloc[0][1]
            int_val = float(df_i_val)

            ## Estimate the Cost of capital using CAPM

            #Twenty years of trading days i.e. 5000 = 250 * 20
            dt = date.today() - timedelta(5000)

            ## 10-year US Treasury Yield
            url = requests.get(f'https://www.cnbc.com/quotes/US10Y').text
            soup = BeautifulSoup(url, 'lxml')
            US_Ten_Year_text = soup.find('span', {'class': 'QuoteStrip-lastPrice'}).text
            Rf = US_Ten_Year_text.strip("%")
            Rf = float(Rf)

            ## Get Beta
            url = requests.get(f'https://www.cnbc.com/quotes/{company}').text
            soup = BeautifulSoup(url, 'lxml')
            beta_summary_text = soup.find('li', {'class': 'Summary-beta'}).text
            beta = re.sub(r'[a-zA-Z]', '', beta_summary_text)
            beta = float(beta)

            ## Get the Market Rate
            url = 'https://www.macrotrends.net/2526/sp-500-historical-annual-returns'
            r = requests.get(url)
            market_text = pd.read_html(r.text)
            df_market = pd.DataFrame(market_text[0])

            # Remove Column Names
            df_market.columns = range(df_market.shape[1])

            # 10 Previous Years of market closing price
            SPY = pd.DataFrame(df_market[1], index=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]).astype(float)

            # Log Returns
            # x = np.log(market_close[0]/ market_close[9]).mean

            SPY['log_returns'] = np.log(SPY[1] / SPY[1].shift(-1))

            log_returns_a = SPY['log_returns'].mean()
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

            avg_growth_rate = (avg_ebitda_growth + avg_rev_growth) / 2

            ## Get projected EPS
            url = 'https://www.marketwatch.com/investing/stock/' + company + '/analystestimates'
            r = requests.get(url)
            df_projected_eps = pd.read_html(r.text)
            df_future_eps = pd.DataFrame(df_projected_eps[4], index=[9])

            pro_eps = df_future_eps.iloc[0][1]
            pro_eps = float(pro_eps)

            #### DCF Valuation

            xn = (avg_growth_rate - 0.04) / 4

            # Value in the first three years

            ## Year One

            # Cash Flows
            CF_Y_One = pro_eps * 0.9

            # Present Value
            PV_Y_One = CF_Y_One / (1 + ke)

            ##Year Two

            # Cash Flow
            CF_Y_Two = CF_Y_One * (1 + avg_growth_rate)

            # Present Value
            PV_Y_Two = CF_Y_Two / (1 + ke) ** 2

            ##  Year Three

            # Cash Flow
            CF_Y_Three = CF_Y_Two * (1 + avg_growth_rate)

            # Present Value
            PV_Y_Three = CF_Y_Three / (1 + ke) ** 3

            # Stage 1
            # Year 4
            CF_Y_Four = CF_Y_Three * (1 + avg_growth_rate)

            # Present Value
            PV_Y_Four = CF_Y_Four / (1 + ke) ** 4

            # Year 5
            CF_Y_Five = CF_Y_Four * (1 + avg_growth_rate)

            # Present Value
            PV_Y_Five = CF_Y_Five / (1 + ke) ** 5

            # Year 6
            CF_Y_Six = CF_Y_Five * (1 + avg_growth_rate)

            # Present Value
            PV_Y_Six = CF_Y_Six / (1 + ke) ** 5

            # Stage 2
            ##Year Four
            # Dividends
            Div_Y_Four = CF_Y_Three * ((1 + avg_growth_rate) ** 4) * ((1 + avg_growth_rate - xn) ** (4 - 3))

            # Cash Flow with Divided
            CF_Y_Four_Div = Div_Y_Four / (1 + required_return) ** (4 + 3)

            ## Year Five
            # Dividends
            Div_Y_Five = Div_Y_Four * (1 + required_return) - (5 - 3) * (xn)

            # Cash Flow with Divided
            CF_Y_Five_Div = Div_Y_Five / (1 + required_return) ** (5 + 3)

            ## Year Six
            # Dividends
            Div_Y_Six = Div_Y_Five * (1 + required_return) - (6 - 3) * (xn)

            # Cash Flow with Divided
            CF_Y_Six_Div = Div_Y_Six / (1 + required_return) ** (6 + 3)

            ## Year Seven
            # Dividends
            Div_Y_Seven = Div_Y_Six * (1 + required_return) - (7 - 3) * (xn)

            # Cash Flow with Divided
            CF_Y_Seven_Div = Div_Y_Seven / (1 + required_return) ** (7 + 3)

            ## Year Six
            # Dividends
            Div_Y_Eight = Div_Y_Seven * (1 + required_return) - (8 - 3) * (xn)

            # Cash Flow with Divided
            CF_Y_Eight_Div = Div_Y_Eight / (1 + required_return) ** (8 + 3)

            ## Terminal Value
            Terminal_Value_Step_one = CF_Y_Eight_Div * (1 + 0.04)
            Terminal_Value_Step_two = Terminal_Value_Step_one / (required_return - 0.04)

            ## Value of first Three Years

            Value_First_Three_Years = PV_Y_One + PV_Y_Two + PV_Y_Three

            ## Value of Stage 1
            Value_Stage_One = PV_Y_Four + PV_Y_Five + PV_Y_Six

            ## Value of Stage 2
            Value_Stage_Two = CF_Y_Four_Div + CF_Y_Five_Div + CF_Y_Six_Div + CF_Y_Seven_Div + CF_Y_Eight_Div

            ## Value at Stage 3
            Value_Stage_Three = Terminal_Value_Step_two / (1 + ke) ** (avg_growth_rate + 5 + 3)

            ##Value of the Stock
            Value_of_Stock = Value_First_Three_Years + Value_Stage_One + Value_Stage_Two + Value_Stage_Three

            ## Get TTM EPS
            url = 'https://www.macrotrends.net/stocks/charts/' + company + '/' + company + '/eps-earnings-per-share-diluted'
            r = requests.get(url)
            df_eps = pd.read_html(r.text)

            # Remove "$" form data
            array_eps = pd.DataFrame(df_eps[0], index=[0]).replace('[\$,]', '', regex=True).astype(float)

            # Remove Column Names
            array_eps.columns = range(array_eps.shape[1])

            eps_df = array_eps.iloc[0][1]

            ## Get the P/E , the P/S, P/B, and P/CF
            url = 'https://www.marketwatch.com/investing/stock/' + company + '/company-profile?mod=mw_quote_tab'
            r = requests.get(url)
            df_ratios = pd.read_html(r.text)
            df_key_ratios = pd.DataFrame(df_ratios[4], index=[2, 3, 4, 5])
            df_num = pd.DataFrame(df_ratios[4])

            # Price per Earning (used is without extraordinary items)
            pe_df = df_key_ratios.iloc[0][1]

            # Relative Valuation of the P/E
            Price_PE = pe_df * eps_df

            # Price to Sales Ratio
            ps_df = df_key_ratios.iloc[1][1]

            # Relative Valuation of the P/S
            Price_PS = ps_df * eps_df

            # Price to Book Ratio
            pb_df = df_key_ratios.iloc[2][1]

            # Relative Valuation of the P/B
            Price_PB = pb_df * eps_df

            # Price to Cash Flows Ratio
            pcf_df = df_key_ratios.iloc[3][1]

            # Relative Valuation of the P/CF
            Price_PCF = pcf_df * eps_df

            ## Relative average
            RA = ((Price_PCF) + (Price_PB) + (Price_PS) + (Price_PE))/4
            RA = round(RA, 2)


## Weighted Average of Estimates
            W_Avg_Est = int_val *.25 +  Value_of_Stock*.5 + RA*.25

            print('The best estimated value of ' + company + ' is $' + str(round(W_Avg_Est,2)) + '.')

# Get the current stock price
            url = requests.get(f'https://www.cnbc.com/quotes/{company}').text
            soup = BeautifulSoup(url, 'lxml')
            current_price = soup.find('span', {'class': 'QuoteStrip-lastPrice'}).text

            print("\nThe current stock price of " + company + " is $" + current_price + '.')

    except ValueError:
        print("Not a valid ticker! \nEnter a ticker symbol.")
    except AttributeError:
        exit()
