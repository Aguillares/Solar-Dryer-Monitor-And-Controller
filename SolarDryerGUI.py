# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 15:30:37 2024

This is a code created for GUI in Raspberry Pi 2B to monitor
and control a solar dryer in Chapingo Autonomous University

@author: Hernández Aguillares Antonio
"""
# Module for comma-separated values.
import csv

# Regular expression, useful for validation proof.
import re

# ttkbootstrap replaces tk, with more appealing widgets.
import ttkbootstrap as ttk

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
# 請 [qǐng] v. -> ask, please (do something)
# 注意 [zhùyì] v. -> to take note of, to pay attention to
# 模組 [mózǔ] n. -> module (computer)
# 和 [hé] conj. -> and
# 類別 [lèibié] n. -> classification, category, class
# 的 [de] p. -> used to denote possession
# 叫 [jiào] v. -> to name, to call (naming)
# 法 [fǎ] n. -> way, method, mode, means
# 相同 [xiāngtóng] adj. -> identical, same
from datetime import datetime

# class used for FileManager
from io import TextIOWrapper

# For documention in functions
from collections.abc import Callable


class Monitor(ttk.Window):
    """
    The main window

    ...

    Attributes
    ----------
    screen_height : int
        screen height of the current computer

    screen_width : int
        screen width of the current computer
        
    init_path : str
        relative folder path (text file) where it stores the paths
        to get the previous selected database

    menu : Menu
        It is the upper toolbar to get access to the files
        or more editing
    
    """
    
    def __init__(self):
        """Construct a Monitor"""
        # Inheritance, the themename is 'x'
        # If you don't put this,
        # you are not going to be able to make the window
        super().__init__(themename=THEME_NAME)
        # The screen sizes
        self._SCREEN_HEIGHT = self.winfo_screenheight()
        self._SCREEN_WIDTH = self.winfo_screenwidth()

        # We create the menu
        self._menubar = Menu(self)

        # In the first row we have the first part of the path
        # In the second row we have the file's name
        self._init_path = r"init_path.txt"

        # FileManager is a class used to handle the file.
        # Read
        with FileManager(self._init_path).read() as file:
            # --- COME BACK LATER ---
            # You need to improve the code when there's no table
            self._read_line = file.readline()[:-1] + "/" + file.readline()

        self._data_variables = {
            # The syntax is the following:
            # key: [name of the variable,[headers],[data]]
            "_T": ["Temperature", [], []],
            "_RH": ["Relative Humidity", [], []],
            "_P": ["Pressure", [], []],
        }

        with FileManager(self._read_line).read() as file:
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
        self._MIN_WIN_HEIGHT = self._SCREEN_HEIGHT * 0.5 * 0.95
        self._MIN_WIN_WIDTH = self._SCREEN_WIDTH * 0.45 * 0.95
        self._INIT_POS_X = self._SCREEN_WIDTH / 2 - self._MIN_WIN_WIDTH / 2
        self._INIT_POS_Y = self._SCREEN_HEIGHT / 2 - self._MIN_WIN_HEIGHT / 2
        self.geometry(
            f"{self._MIN_WIN_WIDTH:.0f}x{self._MIN_WIN_HEIGHT:.0f}+{(self._INIT_POS_X):.0f}+{(self._INIT_POS_Y):.0f}"
        )
        # The minsize of the window, 95% of the got dimensions.
        self.minsize(int(self._MIN_WIN_WIDTH*.95),int(self._MIN_WIN_HEIGHT*.95))
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
            # If the variable type are either '_T', '_RH' or '_P'
            # a number different to -1, it will be retrieved.
            if header_var.find("_T")!=-1:
                self._detection('_T',header_var,column)
            elif header_var.find("_RH")!=-1:
                self._detection('_RH',header_var,column)
            elif header_var.find("_P")!=-1:
                self._detection('_P',header_var,column)
            
    def _detection(self,var_type:str,header_var:str,col:int)->None:
        """We assign all values according to their variable type
        
        Parameters
        ----------
        
        var_type : str 
            The variable type, could be pressure (_P), 
            relative humidity (_RH) or temperature (_T)
            
        header_var : str
            It is the whole header, example:
            BME280_2_1_T
        
        col : int
            This is the column where all data is located
        """
        # We append the sensor's name
        self._data_variables[var_type][1].append(header_var)
        # We assign all values (column) to the part of data.
        self._data_variables[var_type][2].append(
            self._sensors_data[:, col]
        )

    def _create_panel(self)->None:
        """The upper menu is made"""
        self.options_menu = OptionsMenu(self).pack(expand=True, fill="both")

def _decorator_check_num(fun:Callable[[type,list[tk.IntVar],str,str,str],bool])->\
Callable[[list[tk.IntVar],str,str,str],bool]:
    """
    Non-public function, to validate the entry
    the user types in the combobox
    
    Parameters
    ----------
    
    fun : Callable[[list[tk.IntVar],str,str,str],bool]
        The function used is the non-public function
        to check out the numbers typed while using
        comboboxes as in either trigger or set options
        
    Return
    ------
    
    wrapper : Callable[[list[tk.IntVar],str,str,str],bool]
        The function returned is an upgraded function of the one
        original given previously"""
        
    def _wrapper(self:type,textvars:list[tk.IntVar],value:str, op:str, widget_name:str):
        """
        This function is retrieved to call the function given
        in the decorator function

        Parameters
        ----------

        textvars : list[tk.IntVar]
            We have a list where the variable type
            is tk.IntVar, these variables used in
            the comboboxes
        
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
        logic=fun(self,textvars,value, op, widget_name)

        return logic
    return _wrapper

@_decorator_check_num
def _check_num(self,textvars:list[tk.IntVar],value:str, op:str, widget_name:str)->bool:
    """
    This function checks each digit typed, as well as,
    when it is focused out to revise if the whole number
    is correct

    Parameters
    ----------

    textvars : list[tk.IntVar]
        The list where you can find all variables to store
        the given values attached to the comboboxes
    
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
    pattern,maxlen=PATTERN_TRIGGER[name_found]
    match = re.match(pattern, value)

    # We need to know if there's a match
    # and the number of digits.
    logic = (
        match is not None and len(value) <= maxlen
    )
    
    return logic
class OptionsMenu(ttk.Frame):
    """This class is the main menu to select
    the different options"""
    def __init__(self, parent):
        # The parent is the window.
        self.parent = parent
        # We use it as master, the inheritance is applied
        super().__init__(parent,name='optionsMenu')
        
        # In this frame will be contained all the several sections
        self.options_menu_frame = ttk.Frame(self, name="options_menu_frame")
        self.options_menu_frame.pack(fill="both", expand=True)
        self.options_menu_frame.grid_columnconfigure(0, uniform="a", weight=2)
        self.options_menu_frame.grid_columnconfigure(1, uniform="a", weight=1)
        self.options_menu_frame.grid_rowconfigure((0, 1), weight=1)

        # All options of trigger: {start, time, stop}
        self.trigger_sections_main_frame = ttk.Labelframe(
            self.options_menu_frame, name="options", text="Trigger Settings"
        )
        self.trigger_sections_main_frame.grid(
            row=0, column=0, sticky="nesw", padx=10, pady=5
        )
        self.trigger_sections_main_frame.grid_columnconfigure(
            (0, 1, 2), uniform="a", weight=1
        )
        self.trigger_sections_main_frame.grid_rowconfigure(
            0, uniform="a", weight=1
        )

        #  The different sections, are going to be stored in this array
        self.trigger_sections_frame = []
        # The small pop-ups windows that appear when you set
        # either the start or the stop, using date and hour.
        # These are being stored in a dictionary
        self.selection_time = {"Set start": None, "Set stop": None}

        # The variables that are used to store these values,
        # It is for the the date, hour, minute and second
        # for both.
        self.selection_time_vars = {
            "set_start": [
                ttk.StringVar(
                    master=parent,
                    value=datetime.today().strftime(r"%x"),
                    name="date_start",
                ),
                ttk.IntVar(master=parent, value=0, name="hour_start"),
                ttk.IntVar(master=parent, value=0, name="minute_start"),
                ttk.IntVar(master=parent, value=0, name="second_start"),
            ],
            "set_stop": [
                ttk.StringVar(
                    master=parent,
                    value=datetime.today().strftime(r"%x"),
                    name="date_stop",
                ),
                ttk.IntVar(master=parent, value=0, name="hour_stop"),
                ttk.IntVar(master=parent, value=0, name="minute_stop"),
                ttk.IntVar(master=parent, value=0, name="second_stop"),
            ],
        }

        # The object "style" is used to modify 
        # the different styles as frames, labels, etcetera.
        self.style = ttk.Style()
        
        for name, background in zip(
            DATA_TRIGGER_SECTION["texts"], DATA_TRIGGER_SECTION["background"]
        ):
            self.style.configure(
                f"{name}" + ".TLabelframe",
                padding=8,
                relief="sunken",
                background=background,
            )
            self.style.configure(
                f"{name}" + ".TLabelframe.Label",
                font=("Comic Sans MS bold", 10),
                background=background,
                foreground="white",
            )
        self.style.configure("TLabelframe.Label", font=("Impact", 12))
        self.style.configure(
            "Time.TLabel", font=("Comic Sans MS bold", int(15))
        )

        self.time_values = [
            ttk.IntVar(name="minute_trigger", value=0),
            ttk.IntVar(name="second_trigger", value=0),
            ttk.IntVar(name="minute_avg_trigger", value=0),
            ttk.IntVar(name="second_avg_trigger", value=0),
        ]
    
        indx_trigger_values = 0
        indx_trigger_btns = 0
        self.trigger_values_comboboxes = []
        self.indx_array = []
        self.trigger_buttons = []

        for val in self.time_values:
            print(f"The type is -> {str(val)=='trigger_min'}")
            
        for i in range(3):
            self.trigger_sections_frame.append(
                ttk.Labelframe(
                    self.trigger_sections_main_frame,
                    name="trigger_section_" + str(i),
                    text=DATA_TRIGGER_SECTION["texts"][i],
                    style=f"{DATA_TRIGGER_SECTION['texts'][i]}.TLabelframe",
                    borderwidth=0,
                )
            )
            self.trigger_sections_frame[i].grid(
                row=0,
                column=DATA_TRIGGER_SECTION["column"][i],
                sticky="nesw",
                padx=10,
                pady=10,
            )
            self.trigger_sections_frame[i].rowconfigure(
                list(range(4)), uniform="a", weight=1
            )
            self.trigger_sections_frame[i].columnconfigure(
                list(range(2)), uniform="a", weight=1
            )

            for ind, option_name in enumerate(
                DATA_TRIGGER_SECTION["options"][i]
            ):
                plus = 1
                if i == 1:
                    print(f"Option name = {option_name}")
                    ind == 0 and self.trigger_sections_frame[i].rowconfigure(
                        list(range(4)), uniform="a", weight=1)  
                    ind == 0 and self.trigger_sections_frame[i].columnconfigure(
                        list(range(2)), uniform="a", weight=1) 
                    row_label = ind * 2
                    ttk.Label(
                        self.trigger_sections_frame[i],
                        text=option_name,
                        style="Time.TLabel",
                    ).grid(column=0, row=row_label, columnspan=2)
                
                    check_num_wrapper = (
                        self.parent.register(
                            lambda value, op, widget_name: 
                            _check_num(
                                self,
                                self.time_values,
                                       value,
                                       op,
                                       widget_name)),
                                       "%P",
                                       "%V",
                                       "%W",
                                       )
                    modified_option_name = (
                        option_name.lower().replace(" ", "").replace(".", "_")
                    )
                    try:
                        for range_time, boo, name in zip(
                            (SHORT_MIN_RANGE,SEC_RANGE),
                            range(2),
                            (
                                "minute_" + modified_option_name,
                                "second_" + modified_option_name,
                            ),
                        ):
                            print(f"Given name = {name}")
                            self.trigger_values_comboboxes.append(
                                ttk.Combobox(
                                    self.trigger_sections_frame[i],
                                    name=name,
                                    textvariable=self.time_values[
                                        indx_trigger_values
                                    ],
                                    state="normal",
                                    values=range_time,
                                    width=20,
                                    validate="all",
                                    validatecommand=check_num_wrapper,
                                )
                            )
                            self.indx_array.append(indx_trigger_values)
                            self.trigger_values_comboboxes[
                                indx_trigger_values
                            ].bind(
                                "<<ComboboxSelected>>",
                                self.update_combobox_value,
                            )
                            self.trigger_values_comboboxes[
                                indx_trigger_values
                            ].grid(column=boo, row=row_label + 1, padx=5)
                            indx_trigger_values += 1
                    except Exception as e:
                        print(e)
                    continue

                self.trigger_buttons.append(
                    ttk.Button(
                        self.trigger_sections_frame[i],
                        text=option_name,
                        style=DATA_TRIGGER_SECTION["style"][i],
                        state="normal",
                        cursor="hand2",
                    )
                )

                self.trigger_buttons[indx_trigger_btns].grid(
                    column=0,
                    row=ind * 2,
                    columnspan=2,
                    rowspan=2,
                    sticky="nsew",
                    pady=15,
                )
                indx_trigger_btns += 1

        self.trigger_buttons[0].config(command=self.start_fun)
        self.trigger_buttons[1].config(
            command=lambda: self.set_time(
                "Set start", 1, DATA_TRIGGER_SECTION["style"][0]
            )
        )
        self.trigger_buttons[2].config(command=self.stop_fun)
        self.trigger_buttons[3].config(
            command=lambda: self.set_time(
                "Set stop", 3, DATA_TRIGGER_SECTION["style"][2]
            )
        )
        plots_frame_section = ttk.Labelframe(
            self.options_menu_frame, name="plots_frame", text="Plots"
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
        self.style.configure(
            "TButton",
            font=("Comic Sans MS bold", 15),
            justify="center",
            compound="left",
        )
        self.symmetric_text(BUTTONS_INFO)
        self.buttons = []

        for i, button_info in enumerate(BUTTONS_INFO):
            # This is saved in an array because we want the images to appeared in the buttons.
            # If they are not saved, they disappear.
            self.images.append(Image.open(button_info[2]))
            # We resize and save the images in the array.
            self.images_tk.append(
                ImageTk.PhotoImage(self.images[i].resize(self.image_size))
            )
            # ImageTk.PhotoImage
            temp = ttk.Frame(plots_frame)

            self.buttons.append(
                ttk.Button(
                    plots_frame,
                    cursor="hand2",
                    text=button_info[0],
                    padding=(20, 0, 0, 0),
                    style="info",
                    image=self.images_tk[i],
                    compound=ttk.LEFT,
                )
            )
            self.buttons[i].grid(
                row=button_info[1][0],
                column=button_info[1][1],
                pady=10,
                padx=10,
                sticky="nsew",
            )

        self.parent.bind("<Configure>", self.resizing_images)
        self.changes_counter = 0
        self.changes_number = 2
        # This property lets us modify the number of changes the window suffer either it's moved or its size is changed.
        self.activate = True

        # Table Preview
        self.preview_table_frame = ttk.Labelframe(
            self.options_menu_frame, name="preview_table_frame", text="Preview"
        )
        self.preview_table_frame.grid(
            row=0, column=1, rowspan=2, sticky="nswe", pady=5, padx=5
        )
        self.preview_table = ttk.Treeview(self.preview_table_frame)
        self.preview_table.pack(expand=True, fill="both", padx=10, pady=10)

        self.print_value = 0

        # Time variables
        self.start_time = []
        self.stop_time = []
        for name in ("hour_", "minute_", "second_"):
            self.start_time.append(ttk.IntVar(name=name + "start", value=0))
            self.stop_time.append(ttk.IntVar(name=name + "stop", value=0))
        # Date variables
        self.start_date = datetime.now().strftime("%x")
        self.stop_date = self.start_date
    
    def update_combobox_value(self, ev):
        print(f"GETTING NUMBER => {ev.widget.selection_get()}")

    def start_fun(self):
        # Disabling trigger values widgets
        self.trigger_time_check()
        today = datetime.now()
        print(f"Today is {today.strftime('%c')}")

    def trigger_time_check(self):
        try:
            count = 0
            value = 0
            indx = 0
            values_array = [0, 0]
            factors_array = [60, 1]

            for val in self.time_values:
                value = value + val.get()
                print(f"value is {value}")
                print(f"count is {count}")
                values_array[indx] += val.get() * factors_array[count]

                if value == 0 and count == 1:
                    raise Exception

                if count == 1:
                    count = 0
                    value = 0
                    indx = 1
                    continue
                count = count + 1

            if values_array[0] > values_array[1]:
                raise Exception

        except Exception as e:
            print(f"You need to specify a correct time trigger")
            self.parent.focus_set()
            ttk.dialogs
            message = Messagebox()
            message.show_error(
                message="Sorry, you need to establish a correct time for the trigger",
                parent=self.parent,
            )

    def set_time(self, name, indx, style):
        self.selection_time[name] = SelectionTime(self.parent, self, name, style)
        self.selection_time[name].bind("<Destroy>", lambda ev: self.enable_btn(indx))
        self.print_value = 0
        self.trigger_buttons[indx].config(state=ttk.DISABLED)

    def enable_btn(self, indx):
        # If the main window is destroyed instead of the small one
        if self.print_value == 0:
            if self.trigger_buttons[indx].winfo_exists():
                self.trigger_buttons[indx].config(state=ttk.NORMAL)
            for key, val in self.selection_time_vars.items():
                print(f"{key} :-> ", end="")
                for i, x_val in enumerate(val):
                    print(f"{x_val.get()}", end="")
                    if i < len(val) - 1:
                        print(", ", end="")
                    else:
                        print(".")

        self.print_value = self.print_value + 1

    def stop_fun(self):
        # Disabling trigger values widgets
        print("You are inside the function stop")

    def fun_trigger(self, var):
        try:
            print(f"Var => {var.get()}")

        except Exception as e:
            print("Something occured")
            print(f"We have the next exception {e}")

    def set_changes_number(self, ev):
        self.parent.bind("<Configure>", self.resizing_images)
        if self.changes_counter >= 10:
            self.changes_number = 30

    def resizing_images(self, ev):
        parent_width = self.parent.winfo_width()
        if parent_width > 1:
            # We count the number of changes
            self.changes_counter += 1
            # This is done not to make the program so slow, because if it's constantly getting
            # the window's size, it can be slowed down.
            # If the counter is greater than the changes number
            if self.changes_counter > self.changes_number:
                if self.activate:
                    self.changes_number = 30
                    self.activate = False
                # We chose the width_factor since with the height_factor the letters were bigger than the buttons.
                width_factor = parent_width / self.parent._MIN_WIN_WIDTH
                width_factor = 1.4 if width_factor > 1.4 else width_factor
                # We reset changes_counter
                self.changes_counter = 0
                # We determine the width and height of the image using a the width_factor, and speed is added.
                width_tk = np.ceil(
                    self.image_size[0] * width_factor,
                    dtype=int,
                    casting="unsafe",
                )
                height_tk = np.ceil(
                    self.image_size[1] * width_factor,
                    dtype=int,
                    casting="unsafe",
                )
                # Each image is resized.
                try:
                    for i, current_image in enumerate(self.images):
                        self.images_tk[i] = ImageTk.PhotoImage(
                            current_image.resize((width_tk, height_tk))
                        )
                        self.buttons[i].configure(image=self.images_tk[i])
                except Exception as error:
                    print("An exception is encountered -> ", error)
                # The font size's button is changed.
                font_size = int(width_factor * 14)
                self.style.configure(
                    "TButton", font=("Comic Sans MS bold", font_size)
                )
                self.style.configure(
                    "Time.TLabel",
                    font=("Comic Sans MS bold", int(font_size * 0.9)),
                )

    def symmetric_text(self, var):
        total_max = 0
        set_sizes = []
        for text in var:
            for item in text[0].split("\n"):
                set_sizes.append(len(item))

        total_max = max(set_sizes)
        print(total_max)


class SelectionTime(ttk.Toplevel):
    def __init__(self, window, father, name, cal_style):
        self.window = window
        self.father = father
      
        super().__init__()
        height = self.winfo_screenheight() * 0.12
        width = self.winfo_screenwidth() * 0.35
        self.pos_x = (
            self.window.winfo_x() + self.window.winfo_width() / 2 - width / 2
        )
        self.pos_y = (
            self.window.winfo_y() + self.window.winfo_height() / 2 - height / 2
        )
        self.geometry(
            f"{width:.0f}x{height:.0f}+{self.pos_x:.0f}+{self.pos_y:.0f}"
        )
        self.name = name.lower().replace(' ','_')
        self.resizable(False, False)
        self.title(name)
        self.rowconfigure(0, weight=7, uniform="a")
        self.rowconfigure(1, weight=3, uniform="a")
        self.columnconfigure(0, weight=2, uniform="a")
        self.columnconfigure(1, weight=3, uniform="a")

        # 
        print(f"The name is {name.lower().replace(' ','_') }")
        
    
        # check_num_wrapper
        check_num_wrapper = (
            self.father.register(lambda value, op, widget_name: 
                                 _check_num(self,
                                     self.father.selection_time_vars,
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

        style.map(
            "TCheckbutton",
            indicatorcolor=[
                ("pressed", "#ececec"),
                ("selected", "#db1b1b"),
                ("!selected", "#10dfed"),
            ],
        )
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
            print(indx)
            self.sel_time_frames.append(
                ttk.Labelframe(
                    self, text=title, style="trigger.TLabelframe", padding=10
                )
            )
            self.sel_time_frames[indx].grid(
                row=0, column=indx, sticky="news", padx=10
            )

        self.date = ttk.StringVar(
            name="date", value=datetime.today().strftime(r"%x")
        )

        # Selecting the date
        calendar = ttk.DateEntry(self.sel_time_frames[0], bootstyle=cal_style)
        calendar.entry.config(
            textvariable=self.father.selection_time_vars[self.name][0]
        )
        calendar.pack()

        self.start_time_frame = ttk.Frame(self.sel_time_frames[1])
        self.start_time_frame.pack(fill="both", expand=True)
        self.start_time_frame.rowconfigure(0, weight=1)
        self.start_time_frame.columnconfigure((0, 1, 2), weight=1, uniform="a")

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
            print(values)
            time_section = ttk.Labelframe(
                self.start_time_frame,
                text=ABBR_TIME[values[0][:values[0].find('_')]],
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
        print("Date : %s" % self.date.get())

    def set_date_time(self, date):

        self.date.set(date)
        print("Date modified to : %s" % self.date.get())

    def get_time_values(self):

        for val in self.father.selection_time_vars[self.name]:
            print(f"{val} = {val.get()}")

    def set_time_values(self, values):

        for val, value in zip(
            self.father.selection_time_values[self.name], values
        ):
            val.set(value)
            print(f"{val} = {val.get()}")


class Menu(ttk.Frame):

    def __init__(self, parent):
        self.parent = parent
        super().__init__(parent)
        # Menu
        self.menu = ttk.Menu(parent)
        parent.configure(menu=self.menu)
        self.menuContainer = ttk.Menu(self, tearoff=False)
        self.menuContainer.add_command(
            label="New", command=lambda: self.new_file()
        )
        self.menuContainer.add_command(
            label="Open", command=lambda: self.open_file()
        )
        # With "File" you can open a previous table
        # or making a new one
        self.menu.add_cascade(label="File", menu=self.menuContainer)

        # Submenugit

    def open_file(self):
        # --TODO-- You have to find a way to let the last file's directory to be the init directory
        self.open_dialog = filedialog.askopenfilename(
            title="Open a file",
            filetypes=(
                ("All", "*.*"),
                ("Text files", "*.txt"),
                ("Comma-separated values", "*.csv"),
            ),
        )

        print(self.open_dialog)

    def humidity(self, screen_width, screen_height):
        self.humidity_chart = Humidity(screen_width, screen_height)

    def temperatures(self, screen_width, screen_height):
        self.temperatures_chart = Temperature(
            screen_width, screen_height
        )  # type:ignore

    def psychrometric(self):
        self.psychrometric_chart = Psychrometric()
        self.plot_psy = self.psychrometric_chart

    def weight(self, screen_width, screen_height):
        self.weight_chart = Weight(screen_width, screen_height)

    def all(self, screen_width, screen_height):
        self.all = All(screen_width, screen_height)  # type:ignore

    def new_file(self):
        # --TODO-- It has to start an empty
        pass


class Psychrometric(Monitor):
    def __init__(self):
        super().__init__()
        self.psy_height = self._SCREEN_HEIGHT * 0.42
        self.psy_width = self._SCREEN_WIDTH * 0.33
        self.geometry(
            f"{self.psy_width:.0f}x{self.psy_height:.0f}\
                      +{(self._INIT_POS_X-(self._MIN_WIN_WIDTH+self.psy_width)/2+15):.0f}+{(self._INIT_POS_Y):.0f}"
        )
        print(f"Psy width = {self._MIN_WIN_WIDTH},Psy height = {self._MIN_WIN_HEIGHT}")
        self.title("Psychrometric Chart")


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


class Weight(Monitor):
    def __init__(self, screen_width, screen_height):
        super().__init__()


class Humidity(ttk.Window):
    def __init__(self, screen_width, screen_height):
        super().__init__()
        self.win_width = 100
        self.win_height = 200
        self.geometry(
            f"{self.win_width:.0f}x{self.win_height:.0f}\
                      +{(self.screen_width/2-self.win_width/2):.0f}+{(self.screen_height/2-self.win_height/2):.0f}"
        )  # type: ignore


class Temperature(ttk.Window):
    def __init__(self):
        super().__init__()


class All:
    def __init__(self):
        self.temperature = Temperature()
        self.psychrometric = Psychrometric()
        self.humidity = Humidity()  # type: ignore
        self.psychrometric = Psychrometric()

monitor=Monitor()