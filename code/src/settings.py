''' -*-*-*-*-*-*-* Settings -*-*-*-*-*-*-* ''' 

# -> Theme <-
THEME_NAME = "solar_dryer"

# -> Ranges <-
HOUR_RANGE = [str(x) for x in range(24)]
SHORT_MIN_RANGE = [str(x) for x in range(6)]
FULL_MIN_RANGE = [str(x) for x in range(60)]
SEC_RANGE = [str(x) for x in range(60)]

# Addresses
NAME = {
    0x44 : "SHT31",
    0x45 : "SHT31",
    0x5A : "MLX90614",
    0x76 : "BME280",
    0x77 : "BME280"
}

# -> COLORS <-
COLOR_VAR_METERS = {
    'T': 'danger', 
    'RH': 'primary',
    'P': 'light'
}

COLOR_TITLE_BG = {
    'T': '#E74C3C', 
    'RH': '#1C189E',
    'P': '#ADB5BD'
}

COLORS_HEX = {
    'success': '#1BBF82',
    'danger': '#D9534F'
}


# -> Mouse's settings <-
MOUSE_SPEED_WIN = 120
MOUSE_SPEED_LNX = 1


# -> Fonts <-
TITLE_VAR_FONT = ('Title',"Times New Roman",15)
SENSOR_NAME_FONT = ("Sensors_Name","Comic Sans MS",12)


# -> Settings in widgets <-
DATA_TRIGGER_SECTION = {'texts': ('Start', 'Time', 'Stop'),
                        'options': (('Start Now','Set Start'),('Trigger','Avg. Trigger'),('Stop','Set Stop')),
                        'background': ("#00422A","#8D8D8D","#5B2220"),
                        'style': ('success','','danger'),
                        'font':("Comic Sans MS bold",15),
                        'column':(0,1,2)}

TRIGGER_TIME = {'text': 'Data Trigger',
                'anchor' : 'Center',
                'foreground': 'white',
                'justify': 'right',
                'background': '', 
                'font': ("Comic Sans MS bold",16)
                }

BUTTONS_INFO = (
    [('Fruit\nTemperature',(0,0),'hot-and-cold.png'), 
     ('Environmental\nVariables',(0,1),'filter.png'),
     ('Fruit Weight',(1,0),'weight-scale.png'),
     ('Psychometric \nChart',(1,1),'graphical-presentation.png')]
     )


# -> Pattern <-
PATTERN_TRIGGER = {
    # (Pattern,length)
    'hour': ('^([0-1]?[0-9]?)$|(^2[0-3]$)'),
    'minute_trigger': ('^[0-5]?$'),
    'minute': ('^[1-5]?[0-9]?$'),
    'second': ('^[1-5]?[0-9]?$')
}


# -> Abbreviations <-
ABBR_TIME = {
    "hour": 'h',
    "minute": 'min',
    "second": 's'
}

SHORTCUT_VARS = {
    'T': 'Temperature',
    'RH': 'Relative Humidity',
    'P': 'Pressure'
}
