import requests
import pandas as pd
import numpy as np

while True:
        try:
            company = input("\n To get a growth rate estimate growth rate: ").upper()
            if company == 'exit':
                exit()
            else:
        ## Get the Five-Year EBITDA Growth Rate

                url = 'https://www.macrotrends.net/stocks/charts/' + company + '/' + company + '/ebitda'
                r = requests.get(url)
                df_ebitda = pd.read_html(r.text)
                df_e = pd.DataFrame(df_ebitda[0])

                # Remove Column Names
                df_e.columns = range(df_e.shape[1])


                #Remove "$" form data
                array_grwth_ebitda = pd.DataFrame(df_e[1], index=[0,1,2,3,4,5]).replace('[\$,]', '', regex=True).astype(float)


                # Get the log growth rate

                array_grwth_ebitda = np.log(array_grwth_ebitda / array_grwth_ebitda.shift(-1))


                # Get the five-year average revenue growth rate

                avg_ebitda_growth = array_grwth_ebitda.mean()

                # To numpy array

                np_avg_ebitda_growth = avg_ebitda_growth.to_numpy()

                # The next two lines are for the print statement
                n_a_e_g = np_avg_ebitda_growth * 100
                n_a_e_g


                ## Get the Five-year Revenue Growth Rate
                url = 'https://www.macrotrends.net/stocks/charts/' + company + '/' + company + '/revenue'
                r = requests.get(url)
                df_rev = pd.read_html(r.text)
                df_r = pd.DataFrame(df_rev[0])

                # Remove Column Names
                df_r.columns = range(df_r.shape[1])

                #Remove "$" form data
                array_grwth_rev = pd.DataFrame(df_r[1], index=[0,1,2,3,4,5]).replace('[\$,]', '', regex=True).astype(float)

                # Get the log growth rate
                array_grwth_rev = np.log((array_grwth_rev) / array_grwth_rev.shift(-1))

                # Get the five-year average revenue growth rate

                avg_rev_growth = array_grwth_rev.mean()

                # To numpy array

                np_avg_rev_growth = avg_rev_growth.to_numpy()

                # The next two lines are for the print statement
                n_a_r_g = np_avg_rev_growth * 100
                n_a_r_g

                # The next two lines are for the print statement
                avg_rate = (n_a_r_g + n_a_e_g) / 2
                avg_rate

                print('\nThe five-year average of the revenue and EBITDA growth rate for ' + company + ' is ' + str(round(*avg_rate, 4)) + '%.')
        except ValueError:
                print("Not a valid ticker! \nEnter a ticker symbol!")