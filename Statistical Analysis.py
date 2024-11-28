from pandas import read_csv
import pandas as pd
import matplotlib.pyplot as plt


plt.style.use('ggplot')

class Analyser():
    def __init__(self,name):
        self.colours = ['black','red','blue','green']
        self.analize_data(name)
        self.organize_data()
        self.get_stats()
        self.visualize_data()
        
        print(self.colours)

    def variable_detection(self,variable):
        var=variable[variable.rfind('_'):]
        print(var)
        if '_T' in var:
            return 'Temperature'
        elif '_RH' in var:
            return 'Relative Humidity'
        elif '_P' in var:
            return 'Pressure'
        else:
            return None

    def sensor_detection(self,sensor):
        if 'BME280' in sensor:
            return 'BME280'
        elif 'SHT31' in sensor:
            return 'SHT31'
        elif 'MLX90614' in sensor:
            return 'MLX90614'
    def mean_detection(self,var):
        if 'Mean' in var:
            return 'Mean'
    def error_detection(self,var):
        if '_E_' in var:
            return 'Error'
    def total_detection(self,var):
        if 'Total' in var:
            return 'Total'
    
    def analize_data(self,name):
        self.data_ = read_csv(name)
        self.data_time = self.data_.iloc[:,0:4]
        self.data_sensors = self.data_.iloc[:,4:-2]
        self.index_range = list(range(self.data_sensors.count()[0]))
        # We transpose the dataframe to get group the data by the variable and sensor's type
        self.data_sensors = self.data_sensors.T
        self.groups = self.data_sensors.groupby([self.sensor_detection,self.variable_detection]).groups
        self.ind = list(self.groups)
        print(self.groups)
        
    
    def organize_data(self):
        self.order_data_sensors = []
        self.diff_info = []
        self.error_vs_var = []
        for i in self.ind:
            print(i[1])
            self.index = self.groups[i]
            # Getting the variable name : {P,RH or T}
            self.sensor_name = self.index[0][:self.index[0].find('_')]
            self.var_name = self.index[0][self.index[0].rfind('_')+1:]
            self.temp = self.data_sensors.loc[self.index].T
            self.var_mean= self.temp.mean(axis=1).rename(self.sensor_name+'_Total_Mean_'+self.var_name)

            self.order_data_sensors.append(pd.concat([self.temp,self.var_mean],axis=1).round(2))
            self.diff_var = []
            for per in range(1,len(self.temp.columns)):
                self.diff_temp = abs(self.temp.diff(periods = per,axis=1).iloc[:,per:]).copy()
                header = []
                for j in range(1,len(self.diff_temp.columns)+1):
                    header.append(str(j)+'-'+str(j+per))

                self.diff_temp.index.name = i[0]+ ' '+ i[1] + ' |E|'
                self.diff_temp=self.diff_temp.set_axis(header, axis = 'columns')
                self.diff_var.append(self.diff_temp)
            try:
                self.diff_var = pd.concat(self.diff_var,axis =1)
                self.diff_var_mean= self.diff_var.mean(axis=1).rename(self.sensor_name+'_E_Mean_'+self.var_name)
                self.diff_var=pd.concat([self.diff_var,self.diff_var_mean],axis=1).round(2)
                self.diff_info.append(self.diff_var)
                self.error_vs_var.append(pd.concat([self.var_mean,self.diff_var_mean],axis = 1))
            except Exception as e:
                print(f"You are not working properly with the library {e}")
    def get_stats(self):
        self.diff_stats = []
        for diff_sel in self.diff_info:
            name=diff_sel.index.name
            diff_sel = pd.concat([diff_sel.describe(),diff_sel.describe().mean(axis=1)],axis=1).rename(columns = {0:'Mean'})
            diff_sel.index.name = name + ' Stats'
            self.diff_stats.append(diff_sel)

    def visualize_data(self):
        print(self.colours)
        print(self.order_data_sensors)
        print(self.diff_info)
        print(self.error_vs_var)
        grouped =pd.concat(self.error_vs_var,axis=1)
        grouped=grouped.T
        total_group = grouped.groupby([self.variable_detection,self.total_detection]).groups
        ind_total = list(total_group.keys())
        print(total_group)
        print(total_group.keys())
        grouped=grouped.T
        print(grouped)
        col_i = 0
        for ind in range(0,len(total_group.keys()),2):
            tuple_x = ind_total[ind]
            tuple_y = ind_total[ind+1]
            label_x = tuple_x[0]
            print(total_group[tuple_x])
            print(total_group[tuple_y])
            print(grouped[total_group[tuple_x]])
            print(grouped[total_group[tuple_y]])
            print(label_x)
            
            ax_=grouped.plot(x =list(total_group[tuple_x])[0], 
                             y = list(total_group[tuple_y])[0],
                             xlabel=label_x,
                             ylabel='Error',
                             kind='scatter',
                             color=self.colours[col_i])
            
            for number in range(1,len(total_group[tuple_x])):
                col_i += 1
                ax_=grouped.plot(x =list(total_group[tuple_x])[number],
                                  y = list(total_group[tuple_y])[number],
                                  xlabel=label_x,
                                  ylabel='Error',
                                  kind='scatter',
                                  ax =ax_,c=self.colours[col_i])
            
            plt.legend(list(total_group[tuple_y]))
            
            
           
        plt.show()  




# # Comparing the different variables
# for sensor_data in order_data_sensors:
#     pass

if __name__ == '__main__':
    analizer = Analyser('Sensors_data_room.csv')
    analizer = Analyser('Sensors_data_outside.csv')
    analizer = Analyser('Sensors_data_Chamber.csv')
    analizer = Analyser('Sensors_data_Chamber2.csv')
    print("Hello")