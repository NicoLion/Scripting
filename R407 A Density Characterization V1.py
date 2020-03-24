#!/usr/bin/env python
# coding: utf-8

# In[38]:


### Hello


# In[1]:


#Import the necessary libraries
import math as math
import numpy as np
import pandas as pd
import pickle
import itertools
from CoolProp.CoolProp import PropsSI
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn import linear_model
from pandas import ExcelWriter
import statsmodels.api as sm
import statsmodels.formula.api as sm
from scipy.optimize import curve_fit
import scipy.optimize as optimize
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"

get_ipython().run_line_magic('matplotlib', 'inline')


# In[2]:


# Iteration parameters
fluid = 'R407A.mix'
P_min_kPa = 100 #Minimum pressure in kPa we will be evaluating
P_max_kPa = 2500 #Maximum pressure in kPa we will be evaluating
T_min_K = -50+273 #Minimum temp
T_max_K = 79+273 #Max temp
n = 2400 #Number of samples we will collect
m = 180
P_kPa = np.linspace(P_min_kPa, P_max_kPa, n) #The array of the pressures we will be evaluating
T_K = np.linspace(T_min_K, T_max_K, m) # This is the array of temperatures divided into m spaces
Dvapor = [] # create a list
combo = list(itertools.product(P_kPa,T_K)) # assign to combo the combination of pressures and arrays


# In[ ]:


for i in combo: #  getting data from cool props make sure coolprops is activated as a library
    [p,t]= i
    try:
        Dvapor.append(PropsSI('D','P', p*1000,'T',t,'REFPROP::R407a.mix')) # use the function PropsSI to get Densities and assign to Dvapor
    except:
        Dvapor.append(0) # we don't know if there is values in all the spaces, or the extent of the ProposSI Function
        #Test values to make sure there was a coherent answer according to R407a tables, since those are mostly experimental tests
        #print("Density at 300K and 13.216 bar :", PropsSI('D', 'T', 290.743, 'P', 2500000,'REFPROP::R407a.mix'), "Kg/m^3")
        # What happened above is to make sure or assess if there is data in the file that will adjust ot our workspace


# In[ ]:


print(Dvapor) # This is density, I have used the variable Dvapor because it was easy to start with and have a reference
combo


# ### Save DVapor as picke file

# In[ ]:


# run this only when you want to extract data again from propsi, if there is already a Density_values.p; there is no need to run
#pickle.dump(Dvapor, open( "Density_values.p", "wb" ) ) # save values from propsi in file so we don't have to run each time


# #### Load Density Values

# In[3]:


Dvapor = pickle.load( open( "Density_values.p", "rb" ) ) # load values from ".p" file

#### Creating a meshgrid
X, Y = np.meshgrid(T_K,P_kPa) # create a grid of appropiate size to set values for plotting
X.shape # sizing
Y.shape # sizing
Y # a look on how it is being sized
Z = np.split(np.array(Dvapor),2400)
Z = np.array(Z)
Z.shape


# In[4]:


# General extracted data display
from mpl_toolkits.mplot3d import Axes3D # import libraries for drawing in 3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
get_ipython().run_line_magic('matplotlib', 'inline')
fig = plt.figure(figsize =(15,10))
ax = fig.gca(projection='3d')
surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,linewidth=0, antialiased=False)
# plot the plot will give two distinc surfaces with an area in between
ax.set_xlabel('Temperature', fontsize = 14)
ax.set_ylabel('Pressure (kPa)', fontsize = 14)
ax.set_zlabel('Density', fontsize = 14)


# #### Create Data Frame called "df" from Density values

# In[5]:


df = pd.DataFrame.from_records(combo, columns = ['Pressure','Temperature'])
df =  df.assign(Density = Dvapor)
len(df) # for the sake of robustness
df.head(3) # displaying data in appropiate table


# ### Regression model for Vapor (according to saturated vapor caracterization)

# In[6]:


Vapor_df = df[df.Temperature > 151.12 + 27.9058*df.Pressure**0.237508] # cut off value for densities
Vapor_df.tail(3) # mock display values to see how are they are being arranged
threedee = plt.figure().gca(projection='3d')
threedee.scatter(Vapor_df['Temperature'],Vapor_df['Pressure'], Vapor_df['Density'])
threedee.set_xlabel('Temperature (K)')
threedee.set_ylabel('Pressure (kPa)')
threedee.set_zlabel('Density (kg/m^3)')
plt.show()


# In[26]:


Vapor_df = Vapor_df.assign(Temp_sq = Vapor_df.Temperature**2)
resultVapor = sm.ols(formula= "Density ~ Temperature+Pressure", data=Vapor_df).fit()
forecast = resultVapor.predict(Vapor_df[['Temperature','Pressure']])
ErrorV = pd.DataFrame({'Error': forecast-Vapor_df.Density})
print(resultVapor.params)
print(resultVapor.summary())
ErrorV.describe()


# In[22]:


plt.hist(ErrorV.Error, bins = 150) # histogram of error distribution
plt.title('Error distribution')
plt.xlabel('Spread from function (kg/m^3))')
plt.ylabel('Frecuency')


# ## Result for Vapor portion Density Vapor= aT^2+bT+cP+f
# 
# ### R2 = 0.988
# #### a Temp_sq  : -0.001718             
# #### b Temperature : 0.939123         
# #### c Pressure : 0.046092               
# #### f is the Intercept: -129.137325
# 
# ## Result for Vapor portion Density Vapor= bT+cP+f
# 
# ### R2 = 0.987          
# #### b Temperature : -0.126876        
# #### c Pressure : 0.046125               
# #### f is the Intercept: 35.066588
# 
# 

# ## Regression model for Liquid ( according to saturated liquid characterization)

# In[27]:


Liquid_df = df[df.Temperature < 148.074237046 + 25.495200*df.Pressure**0.24854063] # cut off value for densities


# In[28]:


threedee = plt.figure().gca(projection='3d')
threedee.scatter(Liquid_df['Temperature'],Liquid_df['Pressure'],Liquid_df['Density'])
threedee.set_xlabel('Temperature (K)')
threedee.set_ylabel('Pressure (kPa)')
threedee.set_zlabel('Density')
plt.show()


# In[29]:


Liquid_df.head(5)


# In[30]:


#Liquid_df = Liquid_df.assign(logtemp = list(map(lambda d: math.log(d),Liquid_df.Temperature)))
#Liquid_df = Liquid_df.assign(logpress = list(map(lambda d: math.log(d),Liquid_df.Pressure)))
#Liquid_df = Liquid_df.assign(logdens = list(map(lambda d: math.log(d),Liquid_df.Density)))
Liquid_df = Liquid_df.assign(Temp_sq = Liquid_df.Temperature**2)


# In[37]:


result = sm.ols(formula="Density ~ Temperature", data=Liquid_df).fit()
forecast = result.predict(Liquid_df[['Temperature']])
ErrorL = pd.DataFrame({'Error': forecast-Liquid_df.Density})
print(result.params)
print(result.summary())
ErrorL.describe()


# In[36]:


plt.hist(ErrorL.Error, bins = 150);
plt.title('Error distribution')
plt.xlabel('Spread from function (kg/m^3))')
plt.ylabel('Frecuency')


# ## Result for liquid portion Density Liquid = aT^2+bT+cP+f
# ### R2 = 0.993
# #### a is the parameter for Temp_sq  : -0.012582
# #### b is the parameter for Temperature : 2.921847
# #### c is the parameter for Pressure : 0.003973
# #### f is the Intercept: 1387.742466
# 
# ## Result for liquid portion Density Liquid = bT+cP+f
# ### R2 = 0.986
# #### b is the parameter for Temperature : -3.777687
# #### c is the parameter for Pressure : 0.002167
# #### f is the Intercept: 2273.909536
# 
# ## Result for liquid portion Density Liquid = bT+f
# #### R2 = 0.986
# #### b is the parameter for Temperature : -3.758059
# #### f is the Intercept: 2272.071108
# 
# 

# ### Regression model for density over mix phase portion

# In[ ]:


Mix_df = df[(df['Temperature'] > 148.074237046 + 25.495200*df['Pressure']**0.24854063 )& (df['Temperature'] < 151.12 + 27.9058*df['Pressure']**0.237508)] # cut off value for densities] # cut off value for densities


# In[ ]:


threedee = plt.figure().gca(projection='3d')
threedee.scatter(Mix_df['Temperature'],Mix_df['Pressure'],Mix_df['Density'])
threedee.set_xlabel('Temperature (K)')
threedee.set_ylabel('Pressure (kPa)')
threedee.set_zlabel('Density')
plt.show()


# In[ ]:


Mix_df = Mix_df.assign(Temp_sq = Mix_df.Temperature**2.6)
Mix_df = Mix_df.assign(Press_sq = Mix_df.Pressure**1.3)
Mix_df.head(3)


# In[ ]:


resultMix = sm.ols(formula="Density ~ Temp_sq + Press_sq +Temperature + Pressure", data=Mix_df).fit()
forecastMix = resultMix.predict(Mix_df[['Pressure', 'Temperature', 'Temp_sq', 'Press_sq']])
ErrorMix = pd.DataFrame({'Error': forecastMix-Mix_df.Density})
print(resultMix.params)
print(resultMix.summary())
ErrorMix.describe()


# #### Preliminary results for Mixed phase portion in table above - under revision -  there is no  requirement until the moment for further charcterization of this portion

# In[ ]:




