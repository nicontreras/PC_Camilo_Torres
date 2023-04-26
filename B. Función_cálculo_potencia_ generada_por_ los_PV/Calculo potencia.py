# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 22:29:36 2022

@author: ADMIN
"""

#Librerías

import pandas as pd
from datetime import datetime
import time
from datetime import timedelta
from time import strptime, strftime, mktime, gmtime
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import load_model
from statsmodels.tsa.seasonal import seasonal_decompose
from numpy import radians as rad
from numpy import cos as cos
from numpy import sin as sin
import numpy as np

#Funciones

### Función para cálcular la generación de los paneles solares
def power_PV_calculation(df_meteo, PVtype, azimut, inc_panel, lat, PV_tecnology ):

    df = df_meteo.copy()

    azimut, inc_panel = rad(azimut), rad(inc_panel)

    df["Day of year"] = df.index.day_of_year
    df['Hour'] = df.index.hour
    df['decl'] = 23.45*np.sin(2*np.pi*(284+df['Day of year'].to_numpy())/365) #angulo de declinación solar
    df['omega'] = 15*(df['Hour']- 12)# angulo de la hora solar

    decl = rad(df['decl'].to_numpy())#angulo de declinación solar
    omega = rad(df['omega'].to_numpy())# angulo de la hora solar
    lat_r = rad(lat) #latitud

    df['tetha'] = np.arccos(np.sin(decl)*np.sin(lat_r)*(np.cos(inc_panel)-np.cos(azimut)) +
                            np.cos(decl)*np.cos(lat_r)*np.cos(inc_panel)*np.cos(omega) +
                            np.cos(decl)*np.sin(lat_r)*np.sin(inc_panel)*np.cos(azimut)*np.cos(omega) +
                            np.cos(decl)*np.sin(inc_panel)*np.sin(azimut)*np.sin(omega))  #angulo de incidencia del sol 

    df['zenit'] = np.arccos(np.cos(lat_r)*np.cos(decl)*np.cos(omega) +
                        np.sin(lat_r)*np.sin(decl)) #angulo zenith

    Rb = np.cos(df['tetha'].to_numpy())/np.cos(df['zenit'].to_numpy()) #corrección de irradiancia

    df['IRR'] = df['solar_rad'].to_numpy()*Rb*1.5
    
    df['IRR'] = df['IRR'].where(df['IRR']>0, 0)
    
    #modelo de king
    Tm = df['IRR'].values*np.exp(-3.47-0.0594*df['wind_speed_hi_last_2_min'].values)+df['temp'].values

    T_panel = Tm+(df['IRR'].values/1000)*3

    P_mpp = pd.DataFrame(index = df.index, columns = PVtype.columns)

    df['P_mpp'] = (PVtype.loc['P_stc',PV_tecnology]*(1+(PVtype.loc['Tc_Pmax',PV_tecnology]/100)*(T_panel-25))*(df['IRR'].values/1000)) #potencia unidad normal
                
    return df

#lectura de datos meterologicos

t = datetime.fromtimestamp(time.time())
year = t.year
month = t.month
day= t.day
name = "UN_meteo_station_" + str(year) + "_" + str(month)
xl_name = name+".xlsx"

#lectura de últimos 60 datos 
df_weather = pd.read_excel(r"C:\Users\ADMIN\Documents\API\Bases de datos\_"+ xl_name ,sheet_name='Sensor1',header=0,index_col=0 )
df_weather=df_weather.iloc[len(df_weather)-60:len(df_weather)]

#conversión a unidades del sistema universidad 
df_prediccion= pd.DataFrame()
millas_a_metros=1609.34
hora_a_segundo=1/3600
farenhait_a_centigrados=(-32)*5/9

df_prediccion["solar_rad"]=df_weather["solar_rad"]
df_prediccion["wind_speed_hi_last_2_min"]=df_weather["wind_speed_hi_last_2_min"]*millas_a_metros*hora_a_segundo
df_prediccion["temp"]=(df_weather["temp"]-32)*(5/9)

df_prediccion["TS"]=df_prediccion.index
TS=pd.date_range(start=df_prediccion.iloc[-60,3] , freq="15min", periods=60)
df_prediccion.set_index(TS,inplace=True)
df_prediccion=df_prediccion.drop(['TS'], axis=1)
df_prediccion=df_prediccion.resample("15min",convention="start").asfreq()
df_prediccion=df_prediccion.interpolate(method="spline",order=3)
df_prediccion=df_prediccion.fillna(0.0)
df_prediccion["TS"]=df_prediccion.index

##Predicción irradiancia

#tratamiendo dataframe
df_prediccion_irr=df_prediccion
decomp_irr = seasonal_decompose(df_prediccion_irr['solar_rad'], period = 24, extrapolate_trend='freq')
df_prediccion_irr['trend'] = decomp_irr.trend
df_prediccion_irr['seasonal'] = decomp_irr.trend
df_prediccion_irr['resid'] = decomp_irr.resid
df_prediccion_irr["Hora del dia"] = df_prediccion_irr.index.hour
df_prediccion_irr=df_prediccion_irr.iloc[len(df_prediccion_irr)-40:len(df_prediccion_irr)]

#escalar datos
f_columns_irr = ['trend','seasonal','resid','temp',"Hora del dia"] 
y_columns_irr = ['solar_rad']

f_transformer_irr = MinMaxScaler(feature_range=(0, 1))
y_transformer_irr = MinMaxScaler(feature_range=(0, 1))

f_transformer_irr = f_transformer_irr.fit(df_prediccion_irr[f_columns_irr].to_numpy())
y_transformer_irr = y_transformer_irr.fit(df_prediccion_irr[y_columns_irr].to_numpy())

df_prediccion_irr_escal = f_transformer_irr.transform(df_prediccion_irr[f_columns_irr].to_numpy())
x_pred_irr = []
x_pred_irr.append(df_prediccion_irr_escal)
x_pred_irr = np.array(x_pred_irr)


#predecir
model_irr = load_model('RN_IRR_3h.h5')
y_pred_inv_irr = model_irr.predict(x_pred_irr)
y_pred_irr = y_transformer_irr.inverse_transform(y_pred_inv_irr).flatten()
y_pred_irr=np.where(np.array(y_pred_irr)>0, np.array(y_pred_irr),0)
df_pred= pd.DataFrame()
df_pred["solar_rad"]=y_pred_irr

TS=pd.date_range(start=df_prediccion.iloc[-1,3]+timedelta(minutes=15) , freq="15min", periods=12)
df_pred.set_index(TS,inplace=True)

##Predicción viento

#tratamiendo dataframe
df_prediccion_viento=df_prediccion
decomp_viento = seasonal_decompose(df_prediccion_viento['wind_speed_hi_last_2_min'], period = 24, extrapolate_trend='freq')
df_prediccion_viento['trend'] = decomp_viento.trend
df_prediccion_viento['seasonal'] = decomp_viento.trend
df_prediccion_viento['resid'] = decomp_viento.resid
df_prediccion_viento["Hora del dia"] = df_prediccion_viento.index.hour
df_prediccion_viento=df_prediccion_viento.iloc[len(df_prediccion_viento)-20:len(df_prediccion_viento)]

#escalar datos
f_columns_viento = ['trend','seasonal','resid','temp',"Hora del dia"] 
y_columns_viento = ['wind_speed_hi_last_2_min']

f_transformer_viento = MinMaxScaler(feature_range=(0, 1))
y_transformer_viento = MinMaxScaler(feature_range=(0, 1))

f_transformer_viento = f_transformer_viento.fit(df_prediccion_viento[f_columns_viento].to_numpy())
y_transformer_viento = y_transformer_viento.fit(df_prediccion_viento[y_columns_viento].to_numpy())

df_prediccion_viento_escal = f_transformer_viento.transform(df_prediccion_viento[f_columns_viento].to_numpy())
x_pred_viento = []
x_pred_viento.append(df_prediccion_viento_escal)
x_pred_viento = np.array(x_pred_viento)


#predecir
model_viento = load_model('RN_V_3h.h5')
y_pred_inv_viento = model_viento.predict(x_pred_viento)
y_pred_viento = y_transformer_viento.inverse_transform(y_pred_inv_viento).flatten()
y_pred_viento=np.where(np.array(y_pred_viento)>0, np.array(y_pred_viento),0)
df_pred["wind_speed_hi_last_2_min"]=y_pred_viento


##Predicción temperatura

#tratamiendo dataframe
df_prediccion_temp=df_prediccion
decomp_temp = seasonal_decompose(df_prediccion_temp['temp'], period = 24, extrapolate_trend='freq')
df_prediccion_temp['trend'] = decomp_temp.trend
df_prediccion_temp['seasonal'] = decomp_temp.trend
df_prediccion_temp['resid'] = decomp_temp.resid
df_prediccion_temp["Hora del dia"] = df_prediccion_temp.index.hour
df_prediccion_temp=df_prediccion_temp.iloc[len(df_prediccion_temp)-30:len(df_prediccion_temp)]

#escalar datos
f_columns_temp = ['trend','seasonal','resid',"Hora del dia"] 
y_columns_temp = ['temp']

f_transformer_temp = MinMaxScaler(feature_range=(0, 1))
y_transformer_temp = MinMaxScaler(feature_range=(0, 1))

f_transformer_temp = f_transformer_temp.fit(df_prediccion_temp[f_columns_temp].to_numpy())
y_transformer_temp = y_transformer_temp.fit(df_prediccion_temp[y_columns_temp].to_numpy())

df_prediccion_temp_escal = f_transformer_temp.transform(df_prediccion_temp[f_columns_temp].to_numpy())
x_pred_temp = []
x_pred_temp.append(df_prediccion_temp_escal)
x_pred_temp = np.array(x_pred_temp)


#predecir
model_temp = load_model('RN_T_3h.h5')
y_pred_inv_temp = model_temp.predict(x_pred_temp)
y_pred_temp = y_transformer_temp.inverse_transform(y_pred_inv_temp).flatten()
#y_pred_temp=np.where(np.array(y_pred_viento)>0, np.array(y_pred_viento),0)
df_pred["temp"]=y_pred_temp

#Calculo de potencia generada por un panles solar
df_PVtype = pd.read_excel(r'C:\Users\ADMIN\Documents\D. Datos del programa de diseño\Características equipos.xlsx',sheet_name='PV',header=0,index_col=1)
PV_tecnology="JASolar_450W"
lat, lon = 4.60971, -74.08175
azimut= 0
ele=5

salida_potencia_dc=power_PV_calculation(df_pred, df_PVtype, azimut, ele, lat, PV_tecnology )
salida_potencia_dc=salida_potencia_dc.reset_index().reset_index()
salida_potencia_dc.to_csv(r"C:\Users\ADMIN\Documents\EMS\salida_potencia_dc.csv")

