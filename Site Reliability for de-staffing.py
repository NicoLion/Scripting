#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#pip install cufflinks - might be necessary to run this script


# In[1]:


# here we import the packages for the code to run
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
import pytz
from scipy.special import factorial

import plotly.plotly as py
import plotly.graph_objs as go
from plotly.offline import iplot

import cufflinks as cf
cf.go_offline()
cf.set_config_file(world_readable=True, theme='pearl')

from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = 'all'


# ## Probability of failure (Poisson)

# In[2]:


# we define the poisson distribution parametes - most of the structure was gathered from online sources including : https://towardsdatascience.com/the-poisson-distribution-and-poisson-process-explained-4e2cb17d459

events_per_month = 12/3 # this is the operational data gathered from https://docs.google.com/spreadsheets/d/1YW1f6XBMr1GiINS1MoDf7u1izXh4_wf7l3SVYILdtgo/edit#gid=1171588847
# there were 11 events over 3m
month = 1 # we define the period of interest as a month since that is the lenght of the billing cycle if we set it up! 0.5 then it will mean 15 days or a sprint

# Expected events
lam = events_per_month * month

k = 1 # this is the number of failures whose probabilty is to be known
p_k = np.exp(-lam) * np.power(lam, k) / factorial(k)
print(f'The probability of {k} failures in {month} billing period is {100*p_k:.2f}%.')


# In[3]:


#This is a simulation of 10000 events of a poisson distribution with lambda as defined above
x = np.random.poisson(lam, 10000)
(x == 3).mean()


# In[4]:


# this is a simple function to calculate the poisson probabilities 
def calc_prob(events_per_month, month, k):
    # Calculate probability of k events in specified number of months
    lam = events_per_month * month
    return np.exp(-lam) * np.power(lam, k) / factorial(k)
    
calc_prob(events_per_month, month, 3)


# In[5]:


# Different numbers of failures could potentially be present within a month so we generate an array of possible failures
ns = np.arange(14)
p_n = calc_prob(events_per_month, month, ns)

print(f'The most likely value is {np.argmax(p_n)} failures with probability {np.max(p_n):.4f}')


# In[6]:


p_n


# In[7]:


def plot_pdf(x, p_x, title=''):
    # Plot PDF of Poisson distribution ( probability density function)
    df = pd.DataFrame({'x': x, 'y': p_x})
    print(f'The most likely value is {np.argmax(p_x)} failures with probability {np.max(p_x):.4f}')
    annotations = [dict(x=x, y=y+0.01, text=f'{y:.2f}', 
                        showarrow=False, textangle=0) for x, y in zip(df['x'], df['y'])]
    df.iplot(kind='scatter', mode='markers+lines',
             x='x', y='y', xTitle='Number of failure events that makes us go to site',
             yTitle='Probability', annotations=annotations,
             title=title)


# In[8]:


plot_pdf(ns, p_n, title='Probability as a Function of Number of Failures in Billing Beriod  (Lambda = 12/3)')


# ## Distribution with different rates, assuming our site improvements lower the failure rate

# In[9]:


def plot_different_rates(events_per_month, month, ns, title=''):
    df = pd.DataFrame()
    annotations=[]
    colors = ['orange', 'green', 'red', 'blue', 'purple', 'brown']
    for i, events in enumerate(events_per_month):
        probs = calc_prob(events, month, ns)
        annotations.append(dict(x=np.argmax(probs)+1, y=np.max(probs)+0.025, 
                                text=f'{int(events * month)} FPM<br>Failures = {np.argmax(probs) + 1}<br>P = {np.max(probs):.2f}',
                                color=colors[i],
                               showarrow=False, textangle=0))
        df[f'Failures Per Month = {int(events * month)}'] = probs
    df.index = ns
    df.iplot(kind='scatter', mode='markers+lines', colors=colors, size=8, annotations=annotations,
             xTitle='Failure Events that makes us go to site', yTitle='Probability', title=title)
    return df


# In[10]:


df = plot_different_rates(events_per_month=np.array([1, 2, 3, 4, 5, 6]),
                          month=1,
                          ns=list(range(10)), 
                          title='Probability of Failures Events in 1 Billing Cycle at different WMEC site failure rates')


# ## Waiting times until next failure

# In[20]:


def waiting_time_more_than(events_per_month, t, quiet=False):
    p = np.exp(-events_per_month * t)
    if not quiet:
        print(f'{int(events_per_month*1)} Failures per month. Probability of waiting more than {t} months: {100*p:.2f}%.')
    return p
    
def waiting_time_less_than_or_equal(events_per_month, t, quiet=False):
    p = 1 - waiting_time_more_than(events_per_month, t, quiet=quiet)
    if not quiet:
        print(f'{int(events_per_month*1)} Failures per month. Probability of waiting at most {t} months: {100*p:.2f}%.')
    return p

def waiting_time_between(events_per_month, t1, t2):
    p1 = waiting_time_less_than_or_equal(events_per_month, t1, True)
    p2 = waiting_time_less_than_or_equal(events_per_month, t2, True)
    p = p2-p1
    print(f'Probability of waiting between {t1} and {t2} months: {100*p:.2f}%.')
    return p

assert waiting_time_more_than(events_per_month, 15, True) + waiting_time_less_than_or_equal(events_per_month, 15, True) == 1


# In[21]:


def plot_waiting_time(events_per_month, ts, title=''):
    p_t = waiting_time_more_than(events_per_month, ts, quiet=True)
    
    df = pd.DataFrame({'x': ts, 'y': p_t})
    df.iplot(kind='scatter', mode='markers+lines', size=8,
             x='x', y='y', xTitle='Waiting Time',
             yTitle='Probability', 
             title=title)
    
    return p_t


# In[22]:


_ = waiting_time_less_than_or_equal(events_per_month, 0.5)


# In[36]:


_ = waiting_time_between(events_per_month,0.1, 0.5)


# In[31]:


p_t = plot_waiting_time(events_per_month, np.arange(5), title='Probability (T > t)')


# ## Average waiting time

# In[39]:


np.random.seed(42)

events = np.random.choice([0, 1], size = 100000, replace=True, 
                          p=[1-0.27, 0.27])

success_times = np.where(events==1)[0]
waiting_times = np.diff(success_times)
waiting_times[:10]


# In[40]:


np.mean(waiting_times)


# In[41]:


def plot_hist_waiting_time(x, title=''):
    df = pd.DataFrame(x)
    df.iplot(kind='hist', xTitle='Waiting Time between Events', bins=(0, 100, 1),
             yTitle='Count', title=title)


# In[42]:


plot_hist_waiting_time(waiting_times, title='Waiting Time Distribution')


# In[ ]:




