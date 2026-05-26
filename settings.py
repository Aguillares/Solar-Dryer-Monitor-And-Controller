''' -*-*-*-*-*-*-* Settings -*-*-*-*-*-*-* ''' 
import tkinter as tk

# -> Theme <-
THEME_NAME = "solar_dryer"

# -> Ranges <-
HOUR_RANGE = [str(x) for x in range(24)]
SHORT_MIN_RANGE = [str(x) for x in range(6)]
FULL_MIN_RANGE = [str(x) for x in range(60)]
SEC_RANGE = [str(x) for x in range(60)]


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

<<<<<<< HEAD
MOUSE_SPEED_WIN = 120
MOUSE_SPEED_LNX = 1
# -> Fonts
TITLE_VAR_FONT = ('Title',"Times New Roman",15)
SENSOR_NAME_FONT = ("Sensors_Name","Comic Sans MS",12)

# -> Theme
THEME_NAME = "solar_dryer"
=======
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
DATA_TRIGGER_SECTION = {'texts': ('Start','Time', 'Stop'),
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
    [('Fruit\nTemperature',(0,0),r'Icons\hot-and-cold.png'), 
     ('Environmental\nVariables',(0,1),r'Icons\filter.png'),
     ('Fruit Weight',(1,0),r'Icons\weight-scale.png'),
     ('Psychometric \nChart',(1,1),r'Icons\graphical-presentation.png')]
     )


# -> Pattern <-
PATTERN_TRIGGER = {
    # (Pattern,length)
    'hour': ('^([0-1]?[0-9]?)$|(^2[0-3]$)',2),
    'minute_trigger': ('^[0-5]?$',1),
    'minute': ('^[1-5]?[0-9]?$',2),
    'second': ('^[1-5]?[0-9]?$',2 )
}


# -> Abbreviations <-
ABBR_TIME = {
    "hour": 'h',
    "minute": 'min',
    "second": 's'
}
>>>>>>> tester

SHORTCUT_VARS = {
    'T': 'Temperature',
    'RH': 'Relative Humidity',
    'P': 'Pressure'
}