import matplotlib.pyplot as plt
import tkinter as TK
import numpy as np
import pydicom as pyd
import os, cv2, fitting
from scipy.optimize import curve_fit
from tkinter import filedialog, ttk, messagebox, Menu
from PIL import Image, ImageTk, ImageDraw, ImageFont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

CMAP = ["jet","gnuplot","gnuplot2","CMRmap","ocean","gist_earth","gist_stern","terrain",
        "cubehelix","brg","gist_rainbow","rainbow","nipy_spectral","gist_ncar"]

class Thresholder:
    def __init__(self, master, src):
        self.Master = master
        self.MAIN = TK.Toplevel(self.Master.WINDOW)
        self.MAIN.geometry('580x350+100+100')
        self.MAIN.title('ROI Maker')
        self.MAIN.resizable(0,0)
        self.src = (src/src.max()*255).astype(np.uint8)
        self.src = cv2.pyrMeanShiftFiltering(np.dstack((self.src,self.src,self.src)),20,50)[:,:,0]
        self.src_backup = self.src.copy()
        self.Presets_Names = ["THRESH_OTSU","THRESH_BINARY"]
        self.Gaussian_Presets = ["(None)","(3,3)","(5,5)","(7,7)","(9,9)"]                            
        self.threshold, self.threshold_show = TK.IntVar(), TK.StringVar(); self.threshold_show.set("%3d"%(000))
        self.contrast_value, self.contrast_value_show = TK.IntVar(), TK.StringVar(); self.contrast_value_show.set("%3d"%(000))                           

        self.SI_FRAME = TK.Frame(self.MAIN)
        self.SI_FRAME.place(x=10,y=10,width=280,height=280)
        self.SI_FIG = plt.figure(1,[5,5])
        plt.rc('font', size=4) 
        self.SI_CANVAS = FigureCanvasTkAgg(self.SI_FIG, master=self.SI_FRAME)
        self.SI_CANVAS.get_tk_widget().pack(fill='both')
        self.SI_CANVAS.draw()

        self.SI_FRAME2 = TK.Frame(self.MAIN)
        self.SI_FRAME2.place(x=300,y=10,width=270,height=150)
        self.SI_FIG2 = plt.figure(2,[9,5])
        self.SI_CANVAS2 = FigureCanvasTkAgg(self.SI_FIG2, master=self.SI_FRAME2)
        self.SI_CANVAS2.get_tk_widget().pack(fill='both')

        self.LABEL1 = TK.Label(self.MAIN,text='Mode')
        self.LABEL1.place(x=300, y=170)
        self.MODE_COMBOBOX = ttk.Combobox(self.MAIN, height=30, values=self.Presets_Names, state='readonly')
        self.MODE_COMBOBOX.place(x=360,y=170,width=205)
        self.MODE_COMBOBOX.current(0)
        self.MODE_COMBOBOX.bind("<<ComboboxSelected>>", self.Process)

        self.LABEL2 = TK.Label(self.MAIN,text='Gaussian')
        self.LABEL2.place(x=300, y=200)
        self.Gaussian_COMBOBOX = ttk.Combobox(self.MAIN, height=30, values=self.Gaussian_Presets, state='readonly')
        self.Gaussian_COMBOBOX.place(x=360,y=200,width=205)
        self.Gaussian_COMBOBOX.current(0)
        self.Gaussian_COMBOBOX.bind("<<ComboboxSelected>>", self.Process)

        self.LABEL3 = TK.Label(self.MAIN,text='Threshold')
        self.LABEL3.place(x=300, y=230)
        self.Value1_Set = TK.Scale(self.MAIN,variable=self.threshold,command=self.Change_Value, orient='horizontal',showvalue=0, to=255, from_=0)#,bg='#3C3C3C', fg='#FFFFFF' )
        self.Value1_Set.place(x=360,y=230,width=185)
        self.Value1_Set.bind('<ButtonRelease-1>',self.Process) 
        self.Value1_Show = TK.Label(self.MAIN, textvariable=self.threshold_show)
        self.Value1_Show.place(x=545,y=230)

        self.LABEL4 = TK.Label(self.MAIN,text='Contrast')
        self.LABEL4.place(x=300, y=260)
        self.Value2_Set = TK.Scale(self.MAIN,variable=self.contrast_value,command=self.Change_Value, orient='horizontal',showvalue=0, to=300, from_=100)#,bg='#3C3C3C', fg='#FFFFFF' )
        self.Value2_Set.place(x=360,y=260,width=185)
        self.Value2_Set.bind('<ButtonRelease-1>',self.Process) 
        self.Value2_Show = TK.Label(self.MAIN, textvariable=self.contrast_value_show)
        self.Value2_Show.place(x=545,y=260)

        self.Generate_Bttn = TK.Button(self.MAIN,text='확인',command=self.GENERATE_ROI)
        self.Generate_Bttn.place(x=300,y=290,width=120)
        self.Cancel_Bttn = TK.Button(self.MAIN,text='취소',command=self.Close)
        self.Cancel_Bttn.place(x=450,y=290,width=120)
        self.Process(); self.Change_Value()
        self.MAIN.protocol('WM_DELETE_WINDOW',self.Close)
        self.MAIN.grab_set()

    def Change_Value(self, event=None): 
        self.threshold_show.set("%d"%(self.threshold.get())); self.contrast_value_show.set("%d"%(self.contrast_value.get()))
        values = self.img.ravel()
        plt.figure(2); plt.cla(); #plt.axis('off')
        a, b, _ = plt.hist(values,bins=30)
        plt.plot([self.threshold.get(),255],[10000,a.max()])
        #plt.plot(self.threshold.get(),0,values.max(),values.argmax())
        self.SI_CANVAS2.draw() #; plt.cla(); plt.axis('off')

    def Process(self,event=None):
        OPTION = self.MODE_COMBOBOX.current()
        Blur   = self.Gaussian_COMBOBOX.current()
        self.threshold_show.set("%d"%(self.threshold.get()))
        self.src = cv2.convertScaleAbs(self.src_backup.copy(),alpha=self.contrast_value.get()/100,beta=0)
        if Blur==0: self.img = self.src
        if Blur==1: self.img = cv2.GaussianBlur(self.src, (3,3), 0)
        if Blur==2: self.img = cv2.GaussianBlur(self.src, (5,5), 0)
        if Blur==3: self.img = cv2.GaussianBlur(self.src, (7,7), 0)
        if Blur==4: self.img = cv2.GaussianBlur(self.src, (9,9), 0)

        if OPTION<2:
            if   OPTION==0: 
                mode = cv2.THRESH_BINARY + cv2.THRESH_OTSU
                self.Value1_Set.config(state='disabled')
            elif OPTION==1: 
                mode = cv2.THRESH_BINARY 
                self.Value1_Set.config(state='normal')
            _, result = cv2.threshold(self.img, self.threshold.get(), 255, mode)

        _, self.contour, _ = cv2.findContours(result, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        MASK = np.zeros_like(result); MASK = cv2.drawContours(MASK, self.contour, -1, (255,255,255),2)
        plt.figure(1); plt.cla(); plt.imshow(MASK,cmap='gray'); plt.axis('off'); self.SI_CANVAS.draw()
        self.Change_Value()

    def GENERATE_ROI(self):
        if self.Master.AUTO_ROI(self.contour): self.Close()

    def Close(self): 
        plt.close(self.SI_FIG); plt.close(self.SI_FIG2)
        self.MAIN.destroy()

class T1_T2_Mapper:
    def __init__(self, master, src, roi):
        self.Master = master
        self.MAIN = TK.Toplevel(self.Master.WINDOW)
        self.MAIN.geometry('290x300+100+100')
        self.MAIN.title('T1/T2 Mapper')
        self.MAIN.resizable(0,0)
        self.src = src
        self.MAP = np.zeros(self.src.shape[:2])
        self.ROI = roi
        self.TITLE = ''
        self.Methods = ["T1 (IR method)","T1 (Normal method)","T2 (Normal method)"]

        self.LABEL1 = TK.Label(self.MAIN,text='Method')
        self.LABEL1.place(       x=10, y=10)
        self.MODE_COMBOBOX = ttk.Combobox(self.MAIN, height=30, values=self.Methods, state='readonly')        
        self.MODE_COMBOBOX.current(0)
        self.MODE_COMBOBOX.place(x=70,y=10,width=210)
        self.MODE_COMBOBOX.bind("<<ComboboxSelected>>", self.Refresh)
        self.LABEL2 = TK.Label(self.MAIN,text='Time(ms)')
        self.LABEL2.place(       x=10, y=40)
        self.INPUT1 = TK.Entry(self.MAIN)
        self.INPUT1.insert(0,str( [ (i*50) for i in range(1,self.src.shape[-1]+1)])[1:-1] ) 
        self.INPUT1.place(       x=70,y=40,width=210, height=20)

        self.Advanced_FRAME = TK.LabelFrame(self.MAIN, text="Fitting Parameters")
        self.Advanced_FRAME.place(x=10, y=70, width=270, height=150)

        self.LABEL4 = TK.Label(self.Advanced_FRAME,text='M0')
        self.LABEL4.place(       x=10, y=10)
        self.INPUT_M0_bound1 = TK.Entry(self.Advanced_FRAME)
        self.INPUT_M0_bound1.insert(0,0)
        self.INPUT_M0_bound1.place(x=70,y=10,width=80)
        self.LABEL4 = TK.Label(self.Advanced_FRAME,text='~')
        self.LABEL4.place(       x=160, y=10)
        self.INPUT_M0_bound2 = TK.Entry(self.Advanced_FRAME)
        self.INPUT_M0_bound2.insert(0,self.src.max())
        self.INPUT_M0_bound2.place(x=180,y=10,width=80)

        self.LABEL5 = TK.Label(self.Advanced_FRAME,text='T1/T2 (s)')
        self.LABEL5.place(       x=10, y=50)
        self.INPUT_T1_T2_bound1 = TK.Entry(self.Advanced_FRAME)
        self.INPUT_T1_T2_bound1.insert(0,0)
        self.INPUT_T1_T2_bound1.place(x=70,y=50,width=80)
        self.LABEL4 = TK.Label(self.Advanced_FRAME,text='~')
        self.LABEL4.place(       x=160, y=50)
        self.INPUT_T1_T2_bound2 = TK.Entry(self.Advanced_FRAME)
        self.INPUT_T1_T2_bound2.insert(0,1)
        self.INPUT_T1_T2_bound2.place(x=180,y=50,width=80)

        self.LABEL6 = TK.Label(self.Advanced_FRAME,text='R^2 기준')
        self.LABEL6.place(       x=10, y=90)
        self.INPUT_RR_LIMIT = TK.Entry(self.Advanced_FRAME)
        self.INPUT_RR_LIMIT.insert(0,0.95)
        self.INPUT_RR_LIMIT.place(x=70,y=90,width=190)

        self.Generate_Bttn = TK.Button(self.MAIN,text='작업 시작',command=self.Start_Fitting)
        self.Generate_Bttn.place(x=10,y=230,width=270,height=30)

        self.PROGRESSBAR = ttk.Progressbar(self.MAIN, length=150,style="red.Horizontal.TProgressbar")
        self.PROGRESSBAR.place(x=10,y=270,width=270,height=20)

        self.MAIN.protocol('WM_DELETE_WINDOW',self.Close)
        self.MAIN.grab_set()

    def Start_Fitting(self):
        try:
            TIME = np.array([float(n) for n in (self.INPUT1.get()).split(',')]) /1000
            if len(TIME)!=self.src.shape[-1]: raise IndexError
        except ValueError: 
            messagebox.showerror('ERROR!', '"t1,t2,...,tn" 형식으로 입력되었는지 확인하세요.')
            return None
        except IndexError: 
            messagebox.showerror('ERROR!','이미지 개수와 TIME의 개수가 일치하지 않습니다.')
            return None
        #EarlyStopper = float(self.INPUT_RR_LIMIT.get())
        FUNC = [fitting.IR_T1_Fitting,fitting.Normal_T1_Fitting,fitting.Normal_T2_Fitting]
        
        Y,X = np.where(self.ROI==1)
        self.Generate_Bttn.config(state='disabled')
        for p in range(len(Y)):
            y,x = Y[p], X[p]
            THIS = self.src[y,x,:]
            BOUND_START = [float(self.INPUT_T1_T2_bound1.get()), THIS.min() ]  
            BOUND_END   = [float(self.INPUT_T1_T2_bound2.get()), THIS.max() ]
            if self.MODE_COMBOBOX.current()==0: THIS = fitting.Inversion_Method_for_IR_T1(THIS)
            popt, pcov = curve_fit(f=FUNC[self.MODE_COMBOBOX.current()],xdata=TIME,ydata=THIS,bounds=[BOUND_START,BOUND_END])
            self.PROGRESSBAR.step(100/len(Y))
            self.PROGRESSBAR.update_idletasks()
            Residual = THIS - FUNC[self.MODE_COMBOBOX.current()](TIME,*popt)
            Rsquare = fitting.R_squared(THIS, Residual)
            #if Rsquare<EarlyStopper:
            #    messagebox.showerror('Stopped!', 'R^2가 기준보다 낮아 중단되었습니다.')
            #    self.Generate_Bttn.config(state='normal')
            #    self.PROGRESSBAR.stop(); return None
            self.MAP[y,x] = popt[0]
        self.MAP = cv2.GaussianBlur(self.MAP,(3,3),0)
        self.Master.FITTING = self.MODE_COMBOBOX.current()
        messagebox.showinfo('Done!','Mapping 작업이 완료되었습니다!')
        self.PROGRESSBAR.stop()
        self.Generate_Bttn.config(state='normal')
        self.Master.MAP = self.MAP
        self.Close()
        TEST = MAP_VIEWER(self.Master.WINDOW,self.MAP,title=self.Master.IMAGEs.Name)

    def Refresh(self, event=None):
        self.INPUT1.delete(0,'end')
        try:
            if   self.MODE_COMBOBOX.current()==0: self.INPUT1.insert(0, str([TI for TI in self.Master.IMAGEs.TI])[1:-1] )
            elif self.MODE_COMBOBOX.current()==1: self.INPUT1.insert(0, str([TR for TR in self.Master.IMAGEs.TR])[1:-1] )
            elif self.MODE_COMBOBOX.current()==2: self.INPUT1.insert(0, str([TE for TE in self.Master.IMAGEs.TE])[1:-1] )
        except: self.INPUT1.insert(0,str( [ (i*50) for i in range(1,self.src.shape[-1]+1)])[1:-1] )

    def Close(self): self.MAIN.destroy()

class MAP_VIEWER: #3
    def __init__(self, master, src, fig_index=3, title='', lock=False):
        self.POPUP = TK.Toplevel(master)
        self.screen_width = self.POPUP.winfo_screenwidth()
        self.screen_height = self.POPUP.winfo_screenheight()
        self.fig_index = fig_index
        self.POPUP.geometry('750x645+100+100')
        self.POPUP.title('Image Viewer')
        self.POPUP.resizable(0,0)
        self.src = src
        self.title = title
        self.idx = 0
        self.SI_FRAME = TK.Frame(self.POPUP)
        self.SI_FRAME.place(x=0,y=0,width=750,height=645)
        self.SI_FIG = plt.figure(self.fig_index,[7,6])
        self.SI_CANVAS = FigureCanvasTkAgg(self.SI_FIG, master=self.SI_FRAME)
        self.SI_CANVAS.get_tk_widget().pack(fill='both')
        self.VMIN, self.VMAX = self.src.min(), self.src.max()
        self.PLOT()
        self.toolbarFrame = TK.Frame(master=self.POPUP)
        self.toolbarFrame.place(x=0,y=610,width=750)
        self.toolbar = NavigationToolbar2Tk(self.SI_CANVAS, self.toolbarFrame)
        self.RANGE_SET = TK.Button(self.POPUP, text='Range', command=self.Range_Setup)
        self.RANGE_SET.place(x=240,y=612,width=45,height=30)

        self.SAVE_AS_FILE = TK.Button(self.POPUP, text='Export', command=self.EXPORT_MENU_POPUP)
        self.SAVE_AS_FILE.place(x=295,y=612,width=45,height=30)
        self.MENU_FILE = Menu(self.POPUP, tearoff=0)
        self.MENU_FILE.add_command(label="Save as NiFTI",    command=self.SAVE_AS_NIFTI_FILE)
        self.MENU_FILE.add_command(label="Save as Numpy",    command=self.SAVE_AS_NUMPY_FILE)
        self.MENU_FILE.add_command(label="Save as MAT",      command=self.SAVE_AS_MATLAB_FILE)

        if lock: self.POPUP.grab_set()
        self.POPUP.protocol('WM_DELETE_WINDOW',self.Close)
    
    def PLOT(self):
        plt.figure(self.fig_index); plt.cla(); plt.grid(b=None)#; plt.style.use('dark_background')
        if self.title!='': plt.title(self.title)
        plt.imshow(self.src, cmap=CMAP[self.idx],vmin=self.VMIN, vmax=self.VMAX)
        plt.colorbar()
        self.SI_CANVAS.draw()
    
    def Close(self):
        plt.close(self.SI_FIG)
        self.POPUP.destroy()

    def EXPORT_MENU_POPUP(self):
        self.MENU_FILE.tk_popup(self.POPUP.winfo_x()+295, self.POPUP.winfo_y()+542, 0)
        self.MENU_FILE.grab_release()

    def SAVE_AS_NIFTI_FILE(self):
        FILE = filedialog.asksaveasfilename(initialdir=os.getcwd(),defaultextension=".nii.gz", title='Save as NiFTI file', initialfile='data.nii.gz',filetypes=[("NiFTI files","*.nii.gz")])
        if FILE!='':
            os.chdir(os.path.dirname(FILE)); import nibabel as nib
            temp = nib.Nifti1Image(self.src.swapaxes(-2,-1), affine=np.eye(4))
            nib.save(temp, FILE)
            messagebox.showinfo('Done!',"Data just saved as \n{0}".format(FILE))
    
    def SAVE_AS_NUMPY_FILE(self):
        FILE = filedialog.asksaveasfilename(initialdir=os.getcwd(),defaultextension=".npy", title='Save numpy array file', initialfile='data.npy',filetypes=[("Numpy files","*.npy")])
        if FILE!='': os.chdir(os.path.dirname(FILE)); np.save(FILE,self.src); messagebox.showinfo('Done!',"Data just saved as \n{0}".format(FILE))

    def SAVE_AS_MATLAB_FILE(self):
        FILE = filedialog.asksaveasfilename(initialdir=os.getcwd(),defaultextension=".mat", title='Save as MATLAB file', initialfile='data.mat',filetypes=[("MATLAB file","*.mat")])
        if FILE!='':
            import scipy.io as sio 
            os.chdir(os.path.dirname(FILE))
            mdic = {self.title: self.src}; sio.savemat(FILE, mdic, True)
            messagebox.showinfo('Done!',"Data just saved as \n{0}".format(FILE))

    def Range_Setup(self):
        self.window = TK.Toplevel(self.POPUP)
        self.window.config(bg='#1E1E1E')
        self.window.geometry('210x170+{0}+{1}'.format(self.screen_width//2-105, self.screen_height//2-85))
        self.window.resizable(0,0)
        self.LABEL_INTERVAL1 = TK.Label(self.window, text='VMIN',background='#1E1E1E',foreground='#FFFFFF')
        self.LABEL_INTERVAL1.place(x=10,y=10,width=70, height=20)
        self.INPUT_INTERVAL1 = TK.Entry(self.window)
        self.INPUT_INTERVAL1.place(x=85,y=10,width=95, height=20)
        self.INPUT_INTERVAL1.insert(0,self.VMIN)
        self.LABEL_INTERVAL2 = TK.Label(self.window, text='VMAX',background='#1E1E1E',foreground='#FFFFFF')
        self.LABEL_INTERVAL2.place(x=10,y=50,width=70, height=20)
        self.INPUT_INTERVAL2 = TK.Entry(self.window)
        self.INPUT_INTERVAL2.place(x=85,y=50,width=95, height=20)
        self.INPUT_INTERVAL2.insert(0,self.VMAX)
        self.LABEL_CMAP = TK.Label(self.window, text='CMAP',background='#1E1E1E',foreground='#FFFFFF')
        self.LABEL_CMAP.place(x=10,y=90,width=70, height=20)
        self.MODE_COMBOBOX = ttk.Combobox(self.window, height=30, values=CMAP, state='readonly')
        self.MODE_COMBOBOX.place(x=85,y=90,width=95)
        self.MODE_COMBOBOX.current(self.idx)
        self.PROCESS = TK.Button(self.window, command=self.Range_Setup_Close, text='Change',bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771' )
        self.PROCESS.place(x=60,y=130,width=90,height=30)
        self.window.grab_set()

    def Range_Setup_Close(self):
        try: self.VMIN = float(self.INPUT_INTERVAL1.get()); self.VMAX = float(self.INPUT_INTERVAL2.get())
        except: messagebox.showerror('ERROR!',"Invalid parameter!"); return None
        self.idx=self.MODE_COMBOBOX.current()
        self.SI_FIG.clear(); self.PLOT()
        self.window.destroy()