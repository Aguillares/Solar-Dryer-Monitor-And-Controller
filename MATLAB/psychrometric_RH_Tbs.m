table = readtable("D:/Users/perro/Documents/Thesis/Process/Codes/Mean_Data.xlsx");
Tbs_BME280 = table{:,'BME280_Mean_T'};
RH_BME280 = table{:,'BME280_Mean_RH'};
P = table{:,'BME280_Mean_P'}*100;
disp(size(P))
disp(P)
Tbs_SHT31 = table{:,'SHT31_Mean_T'};
RH_SHT31 = table{:,'SHT31_Mean_RH'};

Pvs_BME280 = saturationVapourPressure(Tbs_BME280)';
disp(Pvs_BME280)
Pvs_SHT31 = saturationVapourPressure(Tbs_SHT31)';

Pv_BME280 = Pvs_BME280  .*RH_BME280*0.01;
Pv_SHT31 = Pvs_SHT31  .*RH_SHT31*0.01;
disp(size(Pv_SHT31))
disp(Pv_BME280)

W_BME280 = humidityRatio(Pv_BME280,P)'
W_SHT31 = humidityRatio(Pv_SHT31,P)'

fprintf("W_BME280 max =  %.3f, min =  %.3f\n",max(W_BME280),min(W_BME280))
fprintf("W_SHT31 max =  %.3f, min =  %.3f",max(W_SHT31),min(W_SHT31))
plot(Tbs_BME280,W_BME280,"Color",'r')
hold on
plot(Tbs_SHT31,W_SHT31,"Color",'b')
xlabel("Temperature")
ylabel("W")
legend("BME280","SHT31")
hold off