import asyncio
from adafruit_mlx90614 import MLX90614 as mlx90614
from adafruit_bme280 import basic as adafruit_bme280
from adafruit_sht31d import SHT31D as sht31d
import adafruit_tca9548a
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
    def __init__(self,tca:tca9548a,port:int,number:int,address:int)        super().__init__(sht31d(tca[port],address),'SHT31',port,number,address)
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
