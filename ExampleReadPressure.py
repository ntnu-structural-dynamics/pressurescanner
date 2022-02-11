# -*- coding: utf-8 -*-
"""
Created on 

@author: OWP
"""
    
#%%

import numpy as np
import presscan


#%% Read data

filename='191_30_90_182.dat'
folder='Exampledata//'

(t_frame,t_trig,pres,temp,_)=presscan.readdatfile(filename,folder)

#%% Plot time series

# To come

