#David Tsang
#davidtsanghw.github.io
#20 March 2021
#Correlation Coefficient Analysis

import numpy as np
import pandas as pd

#to visualize the results
import matplotlib.pyplot as plt
import matplotlib.cm
import seaborn

import sqlite3

from PIL import Image, ImageDraw, ImageFont

from datetime import datetime, timedelta
from datetime import timedelta
from datetime import date

from pandas.plotting import table

import matplotlib.image as mpimg

try:
    from PIL import Image
except ImportError:
    import Image

#Database is available at davidtsanghw.github.io
wdir = '\\Python\\data\\'
afile = wdir + 'fin.db'

con = sqlite3.connect(afile)
cursor = con.cursor()

def createChart(base_list, compare_list, chartTitle, fileName, dayShift, bcompany_list, company_list):

    #array to store prices
    symbols=[]

    shift = "date([DATE],'-" +  str(dayShift) + " day')"

    for symbol in base_list: 
        print(symbol)

        sql = 'select * from [Historical] '
        sql = sql + ' where [Date] >= \'' + str(startDate) + '\' and [Date] <= \'' + str(endDate) + '\''
        sql = sql + ' and SYMBOL = \''+ symbol + '\''

        r = pd.read_sql(sql,con)
        
        r['SYMBOL'] = r['SYMBOL']
        
        symbols.append(r)

    for symbol in compare_list: 

        print(symbol)

        sql = "select " +  shift  + " as [DATE], [OPEN], [HIGH], [LOW], [CLOSE], [SYMBOL] from [Historical]"
        sql = sql + " where " +  shift  + " >= '" + str(startDate) + "' and " +  shift  + " <= '" + str(endDate) + "'"
        sql = sql + " and SYMBOL = '" + symbol + "'"

        print(sql)
        
        r = pd.read_sql(sql,con)
        
        symbols.append(r)

    df = pd.concat(symbols)
    df = df.reset_index()
    df = df[['DATE', 'CLOSE', 'SYMBOL']]
    df.head()

    df_pivot = df.pivot('DATE','SYMBOL','CLOSE').reset_index()
    df_pivot.head()

    corr_df = df_pivot.corr(method='pearson')

    #reset symbol as index (rather than 0-X)
    corr_df.head().reset_index()

    #del corr_df.index.name
    corr_df = corr_df.rename_axis(None, axis=1)

    corr_df = corr_df.round(1)

    #take the bottom triangle since it repeats itself
    mask = np.zeros_like(corr_df)
    mask[np.triu_indices_from(mask)] = True

    ax = plt.axes()

    hmax = seaborn.heatmap(corr_df, annot=True, cmap="YlGnBu", vmax=1.0, vmin=-1.0 , mask = mask, linewidths=2.5, ax = ax, xticklabels=True, yticklabels=True)
    
    plt.yticks(rotation=0) 
    plt.xticks(rotation=90)

    ax.set_title(chartTitle, fontdict={'fontsize': 20, 'fontweight': 'medium'})

    ax.text(0.9, 4, 'Correlation Analysis',
             fontsize=75, color='gray',
             ha='left', va='bottom', alpha=0.3)

    figure = plt.gcf() # get current figure
    figure.set_size_inches(16, 12)

    # when saving, specify the DPI
    plt.savefig(fileName, dpi = 120)

    text1 = ''
    text2 = ''

    print(company_list)

##    for i in range(0,len(base_list)):
##        text1 = text1 + base_list[i] + '\n'
##        text2 = text2 + bcompany_list[i] + '\n'
##
##    for i in range(0,len(compare_list)):
##        text1 = text1 + '*' + compare_list[i] + '\n'
##        text2 = text2 + company_list[i] + '\n'

    text1 = text1 + '*Date shifting by ' + str(dayShift) + ' day(s)\n\n'

    text1 = text1 + '+1 indicates moving in the same direction\n'
    text1 = text1 + '-1 indicates moving in the opposite direction'

    img = Image.open(fileName)
     
    fnt = ImageFont.truetype('drawtext.ttc', 20)

    d = ImageDraw.Draw(img)
    d.text((800,260), text1, font=fnt, fill=(0, 0, 0))
    d.text((945,260), text2, font=fnt, fill=(0, 0, 0))
    
    d.text((945,1400), fileName, font=fnt, fill=(0, 0, 0))     

    img.save(fileName)

    plt.close()

    return

#
#
#
def get_risk(prices):
    return (prices / prices.shift(1) - 1).dropna().std().values

def get_return(prices):
    print(len(prices))
    print(np.sqrt(250))
    p = 250
    p = len(prices)
    return ((prices / prices.shift(1) - 1).dropna().mean() * np.sqrt(p)).values    


def returnAndRisk(symbols, chartTitle, fileName):

    sql = 'select * from [TimeSeries] '
    sql = sql + ' where [Date] >= \'' + str(startDate) + '\' and [Date] <= \'' + str(endDate) + '\''

    df_dates = pd.read_sql(sql,con)

    prices = df_dates

    for symbol in symbols:

        print(symbol)

        sql = 'select [DATE], [PRICE] from ('
        #sql = sql + 'select [OPEN] as [PRICE], [DATE] from [Historical] where symbol = \'' + symbol + '\''
        #sql = sql + ' union all '
        #sql = sql + 'select [LOW] as [PRICE], [DATE] from [Historical] where symbol = \'' + symbol + '\''
        #sql = sql + ' union all '    
        #sql = sql + 'select [HIGH] as [PRICE], [DATE] from [Historical] where symbol = \'' + symbol + '\''
        #sql = sql + ' union all '    
        sql = sql + 'select [CLOSE] as [PRICE], [DATE] from [Historical] where symbol = \'' + symbol + '\''
        sql = sql + ') order by [DATE]'

        portfolio = pd.read_sql(sql,con)
        close = portfolio[['PRICE']]
        close = close.rename(columns={'PRICE': symbol})
        prices = prices.join(close)
        
    prices = prices.dropna()

    prices = prices.set_index('Date')

    risk_v = get_risk(prices)

    return_v = get_return(prices)

    fig, ax = plt.subplots()
    ax.scatter(x=risk_v, y=return_v)

    ax.set_title(chartTitle, fontdict={'fontsize': 20, 'fontweight': 'medium'})

    ax.text(0.01, 0.01, '(Incomplete - Risk and Return Analysis',
             fontsize=75, color='gray',
             ha='left', va='bottom', alpha=0.3)

    ax.set(xlabel='Risk', ylabel='Return')

    for i, symbol in enumerate(symbols):
        text = symbol
        text = text.replace('AUDUSD-ASX-','US$')        
        text = text.replace('ASX-','A$')
        x = risk_v[i]
        y = return_v[i]

        x1 = +30
        y1 = +100

        if text.find('US$') > -1:
            x1 = -x1
            y1 = -y1
        
        ax.annotate(text,(x,y),
                    xytext=(x1, y1),
                    textcoords='offset points',
                    arrowprops=dict(arrowstyle='->, head_width=0.3', facecolor='black', color='black'))

    #Draw a red line for at 0
    plt.axhline(y=0.0, color='r', linestyle='-')

    plt.grid()
    figure = plt.gcf()
    figure.set_size_inches(16, 12)

    print(fileName)

    plt.savefig(fileName, dpi = 120)

    plt.close()

    img = Image.open(fileName)
     
    fnt = ImageFont.truetype('drawtext.ttc', 20)

    d = ImageDraw.Draw(img)
    
    d.text((945,1400), fileName, font=fnt, fill=(0, 0, 0))     

    img.save(fileName)

    return


startDate = date(2010, 3, 31)
endDate = date(2020, 12, 31)
dayShift = 1

page = 0

base_list = []
base_list =['AUDCAD=X','AUDCHF=X','AUDJPY=X','AUDNZD=X','AUDUSD=X','AUDHKD=X','CADCHF=X','CADJPY=X','CHFJPY=X','EURAUD=X','EURCAD=X','EURCHF=X','EURGBP=X','EURJPY=X','EURNZD=X','EURUSD=X','GBPAUD=X','GBPCAD=X','GBPCHF=X','GBPJPY=X','GBPNZD=X','GBPUSD=X','NZDCAD=X','NZDCHF=X','NZDJPY=X','NZDUSD=X','USDCAD=X','USDCHF=X','USDJPY=X']

bcom_list = []
bcom_list =['AUDCAD=X','AUDCHF=X','AUDJPY=X','AUDNZD=X','AUDUSD=X','AUDHKD=X','CADCHF=X','CADJPY=X','CHFJPY=X','EURAUD=X','EURCAD=X','EURCHF=X','EURGBP=X','EURJPY=X','EURNZD=X','EURUSD=X','GBPAUD=X','GBPCAD=X','GBPCHF=X','GBPJPY=X','GBPNZD=X','GBPUSD=X','NZDCAD=X','NZDCHF=X','NZDJPY=X','NZDUSD=X','USDCAD=X','USDCHF=X','USDJPY=X']


sub_list = base_list
com_list = bcom_list

#sub_list.remove('AUDHKD=X')
#com_list.remove('AUDHKD=X')

base_list = ['GC=F']
bcom_list = ['GC=F']

mTitle = 'Pearson\'s Correlation Coefficient in FX \nFor the period from ' + str(startDate) + ' to ' + str(endDate) 
filename = 'correlation\\' + str(page) + 'A.png'
createChart(base_list,sub_list,mTitle, filename, dayShift, bcom_list, com_list)

filename = 'correlation\\' + str(page) + 'B.png'
mTitle = 'Return and risk in FX \nFor the period from ' + str(startDate) + ' to ' + str(endDate) 
returnAndRisk(base_list+sub_list,mTitle,filename)

page = 1

for dayShift in range(1, 90):
    
        #symbols_list = bsymbols        

        mTitle = 'Pearson\'s Correlation Coefficient in FX\nFor the period from ' + str(startDate) + ' to ' + str(endDate) 

        filename = 'correlation\\' + str(page) + 'A.png'
        createChart(base_list,sub_list,mTitle, filename, dayShift, bcom_list, com_list)

        filename = 'correlation\\' + str(page) + 'B.png'
        mTitle = 'Return and risk in FX\nFor the period from ' + str(startDate) + ' to ' + str(endDate) 
        returnAndRisk(base_list+sub_list,mTitle,filename)

        page = page + 1

con.close()
