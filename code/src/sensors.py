from settings import SENSORS_NAMES
from adafruit_mlx90614 import MLX90614 as mlx90614
from adafruit_bme280 import basic as adafruit_bme280
from adafruit_sht31d import SHT31D as sht31d
import adafruit_tca9548a
import os
import time
# We need to simplify the notation
from typing import TypeAlias
from typing import TypeVar
tca9548a : TypeAlias = adafruit_tca9548a.TCA9548A
bme280 : TypeAlias = adafruit_bme280.Adafruit_BME280_I2C

class Sensor():
    """
    General class for any sensor
    
    ...
    
    Attributes
    ----------
    sensor : Bme280|sht31d
        The sensors that take temperature and relative humidity
    type_ : str
        The supported types, BME280 and SHT31
    port : int
        The port where it is connected
    number : int
        The number of sensor: 0, 1, 2, ...
    address : int 
        The address that the sensor has
    name : str
        The name given to the sensor with the format
        "typeOfSensor_Port_Number
    all_properties_values : dict[str:float]
        All the names of the properties such as Temperature, Relative Humidity, Pressure, ...
    all_set_fun : list[Callable]
        All the functions that trigger the sensors
    self.attempts_trigger : int
        The number of attempts in trying to trigger the sensors,
        after reaching the maximum, the program is shut down
               
    Methods
    -------
    set_all(value : float|nan)
        Sets a specific value for each sensor, mimicking when the sensors are triggered
    """
    def __init__(self,sensor:bme280|sht31d,type_:str, port:int, number:int,address:int):
        """
        Parameters
        ----------
        sensor : bme280|sht31d
            The sensors that take temperature and relative humidity
        type_ : str
            The supported types, BME280 and SHT31
        port : int
            The port where it is connected
        number : int
            The number of sensor: 0, 1, 2, ...
        address : int 
            The address that the sensor has
        
        """
        self.sensor = sensor
        self.type = type_
        self.port = port
        self.number = number
        self.address = address
        self.name = self.type + '_' + str(self.port) + '_' + str(self.number)
        self.all_properties_values = dict()
        self.dic ={'p':2}
        self.all_set_fun = []
        self.attempts_trigger = 0
    
    def set_all(self,value):
        """Sets a specific value for each sensor, mimicking when the sensors are triggered"""
        for set_fun in self.all_set_fun:
            set_fun(value)

    async def trigger_all_set_fun(self):
        """triggers all set functions of the sensor"""
        for set_fun in self.all_set_fun:
            set_fun()

class T_RH_Sensor(Sensor):
    """It encompasses both, the BME280 and SHT31 or whichever other sensor that 
        supports temperature and relative humidity."""
    
    def __init__(self,sensor:bme280|sht31d,type_: str, port:int, number:int,address:int):
        """
        Parameters
        ----------
        sensor : Bme280|sht31d
            The sensors that take temperature and relative humidity
        type_ : str
            The supported types, BME280 and SHT31
        port : int
            The port where it is connected
        number : int
            The number of sensor: 0, 1, 2, ...
        address : int 
            The address that the sensor has"""
        super().__init__(sensor,type_,port,number,address)

        self.avg_prop = {
            'T' : [],
            'RH' : [],
        }

    def set_T (self,value = None):
        """Sets the temperature whether 'value' is given
        
        If the argument value is not given, the sensor takes data.

        Parameter 
        ---------
        value : float, optional
            The current temperature (default None)
        """

        self.all_properties_values['T']=round(self.sensor.temperature,2)
        self.avg_prop['T'].append(self.all_properties_values['T'])
        
            
    def set_RH(self,value = None):
        """Sets the relative humidity whether 'value' is given
                    
            If the argument value is not given, the sensor takes data.

            Parameter 
            ---------
            value : float, optional
                The current relative humidity (default None)
        """
        self.all_properties_values['RH'] = round(self.sensor.relative_humidity,2)
        self.avg_prop['RH'].append(self.all_properties_values['RH'])
        

class BME280(T_RH_Sensor):
    """Sensor BME280 detects Temperature, Relative Humidity and Pressure"""
    def __init__(self,tca:tca9548a,port:int,number:int,address:int) -> None:
        """
            Parameters
            ----------
            tca : Tca9548a
                The multiplexer object that let connect different sensors with the same
                address in the same microntroller
            port : int
                The port where it is connected
            number : int
                The number of the sensor: 0, 1, 2, ...
            address : int 
                The address that the sensor has"""
        super().__init__(adafruit_bme280.Adafruit_BME280_I2C(tca[port],address),'BME280',port,number,address)
        # It is the property that SHT31 doesn´t have.
        self.avg_prop['P'] = []
        
        self.all_properties_values={
            'T':0,
            'RH':0,
            'P':0}
        self.all_set_fun=[self.set_T,self.set_RH,self.set_P]

    def set_P(self,value=None):
        """Retrieves pressure 

        If the argument value is not given, the sensor takes data.

        Parameter 
        ---------
        value : float, optional
            The current relative humidity (default None)
        """
        self.all_properties_values['P'] = round(self.sensor.pressure,2)
        self.avg_prop['P'].append(self.all_properties_values['P'])
        

class SHT31(T_RH_Sensor):
    def __init__(self,tca:tca9548a,port:int,number:int,address:int):
        super().__init__(sht31d(tca[port],address),'SHT31',port,number,address)
        self.all_properties_values={'T':0,'RH':0}
        self.all_set_fun=[self.set_T,self.set_RH]

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
        self.all_properties_values = {'amb_T':0,'obj_T':0}
        self.all_set_fun =[self.set_amb_T,self.set_obj_T]

    async def set_amb_T (self,*value):
        if len(value) == 0:
            amb_T = self.sensor.ambient_temperature
        else:
            amb_T = value
        return amb_T
        
    async def set_obj_T(self,*value):
        if len(value) == 0:
            obj_T = self.sensor.object_temperature
        else:
            obj_T = value
        return obj_T

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