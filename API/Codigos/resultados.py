# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 08:30:03 2022

@author: Nikky
"""

import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.io as pio
# from PIL import Image, ImageOps
import os
from datetime import datetime
import time

#Crear libreria
t = datetime.fromtimestamp(time.time())
year = t.year
month = t.month
name = r"C:\Users\ADMIN\Documents\API\Resultados gráficos\ " + "Resultados gráficos" + "_" + str(year) + "_" + str(month)


namep = "UN_meteo_station_" + str(year) + "_" + str(month)
xl_name = namep+".xlsx"

if not os.path.exists(name):
    os.mkdir(name)
    
#leer dataframe
datos=pd.read_excel(r"C:\Users\ADMIN\Documents\API\Bases de datos\_"+ xl_name, sheet_name='Sensor1',header=0,index_col = "TimeStamp")

#constantes
millas_a_metros=1609
farenhait_a_centigrados=(-32)*5/9
hora_a_segundo=1/3600

#editar dataframe
datos["Velocidad_media_del_viento_últimos_10_min_(m/s)"]=datos["wind_speed_avg_last_10_min"]*millas_a_metros*hora_a_segundo
datos["Humedad_(%)"]=datos["hum"]
datos["Índice_UV"]=datos["uv_index"]
datos["Índice_de_calor_(°C)"]=(datos["heat_index"]-32)*(5/9)
datos["Temperatura_(°C)"]=(datos["temp"]-32)*(5/9)
datos["Radiación_solar_(W/m2)"]=datos["solar_rad"]

#crear figuras
fig1=px.line(datos,x=datos.index,y="Velocidad_media_del_viento_últimos_10_min_(m/s)",title="Datos en tiempo real")
pio.write_image(fig1,name+"/Viento.png",engine='kaleido', format="png")

fig2=px.line(datos,x=datos.index,y="Humedad_(%)",title="Datos en tiempo real")
pio.write_image(fig2,name+"/Humedad.png",engine='kaleido', format="png")

fig3=px.line(datos,x=datos.index,y="Índice_UV",title="Datos en tiempo real")
pio.write_image(fig3,name+"/Índice_UV.png",engine='kaleido', format="png")


fig4=px.line(datos,x=datos.index,y="Índice_de_calor_(°C)",title="Datos en tiempo real")
pio.write_image(fig4,name+"/Índice_calor.png",engine='kaleido', format="png")


fig5=px.line(datos,x=datos.index,y="Temperatura_(°C)",title="Datos en tiempo real")
pio.write_image(fig5,name+"/Temperatura.png",engine='kaleido', format="png")


fig6=px.line(datos,x=datos.index,y="Radiación_solar_(W/m2)",title="Datos en tiempo real")
pio.write_image(fig6,name+"/Radicación_solar.png",engine='kaleido', format="png")

# Datos_meteorologicos=datos.iloc[:,[62,63,64,65,66,67]]

# Datos_meteorologicos.to_excel(r'C:\Users\Nikky\OneDrive\Documentos\GitHub\Salida_grafica_EMS\Datos_meteorologicos.xlsx')
# pio.orca.config.executable = "C:\ProgramData\Anaconda3"

#Datos_f=pd.read_excel(r'C:\Users\Nikky\OneDrive\Documentos\GitHub\MR_Operacion\API\Salida grafica EMS\Datos_meteorologicos.xlsx',index_col=0)
# fig3=plt.plot(datos.index,datos.wind_dir_at_hi_speed_last_10_min)
# plt.savefig("Resultados/fig3.png")

# pio.write_image(fig3,"pesultados/fig3.png",engine='orca', format="png")


