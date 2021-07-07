import os, pydicom, cv2, pickle
import data_structure, sub_windows
from PIL import Image, ImageTk
import nibabel as nib
import matplotlib, math
import tkinter as TK
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
from tkinter import filedialog, ttk, messagebox, Menu, Widget
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

__version__ = '2020-07-05'
__TITLE__ = "T1/T2 Mapper"

def nothing(x=None): pass

class MAIN_PROGRAM:
    def __init__(self):
        self.WINDOW = TK.Tk()        
        self.TITLE_BAR = 25
        
        self.BTN_HEIGHT,self.BTN_WIDTH = 35, 65
        self.WINDOW.config(bg='#1E1E1E',highlightbackground='white')
        self.My_Screen = [self.WINDOW.winfo_screenwidth(), self.WINDOW.winfo_screenheight()]
        self.WINDOW.geometry('1330x712+{0}+{1}'.format(self.My_Screen[0]//2-1300//2,self.My_Screen[1]//2-792//2))
        self.WINDOW.resizable(0,0)
        self.WINDOW.title(__TITLE__)    
        self.Variable_Initializer()
        
        #######UI#######
        self.Canvas_Initializer()
        self.MENU_Initializer()
        self.Graph_Initializer()
        
        self.FILE_HANDLE = TK.Scale(self.WINDOW,variable=self.Current_File, command=lambda x: self.Select_Image(Index=self.Current_File.get()),orient='horizontal',showvalue=0, to=1000, from_=0,state='disabled',bg='#3C3C3C', fg='#FFFFFF' )
        self.FILE_HANDLE.place(x=670,y=610,width=650)
        
        self.BTTN1  = TK.Button(self.WINDOW, text="Marker" ,command=lambda: self.BTTN_Command(_mode=1), state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN2  = TK.Button(self.WINDOW, text="ROI 자유형",command=lambda: self.BTTN_Command(_mode=2), state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN3  = TK.Button(self.WINDOW, text="ROI 다각형",command=lambda: self.BTTN_Command(_mode=3), state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN4  = TK.Button(self.WINDOW, text="ROI 사각형",command=lambda: self.BTTN_Command(_mode=4), state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN5  = TK.Button(self.WINDOW, text="ROI 원  형",command=lambda: self.BTTN_Command(_mode=5), state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN6  = TK.Button(self.WINDOW, text="ROI 편  집",command=lambda: self.BTTN_Command(_mode=6), state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN7  = TK.Button(self.WINDOW, text="ROI AUTO",command=self.BTTN7_Command, state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN8  = TK.Button(self.WINDOW, text="ROI 열  기",command=self.BTTN8_Command, state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN9  = TK.Button(self.WINDOW, text="ROI 저  장",command=self.BTTN9_Command, state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN10 = TK.Button(self.WINDOW, text="ROI 초기화",command=self.BTTN10_Command, state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.IMAGE_BTTN_X, self.IMAGE_BTTN_Y = 670, 625
        self.BTTN1.place(x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*0),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        
        self.BTTN2.place(x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*1),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        
        self.BTTN3.place(x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*2),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        
        self.BTTN4.place(x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*3),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        
        self.BTTN5.place(x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*4),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        
        self.BTTN6.place(x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*6),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        
        self.BTTN7.place(x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*5),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        
        self.BTTN8.place(x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*7),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        
        self.BTTN9.place(x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*8),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        
        self.BTTN10.place(x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*9),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        

        self.CWD = TK.Label(self.WINDOW, bd=1, relief='sunken', anchor='w', textvariable=self.Current_Working_File, bg='#007ACD', fg='#FFFFFF')
        self.CWD.place(x=0,y=668+self.TITLE_BAR,width=660+0)
        self.STATUS = TK.Label(self.WINDOW, bd=1, relief='sunken', anchor='e', textvariable=self.Status, bg='#007ACD', fg='#FFFFFF')
        self.STATUS.place(x=660+0,y=668+self.TITLE_BAR,width=280)
        self.PROGRESSBAR = ttk.Progressbar(self.WINDOW, length=150,style="red.Horizontal.TProgressbar")
        self.PROGRESSBAR.place(x=940+0,y=668+self.TITLE_BAR+1,width=150,height=18)
        self.PROGRESSBAR.after(1, nothing)

        self.CUR_MOUSE_POS = TK.Label(self.WINDOW, bd=1, relief='sunken', anchor='e', textvariable=self.Location, bg='#007ACD', fg='#FFFFFF')
        self.CUR_MOUSE_POS.place(x=1090+0,y=668+self.TITLE_BAR,width=240)
        self.WINDOW.protocol('WM_DELETE_WINDOW',self.GOODBYE)
        self.WINDOW.mainloop()

    def GOODBYE(self):  
        if ( messagebox.askyesno('종료','프로그램을 정말 종료하시겠습니까?') ): self.WINDOW.quit()

    def Variable_Initializer(self):
        self.MOUSE_MODE = 0 #0: Nothing, 1: Point, 2: ROI_Free_shape, 3: ROI_Poly, 4: ROI_Rect, 5: Circle
        self.Drawing, self.MOUSE_IN = False, False
        self.IMG_X, self.IMG_Y = 0, 0
        self.Canvas_X, self.Canvas_Y = 0, 0
        self.Marker_Intensities = None
        self.ROI_LIST = []
        self.ROI_Selected = -1
        self.ROI_MOVING = False
        self.LINES, self.ROI_POINTS, self.ROI_POINTS_X, self.ROI_POINTS_Y = [], [], [], []
        self.CONTROL_POINTS = []
        self.Edit_CP, self.CP = False ,None
        self.MAP = None
        self.Location = TK.StringVar(); self.Location.set("(0, 0)")
        self.Current_Working_File = TK.StringVar(); self.Current_Working_File.set("Nothing")
        self.Status = TK.StringVar(); self.Status.set("IDLE")
        
        self.Current_File = TK.IntVar(); self.Current_File.set(0)
        self.Total_File = TK.IntVar(); self.Total_File.set(0)
        self.IMAGEs = None

    def Canvas_Initializer(self):
        self.DICOM_CANVAS = TK.Canvas(self.WINDOW, width=650, height=650, bg='black',cursor='crosshair')
        self.DICOM_CANVAS.place(x=10,y=10+self.TITLE_BAR, width=650,height=650)
        self.DICOM_CANVAS.CWD = self.DICOM_CANVAS.create_text(600,20,font='Arial 10 bold', text='(0000/0000)',fill='yellow')
        self.DICOM_IMAGE = self.DICOM_CANVAS.create_image(0,0,anchor=TK.NW, image=ImageTk.PhotoImage(Image.fromarray(np.zeros([650,650]))))

    def Graph_Initializer(self):
        t = np.arange(0,2*np.pi, 0.1)
        x = 16*np.sin(t)**3
        y = 13*np.cos(t)-5*np.cos(2*t)-2*np.cos(3*t)-np.cos(4*t)
        self.SI_FRAME = TK.Frame(self.WINDOW)
        self.SI_FRAME.place(x=670,y=10+self.TITLE_BAR,width=520+100+30,height=530)
        self.SI_FIG = plt.figure(0,[5+1,6])
        self.SI_AX = self.SI_FIG.add_subplot(111)
        self.SI_AX.set_title("Welcome to {0}".format(__TITLE__))
        self.SI_AX.set_xlabel(" ")
        self.SI_AX.set_ylabel(" ")
        self.SI_AX.plot(x,y)
        self.SI_CANVAS = FigureCanvasTkAgg(self.SI_FIG, master=self.SI_FRAME)
        self.SI_CANVAS.get_tk_widget().pack(fill='both')
        self.SI_CANVAS.draw()
        toolbarFrame = TK.Frame(master=self.WINDOW)
        toolbarFrame.place(x=670,y=565,width=650)
        toolbar = NavigationToolbar2Tk(self.SI_CANVAS, toolbarFrame)

    def MENU_Initializer(self):
        self.MENU1 = TK.Button(self.WINDOW, text="파일",command=self.MENU_FILE_POPUP , bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.MENU1.place(x=10,y=10,width=50,height=20)
        self.MENU1.bind('<Any-Enter>',lambda x: self.MENU1.config(bg='#094771')); self.MENU1.bind('<Any-Leave>',lambda x: self.MENU1.config(bg='#3C3C3C'))
        self.MENU_FILE = Menu(self.WINDOW, tearoff=0)
        self.MENU_FILE.add_command(label="DICOM 열기",    command=self.FILE_OPEN_DICOMS)
        self.MENU_FILE.add_command(label="NiFTI 열기",    command=self.FILE_OPEN_NIFTI)
        self.MENU_FILE.add_command(label="종료",command=self.GOODBYE)

        self.MENU2 = TK.Button(self.WINDOW, text="도구",command=self.MENU_TOOL_POPUP , bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.MENU2.place(x=60,y=10,width=50,height=20)
        self.MENU2.bind('<Any-Enter>',lambda x: self.MENU2.config(bg='#094771')); self.MENU2.bind('<Any-Leave>',lambda x: self.MENU2.config(bg='#3C3C3C'))
        self.MENU_TOOL = Menu(self.WINDOW, tearoff=0)
        self.MENU_TOOL.add_command(label="T1/T2 Mapping" ,command=self.T1_T2_Mapping,state='disabled')

        self.MENU3 = TK.Button(self.WINDOW, text="?",command=self.About_Program , bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.MENU3.place(x=1260,y=40,width=30,height=20)
        self.MENU3.bind('<Any-Enter>',lambda x: self.MENU3.config(bg='#094771')); self.MENU3.bind('<Any-Leave>',lambda x: self.MENU3.config(bg='#3C3C3C'))

        self.RIGHT_CLK_MENU =  Menu(self.DICOM_CANVAS, tearoff = 0)
        self.RIGHT_CLK_MENU.add_command(label='====={0}====='.format(__TITLE__), command=nothing, state='disabled')
        self.RIGHT_CLK_MENU.add_separator()
        self.RIGHT_CLK_MENU.add_command(label="ROI 삭제", command=self.Remove_ROI, state='disabled')

    def BIND_Initializer(self):
        self.WINDOW.bind('<MouseWheel>',self.MOUSE_WHEEL_HANDLER)
        self.DICOM_CANVAS.bind('<Motion>',self.MOUSE_MOTION_HANDLER)
        self.DICOM_CANVAS.bind('<Button-1>',self.MOUSE_B1_CLICK_HANDLER)
        self.DICOM_CANVAS.bind('<Button-3>',self.MOUSE_B3_CLICK_HANDLER)
        self.DICOM_CANVAS.bind('<B1-Motion>',self.MOUSE_B1_DRAG_HANDLER)
        self.DICOM_CANVAS.bind('<ButtonRelease-1>',self.MOUSE_B1_RELEASE_HANDLER)
        self.BTTN1.bind('<Button-3>',lambda x: self.SI_MARKER_PROCESSING(remove=True))

    def MENU_FILE_POPUP(self):
        self.MENU_FILE.tk_popup(self.WINDOW.winfo_x()+63, self.WINDOW.winfo_y()+70, 0)
        self.MENU_FILE.grab_release()

    def MENU_TOOL_POPUP(self):
        self.MENU_TOOL.tk_popup(self.WINDOW.winfo_x()+124, self.WINDOW.winfo_y()+70, 0)
        self.MENU_TOOL.grab_release()

    def FILE_OPEN_DICOMS(self):
        FILE_LIST = list(filedialog.askopenfilenames(initialdir=os.getcwd(),title='DICOM 파일 열기'))
        if len(FILE_LIST)!=0:
            os.chdir(os.path.dirname(FILE_LIST[0]))
            PLZ_WAIT = self.DICOM_CANVAS.create_text(315,325,font='Arial 10 bold', text='Loading...',fill='yellow')
            self.Current_File.set(0); self.Total_File.set(0)
            self.IMAGEs = data_structure.IMAGES()
            try:    self.LIST = sorted(FILE_LIST, key = lambda LIST: int(LIST.split('.')[-1])) #DICOM 확장자(1,2,...,860)
            except: self.LIST = sorted(FILE_LIST, key = lambda LIST: (LIST.split('.')[0]))     #DICOM 파일명(i38491035)
            index = 0
            for path in self.LIST:
                index += 1
                if self.IMAGEs.DICOM_IMPORTER(path): 
                    self.Total_File.set(self.Total_File.get()+1)
                    self.Status.set("파일을 불러오고 있습니다... %2d%%"%(index / len(self.LIST)*100))
                else: messagebox.showerror('ERROR!','{0}은(는) 정상적인 DICOM파일이 아닙니다!')
                self.PROGRESSBAR.step(100/len(self.LIST))
                self.PROGRESSBAR.update_idletasks()
            self.Status.set("IDLE")
            self.DICOM_CANVAS.delete(PLZ_WAIT)
            self.PROGRESSBAR.stop()
            self.FILE_OPENED()

    def FILE_OPEN_NIFTI(self):
        PATH = filedialog.askopenfilename(initialdir=os.getcwd(), title='NiFTI 파일 열기')
        if PATH!='':
            os.chdir(os.path.dirname(PATH))
            self.Current_File.set(0); self.Total_File.set(0)
            self.Status.set("NIFTI파일을 불러오고 있습니다...")
            self.PROGRESSBAR.step(50)
            self.IMAGEs = data_structure.IMAGES()
            if self.IMAGEs.NIFTI_IMPORTER(PATH)==False: 
                self.PROGRESSBAR.stop()
                return None
            else: self.Total_File.set(self.IMAGEs.IMGs.shape[-1])
            self.Status.set("IDLE")
            self.PROGRESSBAR.step(50)
            self.PROGRESSBAR.stop()
            self.FILE_OPENED()

    def FILE_OPENED(self):
        self.MAP = None
        self.DISPLAY_GRAPH()
        self.BIND_Initializer()
        self.IMAGEs.Convert_DISPLAY()
        self.Select_Image(Index=self.Current_File.get())
        if self.MOUSE_MODE==6: self.Set_Mouse_Mode()
        #self.BTTN1.config( state='normal', relief=TK.RAISED, bg='#3C3C3C') #SI_Marker
        self.BTTN2.config( state='normal', relief=TK.RAISED, bg='#3C3C3C') #ROI_FREE
        self.BTTN3.config( state='normal', relief=TK.RAISED, bg='#3C3C3C') #ROI_POLY
        self.BTTN4.config( state='normal', relief=TK.RAISED, bg='#3C3C3C') #ROI_CIRCLE
        self.BTTN5.config( state='normal', relief=TK.RAISED, bg='#3C3C3C') #ROI_RECT
        self.BTTN6.config( state='normal', relief=TK.RAISED, bg='#3C3C3C') #ROI_EDIT
        self.BTTN7.config( state='normal', relief=TK.RAISED, bg='#3C3C3C') #ROI_AUTO
        self.BTTN8.config( state='normal', relief=TK.RAISED, bg='#3C3C3C') #ROI_OPEN
        self.FILE_HANDLE.config(from_=0, to=self.Total_File.get()-1, state='normal')
        self.MENU_TOOL.entryconfig("T1/T2 Mapping" ,state='normal')

    def Select_Image(self, Index):
        self.DICOM_CANVAS.itemconfig(self.DICOM_IMAGE, image=self.IMAGEs.IMGs_Display[Index])
        self.DICOM_CANVAS.delete(self.DICOM_CANVAS.CWD)
        self.DICOM_CANVAS.CWD = self.DICOM_CANVAS.create_text(600,20,font='Arial 10 bold', text='(%04d/%04d)'%(self.Current_File.get()+1,self.Total_File.get()),fill='yellow')
        if self.IMAGEs.FILE_TYPE=='DICOM': self.Current_Working_File.set(self.IMAGEs.FILE_PATH[self.Current_File.get()])
        elif self.IMAGEs.FILE_TYPE=='NIFTI': self.Current_Working_File.set(self.IMAGEs.FILE_PATH[0])
    
    def Set_Mouse_Mode(self,mode=0):
        self.MOUSE_MODE = mode if self.MOUSE_MODE!=mode else 0
        self.BTTN1.config(relief=TK.SUNKEN if self.MOUSE_MODE==1 else TK.RAISED, bg='#094771' if self.MOUSE_MODE==1 else '#3C3C3C')
        self.BTTN2.config(relief=TK.SUNKEN if self.MOUSE_MODE==2 else TK.RAISED, bg='#094771' if self.MOUSE_MODE==2 else '#3C3C3C') #ROI_FREE
        self.BTTN3.config(relief=TK.SUNKEN if self.MOUSE_MODE==3 else TK.RAISED, bg='#094771' if self.MOUSE_MODE==3 else '#3C3C3C') #ROI_POLY
        self.BTTN4.config(relief=TK.SUNKEN if self.MOUSE_MODE==4 else TK.RAISED, bg='#094771' if self.MOUSE_MODE==4 else '#3C3C3C') #ROI_CIRCLE
        self.BTTN5.config(relief=TK.SUNKEN if self.MOUSE_MODE==5 else TK.RAISED, bg='#094771' if self.MOUSE_MODE==5 else '#3C3C3C') #ROI_RECT
        self.BTTN6.config(relief=TK.SUNKEN if self.MOUSE_MODE==6 else TK.RAISED, bg='#094771' if self.MOUSE_MODE==6 else '#3C3C3C') #ROI_MOVE 

    def BTTN_Command(self, _mode):      #BUTTON 1~6
        self.CURRENT_LINE = None
        self.Set_Mouse_Mode(mode=_mode)
        self.Remove_Control_Point()
        if self.Drawing==True:
            self.Drawing = False
            self.DICOM_CANVAS.delete(*self.LINES); self.DICOM_CANVAS.delete(self.END_POINT)
            del(self.ROI_LIST[-1])
        self.LINES, self.ROI_POINTS, self.ROI_POINTS_X, self.ROI_POINTS_Y = [], [], [], []
        self.DISPLAY_GRAPH()

    def BTTN7_Command(self):
        self.Threshold_Settings = sub_windows.Thresholder(self,self.IMAGEs.IMGs[:,:,self.Current_File.get()])
        self.WINDOW.wait_window(self.Threshold_Settings.MAIN)
            
    def BTTN8_Command(self):
        FILE = filedialog.askopenfilename(initialdir=os.getcwd(), title='ROI 열기',filetypes=[("ROI files","*.roi")])
        if FILE!='':
            os.chdir(os.path.dirname(FILE))
            with open(FILE,"rb") as f: DATA = pickle.load(f)
            if (True if len(self.ROI_LIST)==0 else messagebox.askyesno('주의!','기존 ROI는 제거됩니다.\n계속하시겠습니까?')):
                self.ROI_Selected=-1; self.Remove_ROI()
                for idx in range(len(DATA)):
                    self.ROI_LIST.append(data_structure.ROI(self.IMAGEs.IMGs.shape[:2]))
                    THIS = DATA[idx] #ROI_X, ROI_Y, ROI_TK
                    if THIS[3]=='ROI_CIRCLE': self.CURRENT_LINE = self.DICOM_CANVAS.create_oval(   *THIS[2],fill='',outline='red')
                    else:                     self.CURRENT_LINE = self.DICOM_CANVAS.create_polygon(*THIS[2],fill='',outline='red')  
                    self.ROI_LIST[-1].Make_ROI(THIS[3],np.array(THIS[0]), np.array(THIS[1]), np.array(THIS[2]), self.CURRENT_LINE)
                    if self.ROI_LIST[-1].Measure_ROI(self.IMAGEs.IMGs)==False:
                        del(self.ROI_LIST[-1]); self.DICOM_CANVAS.delete(self.CURRENT_LINE)
                    self.DISPLAY_GRAPH()

    def BTTN9_Command(self):
        if len(self.ROI_LIST)!=0:
            FILE = filedialog.asksaveasfilename(initialdir=os.getcwd(), title='ROI 저장',initialfile='ROI.roi',filetypes=[("ROI files","*.roi")])
            if FILE!='':
                os.chdir(os.path.dirname(FILE))
                DATA = []
                for idx in range(len(self.ROI_LIST)): DATA.append(self.ROI_LIST[idx].SAVE_ROI())
                with open(FILE,'wb') as f: pickle.dump(DATA, f)

    def BTTN10_Command(self): 
        if messagebox.askyesno('주의!','ROI가 모두 제거됩니다.\n계속하시겠습니까?'):
            self.ROI_Selected=-1; self.Remove_ROI()
            self.DISPLAY_GRAPH()

    def GET_IMAGE_POSITION(self, x, y):
        O_size = self.IMAGEs.IMGs.shape[:2]
        return int(x / 650 * O_size[0]), int(y / 650 * O_size[1])

    def MOUSE_WHEEL_HANDLER(self, event):
        TOTAL, CURRENT = self.Total_File.get(),self.Current_File.get()
        if TOTAL>0:
            dN = -1 if event.delta>0 else 1
            if CURRENT+dN==TOTAL: self.Current_File.set(0)
            elif CURRENT+dN<0: self.Current_File.set(TOTAL-1)
            else: self.Current_File.set(CURRENT+dN)
            self.Select_Image(Index=self.Current_File.get())
    
    def MOUSE_MOTION_HANDLER(self,event):
        self.Canvas_X, self.Canvas_Y = event.x, event.y
        self.IMG_X, self.IMG_Y = self.GET_IMAGE_POSITION(event.x, event.y)
        self.Location.set('( %3d, %3d ), %3.2f'%(self.IMG_X, self.IMG_Y,self.IMAGEs.IMGs[self.IMG_Y, self.IMG_X,self.Current_File.get()]))
        if self.MOUSE_MODE==3: #ROI_Poly
            if self.Drawing==True:
                self.DICOM_CANVAS.coords(self.LINES[-1], *self.START_POINT, self.Canvas_X, self.Canvas_Y)
                THIS = self.DICOM_CANVAS.find_enclosed(self.Canvas_X-8,self.Canvas_Y-8,self.Canvas_X+8,self.Canvas_Y+8)
                if len(THIS)!=0 and THIS[0]==self.END_POINT: self.MOUSE_IN = True
                else: self.MOUSE_IN = False 
        elif self.MOUSE_MODE==6: #ROI_EDIT
            if self.ROI_Selected!=-1:
                try:
                    TEMP = self.DICOM_CANVAS.find_enclosed(self.Canvas_X-10,self.Canvas_Y-10, self.Canvas_X+10, self.Canvas_Y+10)
                    if TEMP[0] in self.CONTROL_POINTS: 
                        self.DICOM_CANVAS.config(cursor='hand1')
                        self.Edit_CP = TEMP[0]
                        self.CP = self.CONTROL_POINTS.index(self.Edit_CP)
                        return None
                except: self.Edit_CP, self.CP = False, None
            if self.Drawing==False and self.ROI_MOVING==False:
                for idx in range(len(self.ROI_LIST)):
                    if self.ROI_LIST[idx].MASK[self.IMG_Y][self.IMG_X]==1:
                        self.DICOM_CANVAS.config(cursor='hand2')
                        self.ROI_Selected = idx
                        return None
                self.ROI_Selected = -1
                self.DICOM_CANVAS.config(cursor='crosshair')
                    
    def MOUSE_B1_CLICK_HANDLER(self, event):
        self.Canvas_X, self.Canvas_Y = event.x, event.y
        self.IMG_X, self.IMG_Y = self.GET_IMAGE_POSITION(event.x, event.y)
        if   self.MOUSE_MODE==1: self.SI_MARKER_PROCESSING() #1: Point
        elif self.MOUSE_MODE>1 and self.MOUSE_MODE<6:
            if self.MOUSE_MODE!=3: #Not ROI_Poly
                self.ROI_LIST.append(data_structure.ROI(self.IMAGEs.IMGs.shape[:2]))
                self.START_POINT = (self.Canvas_X, self.Canvas_Y)
                self.Drawing = True
                if self.MOUSE_MODE==2: #2: ROI_Free_shape
                    self.LINES, self.ROI_POINTS, self.ROI_POINTS_X, self.ROI_POINTS_Y = [], [], [], []
                    self.LINES.append( self.DICOM_CANVAS.create_polygon(self.Canvas_X,self.Canvas_Y,fill='',outline='yellow') )
                    self.ROI_POINTS.extend([self.Canvas_X,self.Canvas_Y]); self.ROI_POINTS_X.append(self.Canvas_X); self.ROI_POINTS_Y.append(self.Canvas_Y)
                elif self.MOUSE_MODE==4: #4: ROI_Rect
                    self.CURRENT_LINE = self.DICOM_CANVAS.create_polygon(self.Canvas_X,self.Canvas_Y,self.Canvas_X,self.Canvas_Y+1,self.Canvas_X+1, self.Canvas_Y+1,self.Canvas_X+1,self.Canvas_Y,fill='',outline='yellow')                                                                
                elif self.MOUSE_MODE==5: #5: Circler
                    self.CURRENT_LINE = self.DICOM_CANVAS.create_oval(self.Canvas_X,self.Canvas_Y,self.Canvas_X+1,self.Canvas_Y+1,fill='',outline='yellow')
            elif self.MOUSE_MODE==3: #ROI_Poly
                if self.MOUSE_IN==True: return None
                self.START_POINT = (self.Canvas_X, self.Canvas_Y)
                if self.Drawing==False:
                    self.ROI_LIST.append(data_structure.ROI(self.IMAGEs.IMGs.shape[:2]))
                    self.ROI_POINTS, self.ROI_POINTS_X, self.ROI_POINTS_Y = [], [], []
                    self.END_POINT = self.DICOM_CANVAS.create_oval(self.Canvas_X-3,self.Canvas_Y-3,self.Canvas_X+3, self.Canvas_Y+3, fill='white',outline='yellow')
                    self.Drawing = True
                self.ROI_POINTS.extend([self.Canvas_X,self.Canvas_Y]); self.ROI_POINTS_X.append(self.Canvas_X); self.ROI_POINTS_Y.append(self.Canvas_Y)
                self.LINES.append( self.DICOM_CANVAS.create_polygon(*self.START_POINT,self.Canvas_X+1,self.Canvas_Y+1, outline='yellow') )
        elif self.MOUSE_MODE==6: #6: ROI_EDIT
            self.Remove_Control_Point()
            self.START_POINT = (self.Canvas_X, self.Canvas_Y)
            if self.ROI_Selected!=-1: self.Draw_Control_Point(self.ROI_Selected)
            else: self.Edit_CP, self.CP = False, None
        else: pass

    def MOUSE_B1_DRAG_HANDLER(self, event):
        self.Canvas_X, self.Canvas_Y = event.x, event.y
        if self.MOUSE_MODE>1 and self.MOUSE_MODE<6:
            if self.MOUSE_MODE==2: #2: ROI_Free_shape
                self.LINES.append( self.DICOM_CANVAS.create_polygon(self.Canvas_X,self.Canvas_Y,fill='',outline='yellow') )
                self.ROI_POINTS.extend([self.Canvas_X,self.Canvas_Y]); self.ROI_POINTS_X.append(self.Canvas_X); self.ROI_POINTS_Y.append(self.Canvas_Y)
            elif self.MOUSE_MODE==4: #4: ROI_Rect
                self.DICOM_CANVAS.coords(self.CURRENT_LINE,*self.START_POINT, self.START_POINT[0], self.Canvas_Y, self.Canvas_X, self.Canvas_Y, self.Canvas_X, self.START_POINT[1])                                                                           
            elif self.MOUSE_MODE==5: #5: Circle
                self.DICOM_CANVAS.coords(self.CURRENT_LINE,*self.START_POINT,self.Canvas_X, self.Canvas_Y)
        elif self.MOUSE_MODE==6: #6: ROI_EDIT
            if self.Edit_CP:
                dx, dy = self.Canvas_X - self.START_POINT[0], self.Canvas_Y - self.START_POINT[1]
                self.START_POINT = (self.Canvas_X, self.Canvas_Y)
                self.ROI_LIST[self.ROI_Selected].EDIT_ROI(self.CP, dx, dy)
                self.DICOM_CANVAS.coords(self.Edit_CP,*self.ROI_LIST[self.ROI_Selected].ROI_for_TK)
                self.DICOM_CANVAS.coords(self.ROI_LIST[self.ROI_Selected].TK_INDEX,*self.ROI_LIST[self.ROI_Selected].ROI_for_TK)
                self.Draw_Control_Point(self.ROI_Selected)
            elif self.ROI_Selected!=-1:
                self.ROI_MOVING = True
                dx, dy = self.Canvas_X - self.START_POINT[0], self.Canvas_Y - self.START_POINT[1]
                self.START_POINT = (self.Canvas_X, self.Canvas_Y)
                self.ROI_LIST[self.ROI_Selected].MOVE_ROI(dx,dy,False)
                self.DICOM_CANVAS.coords(self.ROI_LIST[self.ROI_Selected].TK_INDEX,*self.ROI_LIST[self.ROI_Selected].ROI_for_TK)
                self.Draw_Control_Point(self.ROI_Selected)
        else: pass

    def MOUSE_B1_RELEASE_HANDLER(self, event):
        self.Canvas_X, self.Canvas_Y = event.x, event.y
        if self.MOUSE_MODE>1 and self.MOUSE_MODE<6:
            if   self.MOUSE_MODE==2: #2: ROI_Free_shape
                self.DICOM_CANVAS.delete(*self.LINES)
                self.CURRENT_LINE = self.DICOM_CANVAS.create_polygon(*self.ROI_POINTS,fill='',outline='red')
                self.ROI_LIST[-1].Make_ROI('ROI_FREE',np.array(self.ROI_POINTS_X), np.array(self.ROI_POINTS_Y), self.ROI_POINTS, self.CURRENT_LINE)
                self.DISPLAY_GRAPH()
                self.Drawing = False
            elif self.MOUSE_MODE==3: #3: ROI_Poly
                if self.MOUSE_IN==True:
                    self.DICOM_CANVAS.delete(self.END_POINT); self.DICOM_CANVAS.delete(*self.LINES)
                    self.CURRENT_LINE = self.DICOM_CANVAS.create_polygon(*self.ROI_POINTS, *self.ROI_POINTS[:2], fill='',outline='red')
                    self.Drawing,self.MOUSE_IN = False, False
                    self.ROI_LIST[-1].Make_ROI('ROI_POLY',np.array(self.ROI_POINTS_X), np.array(self.ROI_POINTS_Y), self.ROI_POINTS, self.CURRENT_LINE)
                    self.ROI_LIST[-1].Measure_ROI(self.IMAGEs.IMGs)
                    self.DISPLAY_GRAPH()
                else: return None
            elif self.MOUSE_MODE==4: #4: ROI_Rect
                X,Y, X2,Y2  = self.START_POINT[0], self.START_POINT[1], self.Canvas_X, self.Canvas_Y
                ROI_X, ROI_Y = np.array([X,X,X2,X2]), np.array([Y,Y2,Y2,Y])
                ROI_POINTS = np.array([X,Y,X,Y2,X2,Y2,X2,Y])
                self.Drawing = False
                if abs(X-X2)>3 and abs(Y-Y2)>3:
                    self.DICOM_CANVAS.itemconfig(self.CURRENT_LINE,outline='red')
                    self.ROI_LIST[-1].Make_ROI('ROI_RECT',ROI_X, ROI_Y, ROI_POINTS, self.CURRENT_LINE)
                    self.ROI_LIST[-1].Measure_ROI(self.IMAGEs.IMGs)
                    self.DISPLAY_GRAPH()
                else:
                    self.DICOM_CANVAS.delete(self.CURRENT_LINE)
                    del(self.ROI_LIST[-1])
            elif self.MOUSE_MODE==5: #5: Circle
                X,Y,X2,Y2 = self.START_POINT[0], self.START_POINT[1], self.Canvas_X, self.Canvas_Y
                ROI_X, ROI_Y = np.array([X,X2]), np.array([Y,Y2])
                ROI_POINTS = np.array([X,Y,X2,Y2])
                self.Drawing = False
                if abs(X-X2)>3 and abs(Y-Y2)>3:
                    self.DICOM_CANVAS.itemconfig(self.CURRENT_LINE,outline='red')
                    self.ROI_LIST[-1].Make_ROI('ROI_CIRCLE',ROI_X, ROI_Y, ROI_POINTS, self.CURRENT_LINE)
                    self.ROI_LIST[-1].Measure_ROI(self.IMAGEs.IMGs)
                    self.DISPLAY_GRAPH()
                else:
                    self.DICOM_CANVAS.delete(self.CURRENT_LINE)
                    del(self.ROI_LIST[-1])
        elif self.MOUSE_MODE==6: #6: ROI_EDIT
            if self.Edit_CP:
                dx, dy = self.Canvas_X - self.START_POINT[0], self.Canvas_Y - self.START_POINT[1]
                self.START_POINT = (self.Canvas_X, self.Canvas_Y)
                self.ROI_LIST[self.ROI_Selected].EDIT_ROI(self.CP, dx, dy, True)
                self.DICOM_CANVAS.coords(self.Edit_CP,*self.ROI_LIST[self.ROI_Selected].ROI_for_TK)
                self.DICOM_CANVAS.coords(self.ROI_LIST[self.ROI_Selected].TK_INDEX,*self.ROI_LIST[self.ROI_Selected].ROI_for_TK)
                self.DICOM_CANVAS.coords(self.ROI_LIST[self.ROI_Selected].ROI_INDEX,self.ROI_LIST[self.ROI_Selected].ROI_for_TK[::2].max(),self.ROI_LIST[self.ROI_Selected].ROI_for_TK[::2].min())
                self.Draw_Control_Point(self.ROI_Selected)
                self.Edit_CP, self.CP = False, None
                self.ROI_LIST[-1].Measure_ROI(self.IMAGEs.IMGs)
            elif self.ROI_MOVING==True:
                dx, dy = self.Canvas_X - self.START_POINT[0], self.Canvas_Y - self.START_POINT[1]
                self.START_POINT = (self.Canvas_X, self.Canvas_Y)
                self.ROI_LIST[self.ROI_Selected].MOVE_ROI(dx,dy,True)
                self.DICOM_CANVAS.coords(self.ROI_LIST[self.ROI_Selected].TK_INDEX,*self.ROI_LIST[self.ROI_Selected].ROI_for_TK)
                self.DICOM_CANVAS.coords(self.ROI_LIST[self.ROI_Selected].ROI_INDEX,max(self.ROI_LIST[self.ROI_Selected].ROI_for_TK[::2]),min(self.ROI_LIST[self.ROI_Selected].ROI_for_TK[1::2]))
                self.ROI_MOVING=False
                self.ROI_LIST[-1].Measure_ROI(self.IMAGEs.IMGs)
                self.ROI_Selected = -1
            self.DISPLAY_GRAPH(index=self.ROI_Selected)
        else: pass
        self.LINES, self.ROI_POINTS, self.ROI_POINTS_X, self.ROI_POINTS_Y = [], [], [], []
        self.CURRENT_LINE = None

    def MOUSE_B3_CLICK_HANDLER(self, event):
        self.RIGHT_CLK_MENU.entryconfig("ROI 삭제",state='normal' if self.ROI_Selected!=-1 else 'disabled')
        self.RIGHT_CLK_MENU.tk_popup(event.x_root+80, event.y_root, 0)
        self.RIGHT_CLK_MENU.grab_release()

    def SI_MARKER_PROCESSING(self, event=None, remove=False):
        try:
            self.DICOM_CANVAS.delete(self.DICOM_CANVAS_CROSS1)
            self.DICOM_CANVAS.delete(self.DICOM_CANVAS_CROSS2)
            self.DICOM_CANVAS.delete(self.DICOM_CANVAS_TEXT0)
            self.DICOM_CANVAS.delete(self.DICOM_MARKER_INTENSITY1)
            self.DICOM_CANVAS.delete(self.DICOM_MARKER_NUMS)
        except: pass
        finally:
            if remove==True: self.Marker_Intensities=None; self.DISPLAY_GRAPH() ; return None
            self.Marker_Intensities = self.IMAGEs.IMGs[self.IMG_Y, self.IMG_X, :]
            self.DISPLAY_GRAPH(marker_only=True)    
            self.DICOM_CANVAS_CROSS1=self.DICOM_CANVAS.create_line(self.Canvas_X-10, self.Canvas_Y, self.Canvas_X+10, self.Canvas_Y, fill='red')
            self.DICOM_CANVAS_CROSS2=self.DICOM_CANVAS.create_line(self.Canvas_X, self.Canvas_Y-10, self.Canvas_X, self.Canvas_Y+10, fill='red')
            self.DICOM_MARKER_NUMS = self.DICOM_CANVAS.create_text(10,20,font='Arial 10 bold',text='+', fill='red')
            self.DICOM_CANVAS_TEXT0 =self.DICOM_CANVAS.create_text(50,20,fill='white',font="Arial 10",text='({0}, {1})'.format(self.IMG_X,self.IMG_Y))    
            self.DICOM_MARKER_INTENSITY1 = self.DICOM_CANVAS.create_text(140,20,font='Arial 10', text='%3d'%(self.IMAGEs.IMGs[self.IMG_Y, self.IMG_X, self.Current_File.get()]), fill='white')

    def DISPLAY_GRAPH(self, index=-1, marker_only=False):
        self.SI_AX.clear()
        self.SI_AX.set_xlabel("# of slide")
        self.SI_AX.set_ylabel("Intensity")
        self.BTTN9.config(  state='disabled' if len(self.ROI_LIST)==0 else 'normal')
        self.BTTN10.config( state='disabled' if len(self.ROI_LIST)==0 else 'normal')
        if index!=-1:
            self.SI_AX.set_title("ROI #%d"%(index+1))
            self.SI_AX.plot([i for i in range(1,self.IMAGEs.IMGs.shape[-1]+1)],self.ROI_LIST[index].Intensities,color='red')
            self.SI_CANVAS.draw()
        
    def Draw_Control_Point(self, index):
        try: self.DICOM_CANVAS.delete(*self.CONTROL_POINTS)
        except: pass
        self.CONTROL_POINTS = []
        if self.ROI_LIST[index].ROI_TYPE!='ROI_FREE':
            if self.ROI_LIST[index].ROI_TYPE=='ROI_POLY':
                for idx in range(0,len(self.ROI_LIST[index].ROI_for_TK), 2):
                    X1,Y1 = self.ROI_LIST[index].ROI_for_TK[idx],self.ROI_LIST[index].ROI_for_TK[idx+1]
                    self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X1-1,Y1-1,X1-1,Y1+1,X1+1,Y1+1,X1+1,Y1-1,fill='white',outline='white', width=2))
            elif self.ROI_LIST[index].ROI_TYPE=='ROI_RECT':
                X1,Y1,X2,Y2 = self.ROI_LIST[index].ROI_for_TK[0],self.ROI_LIST[index].ROI_for_TK[1],self.ROI_LIST[index].ROI_for_TK[4],self.ROI_LIST[index].ROI_for_TK[5]
                self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X1-1,Y1-1,X1-1,Y1+1,X1+1,Y1+1,X1+1,Y1-1,fill='white',outline='white', width=2))
                self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X1-1,Y2-1,X1-1,Y2+1,X1+1,Y2+1,X1+1,Y2-1,fill='white',outline='white', width=2))
                self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X2-1,Y2-1,X2-1,Y2+1,X2+1,Y2+1,X2+1,Y2-1,fill='white',outline='white', width=2))
                self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X2-1,Y1-1,X2-1,Y1+1,X2+1,Y1+1,X2+1,Y1-1,fill='white',outline='white', width=2))
            elif self.ROI_LIST[index].ROI_TYPE=='ROI_CIRCLE': 
                X1, X2 = self.ROI_LIST[index].ROI_for_TK[0], self.ROI_LIST[index].ROI_for_TK[2]
                X3     = (X1+X2)//2
                Y1, Y2 = self.ROI_LIST[index].ROI_for_TK[1], self.ROI_LIST[index].ROI_for_TK[3]
                Y3     = (Y1+Y2)//2
                self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X3-1,Y1-1,X3-1,Y1+1,X3+1,Y1+1,X3+1,Y1-1,fill='white',outline='white', width=2))
                self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X1-1,Y3-1,X1-1,Y3+1,X1+1,Y3+1,X1+1,Y3-1,fill='white',outline='white', width=2))
                self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X3-1,Y2-1,X3-1,Y2+1,X3+1,Y2+1,X3+1,Y2-1,fill='white',outline='white', width=2))
                self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X2-1,Y3-1,X2-1,Y3+1,X2+1,Y3+1,X2+1,Y3-1,fill='white',outline='white', width=2))
    
    def Remove_Control_Point(self):
        try: 
            self.DICOM_CANVAS.delete(*self.CONTROL_POINTS)
            self.CONTROL_POINTS = []
        except: pass

    def Remove_ROI(self):
        try: self.DICOM_CANVAS.delete(*self.CONTROL_POINTS)
        except: pass
        for idx in range(len(self.ROI_LIST)-1 if self.ROI_Selected==-1 else self.ROI_Selected, -1 if self.ROI_Selected==-1 else self.ROI_Selected-1, -1):
            try: self.DICOM_CANVAS.delete(self.ROI_LIST[idx].TK_INDEX); self.DICOM_CANVAS.delete(self.ROI_LIST[idx].ROI_INDEX)
            except: pass
            del(self.ROI_LIST[idx])
        self.DISPLAY_GRAPH()

    def AUTO_ROI(self, contour):
        if len(self.ROI_LIST)!=0:
            rtn = messagebox.askyesno('Warning!','기존의 ROI가 전부 제거됩니다.\n계속하시겠습니까?'.format(len(data_structure.PLOT_COLOR)))
            if rtn==False: return False
        self.ROI_Selected = -1
        self.Remove_Control_Point()
        self.Remove_ROI()
        #contour = sorted(contour, key=lambda x: cv2.contourArea(x), reverse=True)
        #contour = sorted( contour, key=lambda x: cv2.boundingRect(x)[0]+cv2.boundingRect(x)[1]*self.IMAGEs.IMGs.shape[1])
        contour = sorted( contour, key=lambda x: (x[:,0,0].mean(),x[:,0,1].mean()) )#, reverse=True )
        #contour = sorted( contour, key=lambda x: x[:,0,1].max())#, reverse=True )
        for i in range(len(contour)):
            self.ROI_POINTS, self.ROI_POINTS_X, self.ROI_POINTS_Y = [], [], []
            self.ROI_LIST.append(data_structure.ROI(self.IMAGEs.IMGs.shape[:2]))
            Contour = contour[i][:,0]
            for ct in Contour:
                self.ROI_POINTS.extend([ct[0]/self.IMAGEs.IMGs.shape[1]*650,ct[1]/self.IMAGEs.IMGs.shape[0]*650])
                self.ROI_POINTS_X.append(ct[0]/self.IMAGEs.IMGs.shape[1]*650); self.ROI_POINTS_Y.append(ct[1]/self.IMAGEs.IMGs.shape[0]*650)
            self.CURRENT_LINE = self.DICOM_CANVAS.create_polygon(*self.ROI_POINTS,fill='',outline='red')#
            self.ROI_INDEX = self.DICOM_CANVAS.create_text(max(self.ROI_POINTS_X),min(self.ROI_POINTS_Y),text="#{}".format(len(self.ROI_LIST)),fill='red')
            self.ROI_LIST[-1].Make_ROI('ROI_FREE',np.array(self.ROI_POINTS_X), np.array(self.ROI_POINTS_Y), self.ROI_POINTS, self.CURRENT_LINE,self.ROI_INDEX)
            if self.ROI_LIST[-1].Measure_ROI(self.IMAGEs.IMGs)==False:
                del(self.ROI_LIST[-1]); self.DICOM_CANVAS.delete(self.CURRENT_LINE)
        plt.rc('font', size=10)
        plt.figure(0)
        self.DISPLAY_GRAPH()
        return True

    def T1_T2_Mapping(self):
        if len(self.ROI_LIST)!=0:
            ROI = np.zeros(self.IMAGEs.IMGs.shape[:2])
            for i in range(len(self.ROI_LIST)): ROI[np.where(self.ROI_LIST[i].MASK==1)]=1
        else: ROI = np.ones(self.IMAGEs.IMGs.shape[:2])
        self.FITTING = 0
        self.Threshold_Settings = sub_windows.T1_T2_Mapper(self,self.IMAGEs.IMGs,ROI)
        self.WINDOW.wait_window(self.Threshold_Settings.MAIN)
        if type(self.MAP)!=type(None):
            if messagebox.askquestion('Mapping','Do you want to save measurements as csv file?')=='yes':
                PATH = filedialog.asksaveasfilename(filetypes=[('csv file(*.csv)','*.csv')],title='Save as csv file',initialfile='unnamed.csv',defaultextension=".csv")
                if PATH!='':
                    import csv
                    MODE = '_R1(^s)' if self.FITTING<2 else '_R2(^s)'
                    while(True):
                        try:
                            save = open(PATH, 'w', newline='')
                            write = csv.writer(save)
                            write.writerow(['ROI #','Max'+MODE,'Min'+MODE,'Mean'+MODE,'Std'+MODE])
                            for i in range(len(self.ROI_LIST)): 
                                write.writerow(self.ROI_LIST[i].Measure_Relaxivity(i+1,self.MAP))
                            save.close()
                            messagebox.showinfo('Done!','The measurements successfully saved as\n{}'.format(PATH))
                            break
                        except PermissionError:  
                            if messagebox.askquestion('ERROR','File already in use!\nRetry?')==False: break
                        except: messagebox.showinfo('ERROR','Unknown error! Contact KYH'); break

    def About_Program(self):
        messagebox.showinfo('About',"""
        {0}
        Ver: {1}\n
        Developed by Kim Yun Heung
        (techman011@gmail.com)
        KNU BMRLab (http://bmr.knu.ac.kr)\n
            --Main modules--
        Pydicom, OpenCV, matplotlib, scipy, numpy, SimpleITK\n
        """.format(__TITLE__,__version__))

if __name__ == "__main__": 
    print("Starting {0}...".format(__TITLE__))
    from matplotlib import style
    style.use('bmh')
    MAIN_WINDOW = MAIN_PROGRAM()