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
        for set_fun in self.all_set_fun:
            #We are going to round it to round it to two places
            self.all_properties_values.append(round(set_fun(),2)) 
            
        if (np.isnan(self.all_properties_values).any()):
            if self.attempts_trigger == 10:
                raise Exception
            self.attempts_trigger += self.attempts_trigger
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
        super().__init__('Hey','BME280')
        self.avg_prop = {
            'T' : [],
            'RH' : [],
            'P' : []
        }
        
        self.set_properties_names(['T','RH','P'])
        self.set_fun([self.set_T,self.set_RH,self.set_P])

    def set_T (self,*value):
        if len(value) == 0:
            temp = 2
        else:
            temp = value
        return temp
        
    def set_RH(self,*value):
        if len(value) == 0:
            humidity = 20
        else:
            humidity = value
        return humidity
        
    def set_P(self,*value):
        if len(value) == 0:
            pressure = 300
        else:
            pressure = value
        return pressure
