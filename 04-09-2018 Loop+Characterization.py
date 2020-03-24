#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#data taken from https://plots.axiomexergy.com/dashboard/db/nc-wmec?refresh=5s&orgId=1&from=1536112456609&to=1536115155109


# In[2]:



import numpy as np
import matplotlib.pyplot as plt


# In[7]:


order = 1


MAV =          [0, .083, .167, .250, .333,  .417,  .500,  .583,  .667,  .750, .833, .917, 1 ]

vFlow_L_s =    [0,0.32,1.12,2.10,3.18,4.27,5.35,6.44,7.58,8.77,9.93,11.15,12.33]
step = 5/60



ref = []
for i in range(0,len(vFlow_L_s)):
    ref.append(i*step)
    
coeffs = np.polyfit(ref, vFlow_L_s,order)




vFlow_LoBF = []
for i in range(0,len(ref)):
    value = 0
    for j in range(0,len(coeffs)):
        value += coeffs[-j-1]*ref[i]**j

        
    vFlow_LoBF.append(value)
plt.figure()
print(coeffs)    
print("polynomial order:",order)
plt.title("MAV vs. Flow")
plt.xlabel("MAV")
plt.ylabel("Flow (L/s)")
plt.plot(ref,vFlow_LoBF)
plt.scatter(ref, vFlow_L_s)
plt.show()

print(len(ref))


# In[8]:


#Head Calculation

order = 2

Head = [284 - 274 , 285-274, 290 - 274, 296 - 274, 304-273, 314-271, 326-271, 342-270, 362-270, 382-270, 403-268, 429-265,455-263 ]

step = 5/60



ref = []
for i in range(0,len(Head)):
    ref.append(i*step)
    
coeffs = np.polyfit(ref, Head,order)




Head_LoBF = []
for i in range(0,len(ref)):
    value = 0
    for j in range(0,len(coeffs)):
        value += coeffs[-j-1]*ref[i]**j

        
    Head_LoBF.append(value)
plt.figure()
# print(ref)
print(coeffs)    
print("polynomial order:",order)
plt.title("MAV vs. Head")
plt.xlabel("MAV")
plt.ylabel("Head (kPa)")
plt.plot(ref,Head_LoBF)
plt.scatter(ref, Head)
plt.show()


print(Head)


# In[11]:


order = 1


vFlow_L_s = [0,0.32,1.12,2.10,3.18,4.27,5.35,6.44,7.58,8.77,9.93,11.15,12.33]
step = 5/60



ref = []
for i in range(0,len(vFlow_L_s)):
    ref.append(i*step)
    
coeffs = np.polyfit(ref, vFlow_L_s,order)




vFlow_LoBF = []
for i in range(0,len(ref)):
    value = 0
    for j in range(0,len(coeffs)):
        value += coeffs[-j-1]*ref[i]**j

        
    vFlow_LoBF.append(value)
plt.figure()
print(coeffs)    
print("polynomial order:",order)
plt.title("MAV vs. Flow")
plt.xlabel("MAV")
plt.ylabel("Flow (L/s)")
plt.plot(ref,vFlow_LoBF)
plt.scatter(ref, vFlow_L_s)
plt.show()

print(len(ref))


# In[13]:


#Head Calculation

order = 2

MAV =          [0,  .083, .167, .250, .333, .417, .500, .583, .667, .750, .833, 0.92, 1 ]

HTF_Pump_out =  [288, 289, 295,  300,  309,  320,  333,  350,  368,  393,  414,  444, 474]

HTF_Pump_in = [295, 295, 294,  295,  295,  295,  293,  294,  294,  293,  294,  294, 293 ]



Head = np.subtract(HTF_Pump_out, HTF_Pump_in)


#Head_old = [0, 269-277, 289.13 - 269.03, 305.82 - 270.1, 328-268, 355-267, 384-268, 419-268, 458-269, 509-264]

step = 5/60
print(Head)

#print(Head_old)

ref = []
for i in range(0,len(Head)):
    ref.append(i*step)
    
coeffs = np.polyfit(ref,Head,order)

coeffs_MAV = np.polyfit(MAV, Head, order)

Head_LoBF = []
for i in range(0,len(ref)):
    value = 0
    for j in range(0,len(coeffs)):
        value += coeffs[-j-1]*ref[i]**j

        
    Head_LoBF.append(value)
plt.figure()
# print(ref)
print(coeffs)  
print(coeffs_MAV)
print("polynomial order:",order)
plt.title("MAV vs. Head")
plt.xlabel("MAV")
plt.ylabel("Head (kPa)")
plt.plot(ref,Head_LoBF)
plt.scatter(ref, Head)
plt.show()


# In[ ]:




