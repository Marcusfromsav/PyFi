# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 22:06:17 2024

@author: Marcus Lawrence
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import warnings
from datetime import datetime
import platform
# use glob to get all the xlsx files in the current

# find if working directory is in Mac or Windows
if platform.system() == 'Darwin':
    #ENTER PATH HERE FOR MAC
    path = r''
else:
    #ENTER PATH HERE FOR WINDOWS
    path = r''
excel_files = glob.glob(os.path.join(path,"*.xlsx"))

# initialize the arrays
Date = []
Debit = []
Credit = []
Runningbalance = []
Description = []

for f in excel_files:
    
    # read the excel file
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
    d_parser = lambda x: datetime.strptime(x, '%d/%m/%Y')    
    df = pd.read_excel(f)
    # print the location and filename
    # print('Location:', f) 
    print('File Name:', f.split("\\")[-1]) 
    # read data and append to respective global array
    date = df.loc[:,'Transaction Date']
    d = df.loc[:,'Debit']
    c = df.loc[:,'Credit']
    rb = df.loc[:,'Running Balance']
    des = df.loc[:,'Description']
    for i in date:
        Date.append(i)
    for i in d:
        Debit.append(i)
    for i in c:
        Credit.append(i)
    for i in rb:
        Runningbalance.append(i)
    for i in des:
        Description.append(i)

# transform completed list to data frames
date = pd.Series(Date)
debit = pd.Series(Debit)
credit = pd.Series(Credit)
runningbalance = pd.Series(Description)
description = pd.Series(Runningbalance)


# Combined data frame of date, debit, credit, and running balance
# Sort DataFrame via ascending Transaction Date
DataFrame = pd.concat([date,debit,credit,description,runningbalance],axis=1)
DataFrame.columns = ['Transaction Date','Debit','Credit','Running Balance','Description']
DataFrame = DataFrame.sort_values('Transaction Date',ascending=True)
# DataFrame['Running Balance'] = DataFrame['Running Balance'].str.strip()
# DataFrame['Running Balance'] = pd.to_numeric(DataFrame['Running Balance'].str.replace(',','').astype(float),errors='coerce',downcast='float')

# Running Balance Chart
# df = DataFrame.sort_values(by='Transaction Date',ascending=True)
x = DataFrame['Transaction Date']
y = DataFrame['Running Balance']
plt.figure(1)
plt.plot(x,y,color='dodgerblue',lw=1.2)
plt.xlim(x.iloc[0],x.iloc[-1])
plt.ylim(0)
plt.xticks(rotation=90)
plt.grid()
plt.title("Running Balance for EZ-Savings 012-60065")
plt.xlabel('Date')
plt.ylabel("Balance (KYD)")

# Projected Budget PieChart
plt.figure(2)
projectedBudget = pd.read_excel('projectedBudget.xlsx')
Total_Income = projectedBudget.iloc[5,5]
subTotals = projectedBudget.iloc[:,3]
Utilites = projectedBudget.iloc[3,3]
Transport = projectedBudget.iloc[6,3]
Personal = projectedBudget.iloc[12,3]
Food = projectedBudget.iloc[17,3]
Other = projectedBudget.iloc[22,3]
Subscriptions = projectedBudget.iloc[28,3]
Savings = projectedBudget.iloc[32,3]
Unallocated = projectedBudget.iloc[37,1]
budget = [Utilites,Transport,Personal,Food,Other,Subscriptions,Savings,Unallocated]
labels = ['Utilites','Transport','Personal','Food','Other','Subscriptions','Savings','Unallocated']
colors = ['#f13057','#f68118','#f9ca00','#e0e300','#aef133','#19ee9f','#01dddd','#00bfaf']
plt.pie(budget,labels=labels, wedgeprops={'edgecolor': 'black'},colors=colors,startangle=50,
        autopct="%1.1f%%",pctdistance=0.8,labeldistance=1.1,textprops={'size':11})
plt.rcParams.update({'font.size': 14})
plt.title('Pie Chart Showing Budget Distribution')
plt.tight_layout()

# Find Financial Insights
transactions = DataFrame['Description']
dates = DataFrame['Transaction Date']
credits_ = DataFrame['Credit']
debits = DataFrame['Debit']
