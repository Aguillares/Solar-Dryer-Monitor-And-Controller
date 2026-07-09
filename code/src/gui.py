# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 15:30:37 2024

This is a code created for GUI in Raspberry Pi 3B to monitor
and control a solar dryer in Chapingo Autonomous University

@author: Hernández Aguillares Antonio
"""
# Module for comma-separated values.
import csv

# Regular expression, useful for validation proof.
import re

# ttkbootstrap replaces tk, with more appealing widgets.
# import ttkbootstrap as ttk

# Module used to display possible errors in the code, and
# to show it to the user.
from ttkbootstrap.dialogs import Messagebox

# Module used to upload a file in the program.
from tkinter import filedialog

# Module for mathematical operations
import numpy as np

# We import all classes from module "panels"
from panels import *

# Classes:

# Father module "PIL" and children modules "Image" and "ImageTk"
from PIL import Image, ImageTk

# Children modules:
#   -> Image (to open the images, it returns "ImageFile" object,
#      you can do multiple operations)
#   -> ImageTk (to convert the "ImageFile" into "PhotoImage",
#      it cannot be modified, but displayed in any widget)
#      the method is ImageTk.PhotoImage

# Module: datetime, class : datetime
# 請注意， ‘模組’ 和 ‘類別’ 的叫法相同
from datetime import datetime

# class used for FileManager
from io import TextIOWrapper

# For documention in functions
from collections.abc import Callable

# Path
from pathlib import Path

# Importing os to use directories
import os

from my_utils.display import show_elements

class Monitor(ttk.Window):
    """
    The main window

    Attributes
    ----------
    SCREEN_HEIGHT : int
        screen height of the current computer

    SCREEN_WIDTH : int
        screen width of the current computer
        
    init_path : str
        relative folder path (text file) where it stores the paths
        to get the previous selected database

    options_menu : Menu
        main panel, where we can display or get data
    
    """
    
    def __init__(self):
        """Construct a Monitor"""
        # Inheritance, the themename is 'x'
        # If you don't put this, you are not going to be able to make the window
        super().__init__(themename=THEME_NAME)
        
        # The screen sizes
        self.SCREEN_HEIGHT = self.winfo_screenheight()
        self.SCREEN_WIDTH = self.winfo_screenwidth()

        # We create the menu
        self._menubar = Menu(self)
        
        self._data_variables = {
            # The syntax is the following:
            # key: [name of the variable,[headers],[data]]
            "T": ["Temperature", [], []],
            "RH": ["Relative Humidity", [], []],
            "P": ["Pressure", [], []],
        }

        # Parent directory is the one that is two levels above
        self._parent_dir = Path(__file__).parent.parent
        self._data_dir = self._parent_dir
        
        # In the first row we have the first part of the path
        # In the second row we have the file's name
        self._init_path = r"init_path.txt"
        
        # FileManager is a class used to handle the file.
        with FileManager(self._init_path).read() as file:
            # --- COME BACK LATER ---
            # You need to improve the code when there's no table
            self._read_line = file.readline().split('/')

        # Creating the real data directory with the pieces of information
        # given by "init_path.txt"
        for item in self._read_line:
            self._data_dir = self._data_dir.joinpath(item)
        
        # From WindowsPath object to string
        with FileManager(str(self._data_dir)).read() as file:
            # We convert the csv into "an array" through list.
            table = np.array(list(csv.reader(file, delimiter=",")))
            # The first four columns we have the date [day,month,year,time] header
            self._HEADER_DATE = table[0, :4]
            # From the 5th column to the last we have the data header
            # it means all sensors' names
            self._HEADER_DATA = table[0, 4:]
            # Now we get the real dates
            self._date = table[1:, :4]
            # The data.
            self._sensors_data = table[1:, 4:]
            # We call the fill_data to know which variables we have
            # this is meant to the creation of the plots.
            self._fill_data()

        # We get the height, width, x and y of the window.
        self._INIT_WIN_HEIGHT = self.SCREEN_HEIGHT * 0.55
        self._INIT_WIN_WIDTH = self.SCREEN_WIDTH * 0.6
        self._INIT_POS_X = self.SCREEN_WIDTH / 2 - self._INIT_WIN_WIDTH / 2
        self._INIT_POS_Y = self.SCREEN_HEIGHT / 2 - self._INIT_WIN_HEIGHT / 2
        # The real origin is at (-9,0)
        self.geometry(
            f"{self._INIT_WIN_WIDTH:.0f}x{self._INIT_WIN_HEIGHT:.0f}+{self._INIT_POS_X:.0f}+{self._INIT_POS_Y:.0f}"
        )
        # The minsize of the window, 80% of the got dimensions.
        self.minsize(int(self._INIT_WIN_WIDTH*.8),int(self._INIT_WIN_HEIGHT*.8))
        # The title of GUI
        self.title("Solar Dryer")
        # We create the options menu
        self._create_panel()
        # We run the program
        self.mainloop()
    
    def _fill_data(self)->None:
        """
        Function to fill data into the dictionary 
        the different variables are:
        
        _T: Temperature
        
        _RH: Relative Humidity

        _P: Pressure
        """
        # This variable 'column' is used to know the column number
        # where the data are.
        for column,header_var in enumerate(self._HEADER_DATA):
            # If the variable type are either "T", "RH" or "P"
            # a number different to -1, it will be retrieved.
            for curr_var in ["T","RH","P"]:
                if header_var.rfind(curr_var) == len(header_var)-len(curr_var):
                    self._detection(curr_var,header_var,column)
                    break
            
            
    def _detection(self,var_type:str,header_var:str,col:int)->None:
        """We assign all values according to their variable type
        
        Parameters:
            var_type (str): The variable type, could be pressure (_P), relative humidity (_RH) or temperature (_T)
                
            header_var (str): It is the whole header of the sensor used, example: BME280_2_1_T
            
            col (int): This is the column where all data are located
        """
        # We append the sensor's name
        self._data_variables[var_type][1].append(header_var)
        # We assign all values (column) to the part of data.
        self._data_variables[var_type][2].append(
            self._sensors_data[:, col]
        )

    def _create_panel(self)->None:
        """The main panel is made"""
        self.options_menu = OptionsMenu(self,self._parent_dir).pack(expand=True, fill="both")

def _decorator_check_num(fun:Callable[[object,str,str,str],bool]) -> Callable[[object,str,str,str],bool]:
    """
    Non-public function, to validate the entry
    the user types in the combobox
    
    Parameters
    ----------
    
    fun : Callable[[object,list[tk.IntVar],str,str,str],bool]
        The function used is the non-public function
        to check out the numbers typed while using
        comboboxes as in either trigger or set options
        
    Return
    ------
    
    wrapper : Callable[[object,list[tk.IntVar],str,str,str],bool]
        The function returned is an upgraded function of the one
        original given previously"""
        
    def _wrapper(self, value:str, op:str, widget_name:str)->bool:
        """
        This function is retrieved to call the function given
        in the decorator function

        Parameters
        ----------
        
        value : str
            The value typed in the combobox
        
        op: str
            Option selected: "focusout", "focusin", "focus"

        widget_name : str
            The widget's name where the action is applied

        Return
        ------

        logic : bool
            It's a boolean variable to know if the validation
            was passed
        """
        # The real function is called
        # "logic" variable, it's boolean, is used to know if 
        # the validation was passed.
        logic=fun(self,value, op, widget_name)

        return logic

    return _wrapper

@_decorator_check_num
def _check_num(self,value:str, op:str, widget_name:str)->bool:
    """
    This function checks each digit typed, as well as,
    when it is focused out to revise if the whole number
    is correct

    Parameters
    ----------
    
    value : str
        The digit typed

    op : str
        Option selected: 'key', 'focus', 'all', 'none', ...

    widget_name : str
        Name of the picked widget

    Return

    logic : bool
        Boolean variable to know if the validation was accepted
    """

    # -> Validation and setting <-

    # The widget name has many points in between
    # We need to get the last one to have the real name
    no_point_name = widget_name.rsplit('.',1)[1]
    
    if (op == "focusout" and value == ""):
        temp_obj=self.nametowidget(widget_name)
        self.after_idle(lambda:temp_obj.set(int(0)))
        return True
    
    # -> Identifying match <-

    # We remove all characters after the first underscore
    # in the already modified name
    name_found = no_point_name.split('_',1)[0]

    # We have two types of minute range: {trigger(5min),set(59min)}
    if re.search('minute.*trigger',no_point_name) is not None  :
        name_found = name_found + '_trigger'
    
    # We get the pattern and the maximum number of digits
    pattern=PATTERN_TRIGGER[name_found]
    match = re.match(pattern, value)

    # We need to know if there's a match
    # and the number of digits.
    
    logic = match is not None
    
    return logic

class OptionsMenu(ttk.Frame):
    """This class is the main menu to select
    the different options"""
    def __init__(self, parent:Monitor, parent_dir:Path)->None:
        self.state_ = 'normal'
        # The parent is the window.
        self.parent = parent
         # Window sizes
        self.width = self.parent.winfo_width()
        self.height = self.parent.winfo_height()
        
        # Icons' directory
        self.parent_dir_icons = parent_dir.joinpath('asset','Icons')
        
        # We use it as master, the inheritance is applied
        super().__init__(parent,name='optionsMenu')

        # The object of this class is placed in the window
        self.pack(fill="both",expand=True)
        self.grid_columnconfigure(0, uniform="a", weight=2)
        self.grid_columnconfigure(1, uniform="a", weight=1)
        self.grid_rowconfigure((0, 1),weight=1)
        
        # Buttons and Labelframe style
        self.styling()

        # We use pack, place, grid methods to give place to the widgets
        self.place_widgets()
    
    def set_start(self):
        "Setting the start"
        self.set_time("Set start", 1, DATA_TRIGGER_SECTION["style"][0])

    def set_stop(self):
        "Setting the stop"
        self.set_time("Set stop", 3, DATA_TRIGGER_SECTION["style"][2])

    def start_now(self):
        "Start now"
        # Disabling trigger values widgets
        self.trigger_time_check()
        today = datetime.now()
        print(f"Today is {today.strftime('%c')}")

    def stop_now(self):
        "Stop now"
        
        # Disabling trigger values widgets
        print("You are inside the function stop")

    def conf_btns(self):
        "The buttons are linked to their commands"
        
        for i, fun in enumerate((self.start_now,
                                self.set_start,
                                self.stop_now,
                                self.set_stop)):
            self.trigger_buttons[i].config(command=fun)
     
    def place_widgets(self):
        "All widgets are placed"
        
        # The trigger section is created
        self.create_trigger_section()

        # Fruit Temperature, Fruit Weight, Psychrometric, Environmental Variables
        self.create_plot_section()

        # This is a table to preview all data
        self.create_preview_section()
        
    def create_trigger_section(self):
        "All widgets of the trigger section are created"
         # All options of trigger: {start, time, stop}
        self.trigger_sections_main_frame = ttk.Labelframe(
            self, name="triggerSectionsMainFrame", text="Trigger Settings"
        )
        self.trigger_sections_main_frame.grid(row=0, column=0, sticky="nesw", padx=10, pady=5)
        # The trigger section is divided by 3, so we have start, the trigger time and stop
        self.trigger_sections_main_frame.grid_columnconfigure((0, 1, 2), uniform="a", weight=1)
        self.trigger_sections_main_frame.grid_rowconfigure(0, uniform="a", weight=1)

        # Creating all variables that are going to store information from the user
        self.create_vars()
        
        #  The different frames, comboboxes and buttons are going to be stored in these arrays
        self.trigger_sections_frame = []
        self.trigger_values_comboboxes = []
        self.trigger_buttons = []  
        
        for section_text,section_column,options,style_ in zip(
            DATA_TRIGGER_SECTION["texts"],
            DATA_TRIGGER_SECTION["column"],
            DATA_TRIGGER_SECTION["options"],
            DATA_TRIGGER_SECTION["style"]):

            # The frame's name is the same as the section_text's
            frame_name= "trigger_section_" + section_text.lower()
            self.trigger_sections_frame.append(
                ttk.Labelframe(
                    self.trigger_sections_main_frame,
                    name=frame_name,
                    text=section_text,
                    style=f"{section_text}.TLabelframe",
                    borderwidth=0,
                )
            )
            
            # We want to get the current selected frame, we use the method "nametowidget"
            current_frame = self.trigger_sections_main_frame.nametowidget(frame_name)
            current_frame.grid(
                row=0,
                column=section_column,
                sticky="nesw",
                padx=10,
                pady=10,
            )
            current_frame.rowconfigure(
                list(range(4)), uniform="a", weight=1
            )
            current_frame.columnconfigure(
                list(range(2)), uniform="a", weight=1
            )

            for ind, option_name in enumerate(
                options
            ):
                if 'Trigger' in option_name:
                    row_label = ind * 2
                    ttk.Label(
                        current_frame,
                        text=option_name,
                        style="Time.TLabel",
                    ).grid(column=0, row=row_label, columnspan=2)
                
                    check_num_wrapper = (
                        self.parent.register(
                            lambda value, op, widget_name: 
                            _check_num(
                                self,
                                value,
                                op,
                                widget_name)
                                ),
                                "%P",
                                "%V",
                                "%W"
                                )
                    modified_option_name = (
                        option_name.lower().replace(" ", "").replace(".", "_")
                    )
                    try: 
                        for  column,range_time, name in zip(
                            range(2),
                            (SHORT_MIN_RANGE,SEC_RANGE),
                            (
                                "minute_" + modified_option_name,
                                "second_" + modified_option_name,
                            )):
                            
                            self.trigger_values_comboboxes.append(
                                ttk.Combobox(
                                    current_frame,
                                    name=name,
                                    textvariable=self.time_values[name],
                                    state="normal",
                                    values=range_time,
                                    width=20,
                                    validate="all",
                                    validatecommand=check_num_wrapper,
                                )
                            )
                            
                            current_combobox = current_frame.nametowidget(name)
                            current_combobox.bind(
                                "<<ComboboxSelected>>",
                                self.update_combobox_value,
                            )
                            current_combobox.grid(column=column, row=row_label + 1, padx=5)
                          
                    except Exception as e:
                        print(e)
                    continue
                btn_name = option_name.lower().replace(" ","_")
                self.trigger_buttons.append(
                    ttk.Button(
                        current_frame,
                        name=btn_name,
                        text=option_name,
                        style=style_,
                        state="normal",
                        cursor="hand2",
                    )
                )

                current_frame.nametowidget(btn_name).grid(
                    column=0,
                    row=ind * 2,
                    columnspan=2,
                    rowspan=2,
                    sticky="nsew",
                    pady=15,
                )
        
        # The button's functions are linked to their buttons
        self.conf_btns()

    def create_preview_section(self):
        # Table Preview
        self.preview_table_frame = ttk.Labelframe(
            self, name="preview_table_frame", text="Preview"
        )
        self.preview_table_frame.grid(
            row=0, column=1, rowspan=2, sticky="nswe", pady=5, padx=5
        )
        self.preview_table = ttk.Treeview(self.preview_table_frame)
        self.preview_table.pack(expand=True, fill="both", padx=10, pady=10)

    def create_plot_section(self):
        "The section where all graphs are going to be employed"
        # You must check it out we didn't divide Labelframe using row/column-configure, but the Frame was used
        # instead, this is because Labelframe is seen as the main container, meanwhile,
        # Frame is the container of the widgets inside.
        plots_frame_section = ttk.Labelframe(
            self, name="plots_frame", text="Plots"
        )
        plots_frame = ttk.Frame(plots_frame_section)
        plots_frame.rowconfigure((0, 1), uniform="a", weight=1)
        plots_frame.columnconfigure((0, 1), uniform="a", weight=1)
        plots_frame.pack(expand=True, fill="both", padx=5)
        plots_frame_section.grid(
            row=1, column=0, sticky="news", padx=5, pady=5
        )
        
        self.images = []
        self.images_tk = []
        self.image_size = (60, 70)
        self.speed = 0.8
        self.symmetric_text(BUTTONS_INFO)
        self.plots_buttons = []

        for i, button_info in enumerate(BUTTONS_INFO):
            # This is saved in an array because we want the images to appeared in the buttons.
            # If they are not saved, they disappear.
            self.images.append(Image.open(self.parent_dir_icons.joinpath(button_info[2])))
            # We resize and save the images in the array.
            self.images_tk.append(
                ImageTk.PhotoImage(self.images[i].resize(self.image_size))
            )
         
            self.plots_buttons.append(
                ttk.Button(
                    plots_frame,
                    name="plot_btn_"+button_info[0].lower().replace("\n","_"),
                    cursor="hand2",
                    text=button_info[0],
                    padding=(20, 0, 0, 0),
                    style="info",
                    image=self.images_tk[i],
                    compound=ttk.LEFT,
                )
            )
            self.plots_buttons[i].grid(
                row=button_info[1][0],
                column=button_info[1][1],
                pady=10,
                padx=10,
                sticky="nsew",
            )

        self.parent.bind("<Configure>", self.resizing_images)
        self.changes_counter = 0
        self.changes_number = 35
 
    def create_vars(self):
        # The small pop-ups windows that appear when you set
        # either the start or the stop, using date and hour.
        # These are being stored in a dictionary
        self.selection_time = {"Set start": None, "Set stop": None}

        # The variables that are used to store these values,
        # It is for the date, hour, minute and second, for both.
        self.selection_time_vars = {
            "set_start": [
                ttk.StringVar(
                    master=self.parent,
                    value=datetime.today().strftime(r"%x"),
                    name="date_start",
                ),
                ttk.IntVar(master=self.parent, value=0, name="hour_start"),
                ttk.IntVar(master=self.parent, value=0, name="minute_start"),
                ttk.IntVar(master=self.parent, value=0, name="second_start"),
            ],
            "set_stop": [
                ttk.StringVar(
                    master=self.parent,
                    value=datetime.today().strftime(r"%x"),
                    name="date_stop",
                ),
                ttk.IntVar(master=self.parent, value=0, name="hour_stop"),
                ttk.IntVar(master=self.parent, value=0, name="minute_stop"),
                ttk.IntVar(master=self.parent, value=0, name="second_stop"),
            ],
        }

        self.time_values ={
            "minute_trigger": ttk.IntVar(master = self.parent, name="minute_trigger", value=0),
            "second_trigger": ttk.IntVar(master = self.parent, name="second_trigger", value=0),
            "minute_avg_trigger": ttk.IntVar(master = self.parent, name="minute_avg_trigger", value=0),
            "second_avg_trigger": ttk.IntVar(master = self.parent, name="second_avg_trigger", value=0)
        }
        
    def styling(self):
        "Giving style to all labels"
        # The object "style" is used to modify 
        # the different styles as frames, labels, etcetera.
        
        self.style = ttk.Style()
        for name, background in zip(
            DATA_TRIGGER_SECTION["texts"], DATA_TRIGGER_SECTION["background"]
        ):
            # -> TLabelframe <-
            self.style.configure(
                f"{name}" + ".TLabelframe",
                padding=8,
                relief="sunken",
                background=background,
            )
            # -> TLabelframe.label <-
            self.style.configure(
                f"{name}" + ".TLabelframe.Label",
                font=("Comic Sans MS bold", 10),
                background=background,
                foreground="white",
            )
        # -> TLabelframe.Label generic one <-
        self.style.configure("TLabelframe.Label", font=("Impact", 12))
        # -> Time.TLabel <-
        self.style.configure(
            "Time.TLabel", font=("Comic Sans MS bold", int(15)),background=DATA_TRIGGER_SECTION["background"][1]
        )
        # -> TButton <-
        self.style.configure(
            "TButton",
            font=("Comic Sans MS bold", 15),
            justify="center",
            compound="left",
        )

    def update_combobox_value(self, ev):
        print(f"GETTING NUMBER => {ev.widget.selection_get()}")

    def trigger_time_check(self):
        "All variables in trigger time are checked out"
        try:
            trigger_time=self.time_values['minute_trigger'].get()*60+self.time_values['second_trigger'].get()
            trigger_avg_time=self.time_values['minute_avg_trigger'].get()*60+self.time_values['second_avg_trigger'].get()

            if trigger_time > trigger_avg_time:
                raise ValueError
        except ValueError:
            print(f"You need to specify a correct time trigger")
            self.parent.focus_set()
            message = Messagebox()
            message.show_error(
                message="Sorry, you need to establish a correct time for the trigger",
                parent=self.parent,
            )

    def set_time(self, name:str, indx, style):
        self.selection_time[name] = SelectionTime(self.parent, self, name, style)  # type: ignore
        self.selection_time[name].bind("<Destroy>", lambda _: self.enable_btn(indx)) # type:ignore
        self.print_value = 0
        for btn in self.trigger_buttons:
            btn.config(state=ttk.DISABLED)    
        
    
    def enable_btn(self, indx):
        # If the main window is destroyed instead of the small one
        if self.print_value == 0:
            if self.trigger_buttons[indx].winfo_exists():
               for btn in self.trigger_buttons:
                    btn.config(state=ttk.NORMAL)
            for key, val in self.selection_time_vars.items():
                print(f"{key} :-> ", end="")
                for i, x_val in enumerate(val):
                    print(f"{x_val.get()}", end="")
                    if i < len(val) - 1:
                        print(", ", end="")
                    else:
                        print(".")

        self.print_value = self.print_value + 1
        self.trigger_time_check()

    def fun_trigger(self, var):
        try:
            print(f"Var => {var.get()}")

        except Exception as e:
            print("Something occured")
            print(f"We have the next exception {e}")

    def resizing_images(self, _):
        "The font and images are resized according to the window's size"
        # We count the number of changes
        self.changes_counter += 1

        # We get the window's state
        win_state= self.parent.state()
        if self.changes_counter >= self.changes_number or win_state =="zoomed" or win_state=="normal" and self.state_=="zoomed":
            # We reset changes_counter
            self.changes_counter = 0

            # We get the parent's width and height.
            current_parent_width = self.parent.winfo_width()
            current_parent_height = self.parent.winfo_height()
            
            if current_parent_width != self.width or current_parent_height != self.height:
                # This is useful to know when we go from maximization
                self.state_ = win_state
                # Updating values of width and height.
                self.width = current_parent_width
                self.height = current_parent_height

                # It must grow slower with the height.
                proportional_factor = ((current_parent_width / (self.parent._INIT_WIN_WIDTH*2))+(current_parent_height/(self.parent._INIT_WIN_HEIGHT*3)))
                
                # We determine the width and height of the image using the width_factor, and speed is added.
                width_height = []
                for i in range(2):
                    width_height.append(np.ceil(
                        self.image_size[i] * proportional_factor,
                        dtype=int,
                        casting="unsafe",
                    ))
            
                # Each image is resized.
                try:
                    for i, current_image in enumerate(self.images):
                        self.images_tk[i] = ImageTk.PhotoImage(current_image.resize((width_height[0], width_height[1])))
                        self.plots_buttons[i].configure(image=self.images_tk[i])
                except Exception as error:
                    print("An exception is encountered -> ", error)
                # The font size's button is changed.
                font_size = int(proportional_factor * 18)
                
                for widget_style in ["TButton","Time.TLabel"]:
                    self.style.configure(
                        widget_style, font=("Comic Sans MS bold", font_size)
                    )
            
    def symmetric_text(self, var):
        """Function to know the number of characters per button,
        knowing this number we can center the text."""
        total_max = 0
        set_sizes = []
        for text in var:
            for item in text[0].split("\n"):
                set_sizes.append(len(item))

        total_max = max(set_sizes)
        print(total_max)

class ControlVariables:
    def __init__(self):
        pass

class SelectionTime(ttk.Toplevel):
    def __init__(self, window, father, name_var, cal_style):

        self.window = window
        self.father = father

        super().__init__()
        height = self.winfo_screenheight() * 0.12
        width = self.winfo_screenwidth() * 0.35
        self.pos_x = (self.window.winfo_x() + self.window.winfo_width() / 2 - width / 2)
        self.pos_y = (self.window.winfo_y() + self.window.winfo_height() / 2 - height / 2)
        self.geometry(f"{width:.0f}x{height:.0f}+{self.pos_x:.0f}+{self.pos_y:.0f}")
        self.name = name_var.lower().replace(' ','_')
        self.resizable(False, False)
        self.title(name_var)
        self.rowconfigure(0, weight=7, uniform="a")
        self.rowconfigure(1, weight=3, uniform="a")
        self.columnconfigure(0, weight=2, uniform="a")
        self.columnconfigure(1, weight=3, uniform="a")
    
        # check_num_wrapper
        check_num_wrapper = (
            self.father.register(lambda value, op, widget_name: 
                                 _check_num(self,
                                            value,
                                            op,
                                            widget_name)),
            "%P",
            "%V",
            "%W"
        )
        
        self.btns_frame = ttk.Frame(self)
        self.btns_frame.grid(row=1, column=1, sticky="nesw", padx=10, pady=1)
        style = ttk.Style()
        style.configure("start.TLabelframe", padding=2)
        style.configure("start.TLabelframe.Label", font=("Arial", 10, "bold"))

        # check_num_wrapper

        style.configure(
            "btn.TButton",
            width=5,
            foreground="black",
            font=("Comic Sans MS bold", 10),
            padding=(20, 2),
            bordercolor=COLORS_HEX[cal_style],
            lightcolor=COLORS_HEX[cal_style],
            darkcolor=COLORS_HEX[cal_style],
        )
        style.map(
            "btn.TButton",
            background=[("active", "#d3cfca"), ("!active", "#f2f1ef")],
        )

        btn_pdy = 3
        btn_pdx = 1
        # Ok, and cancel buttons.
        cancel_btn = ttk.Button(
            self.btns_frame,
            text="cancel",
            style="btn.TButton",
            command=self.destroy,
        )
        cancel_btn.pack(side="right", pady=btn_pdy, padx=btn_pdx)

        ok_btn = ttk.Button(
            self.btns_frame,
            text="ok",
            style="btn.TButton",
            command=self.ok_button_fun,
        )
        ok_btn.pack(side="right", pady=btn_pdy, padx=btn_pdx)

        self.sel_time_frames = []

        for indx, title in enumerate(("Date", "Time")):
            self.sel_time_frames.append(
                ttk.Labelframe(
                    self, text=title, style="trigger.TLabelframe", padding=10
                )
            )
            self.sel_time_frames[indx].grid(
                row=0, column=indx, sticky="news", padx=10
            )

        # Selecting the date
        calendar = ttk.DateEntry(self.sel_time_frames[0], bootstyle=cal_style)
        calendar.entry.config(
            textvariable=self.father.selection_time_vars[self.name][0]
        )
        calendar.pack()

        self.time_frame = ttk.Frame(self.sel_time_frames[1])
        self.time_frame.pack(fill="both", expand=True)
        self.time_frame.rowconfigure(0,weight=1)
        self.time_frame.columnconfigure((0, 1, 2), weight=1, uniform="a")

        # Hour, Minute, Second
        hour_range = [str(x) for x in range(24)]
        min_range = [str(x) for x in range(60)]
        sec_range = [str(x) for x in range(60)]

        for indx, values in enumerate(
            zip(
                ("hour_" + self.name, "minute_" +
                 self.name, "second_" + self.name),
                (hour_range, min_range, sec_range),
                self.father.selection_time_vars[self.name][1:],
            )
        ):
            time_section = ttk.Labelframe(
                self.time_frame,
                text=ABBR_TIME[values[0].split('_')[0]],
                style="start.TLabelframe",
                labelanchor="n",
            )
            ttk.Combobox(
                time_section,
                name = values[0],
                values=values[1],
                justify="center",
                textvariable=values[2],
                validate='all',
                validatecommand=check_num_wrapper
            ).pack(expand=True, fill="both", padx=15, pady=1)
            time_section.grid(row=0, column=indx, sticky="nwes", padx=15)
   
    def ok_button_fun(self):
        self.get_time_values()
        self.get_date_time()
        self.destroy()

    def cancel_button_fun(self):
        self.set_time_values((0, 0, 0))
        self.set_date_time(datetime.now().strftime(r"%x"))
        self.destroy()

    def get_date_time(self):
        print()

    def set_date_time(self, date):

        pass

    def get_time_values(self):

        for val in self.father.selection_time_vars[self.name]:
            print(f"{val} = {val.get()}")

    def set_time_values(self, values):

        for val, value in zip(
            self.father.selection_time_values[self.name], values
        ):
            val.set(value)
            print(f"{val} = {val.get()}")


class Menu(ttk.Menu):
    """_Menu_

    Args:
        parent (ttk.Window): It is the main window
    """

    def __init__(self, parent):
        # Inheritance is initialized
        super().__init__(parent,name='upperMenu')
        # First we set the menu in the window, but until now, it will not appear, it is hidden, we need another menu to make it appear.
        parent.configure(menu=self)
        
        # menuContainer holds all options.
        self.menuContainer = ttk.Menu(self,name='menuContainer')
        self.menuContainer.add_command(
            label="New", command=lambda: self.new_file()
        )
        self.menuContainer.add_command(
            label="Open", command=lambda: self.open_file()
        )
        # With "File" you can open a previous table
        # or making a new one
        self.add_cascade(label="File", menu=self.menuContainer)

    def open_file(self)->None:
        """It opens the file where data is located"""
        # --TODO-- You have to find a way to let the last file's directory to be the init directory
        self.open_dialog = filedialog.askopenfilename(
            title="Open a file",
            filetypes=(
                ("All", "*.*"),
                ("Text files", "*.txt"),
                ("Comma-separated values", "*.csv"),
            ),
        )
        
    def new_file(self):
        """A new file is  created."""
        # --TODO-- It has to start an empty
        print('A new file is created')
        pass


class Psychrometric(Monitor):
    def __init__(self):
        super().__init__()
        self.psy_height = self.SCREEN_HEIGHT * 0.42
        self.psy_width = self.SCREEN_WIDTH * 0.33
        self.geometry(
            f"{self.psy_width:.0f}x{self.psy_height:.0f}\
                      +{(self._INIT_POS_X-(self._INIT_WIN_WIDTH+self.psy_width)/2+15):.0f}+{(self._INIT_POS_Y):.0f}"
        )
        print(f"Psy width = {self._INIT_WIN_WIDTH},Psy height = {self._INIT_WIN_HEIGHT}")
        self.title("Psychrometric Chart")

class Weight(Monitor):
    def __init__(self, screen_width, screen_height):
        super().__init__()


class Humidity(ttk.Window):
    def __init__(self, screen_width, screen_height):
        super().__init__()
        self.win_width = 100
        self.win_height = 200
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.geometry(
            f"{self.win_width:.0f}x{self.win_height:.0f}\
                      +{(self.screen_width/2-self.win_width/2):.0f}+{(self.screen_height/2-self.win_height/2):.0f}"
        )  # type: ignore


class Temperature(ttk.Window):
    def __init__(self,screen_width,screen_height):
        super().__init__()



class FileManager(object):
    "This a class that will make the operations with files easier"

    def __init__(self, file_whole_path: str):
        """
        Parameters:
            file_whole_path (str):
                These are all the folders needed
                to go through to reach the file
        """
        self.file_whole_path = file_whole_path

    def append(self) -> TextIOWrapper:
        """Open the file in appending mode, the information given will be added
        to the previous one at the end, (not replaced).
        It returns a TextIOWrapper object"""
        # Opening in appending mode.
        self.file = open(self.file_whole_path, "a")
        # The file is returned.
        return self.file

    def read(self) -> TextIOWrapper:
        """It opens the file in reading mode.
        It returns a TextIOWrapper object"""
        # Opening in reading mode.
        self.file = open(self.file_whole_path, "r")
        # The file is returned
        return self.file

    def over_write(self) -> TextIOWrapper:
        """It opens the file in writing mode.
        It returns a TextIOWrapper object"""
        self.file = open(self.file_whole_path, "w")
        return self.file

    def detect(self) -> TextIOWrapper:
        """It opens the file in"""
        self.file = open(self.file_whole_path, "x")
        return self.file

    def __exit__(self) -> None:
        self.file.close()

monitor=Monitor()