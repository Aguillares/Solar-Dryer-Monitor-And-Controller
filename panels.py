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

# The GeneralContainer has all widgets in the window.
class GeneralContainer(ttk.Frame):
    def __init__(self,parent):
        self.charts_window = parent
        super().__init__(parent)
        # We get the number of plots 
        number_plots = len(parent.dict_measure)
        # We have the keys name with "keys()" method.
        get_keys = parent.dict_measure.keys()
        # The first part of tuple says in which row will be set.
        # We have plots' number and keys' name.
        tuple_ = tuple(row for row in zip(range(number_plots),get_keys))
        
        for ind,key in tuple_:
            # We create the panel where 
            PanelData(self,key).grid(row=ind,column=1,sticky='nsew')
            PanelPlot(self).grid(row=ind,column=0,sticky='nswe')
        # We get the index, it tells where it can be put.
        # We establish rows and columns.
        self.grid_rowconfigure(list(range(number_plots)), weight = 1, uniform='a')
        self.grid_columnconfigure(0,weight = 7,uniform='b')
        self.grid_columnconfigure(1,weight = 3,uniform='b')

class ScrollbarFrame(ttk.Frame):
    def __init__(self,parent):
        super().__init__(master=parent)
        # self.set_header_and_bg(TITLE_VAR_FONT)

    def set_header_and_bg(self,CONST_FONT,CONST_COLOR,title):
        
        font_ =  ttk.font.Font(name=CONST_FONT[0],
                               family = CONST_FONT[1],
                               size = CONST_FONT[2])
        ttk.Label(self, font = font_, background=CONST_COLOR).place(x = 0,
                                         y = 0,
                                         relwidth = 1,
                                         anchor = 'nw')
        ttk.Label(self, font = font_, background = CONST_COLOR, text = title).pack()
        

# PanelData holds all the widgets are inside it.
class PanelData(ScrollbarFrame):
    # parent: GeneralContainer
    # dict_: Sensors' information.
    # var: Variable name (BME280, SHT31,...)
    def __init__(self, parent,var):
        self.system = platform.system()
        self.general_container = parent
        # Heritage
        super().__init__(parent = parent)
        # We divide the panel for the canvas and the meters.
        # Font for the sensor's name.
        # Notice we use the constant TITLE_VAR_FONT.
        
        # We need to set the title's background, we use a label for it.
        # "place" method is used inasmuch as we can be overrided by the next widget.
        # Even we don't use any word here, we should use the same font
        # in the label background and the label title, to have the 
        # same width between both.
        # The explanation why we don't use fill with the label title
        # it is because we want the title to be centered.
        
        # Here it is the actual title.
        # To print the text we identify the variable with proper method.
        self.set_header_and_bg(TITLE_VAR_FONT,COLOR_TITLE_BG[var],self.identify_var(var))
        # Horizontal canvas used to get all meters widgets and its canvas,
        # it allows horizontal movement.
        self.hor_canvas = ttk.Canvas(self)
        dict_measure = self.general_container.charts_window.dict_measure[var]
        # The number of columns is related to sensors type' number
        number_col= len(dict_measure)
        # The maximum widgets number, it's the maximum sensors' number from all types.
        # At the beginning we have zero.
        self.max_num_widgets = 0
        # We are not interested in sensor's name, just its number.
        for _,number in dict_measure:
            # If the current number is greater to current maximum number, then
            # the current number is converted into the new maximum number.
            if number> self.max_num_widgets:
                self.max_num_widgets = number

        # We are going to give 100 of width for widget
        # There is a difference of 49 between the units of meter_size given, the one measured
        # It means we give 100 to meter's width, but when we measure it with the method
        # "winfo_reqwidth()", it tells 149. Then for each unit given to meter_size, we
        # have a delta of 0.49 more in the real width.
        # If we have then "x" units that we give to meter we get
        # 0.49*x more.
        # # The meter corrected, the delta added.
        # With the meter corrected we can make the canvas dimensions.
       
        # # Canvas just holds the meter widgets.
        # # self.hor_canvas should cover all the frame parent.
        self.hor_canvas.pack(expand=True,fill='both')
        # Every time we make a modification size in the frame we change canvas size.
        self.bind('<Configure>',self.update_canvas)
        # The horizontal scrollbar.
        self.hor_scrollbar = ttk.Scrollbar(self,orient='horizontal',command = self.hor_canvas.xview)
        self.hor_scrollbar.place(x=0,rely=1,anchor='sw',relwidth=1)
        self.hor_canvas.config(xscrollcommand = self.hor_scrollbar.set)
        # Every time we are in the specified widget, we want to activate the scroll motion
        # in that widget, and disable it in all the other widgets.
        # This is done with the "bind" property has already, that is if we don't use 
        # "add" parameter, the last widget that uses the "bind" method will maintain it;
        # and the other will forget it.
        self.bind('<Enter>',self.update_scroll)
        
        # ".winfo_reqwidth" -> is used to know the dimensions of the widget.
        # Meanwhile, we use ".winfo_width" -> for the widget but the part that is seen.
        # If you are going to move in one direction it is just necessary to specify clearly that dimension
        # the others can be subsitute with any number.
        self.hor_canvas.config(scrollregion=(0,0,self.hor_canvas.winfo_reqwidth(),0))
        self.hor_canvas.config(None)
        # We pack the frame that will conver all the canvas.
        # Remember if you want allocate more widgets inside any canvas we must employ
        # a frame to allot all widgets.
        self.frame_measure = ttk.Frame(self.hor_canvas)
        # sensor_name: Sensor name (BME280,SHT45,...)
        # sensor_number: The number of sensors of that type.
        # self.function(2)
        for sensor_name,sensor_number in dict_measure:
            # We all MeasureContainers will be inside of self.frame_measure, and
            # the arrangement is one next to another, they are going to cover all the widget.
            MeasureContainer(var,sensor_name,sensor_number,self.max_num_widgets,number_col,self.system,self).pack(side='left',expand=True,fill='both')
    
    
    def identify_var(self,variable):
        match variable:
            case "T":
                return 'Temperature'
            case "RH":
                return "Relative Humidity"
            case "P":
                return "Pressure"
    
    # up
    def update_scroll(self,ev)->None: 
        if self.hor_canvas.winfo_reqwidth() > self.winfo_width():
            if self.system == "Windows":
                self.hor_canvas.bind_all('<Shift-MouseWheel>',lambda ev:self.hor_canvas.xview_scroll(-int(ev.delta/MOUSE_SPEED_WIN),'units'))
            else:
                self.hor_canvas.bind_all('<Shift-Button-4>',lambda ev: self.hor_canvas.xview_scroll(-MOUSE_SPEED_LNX,'units'))
                self.hor_canvas.bind_all('<Shift-Button-5>',lambda ev: self.hor_canvas.xview_scroll(MOUSE_SPEED_LNX,'units'))
        else:
            # We deactivate the combitination of keys.
            self.hor_canvas.unbind_all('<Shift-MouseWheel>')
        self.hor_canvas.update_idletasks()
        

    def update_canvas(self,*ev):
            
            if self.hor_canvas.winfo_reqwidth()> self.winfo_width():
                # As the horizantal side is bigger than the part that is seen, we continue
                # using the width of the whole canvas.
                current_width = self.hor_canvas.winfo_reqwidth()
                # We bind the behavoir <Shift-MouseWheel> with the horizontal movement of 
                # the canvas.
                self.hor_scrollbar.place(x=0,rely=1,anchor='sw',relwidth=1)
            else:
                # If it is the opposite, it means that the canvas that is shown in the window is bigger than
                # the actual canvas size, which means we need to update canvas to the new size.
                current_width = self.winfo_width()
                # The scrollbar is not longer needed.
                self.hor_scrollbar.place_forget()
            
            self.hor_canvas.create_window(
                (0,0),
                window = self.frame_measure,
                anchor='nw',
                width=current_width,
                height=self.winfo_height()
            )
        
class MeasureContainer(ttk.Frame):
    def __init__(self,variable,sensor_name,sensor_number,max_num_widgets,number_col,system,panel_data):
        self.panel_data= panel_data
        self.system = system
        
        self.meter_w_h = 100
        # self.parent = parent
        # In this case the parent is the canvas.
        super().__init__(panel_data.frame_measure)

        # Font for sensors' name.
        font_ = ttk.font.Font(name=SENSOR_NAME_FONT[0],family=SENSOR_NAME_FONT[1],size=SENSOR_NAME_FONT[2])
        ttk.Label(self,font=font_).place(x=0,y=0,relwidth=1,anchor='nw')
        self.sensor_name_label=ttk.Label(self,text=str(sensor_name),font= font_)
        self.sensor_name_label.pack()

        self.canvas= tk.Canvas(self)
        # For some reason you need to use the "configure" method to make changes.
       
        # This frame is used to put things inside the canvas.
        self.frame = ttk.Frame(self.canvas)
        for number in range(sensor_number):
            self.meter=ttk.Meter(self.frame,
                                 metertype = 'semi',
                                 metersize = self.meter_w_h,
                                 subtext = 'S'+str(number),
                                 amountused = 50,
                                 bootstyle = COLOR_VAR_METERS[variable],
                                )
            self.meter.subtext.place(relx=0.5, rely=0.7, anchor=tk.N)
            self.meter.pack()
        
        self.bind('<Map>',lambda ev:self.canvas_config(max_num_widgets,number_col,sensor_number))
        # Creating a vertical scrollbar
        
        self.height = ttk.DoubleVar(self,value=0.913)
        self.scroll_bar = ttk.Scrollbar(self,orient='vertical',command = self.canvas.yview)
        
        self.canvas.config(yscrollcommand = self.scroll_bar.set)

        self.bind('<Enter>',self.update_scroll)
        self.bind('<Configure>',self.update_size)

    def delta_meter(self,meter):
        pass
        
    def canvas_config(self,max_num_widgets,number_col,sensor_number):
        print(self.meter.winfo_reqwidth())
        print(f"Maximum number of widgets INSIDE = {max_num_widgets}")
        delta =  (self.meter.winfo_reqwidth()-self.meter_w_h)/100*self.meter_w_h
        meter_corrected = self.meter_w_h+delta
        
        print(f"inside meter = {meter_corrected}")
        hor_wid=meter_corrected*number_col
        print(f"hor_wid = {hor_wid}")
        self.panel_data.hor_canvas.config(width = hor_wid ,height=meter_corrected*max_num_widgets,scrollregion=(0,0,hor_wid,0))
        self.panel_data.hor_canvas.pack(expand=True,fill='both')
        self.panel_data.update_canvas()

        self.height_canvas =meter_corrected*sensor_number
        # For some reason you need to use the "configure" method to make changes.
        self.canvas.config(
            width = meter_corrected,
            height = self.height_canvas,
        )
        self.canvas.pack(expand=True,fill='both')
        self.canvas.config(scrollregion = (0,0,meter_corrected,self.height_canvas+self.sensor_name_label.winfo_reqheight()))
        self.update_size()
        if self.meter.winfo_reqwidth()>1:
            self.unbind("<Map>")

    def update_scroll(self,ev):
        if self.canvas.winfo_reqheight() > self.winfo_height():
            if self.system == "Windows":
                self.canvas.bind_all('<MouseWheel>',lambda event: self.canvas.yview_scroll(-int(event.delta/MOUSE_SPEED_WIN),'units'))
            else :
                self.canvas.bind_all('<Button-4>',lambda event: self.canvas.yview_scroll(-MOUSE_SPEED_LNX,'units'))
                self.canvas.bind_all('<Button-5>',lambda event: self.canvas.yview_scroll(MOUSE_SPEED_LNX,'units'))
        else:
            self.canvas.unbind_all('<MouseWheel>')
    def printing(self,event):
        print(-int(event.delta/MOUSE_SPEED_WIN))
        print(event)

    def update_size(self,*event):

        if self.canvas.winfo_reqheight() > self.winfo_height():
            current_height = self.canvas.winfo_reqheight()
            # Setting canvas to respond according to the scrollbar through the frame.
        else:
            current_height = self.winfo_height()
        
        self.canvas.create_window(
            (0,0),
            window = self.frame,
            anchor = 'nw',
            width = self.winfo_width(),
            height = current_height
        )
        

class PanelPlot(ttk.Frame):
    def __init__(self,parent):
        super().__init__(master = parent)
        # (Name of the sensor type , sensors' number)
        self.plot=Plot(self)
        # self.plot.patch.set_facecolor(color)
        self.plot.tk_canvas.configure(height=70)
        self.plot.tk_canvas.pack(expand=True,fill='both')
        self.plot.toolbar.pack(expand=True,fill='both')

class Plot(Figure):
    def __init__(self,parent):
        prop_w = 0.7
        prop_h = 0.3
        fac_dpi = 100
        super().__init__(figsize=(9.7, 
        7.2),
        dpi=fac_dpi)
  
        canvas = FigureCanvasTkAgg(self,master=parent)
        
        canvas.draw()
        
       
        canvas.mpl_connect("key_press_event", key_press_handler)
        self.tk_canvas=canvas.get_tk_widget()

        self.toolbar = NavigationToolbar2Tk(canvas,parent,pack_toolbar=False)
        
class ChartsWindow(ttk.Window):
    def __init__(self):
        # We have started the theme.
        super().__init__(themename=THEME_NAME)
        
        # We have the screen dimensions to set the window dimensions.
        screen_height = self.winfo_screenheight()
        screen_width = self.winfo_screenwidth()
        # Window dimensions.
        win_height = screen_height*0.5
        win_width = screen_width*0.45
        # Window position
        win_x = screen_width/2-win_width/2
        win_y = screen_height/2-win_height/2
        # Window geometry
        self.geometry(f'{win_width:.0f}x{win_height:.0f}+{win_x:.0f}+{win_y:.0f}')
        # Window minimum size.
        self.minsize(f'{win_width*0.8:.0f}',f'{win_height*0.8:.0f}')
        
        self.dict_measure = {
            'T':[('BME280',3),('SHT31',3),('BME680',2),('SHT45',5)],
            'RH':[('BME280',3),('SHT31',3),('BME680',2),('SHT45',5)],
            'P':[('BME280',3),('BME680',2)]
        }
        
        # self.dict_measure = {'T':[('BME280',3)],
        #                     'RH':[('BME280',3)],
        #                     'P':[('BME280',3)]
        #                     }

        GeneralContainer(self).pack(expand = True,fill = 'both')
        
if __name__ == '__main__':
    ChartsWindow().mainloop()