#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Script calculates the total DCHG during the full DCHG session on 3/28
#


# In[2]:


get_ipython().system('pip install pytool')


# In[3]:


import pandas as pd
import numpy as np
import time
import datetime as dt
import axpac.cpl as cpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pickle as pickle
import pytz as pytz
import pytool
from darksky import forecast
import datetime
from datetime import timedelta
import scipy
from itertools import groupby

import math as math

import pickle as pickle
from CoolProp.CoolProp import PropsSI
from scipy.optimize import curve_fit
from sklearn import linear_model
from pandas import DataFrame
from mpl_toolkits.mplot3d import Axes3D
from pandas import ExcelWriter
from IPython.core.interactiveshell import InteractiveShell
import statsmodels.formula.api as sm
InteractiveShell.ast_node_interactivity = "all"
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.dates as mdates

pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 100000)
pd.options.mode.chained_assignment = None  # default='warn'


# In[4]:


df1 = pd.read_csv('FullDCHGcooling.csv')
df = df1.dropna()
#df['Time'] = pd.to_datetime(df.Time)
#df.index = df['Time']


# In[5]:


df.head(1)


# In[6]:


PCES = df.loc[df['Time'] < '2019-03-28T20:00:02-07:00']
PureTemp = df.loc[df['Time'] > '2019-03-28T22:05:02-07:00']
Mixpart = df.loc[df['Time'] < '2019-03-28T22:05:02-07:00']
Mix =  Mixpart.loc[Mixpart['Time'] > '2019-03-28T20:00:02-07:00']


# In[7]:


PCES['Time'] = PCES['Time'].apply(lambda t: pd.to_datetime(t) - datetime.timedelta(hours = 7))
PCES.set_index('Time', inplace=True)


# In[8]:


Mix['Time'] = Mix['Time'].apply(lambda t: pd.to_datetime(t) - datetime.timedelta(hours = 7))
Mix.set_index('Time', inplace=True)


# In[9]:


PureTemp['Time'] = PureTemp['Time'].apply(lambda t: pd.to_datetime(t) - datetime.timedelta(hours = 7))
PureTemp.set_index('Time', inplace=True)


# In[10]:


CoolingkW = df['CoolingkW'] # this value corresponds to power tranfered during the whole lenght of the discharge session
kWht = CoolingkW.sum()/(1800)# data on 2 seconds intervals 
kWhe = CoolingkW.sum()/(1800*3)

PCESCool = PCES['CoolingkW']# this value corresponds to the value of power transfered from PCES tanks
#PCESCool['Time'] = pd.to_datetime(df.Time) - datetime.timedelta(hours = 7)



kWhtPCES = PCESCool.sum()/(1800) 
kWhePCES = PCESCool.sum()/(1800*3) # assuming COP of 3

PureTempCool = PureTemp['CoolingkW'] # this value corresponds to the value of power from PureTemp tanks
kWhtPT = PureTempCool.sum()/(1800)
kWhePT = PureTempCool.sum()/(1800*3) # assuming COP of 3

MixCool = Mix['CoolingkW'] # this value corresponds to the value of power from Mix Tanks
kWhtMix = MixCool.sum()/(1800)
kWheMix = MixCool.sum()/(1800*3) # assuming COP of 3

kWhtPCES/kWht
kWhtPT/kWht
kWhtMix/kWht
kWhtPCES/kWht+kWhtPT/kWht+kWhtMix/kWht


# In[11]:


PCES.head(1)


# In[12]:


print(kWht)
print(kWhe)
print(kWhtPCES)
print(kWhePCES)
print(kWhtPT)
print(kWhePT)
print(kWhtMix)
print(kWheMix)


# In[15]:



ax = plt.gca()
ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
PCESCool.plot(kind='line',x='Time',y='CoolingkW',color='green',ax=ax,label='PCES 75% - 1195 kWht')
MixCool.plot(kind='line',x='Time',y='CoolingkW', color='blue', ax=ax, label='Both PCES-PT 10% - 156 kWht')
PureTempCool.plot(kind='line',x='Time',y='CoolingkW', color='brown', ax=ax,label='PureTemp 15% - 235 kWht')
ax.legend(loc=4)
ax.set_title('Full DCHG Test WMEC - 1587 kWht')
plt.ylabel('Power [kWt]')
plt.xlabel('Time [03/28 10:00 - 03/29 04:45]')
plt.show()


# ## 

# 
