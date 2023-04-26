# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 12:21:38 2022

@author: ADMIN
"""

#liberías

import pandas as pd
from datetime import datetime
import time
from datetime import timedelta
from time import strptime, strftime, mktime, gmtime
import numpy as np
from numpy import random
from sklearn.preprocessing import MinMaxScaler
from keras.models import load_model
from statsmodels.tsa.seasonal import seasonal_decompose
import holidays_co

#lectura de datos meterologicos

t = datetime.fromtimestamp(time.time())
year = t.year
month = t.month
day= t.day
name = "UN_meteo_station_" + str(year) + "_" + str(month)
xl_name = name+".xlsx"

#lectura de últimos 60 datos 
df_weather = pd.read_excel(r"C:\Users\ADMIN\Documents\API\Bases de datos\_"+ xl_name ,sheet_name='Sensor1',header=0,index_col=0 )
df_weather=df_weather.iloc[len(df_weather)-192:len(df_weather)]

#conversión a unidades del sistema universidad 
df_prediccion= pd.DataFrame()

farenhait_a_centigrados=(-32)*5/9


df_prediccion["temp"]=(df_weather["temp"]-32)*(5/9)
df_prediccion["TS"]=df_prediccion.index


TS=pd.date_range(start=df_prediccion.iloc[-192,1], freq="15min", periods=192)
df_prediccion.set_index(TS,inplace=True)

df_prediccion=df_prediccion.drop(['TS'], axis=1)
df_prediccion=df_prediccion.resample("15min",convention="start").asfreq()
df_prediccion=df_prediccion.interpolate(method="spline",order=3)
df_prediccion["TS"]=df_prediccion.index

##Predicción demanda

#lectura de datos hospital
Datos_demanda_hospital15m = pd.read_excel('hospital marzo 15m.xlsx', skiprows=0,header=0,index_col=0)
Datos_demanda_hospital15m = Datos_demanda_hospital15m.iloc[len(Datos_demanda_hospital15m)-192:len(Datos_demanda_hospital15m)]

#tratamiendo dataframe
df_prediccion_demanda=df_prediccion

df_prediccion_demanda["Demanda"] = (Datos_demanda_hospital15m.Carga/(max(Datos_demanda_hospital15m.Carga)/5000)).to_numpy()
df_prediccion_demanda["Hora del dia"] = df_prediccion_demanda.index.hour
df_prediccion_demanda['Dia de la semana'] = df_prediccion_demanda.index.dayofweek
df_prediccion_demanda['Dia del mes'] = df_prediccion_demanda.index.day

Festivos = pd.DataFrame(holidays_co.get_colombia_holidays_by_year(df_prediccion_demanda.index[0].year))
Festivos.set_index('date',inplace=True)
df_prediccion_demanda['Festivos'] = np.zeros(len(df_prediccion_demanda))  
df_prediccion_demanda.index
for i in df_prediccion_demanda.index:
            if i.year != Festivos.index[0].year:
                Festivos = pd.DataFrame(holidays_co.get_colombia_holidays_by_year(i.year))    
                Festivos.set_index('date',inplace=True)
            for j in Festivos.index:
                if i.day == j.day and i.month == j.month:
                    df_prediccion_demanda.loc[i,'Festivos'] = 1    
 
    
 
#escalar datos
f_columns_demanda = ['Hora del dia','Dia de la semana','Dia del mes',"temp","Festivos"]
y_columns_demanda = ['Demanda']

f_transformer_demanda = MinMaxScaler(feature_range=(0, 1))
y_transformer_demanda = MinMaxScaler(feature_range=(0, 1))

f_transformer_demanda = f_transformer_demanda.fit(df_prediccion_demanda[f_columns_demanda].to_numpy())
y_transformer_demanda = y_transformer_demanda.fit(df_prediccion_demanda[y_columns_demanda].to_numpy())


df_interes_demanda_escal = f_transformer_demanda.transform(df_prediccion_demanda[f_columns_demanda].to_numpy())
x_pred_demanda = []
x_pred_demanda.append(df_interes_demanda_escal)
x_pred_demanda = np.array(x_pred_demanda)

#predecir
model_demanda = load_model('RN_Demanda_3h.h5')
y_pred_inv_demanda = model_demanda.predict(x_pred_demanda)
y_pred_demanda = y_transformer_demanda.inverse_transform(y_pred_inv_demanda).flatten()

df_pred_demanda= pd.DataFrame()
df_pred_demanda["Cargas_criticas"]=y_pred_demanda

TS=pd.date_range(start=df_prediccion_demanda.iloc[-1,1]+timedelta(minutes=15) , freq="15min", periods=12)
df_pred_demanda.set_index(TS,inplace=True)


###Indisponibildad red
Grid_dis=np.ones(12)

###Indisponibilidad generador
Gen_dis=np.ones(12)

# ###Disponibilidad inversor
Inv_dis=np.ones(12)

##Perfil de puerto carreño - cargas críticas
df_perfiles=df_pred_demanda
df_perfiles["Cargas_criticas"]=df_pred_demanda["Cargas_criticas"]
df_perfiles["Cargas_no_esenciales"]=df_pred_demanda["Cargas_criticas"]*2
df_perfiles["Disponibilidad_red"]=Grid_dis
df_perfiles["Disponibilidad_generador"]=Gen_dis
df_perfiles["Disponibilidad_inversor"]=Inv_dis
df_perfiles=df_perfiles.reset_index().reset_index()

#Dataframe exportado a la carpeta del EMS

df_perfiles.to_csv(r"C:\Users\ADMIN\Documents\EMS\df_perfiles.csv")


