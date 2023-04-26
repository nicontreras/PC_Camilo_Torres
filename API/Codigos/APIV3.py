import collections
import hashlib
import hmac
import time
import pandas as pd
from pandas.io.json import json_normalize
import json
import requests
import glob 
from datetime import datetime
from pandas import ExcelWriter
import urllib.request
import numpy as np

##Función para subir las principales variables
def update_thingspeak_principal(data):
    
    base_url = "https://api.thingspeak.com/update?api_key=LP6D76CT7CS7KJJ9"
    
    for i in data.keys():
        base_url += "&" + i + "=" + str(np.round(data[i],3))
    
    urllib.request.urlopen(base_url)
 
##Función para subir las variables de lluvia
def update_thingspeak_rain(data):
    
    base_url = "https://api.thingspeak.com/update?api_key=K4TFYE5C5C8KXUUU"
    
    for i in data.keys():
        base_url += "&" + i + "=" + str(np.round(data[i],3))
    
    urllib.request.urlopen(base_url)

##Función para subir las variables de viento
def update_thingspeak_wind(data):
    
    base_url = "https://api.thingspeak.com/update?api_key=LNCABRZ9Y6QPKBQY"
    
    for i in data.keys():
        base_url += "&" + i + "=" + str(np.round(data[i],3))
    
    urllib.request.urlopen(base_url)
    
#Datos generales de la estación meteorológica
def Get_Station_data(): 
    api_key= "nizaer1vpdocygwtk1h8afowshqkixmg"
    api_secret= "dn2wdxnzzsh2ghtnfmfo5yrdvnx8rq1d"
    t= int(time.time())

    cadena_id="api-key"+str(api_key)+"t"+str(t)

    # codificación
    byte_key = api_secret.encode() 
    message = cadena_id.encode()

    # HMAC como una cadena hexadecimal
    api_signature = hmac.new(byte_key, message, hashlib.sha256).hexdigest()
    URL= "https://api.weatherlink.com/v2/stations?api-key="+api_key+"&t="+str(t)+"&api-signature="+api_signature
    with requests.Session() as s:
        Station_data=s.get(URL).json()

    return(Station_data)

#ID de la estación meteorológica
def Get_Station_ID(): 
    api_key= "nizaer1vpdocygwtk1h8afowshqkixmg"
    api_secret= "dn2wdxnzzsh2ghtnfmfo5yrdvnx8rq1d"
    t= int(time.time())

    cadena_id="api-key"+str(api_key)+"t"+str(t)

    # codificación
    byte_key = api_secret.encode() 
    message = cadena_id.encode()

    # HMAC como una cadena hexadecimal
    api_signature = hmac.new(byte_key, message, hashlib.sha256).hexdigest()
    URL= "https://api.weatherlink.com/v2/stations?api-key="+api_key+"&t="+str(t)+"&api-signature="+api_signature
    with requests.Session() as s:
        Station_data=s.get(URL).json()
    Datos_station = Station_data['stations']
    station_id= Datos_station[0]['station_id']
    return(station_id)



#Obtener datos de las condiciones actuales
def Get_Sensors_Data(station_id): 
    api_key= "nizaer1vpdocygwtk1h8afowshqkixmg"
    api_secret= "dn2wdxnzzsh2ghtnfmfo5yrdvnx8rq1d"
    t= int(time.time())

    cadena_datos_reales="api-key"+str(api_key)+"station-id"+str(station_id)+"t"+str(t)
    cadena_datos_reales

    # codificación
    byte_key = api_secret.encode() 
    message2 = cadena_datos_reales.encode()

    # HMAC como una cadena hexadecimal
    api_signature2 = hmac.new(byte_key, message2, hashlib.sha256).hexdigest()
    URL2= "https://api.weatherlink.com/v2/current/"+str(station_id)+"?api-key="+api_key+"&t="+str(t)+"&api-signature="+api_signature2
    with requests.Session() as s:
        Sensor_Data=s.get(URL2).json()

    return(Sensor_Data)


#Obtener datos historicos de la estación meteorológica (necesita permisos)

def Get_Hist_Data(station_id,start_timestamp,end_timestamp):
    #Ejemplos de como crear los datos de start_timestamp y end_timestamp:
    #end_timestamp=int(datetime.strptime("16-03-2022 16:00:00","%d-%m-%Y %H:%M:%S").timestamp())
    #start_timestamp=int(datetime.strptime("16-03-2022 15:00:00","%d-%m-%Y %H:%M:%S").timestamp())
    api_key= "nizaer1vpdocygwtk1h8afowshqkixmg"
    api_secret= "dn2wdxnzzsh2ghtnfmfo5yrdvnx8rq1d"
    t= int(time.time())
    cadena_datos_historicos="api-key"+str(api_key)+"end-timestamp"+str(end_timestamp)+"start-timestamp"+str(start_timestamp)+"station-id"+str(station_id)+"t"+str(t)
    # codificación
    byte_key = api_secret.encode() 
    message3 = cadena_datos_historicos.encode()
    # HMAC como una cadena hexadecimal
    api_signature3 = hmac.new(byte_key, message3, hashlib.sha256).hexdigest()
    URL3= "https://api.weatherlink.com/v2/historic/"+str(station_id)+"?api-key="+api_key+"&t="+str(t)+"&start-timestamp="+str(start_timestamp)+"&end-timestamp="+str(end_timestamp)+"&api-signature="+api_signature3
    with requests.Session() as s:
        resultado3=s.get(URL3).json()

    return(resultado3)


#Obtener datos de los sensores 
def Get_n_Sensor_Data(S_Data,n): #n from 0 to 3
    df = json_normalize(S_Data['sensors'][n]['data'])
    df['ts'] = datetime.fromtimestamp(df['ts'])
    df.index = df['ts']
    df = df.drop('ts',1)
    df.insert(0, 'TimeStamp', df.index)
    return (df)


#Lectura de archivos .xlsx    
files = glob.glob(r'C:\Users\ADMIN\Documents\API\Bases de datos\*.xlsx')

#Condición creación archivo o sobreescribir archivo
t = datetime.fromtimestamp(time.time())
year = t.year
month = t.month
day= t.day
name = "UN_meteo_station_" + str(year) + "_" + str(month)
xl_name = name+".xlsx"
a = 1





if day == 1:
    a = 0

if a == 0:
    S_Data = Get_Sensors_Data(Get_Station_ID())
    sensor_1 = Get_n_Sensor_Data(S_Data,0)
    sensor_2 = Get_n_Sensor_Data(S_Data,1)
    sensor_3 = Get_n_Sensor_Data(S_Data,2)
    sensor_4 = Get_n_Sensor_Data(S_Data,3)
    writer = ExcelWriter(r"C:\Users\ADMIN\Documents\API\Bases de datos\_"+ xl_name)
    sensor_1.to_excel(writer, sheet_name='Sensor1', index=False)
    sensor_2.to_excel(writer, sheet_name='Sensor2', index=False)
    sensor_3.to_excel(writer, sheet_name='Sensor3', index=False)
    sensor_4.to_excel(writer, sheet_name='Sensor4', index=False)
    writer.save()
    
elif a==1: 
    sensor_1 = pd.read_excel(r"C:\Users\ADMIN\Documents\API\Bases de datos\_"+ xl_name ,sheet_name='Sensor1' )
    sensor_2 = pd.read_excel(r"C:\Users\ADMIN\Documents\API\Bases de datos\_"+ xl_name ,sheet_name='Sensor2' )
    sensor_3 = pd.read_excel(r"C:\Users\ADMIN\Documents\API\Bases de datos\_"+ xl_name ,sheet_name='Sensor3' )
    sensor_4 = pd.read_excel(r"C:\Users\ADMIN\Documents\API\Bases de datos\_"+ xl_name ,sheet_name='Sensor4' )
    S_Data = Get_Sensors_Data(Get_Station_ID())
    
    sensor_1 = sensor_1.append(Get_n_Sensor_Data(S_Data,0))
    sensor_2 = sensor_2.append(Get_n_Sensor_Data(S_Data,1))
    sensor_3 = sensor_3.append(Get_n_Sensor_Data(S_Data,2))
    sensor_4 = sensor_4.append(Get_n_Sensor_Data(S_Data,3))
    writer = ExcelWriter(r"C:\Users\ADMIN\Documents\API\Bases de datos\_"+ xl_name)
    sensor_1.to_excel(writer, sheet_name='Sensor1', index=False)
    sensor_2.to_excel(writer, sheet_name='Sensor2', index=False)
    sensor_3.to_excel(writer, sheet_name='Sensor3', index=False)
    sensor_4.to_excel(writer, sheet_name='Sensor4', index=False)
    writer.save()

millas_a_metros=1609.34
hora_a_segundo=1/3600
farenhait_a_centigrados=(-32)*5/9


data_sensor1 = Get_n_Sensor_Data(S_Data,0)
#editar dataframe

##Carga de variables principales
data_thingspeak_principal = {}
data_thingspeak_principal["field1"]=data_sensor1["rx_state"].values[0] #configured radio receiver state o mean that the station is receiving information
data_thingspeak_principal["field2"]=data_sensor1["hum"].values[0] #most recent valid humidity **(%RH)**
data_thingspeak_principal["field3"]=data_sensor1["uv_index"].values[0]# most recent UV index **(Index)**
data_thingspeak_principal["field4"]=(data_sensor1["heat_index"].values[0]-32)*(5/9)#**(°F)**
data_thingspeak_principal["field5"]=(data_sensor1["temp"].values[0]-32)*(5/9)# most recent valid temperature **(°F)**
data_thingspeak_principal["field6"]=data_sensor1["solar_rad"].values[0]#most recent solar radiation **(W/m²)**
data_thingspeak_principal["field7"]=(data_sensor1["thw_index"].values[0]-32)*(5/9)# **(°F)**
data_thingspeak_principal["field8"]=(data_sensor1["thsw_index"].values[0]-32)*(5/9)# **(°F)**
update_thingspeak_principal(data_thingspeak_principal)     

##Carga de variables fluviometro
data_thingspeak_rain = {}
data_thingspeak_rain["field1"]=data_sensor1["rain_rate_hi_last_15_min_mm"].values[0]*hora_a_segundo #highest rain rate over last 15 min **(counts/hour)**
data_thingspeak_rain["field2"]=data_sensor1["rainfall_year_mm"].values[0]#total rain count since first of user-chosen month at local midnight **(counts)**
data_thingspeak_rain["field3"]=data_sensor1["rainfall_last_60_min_mm"].values[0]#total rain count for last 60 min **(counts)**
data_thingspeak_rain["field4"]=data_sensor1["rainfall_monthly_mm"].values[0]#total rain count since first of month at local midnight **(counts)**
data_thingspeak_rain["field5"]=data_sensor1["rainfall_daily_mm"].values[0]#total rain count since local midnight **(counts)**
data_thingspeak_rain["field6"]=data_sensor1["rain_storm_mm"].values[0]#total rain count since last 24 hour long break in rain **(counts)**
data_thingspeak_rain["field7"]=data_sensor1["rain_rate_hi_mm"].values[0]*hora_a_segundo#highest rain rate over last 1 min **(counts/hour)**
data_thingspeak_rain["field8"]=data_sensor1["rainfall_last_15_min_mm"].values[0]#total rain count over last 15 min **(counts)**
update_thingspeak_rain(data_thingspeak_rain) 


##Carga de variables anemometro
data_thingspeak_wind = {}
data_thingspeak_wind["field1"]=data_sensor1["wind_speed_hi_last_2_min"].values[0]*millas_a_metros*hora_a_segundo # maximum wind speed over last 2 min **(mph)**
data_thingspeak_wind["field2"]=data_sensor1["wind_dir_scalar_avg_last_1_min"].values[0]#scalar average wind direction over last 1 min **(°degree)**
data_thingspeak_wind["field3"]=(data_sensor1["wind_chill"].values[0]-32)*(5/9)#**(°F)**
data_thingspeak_wind["field4"]=data_sensor1["wind_speed_last"].values[0]*millas_a_metros*hora_a_segundo# most recent valid wind speed **(mph)**
data_thingspeak_wind["field5"]=data_sensor1["wind_speed_avg_last_2_min"].values[0]*millas_a_metros*hora_a_segundo #average wind speed over last 2 min **(mph)**
data_thingspeak_wind["field6"]=data_sensor1["wind_dir_last"].values[0]#most recent valid wind direction **(°degree)**
data_thingspeak_wind["field7"]=data_sensor1["wind_dir_scalar_avg_last_2_min"].values[0]#scalar average wind direction over last 2 min **(°degree)**
data_thingspeak_wind["field8"]=data_sensor1["wind_speed_avg_last_1_min"].values[0]*millas_a_metros*hora_a_segundo#average wind speed over last 1 min **(mph)**
update_thingspeak_wind(data_thingspeak_wind) 





