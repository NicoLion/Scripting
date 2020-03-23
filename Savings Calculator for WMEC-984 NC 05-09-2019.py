#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Hello


# In[2]:


get_ipython().system('pip install pytool')


# In[3]:


#General modules including data restructuring and machine learning libraries
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


pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 100000)
pd.options.mode.chained_assignment = None  # default='warn'


# In[4]:


Site = 'WMEC' #Pick 'WFLA' or 'WMEC'

#Start and ends of the periods
Lengths = [
    [dt.datetime(2019, 1, 16, 0, 0, 0), dt.datetime(2019,3,1,0,0,0)],
    [dt.datetime(2019, 1, 16, 0, 0, 0), dt.datetime(2019,1,31,23,59,0)],
    [dt.datetime(2019, 2, 1, 0, 0, 0), dt.datetime(2019,2,28,23,59,0)],
    [dt.datetime(2019, 1, 26, 21, 0, 0), dt.datetime(2019,1,31,21,0,0)],
    [dt.datetime(2019, 1, 21, 21, 0, 0), dt.datetime(2019,3,1,21,0,0)],
]

#Use pickle files that have outputs as dataframes
with open("2018_11_01_to_2019_3_01_weather.pickle", 'rb') as fp: #2018_11_01_to_2019_03_01_perfest1
    weather = pickle.load(fp)

with open("2018_11_01_to_2019_03_01_perfest1.pickle", 'rb') as fp:
    perfest = pickle.load(fp)
   

dfminoff = pd.read_csv('perfest_replay_wmec_ml_2018_11_01_to 2019_02_14V1.csv')
#final_df = final_df.assign(Timestamp = final_df.Timestamp.apply(lambda d: pytz.utc.localize(d).astimezone(USPAC))


# In[5]:


# in this block we make sure the data type of the pickle file matches
weather = pd.DataFrame(data=weather['values'], columns = weather['columns'])
weather['time'] = weather.time.apply(lambda d : pytool.time.fromutctimestamp(d/1000000))
weather.set_index('time', drop=True, inplace=True)


# In[6]:


weather.head(2)


# In[7]:


perfest = pd.DataFrame(data=perfest['values'], columns = perfest['columns'])
perfest['time'] = perfest.time.apply(lambda d : pytool.time.fromutctimestamp(d/1000000))
perfest.set_index('time', drop=True, inplace=True)


# In[8]:


perfest.head(2)


# In[9]:


# Tariffs

if Site == 'WFLA':
    #Demands
    max_on_peak_demand_summer = 19.95
    max_part_peak_demand_summer = 5.5
    max_demand_summer = 17.54

    max_part_peak_demand_winter = .12
    max_demand_winter = 17.54


    #Energy
    on_peak_summer = .16009
    part_peak_summer = .11567
    off_peak_summer = .08625
    
    part_peak_winter = .10958
    off_peak_winter = .09355

elif Site == 'WMEC':
    #Demands
    max_on_peak_demand_summer = 27.47
    max_demand_summer = 21

    max_on_peak_demand_winter = 16.44
    max_demand_winter = 21


    #Energy
    on_peak_summer = .13918
    off_peak_summer = .11736
    super_off_peak_summer = .08863
    
    on_peak_winter = .11621
    off_peak_winter = .10369
    super_off_peak_winter = .08982


# In[10]:


perfest.columns # available in summary


# In[11]:


#crs.baseline.power.kW,'rb.thermal_load.kW','crs.offset.power.kW' removed. Those were included in previous version of the script, in this new version we are using anoher set of  data downloaded from Cirrus that does not have the same fields


# In[12]:


weather.index = weather.index.tz_convert('US/Pacific')
    
perfest.index = perfest.index.tz_convert('US/Pacific')


DF = perfest.join(weather, lsuffix ='_perfest',rsuffix = '_weather')
DF = DF[['building.baseline.power.kW','apparentTemperature','rbCur_num','building.offset.kW','building.actual.power.kW']]
DF = DF.interpolate(method = 'nearest')
DF = DF.loc[DF['apparentTemperature'] >0]
DF = DF.resample("15T").mean()


# In[13]:


DF['COP'] = DF['apparentTemperature']*DF['apparentTemperature']* 0.0011778033118712684 -0.15557305693781495*DF['apparentTemperature'] + 6.632059210693061


# In[14]:



#Holidays
Holidays = [
    dt.datetime(2019,1,1), #new years day
    dt.datetime(2018,5,28), #memorial day
    dt.datetime(2018,7,4), #indepedence day
    dt.datetime(2018,9,3), #labor day
    dt.datetime(2018,11,12), #veterans day
    dt.datetime(2018,12,25), #christmas
    dt.datetime(2018,11,22), #thanksgiving    
]


# In[15]:


#---------------------------------------------Determine date variables from timestamps---------------------------------------------
timedelta_hours = []
time = []
hour = []
day = []
weekday = []
month = []


for i in range(0,len(DF)):
    if i == 0:
        timedelta_local = 0
    elif i == len(DF)-1:
        timedelta_local = 0
    else:        
        timedelta_local = DF.index[i+1]-DF.index[i]
        timedelta_local = timedelta_local.total_seconds()/3600
    timedelta_hours.append(timedelta_local)
    
    time_unaware = DF.index[i].replace(tzinfo=None)
    time.append(time_unaware)

    hour.append(time_unaware.hour)
    day.append(time_unaware.day)
    weekday.append(time_unaware.weekday())
    month.append(time_unaware.month)


DF['timedelta (hours)'] = timedelta_hours
DF['time (tz unaware)'] = time
DF['month'] = month
DF['day'] = day
DF['weekday'] = weekday
DF['hour'] = hour
DF['kWhe'] = DF['building.offset.kW']*DF['timedelta (hours)']
#DF['kWhth'] = DF['rb.thermal_load.kW']*DF['timedelta (hours)']



#---------------------------------------------Determine bill season---------------------------------------------

Bill_season = []
#WFLA
if Site == 'WFLA':
    for i in range(0,len(DF)):
        if DF['month'][i] <= 10 and DF['month'][i] >=5:
            Bill_season.append('summer')
        else:
            Bill_season.append('winter')

elif Site == 'WMEC':
    for i in range(0,len(DF)):
        if DF['month'][i] <= 10 and DF['month'][i] >=6:
            Bill_season.append('summer')
        else:
            Bill_season.append('winter')


DF['bill season'] = Bill_season



#---------------------------------------------Determine peak period---------------------------------------------

Peak_period = []
#WFLA
if Site =='WFLA':
    for i in range(0,len(DF)):
        if DF['bill season'][i] == 'summer':
            if DF['weekday'][i] <= 4: 
                if DF['time (tz unaware)'][i].time() >= dt.datetime(2000,1,1,12,0,0).time() and DF['time (tz unaware)'][i].time() < dt.datetime(2000,1,1,18,0,0).time():
                    Peak_period_local = 'on peak'
                elif DF['time (tz unaware)'][i].time() >= dt.datetime(2000,1,1,8,30,0).time() and DF['time (tz unaware)'][i].time() < dt.datetime(2000,1,1,12,0,0).time():
                    Peak_period_local = 'part peak'
                elif DF['time (tz unaware)'][i].time() >= dt.datetime(2000,1,1,18,0,0).time() and DF['time (tz unaware)'][i].time() < dt.datetime(2000,1,1,21,30,0).time():
                    Peak_period_local = 'part peak'
                else:
                    Peak_period_local = 'off peak'
            else:
                Peak_period_local = 'off peak'
        else:
            if DF['time (tz unaware)'][i].time() >= dt.datetime(2000,1,1,8,30,0).time() and DF['time (tz unaware)'][i].time() < dt.datetime(2000,1,1,21,30,0).time():
                Peak_period_local = 'part peak'
            else:
                Peak_period_local = 'off peak'
        if DF['time (tz unaware)'][i].date() in Holidays:
            Peak_period_local = 'off peak'

        Peak_period.append(Peak_period_local)

        if i%50000 ==0:
            print(i)
#WMEC
elif Site == 'WMEC':
    for i in range(0,len(DF)):
        if DF['bill season'][i] == 'summer': #summer
            if DF['weekday'][i] <= 4 and DF['time (tz unaware)'][i].date() not in Holidays: #weekdays
                if DF['time (tz unaware)'][i].time() >= dt.datetime(2000,1,1,16,0,0).time() and DF['time (tz unaware)'][i].time() < dt.datetime(2000,1,1,21,0,0).time():
                    Peak_period_local = 'on peak'
                elif DF['time (tz unaware)'][i].time() >= dt.datetime(2000,1,1,6,0,0).time() and DF['time (tz unaware)'][i].time() < dt.datetime(2000,1,1,16,0,0).time():
                    Peak_period_local = 'off peak'
                elif DF['time (tz unaware)'][i].time() >= dt.datetime(2000,1,1,21,0,0).time() and DF['time (tz unaware)'][i].time() < dt.datetime(2000,1,1,23,59,59).time():
                    Peak_period_local = 'off peak'
                else:
                    Peak_period_local = 'super off peak'
            else: #on weekends and holidays
                if DF['time (tz unaware)'][i].time() >= dt.datetime(2000,1,1,16,0,0).time() and DF['time (tz unaware)'][i].time() < dt.datetime(2000,1,1,21,0,0).time():
                    Peak_period_local = 'on peak'
                elif DF['time (tz unaware)'][i].time() >= dt.datetime(2000,1,1,14,0,0).time() and DF['time (tz unaware)'][i].time() < dt.datetime(2000,1,1,16,0,0).time():
                    Peak_period_local = 'off peak'
                elif DF['time (tz unaware)'][i].time() >= dt.datetime(2000,1,1,21,0,0).time() and DF['time (tz unaware)'][i].time() < dt.datetime(2000,1,1,23,59,59).time():
                    Peak_period_local = 'off peak'
                else:
                    Peak_period_local = 'super off peak'                
        else: #winter
            if DF['weekday'][i] <= 4 and DF['time (tz unaware)'][i].date() not in Holidays:  #weekdays
                if DF['time (tz unaware)'][i].time() >= dt.datetime(2000,1,1,16,0,0).time() and DF['time (tz unaware)'][i].time() < dt.datetime(2000,1,1,21,0,0).time():
                    Peak_period_local = 'on peak'
                elif DF['time (tz unaware)'][i].time() >= dt.datetime(2000,1,1,6,0,0).time() and DF['time (tz unaware)'][i].time() < dt.datetime(2000,1,1,16,0,0).time():
                    Peak_period_local = 'off peak'
                elif DF['time (tz unaware)'][i].time() >= dt.datetime(2000,1,1,21,0,0).time() and DF['time (tz unaware)'][i].time() < dt.datetime(2000,1,1,23,59,59).time():
                    Peak_period_local = 'off peak'
                else:
                    Peak_period_local = 'super off peak'
                if DF['month'][i] == (3 or 4) and DF['time (tz unaware)'][i].time() >= dt.datetime(2000,1,1,10,0,0).time() and DF['time (tz unaware)'][i].time() < dt.datetime(2000,1,1,14,0,0).time():
                    Peak_period_local = 'super off peak'
            else: #on weekends and holidays
                if DF['time (tz unaware)'][i].time() >= dt.datetime(2000,1,1,16,0,0).time() and DF['time (tz unaware)'][i].time() < dt.datetime(2000,1,1,21,0,0).time():
                    Peak_period_local = 'on peak'
                elif DF['time (tz unaware)'][i].time() >= dt.datetime(2000,1,1,14,0,0).time() and DF['time (tz unaware)'][i].time() < dt.datetime(2000,1,1,16,0,0).time():
                    Peak_period_local = 'off peak'
                elif DF['time (tz unaware)'][i].time() >= dt.datetime(2000,1,1,21,0,0).time() and DF['time (tz unaware)'][i].time() < dt.datetime(2000,1,1,23,59,59).time():
                    Peak_period_local = 'off peak'
                else:
                    Peak_period_local = 'super off peak'

            
            
        Peak_period.append(Peak_period_local)

        if i%50000 ==0:
            print(i)    
            
DF['peak period'] = Peak_period


#---------------------------------------------Determine energy savings---------------------------------------------

Energy_savings = []
if Site == 'WFLA':
    for i in range(0,len(DF)):
        Energy_cost_local = 'n/a'
        if DF['bill season'][i] == 'summer':
            if DF['peak period'][i] == 'on peak':
                Energy_cost_local = DF['building.offset.kW'][i]*on_peak_summer*DF['timedelta (hours)'][i]
            elif DF['peak period'][i] == 'part peak':
                Energy_cost_local = DF['building.offset.kW'][i]*part_peak_summer*DF['timedelta (hours)'][i]
            elif DF['peak period'][i] == 'off peak':
                Energy_cost_local = DF['building.offset.kW'][i]*off_peak_summer*DF['timedelta (hours)'][i]
        elif DF['bill season'][i] == 'winter':
            if DF['peak period'][i] == 'part peak':
                Energy_cost_local = DF['building.offset.kW'][i]*part_peak_winter*DF['timedelta (hours)'][i]
            elif DF['peak period'][i] == 'off peak':
                Energy_cost_local = DF['building.offset.kW'][i]*off_peak_winter*DF['timedelta (hours)'][i]

        Energy_savings.append(Energy_cost_local)

elif Site == 'WMEC':
    for i in range(0,len(DF)):
        Energy_cost_local = 'n/a'
        if DF['bill season'][i] == 'summer':
            if DF['peak period'][i] == 'on peak':
                Energy_cost_local = DF['building.offset.kW'][i]*on_peak_summer*DF['timedelta (hours)'][i]
            elif DF['peak period'][i] == 'off peak':
                Energy_cost_local = DF['building.offset.kW'][i]*off_peak_summer*DF['timedelta (hours)'][i]
            elif DF['peak period'][i] == 'super off peak':
                Energy_cost_local = DF['building.offset.kW'][i]*super_off_peak_summer*DF['timedelta (hours)'][i]
        elif DF['bill season'][i] == 'winter':
            if DF['peak period'][i] == 'on peak':
                Energy_cost_local = DF['building.offset.kW'][i]*on_peak_winter*DF['timedelta (hours)'][i]
            elif DF['peak period'][i] == 'off peak':
                Energy_cost_local = DF['building.offset.kW'][i]*off_peak_winter*DF['timedelta (hours)'][i]
            elif DF['peak period'][i] == 'super off peak':
                Energy_cost_local = DF['building.offset.kW'][i]*super_off_peak_winter*DF['timedelta (hours)'][i]

        Energy_savings.append(Energy_cost_local)


DF['energy savings'] = Energy_savings


# # Compile the info for each week

# In[16]:


Weeks = []
Percent_DCHG = []
Total_DCHG_kWhth = []
Weighted_CHG_Temp = []
Weighted_DCHG_Temp = []
DCHG_kWh_per_day = []
Temp_Delta = []
Total_CHG_kWhe = []
Total_DCHG_kWhe = []
Max_DCHG_kWhe = []
RTE = []
Max_DCHG_Offset_kWe = []
DF_cuts = []
DF_DCHG_cuts = []
DF_CHG_cuts = []
CHG_Run = []
DCHG_Run = []
Run_time = []
DF_DCHG_curb = [] #list with the DCHG mode data only based on currn num
Max_DCHG_1min =[] # maximum DCHG in a one minute interval
Demand_savings = []
Energy_savings = []
Grouping = []
COP = []
Max_BuildingActual = []
Zero_Operation = [] #variable to check if we have zero operation
datetimeFormat = '%Y-%m-%d %H:%M:%S'

for i in range(0,len(Lengths)): #Dataframe for each period
    
    DF_cuts_local = DF.loc[(DF['time (tz unaware)'] >= Lengths[i][0]) & (DF['time (tz unaware)'] <= Lengths[i][1])]
    DF_cuts.append(DF_cuts_local)
    
    
    DF_DCHG_cuts_local = DF_cuts_local.loc[DF_cuts_local['building.offset.kW'] < 0]
    DF_DCHG_cuts_local_local = DF_DCHG_cuts_local.loc[DF_DCHG_cuts_local['rbCur_num'] < 0 ]
    #DF_DCHG_cuts_local['percent DCHG'] = DF_DCHG_cuts_local['crs.offset.power.kW']/DF_DCHG_cuts_local['crs.baseline.power.kW']
    
    DF_CHG_cuts_local = DF_cuts_local.loc[DF_cuts_local['building.offset.kW'] > 0 ]
    DF_CHG_cuts_local_local = DF_CHG_cuts_local.loc[DF_CHG_cuts_local['rbCur_num'] > 0 ]
    
    DF_DCHG_cuts.append(DF_DCHG_cuts_local)
    DF_CHG_cuts.append(DF_CHG_cuts_local_local)
    
    #DF_CHG_cuts_local_local = DF_cuts_local.loc[DF_cuts_local['building.offset.kW'] > 1]
    #DF_CHG_cuts.append(DF_CHG_cuts_local_local)
    
    CHG_Run_local = (len(DF_CHG_cuts[i])-1)*15/60
    CHG_Run.append(CHG_Run_local)
    
    DCHG_Run_local = (len(DF_DCHG_cuts[i])-1)*15/60
    DCHG_Run.append(DCHG_Run_local)
    
    DF_DCHG_curb_local = DF_cuts_local.loc[DF_cuts_local['rbCur_num'] == -1] # get values that are on DCHG only
    DF_DCHG_curb.append(DF_DCHG_curb_local)   # add them to a list
    Grouping_local = pd.DataFrame(DF_DCHG_curb[i]['building.offset.kW']) #from that list get the building offsets and create a data frame
    Grouping_local = Grouping_local.reset_index(drop=False) # remove index
    Grouping_local = Grouping_local.assign(date = Grouping_local.time.apply(lambda d: d.date())) #group by date
    Grouping.append((Grouping_local.groupby('date').sum()/4).min()) #get kWh and add them within that day, select min value ( max DCHG)append them to a new value
    

    Weeks_local = str(Lengths[i][0]),' to ',str(Lengths[i][1])    
    Weeks.append(Weeks_local)
    
    # in this section we calculate the time difference between two dates
    date1 = Weeks[i][0]
    date2 = Weeks[i][2]
    diff = datetime.datetime.strptime(date2, datetimeFormat)    - datetime.datetime.strptime(date1, datetimeFormat)

    Run_time.append(diff)
                                  

    #Percent_DCHG_local = round(DF_DCHG_cuts[i]['percent DCHG'].mean()*100,2)
    #Percent_DCHG_local = float("{0:.2f}".format(Percent_DCHG_local))
    #Percent_DCHG.append(Percent_DCHG_local)
    
    #Total_DCHG_kWhth_local = -DF_DCHG_cuts[i]['kWhth'].sum()
    #Total_DCHG_kWhth.append(Total_DCHG_kWhth_local)
    
    #d = dfminoff[0]['perfest_replay_wmec_ml.building.offset.kW'].min
    #Max_DCHG_1min.append(Max_DCHG_1min_local) 
    
    COP_local = DF_cuts[i]['COP'].min()
    COP.append(COP_local)
    print (COP)

    Total_DCHG_kWhe_local = DF_DCHG_cuts[i]['kWhe'].sum()
    Total_DCHG_kWhe.append(Total_DCHG_kWhe_local)
    
    Max_DCHG_kWhe_local = DF_DCHG_cuts[i]['kWhe'].min()
    Max_DCHG_kWhe.append(Max_DCHG_kWhe_local)
    
    Max_BuildingActuallocal = DF_DCHG_cuts[i]['building.actual.power.kW'].max()
    Max_BuildingActual.append(Max_BuildingActuallocal)
    

    Total_CHG_kWhe_local = DF_CHG_cuts[i]['kWhe'].sum()
    Total_CHG_kWhe.append(Total_CHG_kWhe_local)
    
    Max_DCHG_Local = DF_DCHG_cuts[i]['building.offset.kW'].min()
    Max_DCHG_Offset_kWe.append(Max_DCHG_Local)
    

    

    RTE_local = -Total_DCHG_kWhe_local/Total_CHG_kWhe_local*100
    RTE_local = float("{0:.2f}".format(RTE_local))
    RTE.append(RTE_local)  

    #kWhth_CHG_total = DF_CHG_cuts[i]['kWhth'].sum()
    #DF_CHG_cuts[i]['Weighted temperature'] = DF_CHG_cuts[i]['kWhth']/kWhth_CHG_total*DF_CHG_cuts[i]['apparentTemperature']
    #Weighted_CHG_Temp_local = DF_CHG_cuts[i]['Weighted temperature'].sum()
   #Weighted_CHG_Temp_local = float("{0:.2f}".format(Weighted_CHG_Temp_local))
    #Weighted_CHG_Temp.append(Weighted_CHG_Temp_local)
    
    #kWhth_DCHG_total = DF_DCHG_cuts[i]['kWhth'].sum()
    #DF_DCHG_cuts[i]['Weighted temperature'] = DF_DCHG_cuts[i]['kWhth']/kWhth_DCHG_total*DF_DCHG_cuts[i]['apparentTemperature']
    #Weighted_DCHG_Temp_local = DF_DCHG_cuts[i]['Weighted temperature'].sum()
    #Weighted_DCHG_Temp_local = float("{0:.2f}".format(Weighted_DCHG_Temp_local))
    #Weighted_DCHG_Temp.append(Weighted_DCHG_Temp_local)
    
    #Temp_Delta.append(Weighted_DCHG_Temp_local - Weighted_CHG_Temp_local)

    
    Total_days_local = (Lengths[i][1] - Lengths[i][0]).total_seconds()/86400
    #DCHG_kWh_per_day_local = Total_DCHG_kWhth_local/Total_days_local
    #DCHG_kWh_per_day_local = float("{0:.2f}".format(DCHG_kWh_per_day_local))
    #DCHG_kWh_per_day.append(DCHG_kWh_per_day_local)
    
    
    #---------------------------------------------Determine demand savings---------------------------------------------
    
    if Site == 'WFLA':
        #summer
        Max_on_peak_demand_summer_kW_local = (DF_cuts_local.loc[(DF_cuts_local['bill season'] == 'summer') & (DF_cuts_local['peak period']== 'on peak')]['building.actual.power.kW'].max())
        Max_part_peak_demand_summer_kW_local = (DF_cuts_local.loc[(DF_cuts_local['bill season'] == 'summer') & (DF_cuts_local['peak period']== 'part peak')]['building.actual.power.kW'].max())
        Max_demand_summer_kW_local = (DF_cuts_local.loc[(DF_cuts_local['bill season'] == 'summer')]['building.actual.power.kW'].max())

        Max_bl_on_peak_demand_summer_kW_local = (DF_cuts_local.loc[(DF_cuts_local['bill season'] == 'summer') & (DF_cuts_local['peak period']== 'on peak')]['building.baseline.power.kW'].max())
        Max_bl_part_peak_demand_summer_kW_local = (DF_cuts_local.loc[(DF_cuts_local['bill season'] == 'summer') & (DF_cuts_local['peak period']== 'part peak')]['building.baseline.power.kW'].max())
        Max_bl_demand_summer_kW_local = (DF_cuts_local.loc[(DF_cuts_local['bill season'] == 'summer')]['building.baseline.power.kW'].max())

        On_Peak_demand_savings_summer_kW_local = Max_bl_on_peak_demand_summer_kW_local - Max_on_peak_demand_summer_kW_local
        Part_peak_demand_savings_summer_kW_local = Max_bl_part_peak_demand_summer_kW_local - Max_part_peak_demand_summer_kW_local
        NC_peak_demand_savings_summer_kW_local =     Max_bl_demand_summer_kW_local - Max_demand_summer_kW_local

        Demand_savings_summer = On_Peak_demand_savings_summer_kW_local*max_on_peak_demand_summer + Part_peak_demand_savings_summer_kW_local * max_part_peak_demand_summer + NC_peak_demand_savings_summer_kW_local *  max_demand_summer


        #winter
        Max_part_peak_demand_winter_kW_local = (DF_cuts_local.loc[(DF_cuts_local['bill season'] == 'winter') & (DF_cuts_local['peak period']== 'part peak')]['building.actual.power.kW'].max())
        Max_demand_winter_kW_local = (DF_cuts_local.loc[(DF_cuts_local['bill season'] == 'winter')]['building.actual.power.kW'].max())

        Max_bl_part_peak_demand_winter_kW_local = (DF_cuts_local.loc[(DF_cuts_local['bill season'] == 'winter') & (DF_cuts_local['peak period']== 'part peak')]['building.baseline.power.kW'].max())
        Max_bl_demand_winter_kW_local = (DF_cuts_local.loc[(DF_cuts_local['bill season'] == 'winter')]['building.baseline.power.kW'].max())

        Part_peak_demand_savings_winter_kW_local = Max_bl_part_peak_demand_winter_kW_local - Max_part_peak_demand_winter_kW_local
        NC_peak_demand_savings_winter_kW_local =     Max_bl_demand_winter_kW_local - Max_demand_winter_kW_local

        Demand_savings_winter = Part_peak_demand_savings_winter_kW_local * max_part_peak_demand_winter + NC_peak_demand_savings_winter_kW_local *  max_demand_winter
    
    elif Site == 'WMEC':
        #summer
        Max_on_peak_demand_summer_kW_local = (DF_cuts_local.loc[(DF_cuts_local['bill season'] == 'summer') & (DF_cuts_local['peak period']== 'on peak')]['building.actual.power.kW'].max())
        Max_demand_summer_kW_local = (DF_cuts_local.loc[(DF_cuts_local['bill season'] == 'summer')]['building.actual.power.kW'].max())
        
        #print(Max_on_peak_demand_summer_kW_local)
        #print(Max_demand_summer_kW_local)
        
        Max_bl_on_peak_demand_summer_kW_local = (DF_cuts_local.loc[(DF_cuts_local['bill season'] == 'summer') & (DF_cuts_local['peak period']== 'on peak')]['building.baseline.power.kW'].max())
        Max_bl_demand_summer_kW_local = (DF_cuts_local.loc[(DF_cuts_local['bill season'] == 'summer')]['building.baseline.power.kW'].max())
        
        #print(Max_bl_on_peak_demand_summer_kW_local)
        #print(Max_bl_demand_summer_kW_local)
        
        On_Peak_demand_savings_summer_kW_local = Max_bl_on_peak_demand_summer_kW_local - Max_on_peak_demand_summer_kW_local
        NC_peak_demand_savings_summer_kW_local =     Max_bl_demand_summer_kW_local - Max_demand_summer_kW_local

        Demand_savings_summer = On_Peak_demand_savings_summer_kW_local*max_on_peak_demand_summer + NC_peak_demand_savings_summer_kW_local *  max_demand_summer


        #winter
        Max_on_peak_demand_winter_kW_local = (DF_cuts_local.loc[(DF_cuts_local['bill season'] == 'winter') & (DF_cuts_local['peak period']== 'on peak')]['building.actual.power.kW'].max())
        Max_demand_winter_kW_local = (DF_cuts_local.loc[(DF_cuts_local['bill season'] == 'winter')]['building.actual.power.kW'].max())
        
        print(Max_on_peak_demand_winter_kW_local)
        #print(Max_demand_winter_kW_local) # this is the actual or target

        Max_bl_on_peak_demand_winter_kW_local = (DF_cuts_local.loc[(DF_cuts_local['bill season'] == 'winter') & (DF_cuts_local['peak period']== 'on peak')]['building.baseline.power.kW'].max())
        Max_bl_demand_winter_kW_local = (DF_cuts_local.loc[(DF_cuts_local['bill season'] == 'winter')]['building.baseline.power.kW'].max())

        #print(Max_bl_on_peak_demand_winter_kW_local) # this is the baseline load
        #print(Max_bl_demand_winter_kW_local) # this is also the baseline load
        
        On_Peak_demand_savings_winter_kW_local = Max_bl_on_peak_demand_winter_kW_local - Max_on_peak_demand_winter_kW_local
        NC_peak_demand_savings_winter_kW_local =     Max_bl_demand_winter_kW_local - Max_demand_winter_kW_local

        Demand_savings_winter = On_Peak_demand_savings_winter_kW_local*max_on_peak_demand_winter + NC_peak_demand_savings_winter_kW_local *  max_demand_winter    
    
    
    
    #ratios
    summer_ratio = len(DF_cuts_local.loc[DF['bill season'] =='summer'])/len(DF_cuts_local)
    winter_ratio = len(DF_cuts_local.loc[DF['bill season'] == 'winter'])/len(DF_cuts_local)
    

    
    if summer_ratio == 1:    
        Demand_savings_local = Demand_savings_summer*summer_ratio
    elif winter_ratio == 1:
        Demand_savings_local = Demand_savings_winter*winter_ratio
    else:
        Demand_savings_local = Demand_savings_summer*summer_ratio + Demand_savings_winter*winter_ratio
        
        
    Demand_savings.append(Demand_savings_local)
    
    
    #Calculate Energy Savings
    Energy_savings.append(DF_cuts_local['energy savings'].sum()*-1)
    
    


# In[17]:


GroupedDCHG = [a[0] for a in Grouping] 


# In[18]:


Data = [('Period', Weeks), #organize the data so it can be an input into the dataframe
    ('Time in Period', Run_time),
    ('CHG Run Time (hr)', CHG_Run),
    ('DCHG Run Time (hr)',DCHG_Run),   
    ('Total CHG (kWhe)', Total_CHG_kWhe),
    ('Total DCHG (kWhe)', Total_DCHG_kWhe),
    ('Max DCHG kWe (15 min)', Max_DCHG_Offset_kWe),
       #('Max DCHG kWhe', Max_DCHG_kWhe),
('Largest DCHG session (kWhe)', GroupedDCHG),
#     ('Weighted CHG Temp (°F)', Weighted_CHG_Temp),
#     ('Weighted DCHG Temp (°F)', Weighted_DCHG_Temp),
#('Weighted OAT Delta (°F)', Temp_Delta),
    ('Demand Savings ($)', Demand_savings),
    ('Energy Savings ($)', Energy_savings),
    ('RTE (%)', RTE)]


# In[19]:


Data


# In[20]:


type (Data)


# In[21]:


Sheet = pd.DataFrame.from_items(Data) #make the dataframe
for col in Sheet.columns:
    try:
        Sheet[col] = round(Sheet[col], 2)
    except:
        pass
    finally:
        pass

Sheet['Total Savings ($)'] = Sheet['Demand Savings ($)'] + Sheet['Energy Savings ($)']


# # Method
# - Weighted OAT 
#     - Weights the temperature by percent charge or discharge kWhe. 
#         - e.g. the weighted CHG temperature is calculated using the following methodology: Find the sum of kWhe for all of the CHG intervals. For each 1 minute interval, calculate the kWh divided by the kWhe sum. Sum those values together to find the weighted temperature
# - Percent DCHG = CRS offset/CRS baseline

# In[22]:


Sheet# 0 is the total period # 1 is M&V period #2 is M&V period #2


#  
