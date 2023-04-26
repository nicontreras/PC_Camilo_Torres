# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 16:12:35 2022

@author: ADMIN
"""

#Librerias
from random import random
from unittest import skip
from pyomo.environ import * #optimización
import pandas as pd #manejo de datos
import plotly.graph_objects as go
import numpy as np
from  pyomo import environ as pym
import os

#creacion del modelo
model = AbstractModel()

###Conjuntos de indice
model.T = Set()                                       #Conjunto de tiempo
#--------------------------------------------------------------------------

###Parámetros indexados en T

model.Ld_critical=Param(model.T,within=NonNegativeReals)      # Perfil de demanda del sistema de emergencia
model.Ld=Param(model.T,within=NonNegativeReals)      # Perfil de demanda del sistema de equipos
model.PD_av=Param(model.T,within=NonNegativeReals)    # Disponibilidad del generador
model.PGrid_av=Param(model.T,within=NonNegativeReals) # Disponibilidad de la red
model.Ppv_gen=Param(model.T,within=NonNegativeReals)  # Perfil de generación de un panel solar



#--------------------------------------------------------------------------
###Parámetros no indexados
model.reserva=Param(within=NonNegativeReals)           # Porcentaje de la demanda del sistema de emergencia que las baterías deben tener como reserva.
model.delta_reserva=Param(within=NonNegativeReals)     # Tiempo que el ESS debe tener carga
model.Ld_critical_max=Param(within=NonNegativeReals)   # Potencia de pico máximo de la carfa crítica
#Paneles
model.X_pvIC=Param(within=NonNegativeIntegers)          # Cantidad de paneles solares conectados al inversor cargador
model.X_pvOnG=Param(within=NonNegativeIntegers)          # Cantidad de paneles solares conectados al inversor On-grid
model.C_curt=Param(within=NonNegativeReals)            # Penalización por no vender energía en $/kWh
model.n_mppt=Param(within=NonNegativeReals)            # Eficiencia del controlador de carga

#ESS
model.X_bat=Param(within=NonNegativeIntegers)         # Cantidad de baterías instaladas en la microrred
model.Cap_nom=Param(within=NonNegativeReals)           # Capacidad nominal de las baterías en Wh
model.n=Param(within=NonNegativeReals)                 # Eficiencia de carga y descarga del ESS
model.I_dch_ch=Param(within=NonNegativeReals)          # Corriente de carga y descarga recomendada del ESS en A
model.SOC0=Param(within=NonNegativeReals)              # Estado de carga del ESS en el anterior paso de tiempo en %.
model.Deltat=Param(within=NonNegativeReals)            # Pasos de tiempo
model.Deltac=Param(within=NonNegativeReals)            # Conversión de kW a W
model.Dod_max=Param(within=NonNegativeReals)           # Profundidad máxima de descarga
model.C_rate=Param(within=NonNegativeReals)            # Tasa de carga y descarga recomendada en (A/Ah)

#Red
model.C_sell=Param(within=NonNegativeReals)            # Costo de energía proveniente de la red en $/kWh.
model.C_buy=Param(within=NonNegativeReals)             # Costo de intercambio de energía con la red interna del hospital en $/kWh
model.P_Grid_nom=Param(within=NonNegativeReals)               # Acometida del hospital en W
model.n_t=Param(within=NonNegativeReals)               # Eficiencia del transformador

#Generador
model.C_D=Param(within=NonNegativeReals)          # Costo asociado al diesel en $/L
model.P_D_max=Param(within=NonNegativeReals)           # Máxima potencia del generador en W
model.P_D_min=Param(within=NonNegativeReals)          # Mínima potencia de operación del generador en %
model.Ramp_up=Param(within=NonNegativeReals)           # Rampa subida
model.Ramp_down=Param(within=NonNegativeReals)         # Rampa bajada
model.PD_0=Param(within=NonNegativeReals)              # Valor inicial del generador
model.F_min=Param(within=NonNegativeReals)             # Consumo mínimo de L del generador en funcionamiento
model.F_max=Param(within=NonNegativeReals)             # Consumo máximo de L del generador en funcionamiento

#Inversor cargador
model.X_IC=Param(within=NonNegativeIntegers)            # Cantidad de inversores cargadores instalados en la microrred
model.V_bat_nom=Param(within=NonNegativeReals)          # Tensión nominal de cada batería
model.I_inIC_max=Param(within=NonNegativeReals)            # Corriente máxima de entrada del inversor cargador en A
model.I_chIC_max=Param(within=NonNegativeReals)          # corriente máxima de carga de baterías en A
model.P_IC_out=Param(within=NonNegativeReals)            # Potencia de salida del inversor cargador en W
model.n_IC_acdc=Param(within=NonNegativeReals)           # Máxima eficiencia DC/AC y AC/DC del inversor cargador

#Inversor On-grid
model.X_OnG=Param(within=NonNegativeIntegers)         # Cantidad de inversores On-Grid instalados en la microrred
model.P_OnG_out=Param(within=NonNegativeReals)            # Potencia de salida del inversor On-grid en W
model.n_OnG_dcac=Param(within=NonNegativeReals)           # Máxima eficiencia DC/AC del inversor On-grid

#--------------------------------------------------------------------------
###Variables

#Variables continuas

##Generador + red
model.PGrid=Var(model.T, domain=NonNegativeReals)        # Potencia de la red de baja tensión en el hospital en W
model.PGridL2=Var(model.T, domain=NonNegativeReals)      # Potencia de la red de baja tensión en el hospital hacia L2 en W
model.PGridI=Var(model.T, domain=NonNegativeReals)       # Potencia de la red de baja tensión en el hospital hacia el inversor en W


model.PD=Var(model.T, domain=NonNegativeReals)          # Potencia generada por el generador auxiliar en W
model.PDL2=Var(model.T, domain=NonNegativeReals)        # Potencia generada por el generador auxiliar hacia L2 en W
model.PDI=Var(model.T, domain=NonNegativeReals)         # Potencia generada por el generador auxiliar hacia el inversor en W

#####nodo AC1
model.PAC1=Var(model.T, domain=NonNegativeReals)          # Potencia saliente del nodo AC,1 hacia el inversor en W
model.PAC1L2=Var(model.T, domain=NonNegativeReals)        # Potencia saliente del nodo AC,1 hacia el sistema de emergencia en W

#####inversor cargador entrada
model.PAC1AC2=Var(model.T, domain=NonNegativeReals)       # Potencia saliente del inversor(que viene del nodo AC,1)hacia el sistema de emergencia en W
model.PAC1DC=Var(model.T, domain=NonNegativeReals)        # Potencia saliente del inversor(que viene del nodo AC,1)hacia las baterías en W
model.Dcurt_critical = Var(model.T, domain=NonNegativeReals)      # Potencia no suministrada al sistema de emergencia
model.Dcurt = Var(model.T, domain=NonNegativeReals)      # Potencia no suministrada al sistema de equipos


#PANELES CONECTADOS AL INVERSOR CARGADOR
model.PpvIC = Var(model.T, domain=NonNegativeReals)         # Potencia generada por los paneles solares conectados al inversor cargador en W
model.PpvICCurt = Var(model.T, domain=NonNegativeReals)     # Potencia sin usar de los paneles solares conectados al inversor cargador en W


#####nodo DC
model.DCI = Var(model.T, domain=NonNegativeReals)         # Potencia generada por los paneles solares (que viene luego del MPPT) al inversor cargador en W
model.pvICB = Var(model.T, domain=NonNegativeReals)         # Potencia generada por los paneles solares (que viene luego del MPPT) a las baterías en W

#####inversor cargador salida

model.DCAC2 = Var(model.T, domain=NonNegativeReals)        # Potencia generada por los paneles solares (que viene del inversor cargador) al sistema de emergencia en W
model.pvICL2 = Var(model.T, domain=NonNegativeReals)         # Potencia generada por los paneles solares (que viene del inversor cargador) al sistema de equipos en W

#PANELES CONECTADOS AL INVERSOR ON-GRID
model.PpvOnG = Var(model.T, domain=NonNegativeReals)          # Potencia generada por los paneles solares conectados al inversor On-Grid en W
model.PpvOnGCurt = Var(model.T, domain=NonNegativeReals)      # Potencia sin usar de los paneles solares
model.PpvOnGAC2 = Var(model.T, domain=NonNegativeReals)       # Potencia generada por los paneles solares luego de pasar por el inversor On-grid hacia el sistema de emergencia en W

#BATERIAS

model.SOC = Var(model.T, domain=NonNegativeReals)           # Estado de carga
model.PBDCAC2= Var(model.T, domain=NonNegativeReals)       # Potencia activa de las baterías al sistema de emergencia luego de pasar por el inversor cargador en W
model.Pdch = Var(model.T, domain=NonNegativeReals)          # Potencia activa de las baterías al inversor cargador en W
model.Pch = Var(model.T, domain=NonNegativeReals)          # Potencia activa de carga a las baterías  en W

#Variables binarias/Toma de decisiones logicas (0,1)
model.Bch = Var(model.T, within=Binary)                   # Carga efectiva de baterías (1 = recibe Pot) (0 = no recibe pot)
model.Bdch = Var(model.T, within=Binary)                   # Descarga efectiva de baterías (1 = entrega pot) (0 = no entrega pot)
model.GenOn = Var(model.T, within=Binary)                   # Generador encendido o apagado


#--------------------------------------------------------------------------
###Función objetivo 
def obj_rule(model):#regla(Función python)

    return (sum( model.C_buy*model.PGridI[t] - model.C_sell*model.pvICL2[t]+model.C_curt*model.Dcurt_critical[t] for t in model.T)*model.Deltac + sum(model.C_D*(((model.F_max-model.F_min)/model.P_D_max)*model.PDI[t] + model.F_min*model.GenOn[t]) for t in model.T))*model.Deltat      

model.Obj=Objective(rule=obj_rule,sense=minimize)   

#--------------------------------------------------------------------------
###Restricciones

##Paneles solares
# arreglo 1 
def Balance_pv1_rule(model,t):#,t para todo t en T
    return model.PpvIC[t]+model.PpvICCurt[t] ==model.Ppv_gen[t]*model.X_pvIC
model.Balance_pv1=Constraint(model.T,rule=Balance_pv1_rule)

def Balance_pv_nodo_DC_rule(model,t):#,t para todo t en T
    return model.PpvIC[t]*model.n_mppt ==model.DCI[t]+model.pvICB[t]
model.Balance_pv_nodo_DC=Constraint(model.T,rule=Balance_pv_nodo_DC_rule)

def Balance_pv_inversor_cargador_rule(model,t):#,t para todo t en T
    return model.DCI[t]*model.n_IC_acdc ==model.DCAC2[t]+model.pvICL2[t]
model.Balance_pv_inversor_cargador=Constraint(model.T,rule=Balance_pv_inversor_cargador_rule)



# arreglo 2    

def Balance_pv2_rule(model,t):#,t para todo t en T
    return model.PpvOnG[t]+model.PpvOnGCurt[t] ==model.Ppv_gen[t]*model.X_pvOnG
model.Balance_pv2=Constraint(model.T,rule=Balance_pv2_rule)

def Curtailment_pv_rule(model,t):#,t para todo t en T
    return model.PpvICCurt[t] + model.PpvOnGCurt[t]<= model.Ld_critical[t]
model.Curtailment_pv=Constraint(model.T,rule=Curtailment_pv_rule)

def Flujo_pv2_sistema_emergencia_rule(model,t):#,t para todo t en T
    return model.PpvOnGAC2[t]==model.PpvOnG[t]*model.n_OnG_dcac
model.Flujo_pv2_sistema_emergencia=Constraint(model.T,rule=Flujo_pv2_sistema_emergencia_rule)


##GENERADOR
#Potencia máxima del generador
def Dis_gen_rule(model,t):#,t para todo t en T
    return model.PD[t]<=model.P_D_max*model.PD_av[t]
model.Dis_gen=Constraint(model.T,rule=Dis_gen_rule)

#Potencia minima del generador
def Min_gen_rule(model,t):#,t para todo t en T
    return model.PD[t]>=model.P_D_max*model.P_D_min*model.GenOn[t]
model.Min_gen=Constraint(model.T,rule=Min_gen_rule)

#Rampa del generador de encendido
def Ramp_up_gen_rule(model,t):#,t para todo t en T
    if t==0:
        return model.PD[t]-model.PD_0<=model.Ramp_up*model.P_D_max
    else:
        return model.PD[t]-model.PD[t-1]<=model.Ramp_up*model.P_D_max
model.Ramp_up_gen=Constraint(model.T,rule=Ramp_up_gen_rule)

#Rampa del generador de apagado
def Ramp_dn_gen_rule(model,t):#,t para todo t en T
    if t==0:
        return Constraint.Skip
    else:
        return model.PD[t-1]-model.PD[t]<=model.Ramp_down*model.P_D_max
model.Ramp_dn_gen=Constraint(model.T,rule=Ramp_dn_gen_rule)

##NODO 1 

#Red
def Dis_redF_rule(model,t):#,t para todo t en T
    return model.PGrid[t] +model.PD[t] ==model.PAC1L2[t]+ model.PAC1[t]
model.Dis_redF=Constraint(model.T,rule=Dis_redF_rule)

def Dis_red_rule(model,t):#,t para todo t en T
    return model.PGrid[t] <= model.P_Grid_nom*model.PGrid_av[t]*model.n_t
model.Dis_red=Constraint(model.T,rule=Dis_red_rule)

def generacion_red_rule(model,t):#,t para todo t en T
    return model.PGrid[t] == model.PGridL2[t]+model.PGridI[t]
model.generacion_red=Constraint(model.T,rule=generacion_red_rule)

def generacion_diesel_rule(model,t):#,t para todo t en T
    return model.PD[t] == model.PDL2[t]+model.PDI[t]
model.generacion_diesel=Constraint(model.T,rule=generacion_diesel_rule)

def Balance_nodo_AC1_rule(model,t):#,t para todo t en T
    return model.PGridI[t] +model.PDI[t] == model.PAC1[t]
model.Balance_nodo_AC1=Constraint(model.T,rule=Balance_nodo_AC1_rule)

def Balance_nodo_L2_rule(model,t):#,t para todo t en T
    return model.PGridL2[t] +model.PDL2[t] == model.PAC1L2[t]
model.Balance_nodo_L2=Constraint(model.T,rule=Balance_nodo_L2_rule)

def Balance_AC1_inversor_cargador_rule(model,t):#,t para todo t en T
    return model.PAC1[t] ==model.PAC1AC2[t]+model.PAC1DC[t]
model.Balance_AC1_inversor_cargador=Constraint(model.T,rule=Balance_AC1_inversor_cargador_rule)



##Carga

#Alimentar el sistema de emergencia
def Balance_sistema_emergencia_rule(model,t):#,t para todo t en T
    return model.DCAC2[t] + model.PBDCAC2[t] +model.PAC1AC2[t]+ model.Dcurt_critical[t] + model.PpvOnGAC2[t] == model.Ld_critical[t]
model.Balance_sistema_emergencia=Constraint(model.T,rule=Balance_sistema_emergencia_rule)

# salida potencia del victron
def Ppv_l2_rule2(model,t):
    return model.DCAC2[t] + model.PBDCAC2[t]+model.PAC1AC2[t] <= model.X_IC*model.P_IC_out 
model.Ppv_l2=Constraint(model.T,rule=Ppv_l2_rule2)

# salida potencia del fronius
def Ppv_l1_rule2(model,t):
    return model.PpvOnGAC2[t] <= model.X_OnG*model.P_OnG_out 
model.Ppv_l1=Constraint(model.T,rule=Ppv_l1_rule2)



#Alimentar el sistema de equipos
def Balance_sistema_equipos_rule(model,t):#,t para todo t en T
    return model.pvICL2[t] + model.PAC1L2[t] + model.Dcurt[t]== model.Ld[t]
model.Balance_sistema_equipos=Constraint(model.T,rule=Balance_sistema_equipos_rule)


##Baterías
#Capacidad máxima de las baterías
def Batt_socmax_rule(model,t):#
    return model.SOC[t] <= model.Cap_nom*model.X_bat
model.Batt_socmax=Constraint(model.T,rule=Batt_socmax_rule)

#Potencia de carga de las baterías
def Batt_ch_rule(model,t):#
    return model.PAC1DC[t]*model.n_IC_acdc + model.pvICB[t] == model.Pch[t]
model.Batt_ch=Constraint(model.T,rule=Batt_ch_rule)

#Almacenamiento
def SOC_rule(model,t):#,t para todo t en T
    if t==0:
        return model.SOC[t] == model.Cap_nom*model.X_bat*model.SOC0 + (model.n*(model.Pch[t]) - model.Pdch[t]/(model.n))*model.Deltat
    else:
        return model.SOC[t] == model.SOC[t-1] + (model.n*(model.Pch[t]) - model.Pdch[t]/(model.n))*model.Deltat
model.SOC_t=Constraint(model.T,rule=SOC_rule)


#Capacidad mínima de las baterías
def Batt_socmin_rule(model,t):#
    return model.SOC[t] >= model.X_bat*model.Cap_nom*(1-model.Dod_max)
model.Batt_socmin=Constraint(model.T,rule=Batt_socmin_rule)


# Carga de baterías  
def Charge_max_rule(model,t):
    return model.Pch[t]  <= model.X_bat*model.Cap_nom*model.C_rate
model.Charge_max=Constraint(model.T,rule=Charge_max_rule)

# Estado único de batería
def Ceff_rule1(model,t):#
     return model.Pch[t] <= 100e6*model.Bch[t]
model.Ceff=Constraint(model.T,rule=Ceff_rule1)



#Potencia de carga de baterías 
def PpvB_charge_rule(model,t):#
    return model.PAC1DC[t]*model.n_IC_acdc <= model.X_IC*model.I_chIC_max*model.V_bat_nom
model.PpvB_charge=Constraint(model.T,rule=PpvB_charge_rule)


# Descarga de la batería 
def PBL_lims_rule1(model,t):
    return model.Pdch[t] <= model.X_bat*model.Cap_nom*model.C_rate
model.PBL_lims1=Constraint(model.T,rule=PBL_lims_rule1)

def Deff_rule1(model,t):#
    return model.Pdch[t] <= 100e6*model.Bdch[t]
model.Deff=Constraint(model.T,rule=Deff_rule1)

#alimentar la demanda desde las baterias
def PBL_lims_rule5(model,t):
    return model.PBDCAC2[t] == model.Pdch[t]*model.n_IC_acdc
model.PBL_lims5=Constraint(model.T,rule=PBL_lims_rule5)


# Potencia de descarga de la batería
def PBL_lims_rule2(model,t):
    return model.Pdch[t] <= model.X_IC*model.I_inIC_max*model.V_bat_nom
model.PBL_lims2=Constraint(model.T,rule=PBL_lims_rule2)

def Bstate_rule(model,t):#
    return model.Bch[t] + model.Bdch[t] <= 1
model.Bstate=Constraint(model.T,rule=Bstate_rule)


#Restricción de reserva potencia 
def reserve_rule(model,t):
    return (model.P_D_max*model.GenOn[t]-model.PD[t])+(model.I_dch_ch*model.V_bat_nom*model.X_bat-model.Pdch[t]+model.Pch[t]) >= (model.Ld_critical[t]-model.Dcurt_critical[t])*model.reserva*model.PGrid_av[t]
    
model.reserve=Constraint(model.T,rule=reserve_rule)

# Restricción de reserva energia
def reserve_rule_energy(model,t):
    if t<=1/model.Deltat*3:
         return Constraint.Skip
    else:
        return model.SOC[t]-model.X_bat*model.Cap_nom*(1-model.Dod_max) >=model.Ld_critical_max*model.reserva*model.delta_reserva*model.PGrid_av[t]
model.reserve_energy=Constraint(model.T,rule=reserve_rule_energy)


#--------------------------------------------------------------------------
###Creación de la instancia
instance=model.create_instance("Datos.dat")
#instance.pprint()

#--------------------------------------------------------------------------
###Resultados

# #--- para gurobi ---
results=SolverFactory('gurobi').solve(instance, tee=True )
#--- para cplex ---
#os.environ['NEOS_EMAIL'] = 'nicontrerasal@unal.edu.co'
#results=pym.SolverManagerFactory('neos').solve(instance, opt='cplex', tee=True )
##---            ---


#Conocer el valor de las variables

#a sistema de emergencia
DCAC2=[instance.DCAC2[t].value for t in instance.T]
PBDCAC2=[instance.PBDCAC2[t].value for t in instance.T]
PAC1AC2=[instance.PAC1AC2[t].value for t in instance.T]
Dcurt_critical=[instance.Dcurt_critical[t].value for t in instance.T]
PpvOnGAC2=[instance.PpvOnGAC2[t].value for t in instance.T]

#a baterias 
PAC1DC=[instance.PAC1DC[t].value for t in instance.T]
pvICB=[instance.pvICB[t].value for t in instance.T]
Pdch=[instance.Pdch[t].value for t in instance.T]
    
    
#paneles on-grid
PpvOnG=[instance.PpvOnG[t].value for t in instance.T]
PpvOnGCurt=[instance.PpvOnGCurt[t].value for t in instance.T]
    
#paneles acople DC
PpvIC=[instance.PpvIC[t].value for t in instance.T]
PpvICCurt=[instance.PpvICCurt[t].value for t in instance.T]


#a sistema de equipos
pvICL2=[instance.pvICL2[t].value for t in instance.T]
Dcurt=[instance.Dcurt[t].value for t in instance.T]
PGridL2=[instance.PGridL2[t].value for t in instance.T]
PDL2=[instance.PDL2[t].value for t in instance.T]
PAC1L2=[instance.PAC1L2[t].value for t in instance.T]

SOC= np.array([instance.SOC[t].value for t in instance.T])/(instance.X_bat*instance.Cap_nom)*100

#SOC=[instance.SOC[t].value for t in instance.T]

#otros
PGridI=[instance.PGridI[t].value for t in instance.T]
PDI=[instance.PDI[t].value for t in instance.T]

PGrid=[instance.PGrid[t].value for t in instance.T]
PD=[instance.PD[t].value for t in instance.T]

GenOn=[instance.GenOn[t].value for t in instance.T]


#nodo ac 1
PAC1=[instance.PAC1[t].value for t in instance.T]
DCI=[instance.DCI[t].value for t in instance.T]
PBDCAC2=[instance.PBDCAC2[t].value for t in instance.T]

PGrid_av=[instance.PGrid_av[t] for t in instance.T]
PD_av=[instance.PGrid_av[t] for t in instance.T]

resultados= pd.DataFrame()
resultados["PGrid"]=PGrid
resultados["PD"]=PD
resultados["PDL2"]=PDL2
resultados["PGridL2"]=PGridL2
resultados["PGridI"]=PGridI
resultados["PDI"]=PDI
resultados["PAC1"]=PAC1
resultados["PAC1L2"]=PAC1L2
resultados["PAC1AC2"]=PAC1AC2
resultados["PAC1DC"]=PAC1DC
resultados["Dcurt"]=Dcurt
resultados["Dcurt_critical"]=Dcurt_critical
resultados["PpvIC"]=PpvIC
resultados["PpvICCurt"]=PpvICCurt
resultados["pvICB"]=pvICB
resultados["DCI"]=DCI 
resultados["pvICB"]=pvICB
resultados["DCAC2"]=DCAC2
resultados["pvICL2"]=pvICL2
resultados["PpvOnG"]=PpvOnG
resultados["PpvOnGCurt"]=PpvOnGCurt
resultados["PpvOnGAC2"]=PpvOnGAC2
resultados["Pdch"]=Pdch
resultados["SOC"]=SOC
resultados["PBDCAC2"]=PBDCAC2
resultados
resultados.to_csv("Datos_iteracion_MPC.csv")

resultados_mpc=pd.DataFrame(resultados.iloc[1,:]).T
resultados_mpc.to_excel(r"C:\Users\ADMIN\Documents\F. MPC\Datos_MPC_3h.xlsx")