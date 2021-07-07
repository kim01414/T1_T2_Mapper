import pydicom as pyd
import nibabel as nib
import numpy as np
import cv2, os
import warnings
from skimage.draw import polygon, ellipse
import matplotlib.pyplot as plt 
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont

#warnings.filterwarnings("error")
PLOT_COLOR =  ['red' ,'blue','orange','green','purple','brown',
               'pink','gray','olive' ,'cyan' ,'navy'  ,'khaki',
               'lightblue','gold','violet', 'khaki', 'turquoise', 'thistle']

class IMAGES:
    def __init__(self):
        self.IMGs = None
        self.FILE_TYPE = None
        self.Name = 'TITLE'
        self.FILE_PATH = []
        self.IMGs_Display = []
        self.ROI_Intensities = {}
        self.TR, self.TE, self.TI = [], [], []
        for i in range(len(PLOT_COLOR)): self.ROI_Intensities[i] = []
    
    def DICOM_IMPORTER(self, PATH):
        try:
            FILE = pyd.dcmread(PATH)
            try: self.Name = FILE.SeriesDescription
            except: self.Name = "Unknown"
            try: self.TR.append(float(str(FILE[(0x0018,0x0080)]).split('"')[-2]) )
            except: pass
            try: self.TE.append( float(str(FILE[(0x0018,0x0081)]).split('"')[-2]) )
            except: pass
            try: self.TI.append( float(str(FILE[(0x0018,0x0082)]).split('"')[-2]) )
            except: pass
            if type(self.IMGs)==type(None):
                self.IMGs = FILE.pixel_array.copy(); 
                self.IMGs = self.IMGs.reshape((self.IMGs.shape[0],self.IMGs.shape[1],1))
                self.FILE_TYPE = 'DICOM'
                self.ROIs = ROI((self.IMGs.shape[0],self.IMGs.shape[1]))
            else: self.IMGs = np.dstack([self.IMGs,FILE.pixel_array])
            self.FILE_PATH.append(PATH)
            return True
        except: 
            messagebox.showerror('오류!','{0}은\n 정상적인 DICOM파일이 아닙니다!'.format(PATH))
            return False
            
    def NIFTI_IMPORTER(self, PATH):
        try:
            FILE = (nib.load(PATH)).get_fdata()
            if   len(FILE.shape)==2: 
                self.IMGs = (FILE).swapaxes(-2,-1)
                self.IMGs = self.IMGs.reshape( (self.IMGs.shape[0],self.IMGs.shape[1], 1) )
            elif len(FILE.shape)==3: self.IMGs = (FILE).swapaxes(-3,-2)
            else:
                messagebox.showerror('Sorry!','이 프로그램은 (x, y, slice #)형식의 NiFTI파일만 지원합니다!'.format(PATH)); 
                return False
            self.FILE_PATH.append(PATH)
            self.FILE_TYPE = 'NIFTI'
            self.ROIs = ROI((self.IMGs.shape[0],self.IMGs.shape[1]))
            return True
        except: 
            messagebox.showerror('오류!','{0}은\n 정상적인 NIFTI파일이 아닙니다!'.format(PATH)); 
            return False

    def Convert_DISPLAY(self, index=-1):
        for idx in range(0 if index==-1 else index, self.IMGs.shape[-1] if index==-1 else index+1):
            src = (self.IMGs[:,:,idx] / self.IMGs[:,:,idx].max() * 255).astype(np.uint8)
            display = ImageTk.PhotoImage( Image.fromarray( cv2.resize(src,(650,650),interpolation=cv2.INTER_AREA) ) )
            if index==-1: self.IMGs_Display.append(display)
            else: self.IMGs_Display[index] = display

    def Measure_ROI(self, Index):
        for i in range(self.IMGs.shape[-1]):
            THIS = self.IMGs[:,:,i]
            THIS = THIS[np.where(self.ROI_array[:,:,Index])==1].mean()
            self.ROI_Intensities[Index].append(THIS)

    def Delete_ROI(self, Index):
        self.ROIs.ROI_Using[Index] = False
        self.ROIs.ROI_array[:,:,Index] = np.zeros((self.HEIGHT,self.WIDTH))
        self.ROIs.ROI_for_TK[Index] = []
        self.ROI_Intensities[Index] = []

class ROI:
    def __init__(self, shape):
        self.HEIGHT, self.WIDTH = shape[0], shape[1]
        self.MASK = np.zeros((self.HEIGHT, self.WIDTH)).astype(np.uint8)
        self.Intensities = []
    
    def Make_ROI(self, TYPE, ROI_X, ROI_Y, ROI_for_TK, TK_INDEX, ROI_INDEX=None): 
        self.ROI_TYPE = TYPE
        self.TK_INDEX = TK_INDEX
        self.ROI_INDEX = ROI_INDEX
        self.ROI_X, self.ROI_Y = ROI_X, ROI_Y
        self.ROI_X2, self.ROI_Y2 = (ROI_X / 650 * self.WIDTH).astype(np.uint32), (ROI_Y / 650 * self.HEIGHT).astype(np.uint32)
        self.ROI_for_TK = ROI_for_TK
        if TYPE == 'ROI_CIRCLE':
            CENTER_X, CENTER_Y =  int((self.ROI_X2[0]+self.ROI_X2[1])//2), int((self.ROI_Y2[0]+self.ROI_Y2[1])//2)
            X, Y = ellipse(CENTER_X, CENTER_Y, abs(self.ROI_X2[0]-CENTER_X), abs(self.ROI_Y2[0]-CENTER_Y) )
        else: X, Y = polygon(self.ROI_X2,self.ROI_Y2)
        self.Draw_ROI(X, Y)

    def Measure_ROI(self, src): 
        self.Intensities = []
        try:
            for idx in range(src.shape[-1]):
                THIS = src[:,:,idx]
                if len(THIS[self.MASK==1])==0: raise ValueError
                self.Intensities.append( (THIS[self.MASK==1]).mean() )
            return True
        except: 
            print('Invalid ROI was ignored...')
            return False

    def Measure_Relaxivity(self, IDX, MAP):
        Values = 1/MAP[np.where(self.MASK!=0)]
        return IDX, Values.max(), Values.min(), Values.mean(), Values.std()

    def Draw_ROI(self, X, Y):
        for i in range(len(X)):
            if X[i]<self.WIDTH and Y[i]<self.HEIGHT: self.MASK[Y[i],X[i]] = 1

    def MOVE_ROI(self, dx, dy, Done=False):
        if Done==True: self.ROI_X2, self.ROI_Y2  = [], []
        if self.ROI_TYPE=='ROI_CIRCLE':
            self.ROI_for_TK[0], self.ROI_for_TK[2] = self.ROI_for_TK[0]+dx, self.ROI_for_TK[2]+dx
            self.ROI_for_TK[1], self.ROI_for_TK[3] = self.ROI_for_TK[1]+dy, self.ROI_for_TK[3]+dy
            if Done: 
                self.ROI_X2 = np.array([self.ROI_for_TK[0], self.ROI_for_TK[2]]) / 650 * self.WIDTH
                self.ROI_Y2 = np.array([self.ROI_for_TK[1], self.ROI_for_TK[3]]) / 650 * self.HEIGHT
                CENTER_X, CENTER_Y =  int((self.ROI_X2[0]+self.ROI_X2[1])//2), int((self.ROI_Y2[0]+self.ROI_Y2[1])//2)
                X, Y = ellipse(CENTER_X, CENTER_Y, abs(self.ROI_X2[0]-CENTER_X), abs(self.ROI_Y2[0]-CENTER_Y) )
        else:
            for i in range(len(self.ROI_for_TK)):
                self.ROI_for_TK[i] += dx if i%2==0 else dy
                if i%2==0 and Done: self.ROI_X2.append(int(self.ROI_for_TK[i]/650*self.WIDTH))
                elif i%2!=0 and Done: self.ROI_Y2.append(int(self.ROI_for_TK[i]/650*self.HEIGHT))
            if Done==True:
                self.ROI_X2,self.ROI_Y2 = np.array(self.ROI_X2),np.array(self.ROI_Y2) 
                X, Y = polygon(self.ROI_X2,self.ROI_Y2)       
        if Done:self.MASK = np.zeros((self.HEIGHT, self.WIDTH)).astype(np.uint8); self.Draw_ROI(X, Y)#self.MASK[Y,X] = 1

    def EDIT_ROI(self, cp, dx, dy, Done=False):
        self.ROI_X2, self.ROI_Y2  = [], []
        if self.ROI_TYPE=='ROI_CIRCLE':
            self.ROI_for_TK = np.array([self.ROI_for_TK[0] + (dx if cp==1 else 0), 
                                        self.ROI_for_TK[1] + (dy if cp==0 else 0), 
                                        self.ROI_for_TK[2] + (dx if cp==3 else 0), 
                                        self.ROI_for_TK[3] + (dy if cp==2 else 0)])
            if Done:
                self.ROI_X2 = np.array([self.ROI_for_TK[0], self.ROI_for_TK[2]]) / 650 * self.WIDTH
                self.ROI_Y2 = np.array([self.ROI_for_TK[1], self.ROI_for_TK[3]]) / 650 * self.HEIGHT
                CENTER_X, CENTER_Y =  int((self.ROI_X2[0]+self.ROI_X2[1])//2), int((self.ROI_Y2[0]+self.ROI_Y2[1])//2)
                X, Y = ellipse(CENTER_X, CENTER_Y, abs(self.ROI_X2[0]-CENTER_X), abs(self.ROI_Y2[0]-CENTER_Y) )
        elif self.ROI_TYPE=='ROI_RECT':
            X1, Y1, X2, Y2 = (self.ROI_for_TK[0] + (dx if (cp==0 or cp==1) else 0), 
                              self.ROI_for_TK[1] + (dy if (cp==0 or cp==3) else 0), 
                              self.ROI_for_TK[4] + (dx if (cp==2 or cp==3) else 0), 
                              self.ROI_for_TK[5] + (dy if (cp==1 or cp==2) else 0))
            self.ROI_for_TK = np.array([X1,Y1,X1,Y2,X2,Y2,X2,Y1])
            for i in range(len(self.ROI_for_TK)):
                if i%2==0 and Done: self.ROI_X2.append(int(self.ROI_for_TK[i]/650*self.WIDTH))
                elif i%2!=0 and Done: self.ROI_Y2.append(int(self.ROI_for_TK[i]/650*self.HEIGHT))
            if Done==True:
                self.ROI_X2,self.ROI_Y2 = np.array(self.ROI_X2),np.array(self.ROI_Y2) 
                X, Y = polygon(self.ROI_X2,self.ROI_Y2)       
        elif self.ROI_TYPE=='ROI_POLY':
            self.ROI_for_TK[ cp*2 ] += dx
            self.ROI_for_TK[cp*2+1] += dy
            for i in range(len(self.ROI_for_TK)):
                if i%2==0 and Done: self.ROI_X2.append(int(self.ROI_for_TK[i]/650*self.WIDTH))
                elif i%2!=0 and Done: self.ROI_Y2.append(int(self.ROI_for_TK[i]/650*self.HEIGHT))
            if Done==True:
                self.ROI_X2,self.ROI_Y2 = np.array(self.ROI_X2),np.array(self.ROI_Y2) 
                X, Y = polygon(self.ROI_X2,self.ROI_Y2)   
        if Done: self.MASK = np.zeros((self.HEIGHT, self.WIDTH)).astype(np.uint8); self.Draw_ROI(X, Y)#self.MASK[Y,X] = 1
    
    def SAVE_ROI(self):
        return [self.ROI_X if type(self.ROI_X)==type(list) else self.ROI_X.tolist(),
                self.ROI_Y if type(self.ROI_Y)==type(list) else self.ROI_Y.tolist(),
               self.ROI_for_TK, self.ROI_TYPE]