# -*- coding: utf-8 -*-
"""
Created on 

@author: OWP
"""
    
###

import numpy as np
import os
import struct

###


def readdatfile(filename,folder='',N_frame=5e5):
   
    # Inputs:
    # filename: the name of the file
    # folder: the folder of the file
    # N_frame: number of frames to read (can be overspecified, automatic detection is performed)
    
    # Outputs: (t_frame, t_trig, pres, temp,scan_data)
    # t_frame: time stamp of each frame in seconds
    # t_trig: time stamp of each trig in seconds
    # temp: internal temperatures (8 channels)
    # pres: pressure data (64 channels)
    # scan_data: the full scanned data, 87 parameters
    
    if folder=='':
        folder_str=''
    else:
        folder_str=folder + '\\'
            
    # Extension
    if filename[-4:]!='.dat':
        filename=filename + '.dat'

    file=folder_str + filename
    
    N_frame=int(N_frame)
    
    # Check if file exists
    if not os.path.isfile(file):
        raise Exception(' ***** The scanner file ' + file + ' is not found')


    GB_mem_req=8*N_frame*87/1e9
    
    if GB_mem_req>3:
        print('***** Required memory for pressure data is ' + str(GB_mem_req) + ' GB' )
        print('***** Consider reducing N_frame to save memory')

    # Preallocate matrices
    part_1 = np.zeros((4,N_frame)).astype('int') # packet type, packet size, frame number, scan type
    part_2 = np.zeros((1, N_frame)) # frame rate
    part_3 = np.zeros((2, N_frame)).astype('int') # valve status, units index
    part_4 = np.zeros((1, N_frame)) # unit conversion factor
    part_5 = np.zeros((2, N_frame)).astype('int') # PTP scan start time (sec), PTP scan start time (ns)
    part_6 = np.zeros((1, N_frame)).astype('int') # External trigger time
    part_7 = np.zeros((72, N_frame)) # temperatures (x8), pressures (x64)
    part_8 = np.zeros((4, N_frame)).astype('int') # frame time (sec), frame time (ns), external trigger time (sec), external trigger time (ns)

    fid = open(file, "rb")
    
    # Break
    DoBreak=False
    
    # Loop over all frames (time step)
    for k in range(N_frame):
        
        # Read 4 bytes at a time, total 87 times  
        
        for j in range(4):
            byte = fid.read(4)
            
            # If byte is empty, then break loop
            if not byte:
                DoBreak=True
                break
            else:
                part_1[j,k]=struct.unpack('<i', byte)[0]
            
        if DoBreak==True:
            print('***** Stopped reading at at ' + str(k) + ' frames')
            N_frame_stop=k-1
            break
            
        for j in range(1):
            byte = fid.read(4)
            part_2[j,k]=struct.unpack('<f', byte)[0]
            
        for j in range(2):
            byte = fid.read(4)
            part_3[j,k]=struct.unpack('<i', byte)[0]
            
        for j in range(1):
            byte = fid.read(4)
            part_4[j,k]=struct.unpack('<f', byte)[0]
            
        for j in range(2):
            byte = fid.read(4)
            part_5[j,k]=struct.unpack('<i', byte)[0]
            
        for j in range(1):
            byte = fid.read(4)
            part_6[j,k]=struct.unpack('<I', byte)[0]
            
        for j in range(72):
            byte = fid.read(4)
            part_7[j,k]=struct.unpack('<f', byte)[0]
            
        for j in range(4):
            byte = fid.read(4)
            part_8[j,k]=struct.unpack('<i', byte)[0]
        
        
    fid.close()
    
    # If number of frames was overspecified, then cut where file stops
    if DoBreak:
        part_1=part_1[:,0:N_frame_stop+1]
        part_2=part_2[:,0:N_frame_stop+1]
        part_3=part_3[:,0:N_frame_stop+1]
        part_4=part_4[:,0:N_frame_stop+1]
        part_5=part_5[:,0:N_frame_stop+1]
        part_6=part_6[:,0:N_frame_stop+1]
        part_7=part_7[:,0:N_frame_stop+1]
        part_8=part_8[:,0:N_frame_stop+1]
    

    # Stack all scan data
    scan_data = np.vstack((part_1,part_2,part_3,part_4,part_5,part_6,part_7,part_8)).T
        
    # Time 
    t_frame = scan_data[:,84-1] + scan_data[:,85-1]/1e9 #Time the frame occurred, Time in s plus time in ns
    t_trig = scan_data[:,86-1] + scan_data[:,87-1]/1e9 #Time the external trigger occurred , Time in s plus time in ns
    
    # Temperature and pressure
    temp = scan_data[:,11:18]
    pres = scan_data[:,19:82]

    return (t_frame,t_trig,pres,temp,scan_data)