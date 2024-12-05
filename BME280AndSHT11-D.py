# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 06:40:26 2024

@author: perro
"""
import re
import glob
import time
import board
from adafruit_mlx90614 import MLX90614
from adafruit_bme280 import basic as adafruit_bme280
import sys
import RPi.GPIO as GPIO
from hx711 import HX711
import numpy as np
import csv
import adafruit_tca9548a
from adafruit_sht31d import SHT31D


class Dog_Watcher():
    def __init__(self):
        self.connected_sensors = ['BME280','SHT31','MLX90614']
        # You need to change your initial path
        self.slash = '/'
        self.init_path = r'/home/raspberrypi2/Desktop/Solar-Dryer-Monitor-And-Controller/init_path.txt'
        self.extension ='.csv' 
        self.attempt_init = 1
        self.first_check = False
        
        

    def init(self):
        # We can have one greeting every time is initialize the program.
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
        # Cleaning self.sensors_name
        self.scanner()
        if self.attempt_init == 5:
            print("Sorry, we have tried 5 times, and there are no sensors")
            time.sleep(1)
            print("We are going to shut down the program")
            time.sleep(1)
            print("Good bye...")
            time.sleep(1)
            raise KeyboardInterrupt
        if len(self.connected_sensors) == 0:
            self.connected_sensors = ['BME280','SHT31','MLX90614']
            self.attempt_init += self.attempt_init
            print("There are no sensors connected")
            time.sleep(1)
            print("We are going to try it again in 5 seconds")
            time.sleep(5)
            self.setup()
            return  # To finish before going next, just the original has to continue.
        
        new = True
        self.display_trigger = 10    # 5 seconds
        self.average_trigger = 5*60+ 0*5  # 5 min
        self.minimum_sample = int((self.average_trigger/self.display_trigger + 1)*0.8) # To have at least 80% of the data.
        self.header = "Day,Month,Year,Time"
        print(f"Header = {self.header}")
        self.create_header()
        print(f"Header = {self.header}")
        with FileManager(self.init_path).read() as init_path_file:
                self.path = init_path_file.readline()[:-1]
                self.file_name = init_path_file.readline()
                
                if new == True:
                    self.file_detection(2) # The two is in case there's already a one file there.
        
        # What would it happen if we have two files with the same name, but differet headers?
        # We need to create another file to avoid mixing data.
        with FileManager(self.full_path_file).read() as data_file:
            header = data_file.readline()
            header = re.sub('\s+','',header.strip())
            # There's a double check if it is able to write on the document
            # The headers should be the same.
            if self.header != header:
                self.file_detection(2)

    def scanner(self):
        print("Sensors Scanner", end='')
        for i in range(3):
            print(".",end='')
            time.sleep(0.25)
        print("\n")
        time.sleep(0.4)
        # I2C setup on bus 1
        self.i2c = board.I2C()
        # We are going to use TCA9548A, which is multiplexer
        self.tca = adafruit_tca9548a.TCA9548A(self.i2c)
        # We initialize the dictionary "contro_center" to save all data related to them.
        self.control_center = {
            "BME280_number" : 0,
            "MLX90614_number" : 0,
            "SHT31_number" : 0,
            "BME280" : [],
            "MLX90614" : [],
            "SHT31" : [],
        }
        number_BME280 = 1
        number_SHT31= 1
        number_MLX= 1
        # We have 8 channels or ports.
        for channel in range(8):
             # "attempts" to check if there are sensors connected to a channel, 5 for each channel.
             # After it is added one sensor, no more are accepted with the same address, because we are going to save the same sensor again.
            added_BME280 = [False, False] # We have two addressess for this sensor.
            added_SHT31 = [False, False] # We have two addresses for this sensor
            added_MLX = False
            attempts = 3
            for attempt in range(attempts):
                try:
                    if self.tca[channel].try_lock():
                        addresses = self.tca[channel].scan()
                   
                    #After it is scanned we are going to unlock it again, to let communation flow later
                    self.tca[channel].unlock()
                    try:
                        # We have different addresses according to the sensor.
                        for address in addresses:
                            if hex(address) == hex(0x76) and not added_BME280[0]:
                                added_BME280[0] = True
                                virtual_sensor = BME280(self.tca,channel,address)
                                self.virtual_sensor_creation(virtual_sensor,channel,number_BME280)
                                number_BME280 = number_BME280+1
                                
                            elif hex(address) == hex(0x77) and not added_BME280[1]:
                                added_BME280[1] = True
                                virtual_sensor = BME280(self.tca,channel,address)
                                self.virtual_sensor_creation(virtual_sensor,channel,number_BME280)
                                number_BME280 += number_BME280+1

                            elif hex(address) == hex(0x44) and not added_SHT31[0]:
                                added_SHT31[0] = True
                                virtual_sensor = SHT31(self.tca,channel,address)
                                self.virtual_sensor_creation(virtual_sensor,channel,number_SHT31)
                                number_SHT31 = number_SHT31+1

                            elif hex(address) == hex(0x45) and not added_SHT31[1]:
                                added_SHT31[1] = True
                                virtual_sensor = SHT31(self.tca,channel,address)
                                self.virtual_sensor_creation(virtual_sensor,channel,number_SHT31)
                                number_SHT31 = number_SHT31+1

                            elif hex(address) == hex(0x5A) and not added_MLX:
                                added_MLX = True
                                virtual_sensor = MLX(self.tca,channel,address)
                                self.virtual_sensor_creation(virtual_sensor,channel,number_MLX)
                                number_MLX = number_MLX+1

                    except Exception as e:
                        print(f"Error in Port: {channel+1} : {e}")
                except OSError as e:
                    print(f"Aborting, there are torn wires or desconected, (check power wires) ")
                    time.sleep(2)
                    self.cleanAndExit()
                    
        self.remove_sensors()
    
    def virtual_sensor_creation(self,virtual_sensor,channel,number):
        virtual_sensor.set_port(channel+1)
        
        virtual_sensor.set_number(number)
        
        self.add_sensors(virtual_sensor)

    def add_sensors(self,virtual_sensor):
        self.control_center[virtual_sensor.type+"_number"] += 1
        self.control_center[virtual_sensor.type].append(virtual_sensor)

    def remove_sensors(self):
        inter_var = self.connected_sensors.copy()
        
        for type in inter_var:
            if self.control_center[type+'_number'] > 0:
                print(f"{self.control_center[type+'_number']} " + type + ' connected')
            else:
                # Removing the non connected sensors. Then, all the sensors' names that are in "self.sensors_name" array there are ones in deed.
                del self.connected_sensors[self.connected_sensors.index(type)]
            
            time.sleep(2)
            

    def set_full_path_file(self,path):
        self.full_path_file = path

    def file_detection(self,replica_number):
        # Here you should modify it depending of the directory.
        try:
            self.set_full_path_file(self.path + self.slash + self.file_name)
            
            with FileManager(self.full_path_file).detect() as file:
                file.write(self.header+'\n')
                print(f"Header = {self.header}")
                print("Successfully created!!")
                with FileManager(self.init_path).over_write() as init_file:
                    init_file.write(self.path+'\n')
                    init_file.write(self.file_name)
        except Exception:
            index = self.file_name.rfind("_")
            self.index_real = self.file_name.rfind(".")
            self.real_file_name = self.file_name[:self.index_real]
            if index != -1:
                # The name will be from tha beging until "." position.
                self.file_name_w = self.file_name[:index]
                self.len_real_file_name = len(self.real_file_name)
                try:
                    int(self.file_name[index+1:self.len_real_file_name])
                    if not self.first_check:
                        self.first_check = True
                        self.file_name = self.file_name_w+self.extension
                        self.file_detection(replica_number)
                        return
                    
                    self.file_name = self.file_name_w+'_'+str(replica_number)+self.extension
                except ValueError:
                    # If there's an error means that it is the first copy will be made,
                    # Then, we are going to need an underscore.
                    self.file_name = self.real_file_name+'_'+str(replica_number)+self.extension
            else:
                self.file_name = self.real_file_name+'_'+str(replica_number)+self.extension
            
            replica_number = replica_number +1
            self.file_detection(replica_number)

    def create_header(self):
        # At least there will be one sensor for that reason, the '0'
         # All the sensors listed under, they EXIST.
        header = ''
        
        for type in self.connected_sensors:
            
            
            for virtual_sensor in self.control_center[type]:
                for property in virtual_sensor.get_properties():
                    header = header+',' + virtual_sensor.get_name()+'_'+property
                    
        self.header = self.header+header 
        

    def print_values(self,data_type):
        print(f"---------------{data_type}-------------------------")
        for connected_sensor in self.connected_sensors:
            properties = self.control_center[connected_sensor][0].get_properties()
            for property in properties:
                values = []
                print(f"{connected_sensor+'_'+property}: ",end='')
                virtual_sensors= self.control_center[connected_sensor]
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
        sys.exit()

    def data_operation(self):
        # Maybe here we can add a clock to see the differences between sensors' time.
        for type in self.connected_sensors:
            for virtual_sensor in self.control_center[type]:
                try:
                    self.avg_exception = False
                    virtual_sensor.trigger()
                    time.sleep(0.1)
                    self.add_avg_data(virtual_sensor)
                except Exception:
                    self.avg_exception = True
                    print("There's a problem with the sensor: {} ".format(virtual_sensor.name))
                    self.add_avg_data(virtual_sensor)
                finally:
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
        for type in self.connected_sensors:
            for virtual_sensor in self.control_center[type]:
                properties = virtual_sensor.get_properties()
                prop = properties[0]
                # If one average value doesn't work, none of the others work. They are not useful.
                normal_op = np.nansum(np.invert(np.isnan(virtual_sensor.avg_prop[prop])))>= self.minimum_sample
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
        with FileManager(self.full_path_file).append() as xfile:
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
                        for i in range(5):
                            print(".",end="")
                            time.sleep(0.2)
                        print()
                        print("---------------------------------\n")
                    
    def join_fun(self):
        self.results_avg = []
        i=0
        for connected_sensor in self.connected_sensors:
            for virtual_sensor in self.control_center[connected_sensor]:
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
    def __init__(self,sensor,type):
        self.sensor = sensor
        self.type = type
        self.port = None
        self.number = None
        self.name = self.type + '_' + str(self.port) + '_' + str(self.number)
        self.all_properties_values = []
        self.all_properties_names = []
        self.all_set_fun = []
        self.attempts_trigger = 0
    
    def get_name(self):
        self.name = self.get_type() + '_' + str(self.get_port())+ '_' + str(self.number)
        return self.name
    
    def get_number(self):
        return self.number
    
    def set_number(self,number):
        self.number = number
    
    
    def get_port(self):
        return self.port
    
    def set_port(self,port):
        self.port = port
    
    def get_sensor(self):
        return self.sensor
    
    def set_sensor(self,sensor):
        self.sensor = sensor
    
    def get_type(self):
        return self.type
    
    def trigger(self):
        self.all_properties_values = []
        for set_fun in self.all_set_fun:
            #We are going to round it to round it to two places
            self.all_properties_values.append(float(round(set_fun(),2)))
            
            
        if (np.isnan(self.all_properties_values).any()):
            if self.attempts_trigger == 10:
                self.set_all(np.nan)
                raise Exception
                return
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
        
class BME280(Sensor):
    def __init__(self,tca,channel,address):
        super().__init__(adafruit_bme280.Adafruit_BME280_I2C(tca[channel],address),'BME280')
        self.avg_prop = {
            'T' : [],
            'RH' : [],
            'P' : []
        }
        
        self.set_properties_names(['T','RH','P'])
        self.set_fun([self.set_T,self.set_RH,self.set_P])

    def set_T (self,*value):
        if len(value) == 0:
            temp = self.get_real_sensor().temperature
        else:
            temp = value
        return temp
        
    def set_RH(self,*value):
        if len(value) == 0:
            humidity = self.get_real_sensor().humidity
        else:
            humidity = value
        return humidity
        
    def set_P(self,*value):
        if len(value) == 0:
            pressure = self.get_real_sensor().pressure
        else:
            pressure = value
        return pressure

class SHT31(Sensor):
    def __init__(self,tca,channel,address):
        super().__init__(SHT31D(tca[channel],address),'SHT31')
        self.avg_prop = {
            'T' : [],
            'RH' : [],
        }
        self.set_properties_names(['T','RH'])
        self.set_fun([self.set_T,self.set_RH])

    def set_heater(self,heater_command):
        self.sensor.heater = heater_command

    def set_T (self,*value):
        if len(value) == 0:
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

class MLX(Sensor):
    def __init__(self,tca,channel,address):
        super().__init__(MLX90614(tca[channel],address),'MLX90614')
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

class FileManager(object):
    def __init__(self, file_whole_path):
        self.file_whole_path = file_whole_path
        

    def append(self):
        self.file = open(self.file_whole_path, 'a')
        return self.file
    
    def read(self):
        self.file = open(self.file_whole_path,'r+')
        return self.file

    def over_write(self):
        self.file = open(self.file_whole_path,'w+')
        return self.file

    def detect(self):
        self.file = open(self.file_whole_path,'x')
        return self.file

    def __exit__(self, *args):
        self.file.close()


if __name__ == "__main__":
    try:
        # Reset the sensors power.
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(16,GPIO.OUT)
        GPIO.output(16,False)
        time.sleep(0.1)
        GPIO.output(16,True)
        dog_watcher = Dog_Watcher()
        #dog_watcher.init()
        dog_watcher.setup()
        dog_watcher.save_data()
            
    except KeyboardInterrupt:
        print("Exiting...")
        GPIO.cleanup()
    
        