# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 06:40:26 2024

@author: perro
"""

import re
import time
import board
import RPi.GPIO as GPIO
from hx711 import HX711
import numpy as np
from pathlib import Path
from settings import SENSORS_NAMES
import os
import asyncio
from collections.abc import Callable

from sensors import *

class SensorsController():
    """
    It watches constantly the data sent by the sensors, and it is stored peridiocally

    Methods
    -------
    
    init()
        Initializes the program with a greeting
    
    setup()
        Sets up the environment, checking if there are sensors connected

    save()
        Saves the data given by the sensors
    """
    def __init__(self):
        # Sensor view class.
        self.sensors_view = SensorsView(self)
        # You need to change your initial path
        self._init_path = r'init_path.txt'
        # It is used for scanning a channel to see if 
        # there are any sensors connected.
        self._attempt_init = 1

        self.all_sensors_fun = []

    def init(self):
        """
        It shows the initial message.
        """
        # We can have one greeting every time the program is initialized.
        messages = ["Solar Dryer Software Recorder", 
        "Now you are going to be able to record your data from your system",
        "Welcome!!!"]
        print()
        time.sleep(1)
        for message in messages:
            print(message,end='\r')
            time.sleep(len(message)*0.065)
            print(" "*len(message),end='\r')
    
    def setup(self):
        """Sets up the environment, checking if there are sensors connected
        
        All sensors are detected by each channel  of the multiplexer
        and whether apparently we don't see any of them, we are going to 
        try 4 times more"""
        # Scanning the channels.
        # self._scanner()
        self.tca9548a = TCA9548A()
        self.tca9548a.scanner()

        # Until the 5th try everything collapses, and the program is shut down
        if self._attempt_init == 5:
            print("Sorry, we have tried 5 times, and there are no sensors")
            time.sleep(1)
            print("We are going to shut down the program")
            time.sleep(1)
            print("Good bye...")
            time.sleep(1)
            raise KeyboardInterrupt
        
        # We need to check how many types of sensors are connected,
        # if none, we must try it again 
        if len(self.tca9548a._control_center.keys()) == 0:
            self._attempt_init += self._attempt_init
            print("There are no sensors connected")
            time.sleep(1)
            print("We are going to try it again in 5 seconds")
            time.sleep(5)
            self.setup()
            return  # To finish before going next, just the original has to continue.
        
        self.display_trigger = 5*1    # Each time is taken information.
        self.average_trigger = 0*60+ 3*5  # Up to this point, all data is averaged.
        # The minimum amount of samples is 80% of what we triggered
        self._minimum_sample = np.ceil((self.average_trigger/self.display_trigger)*0.8) # To have at least 80% of the data.
        # We start with this header and we develop it with _create_header method
        self._header = "Day,Month,Year,Time"
        self._create_header()
        # We go two levels above
        self._parent_dir = Path(__file__).parents[1]
        # _data_dir is for where the database is saved
        self._data_dir = self._parent_dir

        with ReadFile(self._init_path) as read_line:
            # And we can make the new pathlib object
            for item in read_line:
                self._data_dir = self._data_dir.joinpath(item)
        self._file_detection(1) # The two is in case there's already a one file there.
        
        # -TODO- Improve, imagine we want to open an existing file and want to add more information to it
        # we need to determine that the sensors connected are the same, to this file header.
        
        # What would it happen if we had two files with the same name, but differet headers?
        # We need to create another file to avoid mixing data.
        with ReadFile(str(self._data_dir)) as data_file:
            header = data_file.readline()
            header = re.sub(r"\s+",'',header.strip())
            
        # There's a double check if it is able to write on the document
        # The headers should be the same.
        if self._header != header:
            self._file_detection(1)

    def save_data(self):
        """Saves the data given by the sensors with the correct format"""
        with open(self._data_dir,'a') as xfile:
            # We have here the start point.
            self.trigger_number = 0
            self.average_number = 0
            self.start_time_trigger = time.time()
            self.start_time_average = self.start_time_trigger
            first = True
            while True:
                self.current_time = time.time()
                # With this one we can get the values of day, month and year
                self.elapsed_time_trigger=int(self.current_time-self.start_time_trigger)
                self.elapsed_time_average=int(self.current_time-self.start_time_average)
                self.trigger_bool = self.elapsed_time_trigger>=self.display_trigger 
                self.average_bool = self.elapsed_time_average>=self.average_trigger
                
                if  self.trigger_bool or self.average_bool or first:
                    first = False
                    self.start_time_trigger = self.current_time
                    asyncio.run(self.trigger())
                    
                    self.sensors_view.print_values('Trigger_'+str(self.trigger_number+1))
                    self.trigger_number = self.trigger_number + 1
                    # The minimum amount to be sure that it is representative.
                    if self.average_bool:
                        self.trigger_number = int(0)
                        self.start_time_average = self.current_time
                        self._set_avg_prop() # We are going to round it to ()
                        # Convert `average_5min` to a string format suitable for CSV, handling NaN values properly
                        self._join_fun()
                        self.sensors_view.print_values('Average')
                        
                        # It is splited [Day Name, Month, Day Number, Hour, Year]
                        self.full_time = time.ctime(self.start_time_average).split()
                        print(f"Captured Date ={self.full_time[0]} {self.full_time[2]} {self.full_time[1]} {self.full_time[4]}, Time = {self.full_time[3]}")
                        xfile.write(f"{self.full_time[2]},{self.full_time[1]},{self.full_time[4]},{self.full_time[3]},{self.results_avg[1:-1]}\n")
                        print("\n---------------------------------")
                        print("Saving data in memory",end="")
                        for _ in range(5):
                            print(".",end="")
                            time.sleep(0.2)
                        print()
                        print("---------------------------------\n")
         

    def _scanner(self):
        """Detects all sensors in the multiplexor, transversing each channel
        """
        print("Sensors' Scanner", end='')
        for _ in range(3):
            print(".",end='')
            time.sleep(0.25)
        print("\n")
        time.sleep(0.8)
        # I2C setup on bus 1
        self._i2c = board.I2C()
        # We are going to use TCA9548A, which is a multiplexor
        self._tca = adafruit_tca9548a.TCA9548A(self._i2c)
        # We initialize the dictionary "control_center" to save all data related to the sensors.
        # First array: the objects themselves.
        # Second array: the objects' addresses.     
        self._control_center = {
            "BME280" : [[],[]],
            "MLX90614" : [[],[]],
            "SHT31" : [[],[]],
        }

        # When it is invoked, an object of the corresponding class is created.
        sensor_types = {
            "BME280" : BME280,
            "SHT31" : SHT31,
            "MLX90614" : MLX90614
        }

        # We have 8 ports in total.
        for port in range(8):
             # We have to check if there are sensors connected in any channel, 3 times for each.
             # After one sensor is added with a particular address, 
             # no more sensors with the same address are going to be accepted, 
             # because we are going to save two different physical sensors with the same address.
      
            for _ in range(3):
                try:
                    # Getting the addresses of the port.
                    if self._tca[port].try_lock():
                        addresses = self._tca[port].scan()
                   
                    #After it is scanned, we are going to unlock it, to let communication flow later.
                    self._tca[port].unlock()
                    try:
                        # We have different addresses according to the sensor.
                        for address in addresses:
                            # As we are using dictionaries, each address is mapped to its correponding sensor name.
                            try:
                                sensor_name = SENSORS_NAMES[address]
                            except KeyError:
                                # As this address doesn't match any of the sensors' names, we need to go to the next loop.
                                continue

                            # Whether we go in, it means the array doesn't have that specific address,
                            # which says we need to add it.
                            if not address in self._control_center[sensor_name][1]:
                                self._control_center[sensor_name][0].append(sensor_types[sensor_name](self._tca,
                                                                port,
                                                                len(self._control_center[sensor_name][1]),    
                                                                address))
                                self._control_center[sensor_name][1].append(address)
                                print(f"The {self._control_center = }")
                                    
                    except ValueError:
                        print(f"Error in Port: {port}, sensor : {SENSORS_NAMES[address]}, address : {address}")
                        time.sleep(1)
                except OSError:
                    print(f"Aborting, there are torn wires or desconected, (check power wires) ")
                    time.sleep(2)
                    self.cleanAndExit()
            # Deleting the addresses
            for sensor_name in self._control_center.keys():
                self._control_center[sensor_name][1] = []

        # We want to get rid of all addresses that are not sensors.
        self._remove_sensors()
        self.append_all_fun()
        
    def append_all_fun(self):
        for type_ in self._control_center.keys():
            for virtual_sensor in self._control_center[type_][0]:
                        self.all_sensors_fun.append(virtual_sensor.trigger_all_set_fun)  

    def _remove_sensors(self):
        """Removes the sensors that are not connected"""
        type_obj=list(self._control_center.items())
        for type_, obj_addr in type_obj:
            total_num = len(obj_addr[0])
            if total_num > 0:
                print(f"{total_num} " + type_ + ' connected. Addresses: ', end='')
                for curr_num, addr in enumerate(obj_addr[1]):
                    print(addr,end='')
                    if curr_num < total_num-1:
                        print(end=', ')
                    else:
                        print()
                    
            else:
                # Removing the non connected sensors. Then, all the sensors' names that are in "self.sensors_name" array.
                del self._control_center[type_]
          
    def _file_detection(self,replica_number):
        """Detects whether there's already a file with the same file"""

        # Here you should modify it depending on the directory.
        # The furthest right side should be a number.
        file_name_arr = self._data_dir.stem.rsplit('_',1)
        
        try:
            # Test to know whether it is a number, if it isn't, it will throw ValueError out
            int(file_name_arr[-1])
            if replica_number == 1:
                # As there's already a replica, we select the base name
                new_name = file_name_arr[0]
            else:
                new_name = file_name_arr[0] +'_'+str(replica_number)
        except ValueError:
            # If just this line is run, it means the original name was 'sensor_data' or whatever other name
            # it could hold that doesn't have the print of replica (the number attached at the end).
            # otherwise the other line is also run.
            new_name = self._data_dir.stem
            
            # If we started with a replica, remember we are going to use always the base name
            # to start with, it means that althought the name is 'sensor_data_5', we will check 
            # the base name first, which is 'sensor_data', 'replica_number' with 2 means we have
            # called '_file_detection' twice.
            if replica_number == 2:
                new_name = new_name +'_'+str(replica_number)
                
        finally:
            
            try:
                # The first try will be always the base name, in this case nothing is changed, but 
                # for the second, third and so on, the name is replaced by the replica's names 1, 2, 3,...
                self._data_dir=self._data_dir.with_stem(new_name)

                # We need to determine if this file exists
                with DetectFile(self._data_dir) as file_header, OverWriteFile(self._init_path) as init_file:
                    file_header.write(self._header+'\n')
                    print(f"Header = {self._header}")
                    print("Successfully created!!")
                    # We want to save the relative path
                    init_path=str(self._data_dir.relative_to(self._parent_dir))
                    print(f"\nThe new {init_path = }")
                    init_file.write(init_path)

            except FileExistsError:
                print(self._data_dir)
                self._file_detection(replica_number+1)
            
    def _create_header(self):
        """Creates the header using its properties
        as a base"""
        
        # At least there will be one sensor for that reason, the '0'
        # All the sensors listed under, they EXIST.
        header = ''
        # All connected sensors are considered to make the header.
        for type_ in self.tca9548a._control_center.keys():
            for virtual_sensor in self.tca9548a._control_center[type_][0]:
                for property in virtual_sensor.all_properties_values.keys():
                    header = header+',' + virtual_sensor.name+'_'+property
                    
        self._header = self._header+header 
        
    def cleanAndExit(self):
        print("Cleaning...")
        print("Bye!")
        os._exit(1)

    async def trigger(self):
        """Triggers all the sensors"""
        print("Data is being taken it...\n")
        start = time.perf_counter()
        
        await asyncio.gather(*[fun() for fun in self.tca9548a.all_sensors_fun])

        print(f"\nElapsed time = {time.perf_counter()-start}\n")            

    def _set_avg_prop(self):
        # The property self._connected_sensors can be eliminated
        for type_ in self.tca9548a._control_center.keys(): 
            for virtual_sensor in self.tca9548a._control_center[type_][0]:
                properties = virtual_sensor.all_properties_values.keys()
                # If one average value doesn't work, none of the others work. They are not useful.
                normal_op = np.nansum(np.invert(np.isnan(virtual_sensor.avg_prop[list(properties)[0]])))>= self._minimum_sample
                # We need to check for each 
                for property in properties:
                    # To save the last sensors reading.
                    # This is not to use more than 1 check if there is enough non nan-data to make a correct average.    
                    if  not normal_op:
                        virtual_sensor.avg_prop[property] = [np.nan]
                    elif normal_op:
                        # The axis is for making the mean for each row, not column.
                        virtual_sensor.avg_prop[property] = [float(round(np.nanmean(virtual_sensor.avg_prop[property]),2))]
                                         
    def _join_fun(self):
        """Joins all results in a big array"""
        self.results_avg = []
        for connected_sensor in self.tca9548a._control_center.keys():
            for virtual_sensor in self.tca9548a._control_center[connected_sensor][0]:
                for value in virtual_sensor.avg_prop.values():
                    # The array has just one value
                    self.results_avg.append(float(value[0]))
                        
        self.results_avg = str(self.results_avg)

class SensorsView():
    def __init__(self,sensor_controller:SensorsController):
        self.sensor_controller = sensor_controller 
        
    def print_values(self,data_type):
        self.keys=self.sensor_controller.tca9548a._control_center.keys()
        print(f"The keys are {self.keys}")
        print(f"---------------{data_type}-------------------------")
        for connected_sensor in self.sensor_controller.tca9548a._control_center.keys():
            properties = self.sensor_controller.tca9548a._control_center[connected_sensor][0][0].all_properties_values.keys()
            for property in properties:
                values = []
                print(f"{connected_sensor+'_'+property}: ",end='')
                virtual_sensors = self.sensor_controller.tca9548a._control_center[connected_sensor][0]
                for virtual_sensor in virtual_sensors:
                    values.append(float(virtual_sensor.avg_prop[property][self.sensor_controller.trigger_number]))
                    if data_type == 'Average':
                        virtual_sensor.avg_prop[property] = []
                
                print(f"{str(values)[1:-1]}",end=' ')
            print() # To print the other sensors' data, one "\n"
        print(f"----------------{data_type}------------------------\n")

class TCA9548A(adafruit_tca9548a.TCA9548A):
    def __init__(self):
        # All sensors' functions
        self.all_sensors_fun = []
        self._i2c = board.I2C()
        super().__init__(self._i2c)
        # We initialize the dictionary "control_center" to save all data related to the sensors.
        # First array: the objects themselves.
        # Second array: the objects' addresses.     
        self._control_center = {
            "BME280" : [[],[]],
            "MLX90614" : [[],[]],
            "SHT31" : [[],[]]
        }


    def scanner(self):
        """Detects all sensors in the multiplexor, transversing each channel
        """
        print("Sensors' Scanner", end='')
        for _ in range(3):
            print(".",end='')
            time.sleep(0.25)
        print("\n")
        time.sleep(0.8)
        # I2C setup on bus 1
        # When it is invoked, an object of the corresponding class is created
        sensor_types = {
            "BME280" : BME280,
            "SHT31" : SHT31,
            "MLX90614" : MLX90614
        }
        # We have 8 ports in total
        for port in range(8):
            # We have to check if there are sensors connected in any channel, 3 times each.
            # After one sensor is added with a particular address,
            # no more sensors with the same address are going to be accepted, 
            # because we are going to save two different physical sensors with the same address.
        
            for _ in range(3):
                try:
                    # Getting the addresses of the port.
                    if self[port].try_lock():
                        addresses = self[port].scan()
                    
                    #After it is scanned, we are going to unlock it, to let communication flow later.
                    self[port].unlock()
                    try:
                        # We have different addresses according to the sensor.
                        for address in addresses:
                            # As we are using dictionaries, each address is mapped to its correponding sensor name.
                            try:
                                sensor_name = SENSORS_NAMES[address]
                            except KeyError:
                                # As this address doesn't match any of the sensors' names, we need to go to the next loop.
                                continue

                            # Whether we go in, it means the array doesn't have that specific address,
                            # which says we need to add it.
                            if not address in self._control_center[sensor_name][1]:
                                self._control_center[sensor_name][0].append(sensor_types[sensor_name](self,
                                                                port,
                                                                len(self._control_center[sensor_name][1]),    
                                                                address))
                                self._control_center[sensor_name][1].append(address)
                                    
                    except ValueError:
                        print(f"Error in Port: {port}, sensor : {SENSORS_NAMES[address]}, address : {address}")
                        time.sleep(1)
                except OSError:
                    print(f"Aborting, there are torn wires or desconected, (check power wires) ")
                    time.sleep(2)
                    self.cleanAndExit()

            # Deleting the addresses
            print(f"The {self._control_center = }")
            for sensor_name in self._control_center.keys():
                self._control_center[sensor_name][1] = []

        # We want to get rid of all addresses that are not sensors.
        self._remove_sensors()
        self._append_all_fun()

    def _remove_sensors(self):
        """Removes the sensors that are not connected"""
        type_obj=list(self._control_center.items())
        for type_, obj_addr in type_obj:
            total_num = len(obj_addr[0])
            if total_num > 0:
                print(f"{total_num} " + type_ + ' connected. Addresses: ', end='')
                for curr_num, addr in enumerate(obj_addr[1]):
                    print(addr,end='')
                    if curr_num < total_num-1:
                        print(end=', ')
                    else:
                        print()
                    
            else:
                # Removing the non connected sensors. Then, all the sensors' names that are in "self.sensors_name" array.
                del self._control_center[type_]

    def _append_all_fun(self):
        for type_ in self._control_center.keys():
            for virtual_sensor in self._control_center[type_][0]:
                self.all_sensors_fun.append(virtual_sensor.trigger_all_set_fun)

    def cleanAndExit(self):
        print("Cleaning...")
        print("Bye!")
        os._exit(1)

class FileManager(object):
    
    _mode = ''
    def __init__(self,file_path:str|Path):
        self._file_path = file_path

    def __enter__(self):
         # The relative path to the database is in 'file'
        self._file = open(self._file_path,self._mode)
        return self._file
    
    def __exit__(self, exc_type,exc_value, exc_tb):
        if self._file:
            self._file.close()

        if isinstance(exc_type,Exception): 
            print(f" {exc_type = }")
            print(f" {exc_value = }")
            print(f" {exc_tb = }")


class ReadFile(FileManager):
    """It opens the file in reading and editing mode"""
    _mode = 'r+'

class DetectFile(FileManager):
    """It helps to detect whether the file exists or not"""
    _mode = 'x'
    def __exit__(self, exc_type,exc_value, exc_tb):
        if self._file:
            self._file.close()

        if isinstance(exc_type,Exception) and not isinstance(exc_type,FileExistsError): 
            print(f" {exc_type = }")
            print(f" {exc_value = }")
            print(f" {exc_tb = }")
    
class OverWriteFile(FileManager):
    _mode = 'w+'

class AddInfo(FileManager):
    _mode = 'a'

if __name__ == "__main__":
    try:
        # Reset the sensors power.
        dog_watcher = SensorsController()
        dog_watcher.setup()
        dog_watcher.save_data()
            
    except KeyboardInterrupt:
        print("Exiting...")
        GPIO.cleanup()
    
        """_summary_
        """        