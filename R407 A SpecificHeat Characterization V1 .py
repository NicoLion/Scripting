#!/usr/bin/env python
# coding: utf-8

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
from pandas import DataFrame
from mpl_toolkits.mplot3d import Axes3D
from pandas import ExcelWriter
from IPython.core.interactiveshell import InteractiveShell
import statsmodels.formula.api as sm
InteractiveShell.ast_node_interactivity = "all"
get_ipython().run_line_magic('matplotlib', 'inline')


# In[2]:


# Iteration parameters
fluid = 'R407A.mix'
P_min_kPa = 100 #Minimum pressure in kPa we will be evaluating
P_max_kPa = 3000 #Maximum pressure in kPa we will be evaluating
T_min_K = -30+273 #Minimum temp
T_max_K = 60+273 #Max temp
n = 2900 #Number of samples we will collect
m = 180
P_kPa = np.linspace(P_min_kPa, P_max_kPa, n) #The array of the pressures we will be evaluating
T_K = np.linspace(T_min_K, T_max_K, m) # This is the array of temperatures divided into m spaces
Spec = [] # create a list
combo = list(itertools.product(P_kPa,T_K)) # assign to combo the combination of pressures and arrays


# In[3]:


# This step is only for extraction of data, if there is already a ' xxxx.p' file, then it is not necesary to load data again

#Test values to make sure there was a coherent answer according to R407a tables, since those are mostly experimental tests
# the function C fro propsSi calculates the Mass specific constant pressure specific heat in [J/kg/K]
#print("Specific heat at 333K and 3000 kPa :", PropsSI('C', 'T', 273+60, 'P', 3000*1000, 'REFPROP::R407a.mix'), "J/kg/K") #Maxi
#print("Specific heat at 243K and 100 kPa :", PropsSI('C', 'T', 273-30, 'P', 100*1000, 'REFPROP::R407a.mix'), "J/kg/K") # Minimi


#for i in combo: # extract data from propsi, use only if library (coolprops) is loaded and functioning
 #   [p,t]= i
  #  try:
   #     Spec.append(PropsSI('C','P', p*1000,'T',t, 'REFPROP::R407a.mix')) # use the function PropsSI to 
        # get the specific heat according to  pressure defined and temperature defined, the pressure array has 2900 points
        #according to 3000 kPa - 100 kPa Range - the temperature similarly has 90 points
   # except:
   #     Spec.append(0) # we don't know if there is values in all the spaces, or the extent of the ProposSI Function
        
        # What happened above is to make sure or assess if there is data in the file that will adjust ot our workspace
        



# In[4]:


#print(Spec) # This is Specific heat, I have used the variable Spec because it wass easy to start with and have a reference


# In[5]:


# run this only when you want to extract data again from propsi, if there is already a SpecificHeat.p file; there is no need to run
#pickle.dump(Spec, open( "SpecificHeat.p", "wb" ) ) # save values from propsi in file so we don't have to run each time


# In[3]:


X, Y = np.meshgrid(T_K,P_kPa)


# In[4]:


Spec = pickle.load( open( "SpecificHeat.p", "rb" ) ) # load values from file


# In[4]:


PropsSI('C','P',1162*1000,'T',264, 'REFPROP::R407a.mix') 


# In[5]:


X.shape
Y.shape
Y


# In[6]:


Z = np.split(np.array(Spec),2900)
Z = np.array(Z)
Z.shape


# In[7]:


# plotting of raw data to visualize the behaviour and see Cp (propsSI) outputs
from mpl_toolkits.mplot3d import Axes3D # import libraries for drawing in 3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
# this is a graph of the data we are dealing with
get_ipython().run_line_magic('matplotlib', 'inline')

threedee = plt.figure().gca(projection='3d')
threedee.scatter(X,Y, Z)
threedee.set_xlabel('Pressure (kPa)')
threedee.set_ylabel('Temp. (K)')
threedee.set_zlabel('Cp(J/kg/K)')
plt.show()
#fig = plt.figure()
#ax = fig.gca(projection='3d')
#surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm, linewidth=0, antialiased=False)# plot the plot will give two distinc surfaces with an area in between
#ax.set_xlabel('T (K)', fontsize = 14)
#ax.set_ylabel('P(kPa)', fontsize = 14)
#ax.set_zlabel('C (kJ/kg/K)', fontsize = 14)


# In[8]:


shf= pd.DataFrame.from_records( combo, columns= ['Pressure','Temperature'])
shf = shf.assign(Cp = Spec)
len (shf)


# In[9]:


shf.head(3)


# In[10]:


Mask = (shf>0)


# In[11]:


shf[Mask]


# In[12]:


groupingtest = shf.loc[shf['Cp']>0]
#len(shf.loc[shf['Cp']>0])
groupingtest.head(2)


# In[ ]:


#writer = pd.ExcelWriter('pandas_simplecp.xlsx', engine='xlsxwriter')
#shf.loc[shf['Cp']<0].to_excel(writer, sheet_name='Sheet1')
#writer.save()


# In[13]:


negatives = shf.loc[shf['Cp']<0]
positives = shf.loc[shf['Cp']>0] 


# In[14]:


# Plot the extracted data from propsi
print(shf.head());
threedee = plt.figure().gca(projection='3d')
threedee.scatter(positives['Temperature'],positives['Pressure'], positives['Cp'])
threedee.set_xlabel('Temp. (K)')
threedee.set_ylabel('Pressure (kPa)')
threedee.set_zlabel('Cp (J/kg/k)')
plt.show()


# In[ ]:


# Time to separate the characterization!! :) 


# Regression model for Mix ( acording to saturated caracterization)

# ### Characterization model for latent heat portion liquid portion

# In[15]:


negatives.head(4) # negatives are the values selected to be outliers from the 'normal' Cp value
Latent_negatives = negatives[(negatives['Temperature']> 148.074237046 + 25.495200*negatives['Pressure']**0.24854063)&(negatives['Temperature'] < 151.12 + 27.9058*negatives['Pressure']**0.237508)]
threedee = plt.figure().gca(projection='3d')
threedee.scatter(Latent_negatives['Temperature'],Latent_negatives['Pressure'],Latent_negatives['Cp'])
threedee.set_xlabel('Temperature (K)')
threedee.set_ylabel('Pressure (kPa)')
threedee.set_zlabel('Cp (J/kg/K)')
plt.show()


# In[ ]:


# Due to the results, it is clear that propsSI for the latent portion of the specific heat data, is throwing a value that does not match with the physical phenomena. 
# The value for the portion should be instead in [J/mol] or [J/kg] since it is a rise described as the mass or molar latent heat at constant temperature
# Therefore, this portion of the characterization will be performed in a seperate krunchy book


# ## Characterization model Specific Heat for liquid portion

# In[16]:


Liquid_positives = positives[(positives['Temperature'] < 148.074237046 + 25.495200534*positives['Pressure']**0.248540630499)]
threedee = plt.figure().gca(projection='3d')
threedee.scatter(Liquid_positives['Temperature'],Liquid_positives['Pressure'],Liquid_positives['Cp'])
threedee.set_xlabel('Temperature (K)')
threedee.set_ylabel('Pressure (kPa)')
threedee.set_zlabel('Cp (J/kg/k)')
plt.show()


# In[17]:


Liquid_positives = Liquid_positives.assign(Temp_sq = Liquid_positives['Temperature']**2)#1.56
Liquid_positives = Liquid_positives.assign(Press_sq = Liquid_positives['Pressure']**2) #1.4
Liquid_positives.head(3)


# In[39]:


resultLiquid = sm.ols(formula="Cp ~ Temperature + Pressure + Temp_sq", data=Liquid_positives).fit()
forecastLiquid = resultLiquid.predict(Liquid_positives[['Temperature','Pressure','Temp_sq']])
ErrorLiquid = pd.DataFrame({'Error': forecastLiquid-Liquid_positives.Cp})

print(resultLiquid.params)
print(resultLiquid.summary())
ErrorLiquid.describe()


# In[40]:


plt.hist(ErrorLiquid.Error, bins = 1500); # histogram of error distribution
plt.title('Error distribution')
plt.xlabel('Spread from function Cp (J/kg/K)))')
plt.ylabel('Frecuency')


# # Result for liquid portion CpLiquid = aT^2+bT+cP+f       [J/kg/K]
# ### R2 = 0.991 
# #### a is the parameter for Temp_sq  : 0.063061
# #### b is the parameter for Temperature : -30.457731
# #### c is the parameter for Pressure : -0.008074
# #### f is the Intercept: 5006.961681
# 
# # Result for liquid portion CpLiquid = bT+cP+f      
# ### R2 = 0.916 
# #### b is the parameter for Temperature : 4.558210
# #### c is the parameter for Pressure : -0.002865
# #### f is the Intercept: 165.200746
# 
# 
# # Result for liquid portion CpLiquid = bT+f       
# ### R2 = 0.916 
# #### b is the parameter for Temperature : 4.525411
# #### f is the Intercept: 169.546153
# 
# 
# 

# ## Characterization model for Specific Heat for Vapor portion

# In[24]:


Vapor_positives = positives[(positives['Temperature'] > 151.12884541 + 27.9058175606*positives['Pressure']**0.23750882839)]
threedee = plt.figure().gca(projection='3d')
threedee.scatter(Vapor_positives['Temperature'],Vapor_positives['Pressure'],Vapor_positives['Cp'])
threedee.set_xlabel('Temperature (K)')
threedee.set_ylabel('Pressure (kPa)')
threedee.set_zlabel('Cp (J/kg/k)')
plt.show()


# In[25]:


Vapor_positives.head(3)


# In[34]:


Vapor_positives = Vapor_positives.assign(Temp_sq = Vapor_positives['Temperature']**2)#1.56 as a suggestion, overall it is reasonable 
Vapor_positives = Vapor_positives.assign(Press_sq = Vapor_positives['Pressure']**2) #1.4


# In[35]:


resultVapor = sm.ols(formula="Cp ~ Temperature + Pressure ", data=Vapor_positives).fit()
forecastVapor = resultVapor.predict(Vapor_positives[['Pressure','Temperature']])
ErrorVapor = pd.DataFrame({'Error': forecastVapor-Vapor_positives.Cp})

print(resultVapor.params)
print(resultVapor.summary())
ErrorVapor.describe()


# In[33]:


plt.hist(ErrorVapor.Error, bins = 150); # histogram of error distribution
plt.title('Error distribution')
plt.xlabel('Spread from function Cp (J/kg/k)))')
plt.ylabel('Frecuency')


# # Result for Vapor portion CpVapor = aT^2+bT+cP+f  
# ## [J/kg/K]
# ### R2 = 0.939
# #### a is the parameter for Temp_sq  : -0.017369
# #### b is the parameter for Temperature : 9.963247
# #### c is the parameter for Pressure : 0.278669
# #### f is the Intercept: -645.880275
# 
# # Result for Vapor portion CpVapor = bT+cP+f  
# ### R2 = 0.937
# #### b is the parameter for Temperature : -0.381473
# #### c is the parameter for Pressure : 0.276162
# #### f is the Intercept: 887.750263
# 
# 

# In[ ]:


#Spec.append(PropsSI('C','P', p*1000,'T',t, 'REFPROP::R407a.mix')) # test
#in case there is a need to export data to excel
#writer = pd.ExcelWriter('pandas_simpledensity.xlsx', engine='xlsxwriter')
#Liquid_df.to_excel(writer, sheet_name='Sheet1')
#writer.save()

