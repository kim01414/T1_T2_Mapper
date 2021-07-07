import numpy as np
from scipy.optimize import curve_fit

############################################################
#                      Instructions                        #
############################################################
# TYPE: xlabel이 TR인지 TE인지를 정합니다.
# User_Fitting():

TYPE = ['T1', # Normal_T1_Fitting()
        'T2', # Normal_T2_Fitting()
        'T1'] # IR_T1_Fitting()

def Inversion_Method_for_IR_T1(y):
    y2 = y.copy()
    min_idx = y2.argmin(); y2[:min_idx] *= (-1)
    return y2

def Normal_T1_Fitting(x,a,b):
    return b*(1-(np.exp(x)**(-1/a)))

def Normal_T2_Fitting(x,a,b):
    return b*(np.exp(x)**(-1/a))

def IR_T1_Fitting(x,a,b):
    return b*(1-2*(np.exp(x)**(-1/a)))

def R_squared(y, residual):
    SS_res = np.sum(residual**2)
    SS_tot = np.sum((y-np.mean(y))**2)
    return 1-(SS_res / SS_tot)