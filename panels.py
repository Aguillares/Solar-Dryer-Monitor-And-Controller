import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from ttkbootstrap.scrolled import ScrolledFrame
import ttkbootstrap as ttk
import tkinter as tk
import numpy as np
from settings import *
import platform

class ChartsWindow(ttk.Toplevel):
    "It is the window that holds every widget"
    def __init__(self):
        # We have started the theme.
        # super().__init__(themename=THEME_NAME)
        super().__init__()
        self.title("Charts Window")
        # We have the screen dimensions to set the window dimensions.
        screen_height = self.winfo_screenheight()
        screen_width = self.winfo_screenwidth()
        # Window dimensions.
        win_height = screen_height*0.5
        win_width = screen_width*0.45
        # Window position
        win_x = screen_width/2 - win_width/2
        win_y = screen_height/2 - win_height/2
        # Window geometry
        self.geometry(f'{win_width:.0f}x{win_height:.0f}+{win_x:.0f}+{win_y:.0f}')
        # Window minimum size.
        self.minsize(f'{win_width*0.8:.0f}',f'{win_height*0.8:.0f}')
        self.sensors_metadata = {
            'T':[('BME280',3),('SHT31',3),('BME680',2),('SHT45',5)],
            'RH':[('BME280',3),('SHT31',3),('BME680',2),('SHT45',5)],
            'P':[('BME280',3),('BME680',2)]
        }
        GeneralContainer(self).pack(expand = True,fill = 'both')

class GeneralContainer(ttk.Frame):
    '''
    The GeneralContainer has all widgets of the window.
    '''
    def __init__(self,parent):
        # The charts_window is the parent.
        self.charts_window = parent
        super().__init__(parent)
        # We get the number of plots 
        number_plots = len(parent.sensors_metadata)
        # The variables keys.
        var_keys = parent.sensors_metadata.keys()
        # The first part of tuple says in which row will be set.
        # We have plots' number and keys' name.
        sensors_num_var = tuple(row for row in zip(range(number_plots),var_keys))
        # We get the index, it tells where it can be put. We establish rows and columns.
        self.grid_rowconfigure(list(range(number_plots)), weight = 1, uniform='a')
        self.grid_columnconfigure(0,weight = 7,uniform='b')
        self.grid_columnconfigure(1,weight = 3,uniform='b')
        
        for ind,key in sensors_num_var:
            # PanelData is where the meters will be put.
            self.panel_data=PanelData(self,key)
            self.panel_data.grid(row=ind,column=1,sticky='nsew')
            # PanelPlot is where the graphs are being plotted.
            PanelPlot(self).grid(row=ind,column=0,sticky='nswe')

class MeterVar(ttk.Meter):
    def __init__(self, parent,metertype,metersize,subtext,amountused,bootstyle):
        super().__init__(
            parent,
            metertype = metertype,
            metersize = metersize,
            subtext = subtext,
            amountused = amountused,
            bootstyle = bootstyle)

class ScrollbarFrame(ttk.Frame):
    '''
    The ScrollbarFrame is the father class.
    '''
    def __init__(self,parent:ttk.Frame):
        # We inherit all Frame's properties and behaviours 
        super().__init__(master = parent)
        # We create a canvas, it can be either horizontal or vertical.
        self.canvas  = ttk.Canvas(self)
        # We need to detect the system type to know which combination of keys to use for "bind" method.
        self.system = platform.system()
        # It can be either "horizontal" or "vertical"
        self.orientation = {
            'x':('horizontal',self.canvas.xview),
            'y':('vertical',self.canvas.yview)
        }
        # The prefix_view_scroll is a dictionary that uses the prefix of the binding sequences in the
        # scrollbars.
        self.prefix_view_scroll = {
            '':self.canvas.yview_scroll,
            'Shift-':self.canvas.xview_scroll
        }
        # The orientation at the beginning is empty.
        self.orient = ''

    def header_config(self,CONST_FONT:tuple[str,str,int],CONST_COLOR:str,title_:str)->None:
        '''
        It configures title's font, background and the text.
        '''
        # We need to set the title's background, we use a label for it. The "place" method is used inasmuch as
        # it can be overrided by the next widget. Even we don't use any word here, we should use the same font
        # in the label background and the label title, to have the same height between both.
        # The explanation why we don't use fill with the label title, it is because we want the title to be centered.
        font_ =  ttk.font.Font(name=CONST_FONT[0],
                               family = CONST_FONT[1],
                               size = CONST_FONT[2])
        self.title = ttk.Label(self, font = font_, background=CONST_COLOR)
        self.title.place(x = 0,y = 0,relwidth = 1,anchor = 'nw')
        ttk.Label(self, font = font_, background = CONST_COLOR, text = title_).pack()

        # We give the orientation (vertical or horizontal)
    def create_scrollbar(self,orient:dict[str,(str,callable)])->None:
        '''
        A scrollbar is created using PLACE method.
        '''
        # We use the dictionary "self.orientation" 
        self.scrollbar = ttk.Scrollbar(self, orient=self.orientation[orient][0], command = self.orientation[orient][1],name=orient)
        self.scrollbar.place(x=0,rely=1,anchor='sw',relwidth=1)
        # We set the (x/y)scrollcommand with the "scrollbar.set" method.
        self.canvas.config({orient+'scrollcommand':self.scrollbar.set})

    def disable_scroll_all(self,event:tk.Event,prefix:str)->None:
        '''
        Scrollbar is disabled depending on the operative system.
        '''
        # For Windows or MacOs, we use the MouseWheel event.
        # For Linux Operative Systems, Buttons 4 and 5 are used.
        if self.system == "Windows" or self.system == 'Darwin':
            self.canvas.unbind_all('<'+prefix+'MouseWheel>')
        else:
            self.canvas.unbind_all('<'+prefix+'Button-4>')
            self.canvas.unbind_all('<'+prefix+'Button-5>')
        
    def enable_scroll_all(self,event:tk.Event,prefix:str)->None:
        '''
        Enable scrolling for the next operative systems:
        1. Windows.
        2. MacOs.
        3. Linux.
        Linux uses Buttons EVENTS meanwhile the others use MouseWheel EVENT
        '''
        # We determine canva's height and is compared with the current window height
        if self.vertical_threshold > self.winfo_height():
            # If the OS is either Windows or Darwin, we use MouseWheel EVENT
            # Otherwise, Buttons are used (Linux)
            if self.system == "Windows":
                self.canvas.bind_all('<'+prefix+'MouseWheel>',lambda event: self.prefix_view_scroll[prefix](-int(event.delta/MOUSE_SPEED_WIN),'units'))
            else :
                self.canvas.bind_all('<'+prefix+'Button-4>',lambda event: self.prefix_view_scroll[prefix](-MOUSE_SPEED_LNX,'units'))
                self.canvas.bind_all('<'+prefix+'Button-5>',lambda event: self.prefix_view_scroll[prefix](MOUSE_SPEED_LNX,'units'))
        # This "else" is interesting because if we have the window higher than the original canvas height
        # we disable the scrollbar.
        else:
            self.disable_scroll_all(event,prefix)
        
class PanelData(ScrollbarFrame):
    '''
    PanelData holds all the widgets that are inside it.
    '''
    # parent: GeneralContainer
    # dict_: Sensors' information.
    # var: Variable name (BME280, SHT31,...)
    def __init__(self, parent, var)->None:
        # "general_container" attribute contains the "GeneralContainer" object.
        self.general_container = parent
        # Variable
        self.var = var
        # Inheritance.
        super().__init__(parent = parent)
        # We set header's properties.
        self.header_config(TITLE_VAR_FONT, COLOR_TITLE_BG[var], SHORTCUT_VARS[var])
        # We get all metadata from chart_window object.
        sensors_metadata = self.general_container.charts_window.sensors_metadata[var]
        # The number of columns is related to sensors type's number
        self.number_col= len(sensors_metadata)
        # We get the maximum sensors number, the name is ignored.
        self.max_num_widgets = max(number for _,number in sensors_metadata)
        # The meter corrected, the delta added.
        # With the meter corrected we can make the canvas dimensions.
        # Canvas just holds the meter widgets.
        # Remember this clases, inherits all properties from ScrollbarFrame,
        # so, it has one canvas.
        self.canvas.pack(expand=True,fill='both')
        # The horizontal scrollbar.
        self.create_scrollbar('x')
        # We pack the frame that will cover all the canvas.
        # Remember if you want allocate more widgets inside any canvas we must employ
        # a frame to allot all widgets.
        self.frame = ttk.Frame(self.canvas, name = 'panel_data')
        self.frame.pack(fill = 'both',expand = True)
        # sensor_name: Sensor name (BME280,SHT45,...)
        # sensor_number: The number of sensors of that type.
        self.bind('<Map>',lambda event: self.placement())
        
        for sensor_name,sensor_number in sensors_metadata:
            # The all MeasureContainers will be inside of self.frame of this Panel, and
            # the arrangement is one next to another, they are going to cover all the widgets.
            self.measure_cont=MeasureContainer(self,sensor_name,sensor_number)
            self.measure_cont.pack(side='left',expand=True,fill='both')
        
    def placement(self):
        meter_corrected = self.measure_cont.meter.winfo_reqwidth()
        # We get the horizontal canvas width, relying on the corrected width and columns' number
        hor_wid = meter_corrected*self.number_col
        # It is set the horizontal canvas.
        self.canvas.config(width = hor_wid ,height = meter_corrected*self.max_num_widgets,scrollregion = (0,0,hor_wid,0))
        # For some reason we need to create a new window every time we change the canvas size.
        self.canvas.create_window(
            (0,0),
            window = self.frame,
            anchor = 'nw',
            width = hor_wid,
            height = self.winfo_height(),
            tags='horizontal'
        )
        # We update the canvas to not disconfigure the dimensions of the widgets.
        # Every time we make a modification size in the frame we change canvas size.
        self.bind('<Configure>',self.update_canvas)
        self.horizontal_threshold = self.canvas.winfo_reqwidth()
        self.vertical_threshold = self.canvas.winfo_reqheight()
        self.update_canvas()

    def update_canvas(self,*events):
        '''
        The canvas is updated.
        '''
        current_width_window=self.winfo_width()
        if self.horizontal_threshold>current_width_window :
            # As the horizantal side is bigger than the part that is seen, we continue
            # using the width of the whole canvas.
            current_width = self.horizontal_threshold
            self.scrollbar.place(x=0,rely=1,anchor='sw',relwidth=1)
            # If the pointer enters in the Canvas, the scrollbar is enabled.
            self.canvas.bind('<Enter>',lambda event: self.enable_scroll_all(event,prefix='Shift-'))
            # But disabled when it goes out.
            self.canvas.bind('<Leave>',lambda event: self.disable_scroll_all(event,prefix='Shift-'))
        else:
            # If it is the opposite, it means that the canvas that is shown in the window is bigger than
            # the actual canvas size, which means we need to update canvas to the new size.
            current_width = current_width_window
            # The scrollbar is not longer needed.
            self.scrollbar.place_forget()
            self.canvas.unbind('<Enter>')
            self.canvas.unbind('<Leave>')

        self.canvas.itemconfig('horizontal',
                               width = current_width,
                               height = self.winfo_height()
                               )

class MeasureContainer(ScrollbarFrame):
    '''
    All meter widgets are contained here.
    '''
    def __init__(self,panel_data:PanelData,sensor_name:str,sensor_number:int)->None:
        # "panel_data" is the PanelData object of the previous one.
        self.panel_data = panel_data
        # We get sensor's name
        self.sensor_name = sensor_name
        # All meters will have a size of 100 per side.
        self.meter_w_h = 100
        # In this case the parent is the canvas.
        super().__init__(panel_data.frame)
        # Font for sensors' name.
        self.header_config(SENSOR_NAME_FONT,"",sensor_name)
        # This frame is used to put things inside the canvas.
        self.frame = ttk.Frame(self.canvas)
        
        for number in range(sensor_number):
            # All meters are set according to their numbers.
            self.meter = ttk.Meter(self.frame,
                                 metertype = 'semi',
                                 metersize = self.meter_w_h,
                                 subtext = 'S'+str(number),
                                 amountused = 50,
                                 bootstyle = COLOR_VAR_METERS[self.panel_data.var])
            if self.system == 'Windows' or self.system == 'Darwin':
                pass
            else:
                self.meter.subtext.place(relx=0.5,rely=0.8,anchor=tk.N)
            self.meter
            self.meter.pack()
        # If it is mapped, canvas_config is triggered, with sensor_number
        self.canvas.bind('<Map>', lambda ev: self.canvas_config(sensor_number))
        self.canvas.pack(expand = True, fill = 'both')
        
    def canvas_config(self,sensor_number:int)->None:
        '''
        The MeasureContainer canvas is set
        '''
        # With the last meter we get its reqwidth
        self.meter_corrected = self.meter.winfo_reqwidth()
        # We get the height
        self.height_canvas = self.meter_corrected*sensor_number
        # We set up canvas' parameters.
        self.canvas.config(
            width = self.meter_corrected,
            height = self.height_canvas
        )
        # We establish updating size automatically everytime the frame size is changed.
        self.bind('<Configure>',self.update_size)
        # The whole scroll height is the canvas height, the panel data height and the title's height.
        self.scroll_height = self.height_canvas + self.panel_data.scrollbar.winfo_reqheight()+self.title.winfo_reqheight()
        # Even if we pulled all the scroll height, all widgets will be seen.
        # The threshold should include the panel data's height
        self.vertical_threshold = self.scroll_height + self.panel_data.title.winfo_reqheight()
        self.canvas.config(scrollregion =(0,0,0,self.scroll_height))
        # The window created is the frame with the same height as the canvas.
        self.id_meter_set = self.canvas.create_window(
            (0,0),
            window = self.frame,
            anchor = 'nw',
            width = self.winfo_width(),
            height = self.height_canvas
            )
        
        # Enabling and disabling scrolls.
        self.canvas.bind('<Enter>',lambda event: self.enable_scroll_all(event, prefix=''))
        self.canvas.bind('<Leave>',lambda event: self.disable_scroll_all(event, prefix=''))

    def update_size(self,*event:tk.Event):
        "The canvas window object is redimensioned according to the window's size"
        current_height=max(self.vertical_threshold,self.winfo_height())
        self.canvas.itemconfig(self.id_meter_set,
                               width = self.winfo_width(),
                               height = current_height)
        self.canvas.update_idletasks()

class PanelPlot(ttk.Frame):
    def __init__(self,parent:GeneralContainer)->None:
        super().__init__(master = parent)
        # (Name of the sensor type , sensors' number)
        self.plot=Plot(self)
        # self.plot.patch.set_facecolor(color)
        # self.plot.tk_canvas.configure(height=70)
        self.plot.tk_canvas.pack(expand=True,fill='both')
        self.plot.toolbar.pack(expand=True,fill='both')

class Plot(Figure):
    def __init__(self,parent):
        fac_dpi = 100
        super().__init__(figsize=(parent.winfo_width()/fac_dpi,
        parent.winfo_height()/fac_dpi),
        dpi=fac_dpi)
        canvas = FigureCanvasTkAgg(self,master=parent)
        canvas.draw()
        canvas.mpl_connect("key_press_event", key_press_handler)
        self.tk_canvas=canvas.get_tk_widget()
        self.toolbar = NavigationToolbar2Tk(canvas,parent,pack_toolbar=False)
        
if __name__ == '__main__':
    ChartsWindow().mainloop()