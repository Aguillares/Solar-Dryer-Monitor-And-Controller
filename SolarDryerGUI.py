# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 15:30:37 2024

This is a code created for GUI in Raspberry Pi 2B to monitor
and control a solar dryer in Chapingo Autonomous University

@author: Hernández Aguillares Antonio
"""
import csv
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import numpy as np
import matplotlib.pyplot as plt


class Monitor(tk.Tk):
    def __init__(self):
        super().__init__() #If you don't put this, you are not going to be able to make the window
        self.screen_height = self.winfo_screenheight()
        self.screen_width = self.winfo_screenwidth()
        self.init_path = r"D:\Users\perro\Thesis\init_path.txt"
        with FileManager(self.init_path).read() as file:
             
            self.read_line = file.readline()
            print(f"Psyco Func {self.read_line}")

        with FileManager(self.read_line).read() as file:
            headers=file.readline()
            print(headers)
            
            dict_reader = csv.reader(file,delimiter = ',')
            for row in dict_reader:
                print(row)
            for row in dict_reader:
                print(row[0])

        self.win_height =self.screen_height*0.4
        self.win_width =self.screen_width*0.35
        self.win_x = self.screen_width/2-self.win_width/2
        self.win_y = self.screen_height/2-self.win_height/2
        print(f"Monitor width = {self.win_width},Monitor height = {self.win_height}")
        self.geometry(f"{self.win_width:.0f}x{self.win_height:.0f}+{(self.win_x):.0f}+{(self.win_y):.0f}")
        self.title("Solar Dryer")
        
        # Run
    def menu(self):
        # Widgets
        self.menu = Menu(self)
        

class Menu(ttk.Frame):

    def __init__(self,parent):
        super().__init__(parent)
        
        
        # self.init_dir_path = 
        # self.init_file_path =
        # Menu
        self.menu = tk.Menu(parent)
        parent.configure(menu = self.menu)
        self.menuContainer = tk.Menu(self,tearoff = False)
        self.menuContainer.add_command(label = "New", command = lambda : self.new_file())
        self.menuContainer.add_command(label = "Open", command = lambda : self.open_file())
        self.menu.add_cascade(label = 'File', menu =  self.menuContainer)
        self.menu.add_command(label = 'Humidity', command = lambda: self.humidity())
        self.menu.add_command(label = 'Temperature', command = lambda: self.temperatures())
        self.menu.add_command(label = 'Humidity', command = lambda: self.humidity())
        self.menu.add_command(label = 'Weight', command = lambda: self.weight())
        self.menu.add_command(label = 'Psychrometry', command = lambda: self.psychrometric())
        self.menu.add_command(label = 'All Charts', command = lambda: self.all())

        # Submenu

        # Placing

        self.pack()
    
    def open_file(self):
        # --TODO-- You have to find a way to let the last file's directory to be the init directory
        self.open_dialog = filedialog.askopenfilename(title = 'Open a file',
                                                      filetypes=(('Text files','*.txt'),
                                                                 ('Comma-separated values','*.csv')))
        print(self.open_dialog)



    def humidity(self,screen_width,screen_height):
        self.humidity_chart = Humidity(screen_width,screen_height)
        
    def temperatures(self,screen_width,screen_height):
        self.temperatures_chart = Temperature(screen_width,screen_height)
    def psychrometric(self):
            

        self.psychrometric_chart = Psychrometric()
        self.plot_psy = self.psychrometric_chart
        
        
    def weight(self,screen_width,screen_height):
        self.weight_chart = Weight(screen_width,screen_height)

    def all(self,screen_width,screen_height):
        self.all = All(screen_width,screen_height)

    def new_file(self):
        # --TODO-- It has to start an empty
        pass

class Psychrometric(Monitor):
    def __init__(self):
        super().__init__()
        self.psy_height = self.screen_height*0.42
        self.psy_width = self.screen_width*0.33
        self.geometry(f"{self.psy_width:.0f}x{self.psy_height:.0f}+{(self.win_x-(self.win_width+self.psy_width)/2+15):.0f}+{(self.win_y):.0f}")
        print(f"Psy width = {self.win_width},Psy height = {self.win_height}")
        self.title("Psychrometric Chart")


class FileManager(object):
    def __init__(self, file_whole_path):
        self.file_whole_path = file_whole_path

    def append(self):
        self.file = open(self.file_whole_path, 'a')
        return self.file
    
    def read(self):
        self.file = open(self.file_whole_path,'r+')
        return self.file

    def over_write(self):
        self.file = open(self.file_whole_path,'w+')
        return self.file

    def detect(self):
        self.file = open(self.file_whole_path,'x')
        return self.file

    def __exit__(self, *args):
        self.file.close()

class Weight(Monitor):
    def __init__(self,screen_width,screen_height):
        super().__init__()

class Humidity(tk.Tk,):
    def __init__(self,screen_width,screen_height):
        super().__init__()
        self.geometry(f"{self.win_width:.0f}x{self.win_height:.0f}+{(self.screen_width/2-self.win_width/2):.0f}+{(self.screen_height/2-self.win_height/2):.0f}")

class Temperature(tk.Tk):
    def __init__(self):
        super().__init__()

class All():
    def __init__(self):
        self.temperature = Temperature()
        self.psychrometric = Psychrometric()
        self.humidity = Humidity()
        self.psychrometric = Psychrometric()


monitor = Monitor()
monitor.menu()
monitor.mainloop()