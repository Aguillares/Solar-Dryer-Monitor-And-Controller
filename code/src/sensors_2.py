# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 06:40:26 2024

@author: perro
"""

import re
import glob
import time
import board
from adafruit_mlx90614 import MLX90614 as mlx90614
from adafruit_bme280 import basic as adafruit_bme280
import sys
import RPi.GPIO as GPIO
from hx711 import HX711
import numpy as np
import csv
import adafruit_tca9548a
from adafruit_sht31d import SHT31D as sht31d
from pathlib import Path
from settings import SENSORS_NAMES
import os
import asyncio
from typing import TypeAlias
from typing import TypeVar

# We need to simplify the notation
Tca9548a : TypeAlias = adafruit_tca9548a.TCA9548A
Bme280 : TypeAlias = adafruit_bme280.Adafruit_BME280_I2C

class Dog_Watcher():
    """
    It watches constantly the data sent by the sensors, and it is stored peridiocally
    
    """
    def __init__(self):
        # These can be any type of sensors.
        self._connected_sensors = ['BME280','SHT31','MLX90614']
        # You need to change your initial path
        self._init_path = r'init_path.txt'
        # It is used for scanning many times a channel to see if 
        # there are any sensors connected.
        self._attempt_init = 1

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
        """All sensors are detected by each channel  of the multiplexor
        and whether apparently we don't see any of them we are going to 
        try 4 times more"""
        # Scanning the channels.
        self._scanner()

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
        if len(self._connected_sensors) == 0:
            self._connected_sensors = ['BME280','SHT31','MLX90614']
            self._attempt_init += self._attempt_init
            print("There are no sensors connected")
            time.sleep(1)
            print("We are going to try it again in 5 seconds")
            time.sleep(5)
            self.setup()
            return  # To finish before going next, just the original has to continue.
        
        self.display_trigger = 5*1    # 5 seconds
        self.average_trigger = 0*60+ 3*5  # 5 min
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
        #  
        # What would it happen if we had two files with the same name, but differet headers?
        # We need to create another file to avoid mixing data.
        with ReadFile(str(self._data_dir)) as data_file:
            header = data_file.readline()
            header = re.sub(r"\s+",'',header.strip())
            
        # There's a double check if it is able to write on the document
        # The headers should be the same.
        if self._header != header:
            self._file_detection(1)

    def _scanner(self):
        """
        It detects all sensors in the multiplexor, transversing each channel
        """
        print("Sensors Scanner", end='')
        for _ in range(3):
            print(".",end='')
            time.sleep(0.25)
        print("\n")
        time.sleep(0.8)
        # I2C setup on bus 1
        self._i2c = board.I2C()
        # We are going to use TCA9548A, which is a multiplexor
        self._tca = adafruit_tca9548a.TCA9548A(self._i2c)
        # We initialize the dictionary "control_center" to save all data related to them.
        # First array: the objects themselves.
        # Second array: the addresses.     
        self._control_center = {
            "BME280" : [[],[]],
            "MLX90614" : [[],[]],
            "SHT31" : [[],[]],
        }

        # When it is invoked, an object of the corresponding class is created.
        sensors_type = {
            "BME280" : BME280,
            "SHT31" : SHT31,
            "MLX90614" : MLX90614
        }

        # We have 8 channels or ports.
        for port in range(8):
             # "attempts" to check if there are sensors connected to a channel, 3 times for each channel.
             # After it is added one sensor, no more are accepted with the same address, because we are going to save the same sensor again.
      
            for _ in range(3):
                try:
                    # Getting the addresses of the port.
                    if self._tca[port].try_lock():
                        addresses = self._tca[port].scan()
                   
                    #After it is scanned we are going to unlock it again, to let communication flow later
                    self._tca[port].unlock()
                    try:
                        # We have different addresses according to the sensor.
                        for address in addresses:
                            # As we are using dictionaries, each address is mapped to its correponding sensor name.
                            try:
                                sensor_name = SENSORS_NAMES[address]
                            except KeyError:
                                # As this address doesn't match any of the sensors, we need to go to the next loop.
                                continue

                            # Whether we go in, it means the array doesn't have that specific address,
                            # which means we need to add it.
                            if not address in self._control_center[sensor_name][1]:
                                self._control_center[sensor_name][0].append(sensors_type[sensor_name](self._tca,
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

        # We want to get rid of all addresses that are not sensors.
        self.remove_sensors()
    
    def add_sensors(self,virtual_sensor):
        self._control_center[virtual_sensor.type].append(virtual_sensor)

    def remove_sensors(self):
        for type_, obj_addr in self._control_center.items():
            total_num = len(obj_addr[1])
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
                del self._connected_sensors[self._connected_sensors.index(type_)]
            
            time.sleep(1)
        
        
    def _file_detection(self,replica_number):
        # Here you should modify it depending of the directory.
        # The furtherest right side should be a number.
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
        """Create header using its properties
        as a base for making it"""
        
        # At least there will be one sensor for that reason, the '0'
        # All the sensors listed under, they EXIST.
        header = ''
        # All connected sensors are considered to make the header.
        
        for type_ in self._connected_sensors:
            for virtual_sensor in self._control_center[type_][0]:
                for property in virtual_sensor.get_properties():
                    header = header+',' + virtual_sensor.get_name()+'_'+property
                    
        self._header = self._header+header 
        

    def print_values(self,data_type):
        print(f"---------------{data_type}-------------------------")
        for connected_sensor in self._connected_sensors:
            properties = self._control_center[connected_sensor][0][0].get_properties()
            for property in properties:
                values = []
                print(f"{connected_sensor+'_'+property}: ",end='')
                virtual_sensors= self._control_center[connected_sensor][0]
                for virtual_sensor in virtual_sensors:
                    values.append(float(virtual_sensor.avg_prop[property][self.trigger_number]))
                    if data_type == 'Average':
                        virtual_sensor.avg_prop[property] = []
                values_str = str(values)
                print(f"{values_str[1:-1]}",end=' ')
            print() # To print the other sensors' data, one "\n"
        print(f"----------------{data_type}------------------------\n")

    def cleanAndExit(self):
        print("Cleaning...")
        print("Bye!")
        os._exit(1)
#         sys.exit()

    def data_operation(self):
        # Maybe here we can add a clock to see the differences between sensors' time.
        for type_ in self._connected_sensors:
            for virtual_sensor in self._control_center[type_][0]:
                try:
                    self.avg_exception = False
                    virtual_sensor.trigger()
                    time.sleep(0.1)
                    self.add_avg_data(virtual_sensor)
                except Exception:
                    self.avg_exception = True
                    print("There's a problem with the sensor: {} ".format(virtual_sensor.name))
                    self.add_avg_data(virtual_sensor)
                    continue
                    
     
    def add_avg_data(self, virtual_sensor):
        # This "i" is just for the detection of the properties' name
        i = 0
        for property in virtual_sensor.get_properties():
            # Now we want to know the property name according to "sensor_property_value"
            if not self.avg_exception:
                value = virtual_sensor.get_values()[i]
                i+=1
            else:
                value = np.nan
            virtual_sensor.avg_prop[property].append(value)

    def set_avg_prop(self):
        for type_ in self._connected_sensors:
            for virtual_sensor in self._control_center[type_][0]:
                properties = virtual_sensor.get_properties()
                prop = properties[0]
                # If one average value doesn't work, none of the others work. They are not useful.
                normal_op = np.nansum(np.invert(np.isnan(virtual_sensor.avg_prop[prop])))>= self._minimum_sample
                # We need to check for each 
                for property in properties:
                    # To save the last sensors reading.
                    # This is not to use more than 1 check if there is enough non nan-data to make a correct average.    
                    if  not normal_op:
                        virtual_sensor.avg_prop[property] = [np.nan]
                    elif normal_op:
                        # The axis is for making the mean for each row, not column.
                        virtual_sensor.avg_prop[property] = [float(round(np.nanmean(virtual_sensor.avg_prop[property]),2))]
                        
            
    def save_data(self):
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
                    self.data_operation()
                    self.print_values('Trigger_'+str(self.trigger_number+1))
                    self.trigger_number = self.trigger_number + 1
                    # The minimum amount to be sure that it is representative.
                    if self.average_bool:
                        self.trigger_number = int(0)
                        self.start_time_average = self.current_time
                        self.set_avg_prop()#We are going to round it to ()
                        # Convert `average_5min` to a string format suitable for CSV, handling NaN values properly
                        self.join_fun()
                        self.print_values('Average')
                        
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
                    
    def join_fun(self):
        self.results_avg = []
        i=0
        for connected_sensor in self._connected_sensors:
            for virtual_sensor in self._control_center[connected_sensor][0]:
                for value in virtual_sensor.avg_prop.values():
                    # The array has just one value
                    self.results_avg.append(float(value[0]))
                    i = i +1
                    if connected_sensor == 'SHT31' and i == 1 and value>=70:
                        virtual_sensor.set_heater(True)
                        time.sleep(0.8)
                        virtual_sensor.set_heater(False)
                        
        self.results_avg = str(self.results_avg)

class Sensor():
    def __init__(self,sensor:Bme280|sht31d,type_:str, port:int, number:int,address:int):
        self.sensor = sensor
        self.type = type_
        self.set_port(port)
        self.set_number(number)
        self.address = address
        self.name = self.type + '_' + str(self.port) + '_' + str(self.number)
        self.all_properties_values = []
        self.all_properties_names = []
        self.all_set_fun = []
        self.attempts_trigger = 0
    
    def get_name(self):
        return self.name
    
    def get_number(self):
        return self.number

    def get_port(self):
            return self.port

    def get_sensor(self):
            return self.sensor

    def get_type(self):
            return self.type
            
    def set_number(self,number):
        self.number = number
    
    def set_port(self,port):
        self.port = port
    
    def set_sensor(self,sensor):
        self.sensor = sensor
    
    def trigger(self):
        self.all_properties_values = []
        for set_fun in self.all_set_fun:
            try:
            # We are going to round it to round it to two places
                print(f"{self.__class__.__name__}, {set_fun.__name__ = }")
                self.all_properties_values.append(float(round(set_fun(),2)))
            except RuntimeError as e:
                print(f"Error, probable reasons: \n 1. Suddenly two sensors have the same address. \n {e}")
            
        if (np.isnan(self.all_properties_values).any()):
            if self.attempts_trigger == 10:
                self.set_all(np.nan)
                raise Exception
                
            self.attempts_trigger = self.attempts_trigger+1
            self.trigger()
                  
    def get_values(self):
        return self.all_properties_values
    
    def get_properties(self):
        return self.all_properties_names
    
    def set_properties_names(self,properties_names):
        self.all_properties_names = properties_names
    
    def set_fun(self,funcs):
        self.all_set_fun = funcs
    
    def set_all(self,value):
        for set_fun in self.all_set_fun:
            set_fun(value)
            
    def get_real_sensor(self):
        return self.sensor

class BME280SHT31(Sensor):
    """It encompasses both, the BME280 and SHT31"""
    def __init__(self,sensor:Bme280,type_: str, port:int, number:int,address:int):
        super().__init__(sensor,type_,port,number,address)

        self.avg_prop = {
            'T' : [],
            'RH' : [],
        }

    def set_T (self,value = None):
            """Sets a 

            If a value is given, it is passed to 'temp' variable,
            """
            if value is None:
                temp = self.get_real_sensor().temperature
            else:
                temp = value
            return temp
            
            
    def set_RH(self,*value):

        if len(value) == 0:
            humidity = self.get_real_sensor().relative_humidity
        else:
            humidity = value
        return humidity

_T =TypeVar("_T")    
ListOrSet: TypeAlias = list[_T] | set[_T]

class BME280(BME280SHT31):
    """Sensor BME280 detects Temperature, Relative Humidity and Pressure"""
    def __init__(self,tca:Tca9548a,port:int,number:int,address:int) -> None:
        super().__init__(adafruit_bme280.Adafruit_BME280_I2C(tca[port],address),'BME280',port,number,address)
        # It is the property that SHT31 doesn´t have.
        self.avg_prop['P'] = []
        
        
        self.set_properties_names(['T','RH','P'])
        self.set_fun([self.set_T,self.set_RH,self.set_P])

        
    def set_P(self,*value):
        if len(value) == 0:
            pressure = self.get_real_sensor().pressure
        else:
            pressure = value
        return pressure

class SHT31(BME280SHT31):
    def __init__(self,tca,channel,address,number):
        super().__init__(sht31d(tca[channel],address),'SHT31',channel,number,address)
        self.set_properties_names(['T','RH'])
        self.set_fun([self.set_T,self.set_RH])

    def set_heater(self,heater_command):
        self.sensor.heater = heater_command

class MLX90614(Sensor):
    def __init__(self,tca,channel,address,number):
        super().__init__(mlx90614(tca[channel],address),'MLX90614',channel,number,address)
        self.avg_prop = {
            'amb_T' : [],
            'obj_T' : [],
        }
        self.amb_T = None
        self.obj_T= None
        self.all_properties_values = [self.amb_T,self.obj_T]
        self.set_properties_names(['amb_T','obj_T'])
        self.all_set_fun =[self.set_amb_T,self.set_obj_T]

    def set_amb_T (self,*value):
        if len(value) == 0:
            amb_T = self.get_real_sensor().ambient_temperature
        else:
            amb_T = value
        return amb_T
        
    def set_obj_T(self,*value):
        if len(value) == 0:
            obj_T = self.get_real_sensor().object_temperature
        else:
            obj_T = value
        return obj_T


class __FileManager(object):
    
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


class ReadFile(__FileManager):
    """It opens the file in reading and editing mode"""
    _mode = 'r+'

class DetectFile(__FileManager):
    """It helps to detect whether the file exists or not"""
    _mode = 'x'
    def __exit__(self, exc_type,exc_value, exc_tb):
        if self._file:
            self._file.close()

        if isinstance(exc_type,Exception) and not isinstance(exc_type,FileExistsError): 
            print(f" {exc_type = }")
            print(f" {exc_value = }")
            print(f" {exc_tb = }")
    
class OverWriteFile(__FileManager):
    _mode = 'w+'

class AddInfo(__FileManager):
    _mode = 'a'

if __name__ == "__main__":
    try:
        # Reset the sensors power.
        
        GPIO.setup(23,GPIO.OUT)
        GPIO.output(23,False)
        time.sleep(0.1)
        GPIO.output(23,True)
        dog_watcher = Dog_Watcher()
        #dog_watcher.init()
        dog_watcher.setup()
        dog_watcher.save_data()
            
    except KeyboardInterrupt:
        print("Exiting...")
        GPIO.cleanup()
    
        """_summary_
        """        