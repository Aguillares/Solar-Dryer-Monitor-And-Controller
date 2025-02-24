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
    def __init__(self,parent,dict_):
        self.system = platform.system()
        print(self.system)
        # if system == "Window" or system == "Darwin":
        #     self.bind_vert = "<MouseWheel>"
        #     self.bind_hor = "<Shift-MouseWheel>"
        # else:
        #     self.bind_vert = ("<Button-4>","<Button-5>")
        #     self.bind_hor = ("<Shift-Button-4>","<Shift-Button-5>")
        super().__init__(parent)
        # We get the number of plots 
        number_plots = len(dict_)
        
        # We have the keys name with "keys()" method.
        get_keys = dict_.keys()
        # The first part of tuple says in which row will be set.
        # We have plots' number and keys' name.
        tuple_ = tuple(row for row in zip(range(number_plots),get_keys))
        
        for ind,key in tuple_:
            # We create the panel where 
            PanelData(self,dict_[key],key,self.system).grid(row=ind,column=1,sticky='nsew')
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
    # var: Variable name (BME280,SHT31,...)
    def __init__(self, parent,dict_,var,system):
        self.system = system
        # Heritage
        super().__init__(parent = parent)
        # We divide the panel for the canvas and the meters.
        # Font for the sensor's name.
        # Notice we use the constant TITLE_VAR_FONT.
        # font_ = ttk.font.Font(name=TITLE_VAR_FONT[0],family=TITLE_VAR_FONT[1],size=TITLE_VAR_FONT[2])
        # We need to set the title's background, we use a label for it.
        # "place" method is used inasmuch as we can be overrided by the next widget.
        # Even we don't use any word here, we should use the same font
        # in the label background and the label title, to have the 
        # same width between both.
        # The explanation why we don't use fill with the label title
        # it is because we want the title to be centered.
        # ttk.Label(self,font=font_,background=COLOR_TITLE_BG[var]).place(x=0,y=0,relwidth=1,anchor='nw')
        # Here it is the actual title.
        # To print the text we identify the variable with proper method.
        # self.sensor_name_label=ttk.Label(self,background=COLOR_TITLE_BG[var],text=self.identify_variable(var),font=font_)
        # self.sensor_name_label.pack()
        self.set_header_and_bg(TITLE_VAR_FONT,COLOR_TITLE_BG[var],self.identify_var(var))
        # Horizontal canvas used to get all meters widgets and its canvas,
        # it allows horizontal movement.
        self.hor_canvas = ttk.Canvas(self)
        
        # The number of columns is related to sensors type' number
        number_col= len(dict_)
        # The maximum widgets number, it's the maximum sensors' number from all types.
        # At the beginning we have zero.
        max_num_widgets = 0
        # We are not interested in sensor's name, just its number.
        for _,number in dict_:
            # If the current number is greater to current maximum number, then
            # the current number is converted into the new maximum number.
            if number> max_num_widgets:
                max_num_widgets = number
    
        # We are going to give 100 of width for widget
        self.meter_w_h = 100
        # There is a difference of 49 between the units of meter_size given, the one measured
        # It means we give 100 to meter's width, but when we measure it with the method
        # "winfo_reqwidth()", it tells 149. Then for each unit given to meter_size, we
        # have a delta of 0.49 more in the real width.
        # If we have then "x" units that we give to meter we get
        # 0.49*x more.
        self.delta = 49/100*self.meter_w_h 
        # The meter corrected, the delta added.
        self.meter_corrected = self.meter_w_h+self.delta
        # With the meter corrected we can make the canvas dimensions.
        self.width=(self.meter_corrected)*number_col
        self.height=(self.meter_corrected)*max_num_widgets
        
        # Canvas just holds the meter widgets.
        self.hor_canvas.config(width=self.width,height=self.height)
        # self.hor_canvas should cover all the frame parent.
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
        # We pack the frame that will conver all the canvas.
        # Remember if you want allocate more widgets inside any canvas we must employ
        # a frame to allot all widgets.
        self.frame_measure = ttk.Frame(self.hor_canvas)
        # sensor_name: Sensor name (BME280,SHT45,...)
        # sensor_number: The number of sensors of that type.
        for sensor_name,sensor_number in dict_:
            # We all MeasureContainers will be inside of self.frame_measure, and
            # the arrangement is one next to another, they are going to cover all the widget.
            MeasureContainer(self.frame_measure,var,sensor_name,sensor_number,self.meter_w_h,self.meter_corrected,self.system).pack(side='left',expand=True,fill='both')
    
    # We can give the proper title variable according to key
    def identify_var(self,variable):
        match variable:
            case "T":
                return 'Temperature'
            case "RH":
                return "Relative Humidity"
            case "P":
                return "Pressure"
    
    # up
    def update_scroll(self,ev):
        if self.hor_canvas.winfo_reqwidth() > self.winfo_width():
            if self.system == "Window":
                self.hor_canvas.bind_all('<Shift-MouseWheel>',lambda ev:self.hor_canvas.xview_scroll(-int(ev.delta/MOUSE_SPEED_WIN),'units'))
            else:
                self.hor_canvas.bind_all('<Shift-Button-4>',lambda ev: self.hor_canvas.xview_scroll(-MOUSE_SPEED_LNX,'units'))
                self.hor_canvas.bind_all('<Shift-Button-5>',lambda ev: self.hor_canvas.xview_scroll(MOUSE_SPEED_LNX,'units'))
        else:
            # We deactivate the combitination of keys.
            self.hor_canvas.unbind_all('<Shift-MouseWheel>')
        self.hor_canvas.update_idletasks()

    def update_canvas(self,ev):
            # self.hor_canvas.config(scrollregion=(0,0,self.hor_canvas.winfo_reqwidth(),self.hor_canvas.winfo_height()))
            
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
    def __init__(self,parent,variable,sensor_name,sensor_number,meter_w_h,meter_corrected,system):
        self.system = system
        # In this case the parent is the canvas.
        
        self.parent = parent
        super().__init__(parent)

        # Font for sensors' name.
        font_ = ttk.font.Font(name=SENSOR_NAME_FONT[0],family=SENSOR_NAME_FONT[1],size=SENSOR_NAME_FONT[2])
        ttk.Label(self,font=font_).place(x=0,y=0,relwidth=1,anchor='nw')
        self.sensor_name_label=ttk.Label(self,text=str(sensor_name),font= font_)
        self.sensor_name_label.pack()

        self.canvas= tk.Canvas(self)
        self.width_canvas = meter_corrected
        self.height_canvas = self.width_canvas*sensor_number
        # For some reason you need to use the "configure" method to make changes.
        self.canvas.config(
            # background = 'gray',
            width = self.width_canvas,
            height = self.height_canvas,
            )

        self.canvas.pack(expand=True,fill='both')
        self.bind('<Configure>',self.update_size)
        # This frame is used to put things inside the canvas.
        self.frame = ttk.Frame(self.canvas)

      
        # ttk.Label(self.frame,text='Forehead\n'*sensor_number,background='blue').pack(side='left',expand=True, fill='both')
        for number in range(sensor_number):
            self.meter=ttk.Meter(self.frame,
                                 metertype='semi',
                                 metersize=meter_w_h,
                                 subtext = 'S'+str(number),
                                 amountused=50,
                                 bootstyle= COLOR_VAR_METERS[variable])
            self.meter.pack()
            
        # Creating a vertical scrollbar
        
        self.height = ttk.DoubleVar(self,value=0.913)
        self.scroll_bar = ttk.Scrollbar(self,orient='vertical',command = self.canvas.yview)
        
        self.canvas.config(yscrollcommand = self.scroll_bar.set)

        self.bind('<Enter>',self.update_scroll)
        
        # for e in range(sensor_number):
        #     Live_Measure(self,tuple_set[e]).pack(side='left',expand=True,fill='both')

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
    def update_size(self,event):
        self.canvas.config(scrollregion = (0,0,self.width_canvas,self.height_canvas+self.sensor_name_label.winfo_reqheight()))
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
        
        
        
        # self.plot.tk_canvas.grid(row = 0,column=0,columnspan=1,sticky='nswe')
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
        
        
        
if __name__ == '__main__':
    
    win = ttk.Window(themename=THEME_NAME)
    #[print(font_tk) for font_tk in ttk.font.families()]
    themes=win.style.theme_names()
    
    win.geometry(f'390x465')
    win.minsize(100,205)
    '''
    dict_measure = {
        'T':[('BME280',3),('SHT31',3),('BME680',2),('SHT45',5)],
        'RH':[('BME280',3),('SHT31',3),('BME680',2),('SHT45',5)],
        'P':[('BME280',3),('BME680',2)]
    }
    '''
    #win.bind('<Configure>', lambda ev: print(f"width = {win.winfo_width()}, height = {win.winfo_height()}"))
    dict_measure = {'T':[('BME280',3)],
                         'RH':[('BME280',3)],
                         'P':[('BME280',3)]
                         }

    # ScrollbarFrame(win)
    GeneralContainer(win,dict_measure).pack(expand = True,fill = 'both')
    
    win.mainloop()