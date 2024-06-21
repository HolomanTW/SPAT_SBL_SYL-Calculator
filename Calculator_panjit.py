import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import polars as pl
from glob import glob
from functools import partial
import time
import threading

def animation():
    for i in ['f','e','d','c','b','a',9,8,7,6,5,4,3,2,1,0]:
        files_amount_label.config(fg=f'#{i}00')
        time.sleep(0.1)
        
def loadfile():
    global title
    global total_files
    retry = None

    folder_path = filedialog.askopenfilenames()
 
    if folder_path != '':
        files = folder_path


        total_files.extend(files)

        
        #print(total_files)
        
        while True:
            header = pl.read_csv(total_files[0],has_header=True,skip_rows=header_row.get()-1,n_rows=0,truncate_ragged_lines=True).drop('')

            if 'User Item' in header.columns:
                title = [x for x in header.columns if x not in ban_list and 'duplicated' not in x]
                files_amount.set(len(total_files))
                test = threading.Thread(target=animation)
                test.start()
                root.mainloop()
                break

            else:
                retry = messagebox.askretrycancel('Error','找不到測項標題\n\n請重新選擇')
                if retry == True:
                    settings()
                else:
                    total_files = []
                    break

def loadfiles():
    global title
    global total_files
    retry = None

    folder_path = filedialog.askdirectory()
 
    if folder_path != '':
        files = glob(f'{folder_path}/**/*.csv',recursive=True)

        try:
            total_files.extend(files)
        except:
            total_files = files
        
        #print(total_files)
        
        while True:
            header = pl.read_csv(total_files[0],has_header=True,skip_rows=header_row.get()-1,n_rows=0,truncate_ragged_lines=True).drop('')

            if 'User Item' in header.columns:
                title = [x for x in header.columns if x not in ban_list and 'duplicated' not in x]
                files_amount.set(len(total_files))
                test = threading.Thread(target=animation)
                test.start()
                root.mainloop()
                break

            else:
                retry = messagebox.askretrycancel('Error','找不到測項標題\n\n請重新選擇')
                if retry == True:
                    settings()
                else:
                    total_files = []
                    break



def calculate():
    global percentage
    global limit_rd
    global Robust_Mean
    global Robust_Sigma
    global spat_rd
    #global combine_forSPAT_rd
    global SPAT_sigmaX

    parameter.set(title)
    SPAT_sigmaX = [6]*len(title)
    
    rd = pl.scan_csv(total_files ,has_header=True,skip_rows=header_row.get()-1,truncate_ragged_lines=False,null_values=[' ----','----']).filter(pl.col('User Item') == 'PASS').select(title)
    limit_rd = pl.read_csv(total_files[0],has_header=True,skip_rows=header_row.get()-1,n_rows=2).drop('')
    combine_forSPAT_rd = rd.collect()
    #print(combine_forSPAT_rd)

    #轉換數據類型為Float
    try:
        spat_rd = combine_forSPAT_rd.cast(pl.Float64)
    except:
        spat_rd = combine_forSPAT_rd.with_columns(pl.all().str.strip_chars()).cast(pl.Float64)
    #計算SPAT的Robust Mean and Robust Sigma

    Robust_Mean = spat_rd.median()
    Robust_Sigma = (spat_rd.quantile(0.75,"linear") - spat_rd.quantile(0.25,"linear")) / 1.35


    
    #SPAT計算DEBUG

    #print(f'Original Max:{MAX} Min:{MIN}')
    #print(f'Robust Mean: {Robust_Mean}')
    #print(f'Robust Sigma: {Robust_Sigma}')
    #print(f'Q1:{data_base.quantile(0.25,"linear").item(0,0)}')
    #print(f'Q3:{data_base.quantile(0.75,"linear").item(0,0)}')
    #with pl.Config(tbl_cols=-1,tbl_rows=-1):
    #    print(f'Robust Mean: {Robust_Mean}')
    #    print(f'Robust Sigma: {Robust_Sigma}')
        #print(bin_data_base)



def spat(category):
    global SPAT_sigmaX
    global lower_limit
    global upper_limit
    n, = listbox.curselection()
    listbox_parameter = listbox.get(n)
    if category == 1:
        SPAT_sigmaX[n] = adj.get()
    else:
        adj.set(SPAT_sigmaX[n])

    #取得原始上下限
    MIN_rd = limit_rd.filter(pl.col('User Item') == 'Lower').select(listbox_parameter).item()   #問題
    if MIN_rd == None:
        MIN = MIN_rd
    else:
        try:
            MIN = float(MIN_rd)
        except:
            MIN = ''.join(filter(lambda x: x.isdigit() or x == '.' or x == '-',MIN_rd))

    MAX_rd = limit_rd.filter(pl.col('User Item') == 'Upper').select(listbox_parameter).item()   #問題
    if MAX_rd == None:
        MAX = MAX_rd
    else:
        try:
            MAX = float(MAX_rd)
        except:
            MAX = ''.join(filter(lambda x: x.isdigit() or x == '.' or x == '-',MAX_rd))

    upper_limit = Robust_Mean.select(listbox_parameter).item() + float(spinbox.get()) * Robust_Sigma.select(listbox_parameter).item()
    lower_limit = Robust_Mean.select(listbox_parameter).item() - float(spinbox.get()) * Robust_Sigma.select(listbox_parameter).item()
    #print(f"SPAT max:{upper_limit}  min:{lower_limit}")
    
    #輸出SPAT
    if MAX == None:
        SPAT.set(round(upper_limit,3))
        btn.config(fg='black')
    elif upper_limit > MAX:
        SPAT.set(round(upper_limit,3))
        btn.config(fg='red')
    else:
        SPAT.set(round(upper_limit,3))
        btn.config(fg='black')
    
    if MIN == None:
        SPAT_1.set(round(lower_limit,3))
        btn_1.config(fg='black')
    elif lower_limit < MIN:
        SPAT_1.set(round(lower_limit,3))
        btn_1.config(fg='red')
    else:
        SPAT_1.set(round(lower_limit,3))
        btn_1.config(fg='black')

    if convert.get() == 1:
        AtonA()
    elif convert.get() == 2:
        ohmtomohm()

    count = spat_rd.select(listbox_parameter).count().item()
    loss_die = spat_rd.select(listbox_parameter).filter((pl.first() > upper_limit) | (pl.first() < lower_limit)).count().item()
    loss.set(f"{round((loss_die / count)*100,3)}%")
    print(f"total{count}")
    #print(f'choose{loss_die}')

def clean():
    global total_files
    global percentage
    global limit_rd
    global Robust_Mean
    global Robust_Sigma
    global title

    total_files = []
    parameter.set('')
    SPAT.set(0.0)
    SPAT_1.set(0.0)
    SYL.set(0.0)
    SYL_1.set(0.0)
    syl_display.set(0)
    syl_display1.set(0)
    files_amount.set(0)
    loss.set('0.0%')

    try:
        del percentage
        del limit_rd
        del Robust_Mean
        del Robust_Sigma
        del title
    except:
        pass


def copy(type):
    root.clipboard_clear()
    root.clipboard_append(type.get())

def copy_spe(type):
    root.clipboard_clear()
    root.clipboard_append(type)

def AtonA():
    SPAT.set(round(upper_limit*1000000000,3))
    SPAT_1.set(round(lower_limit*1000000000,3))

def ohmtomohm():
    SPAT.set(round(upper_limit*1000,3))
    SPAT_1.set(round(lower_limit*1000,3))

def settings():
    Setting = tk.Toplevel()
    Setting.title('Settings')
    Setting.resizable(False, False)
    window_width = root.winfo_screenwidth()    # 取得螢幕寬度
    window_height = root.winfo_screenheight()  # 取得螢幕高度
    width = 400
    height = 400
    left = int((window_width - width)/2)       # 計算左上 x 座標
    top = int((window_height - height)/2)      # 計算左上 y 座標
    Setting.geometry(f'{width}x{height}+{left}+{top}')

    parameter_header_row = tk.Label(Setting,text='測項標題row定位',font=(10))
    parameter_header_row.place(relx=0.1,rely=0.1)
    parameter_header_row_spinbox = tk.Spinbox(Setting,from_=0,to=100,font=('Arial',17),fg='#f00',justify='center',textvariable=header_row)
    parameter_header_row_spinbox.place(relx=0.5,rely=0.1,width=50)

    def close():
        Setting.destroy()
        Setting.quit()

    close_btn = tk.Button(Setting,text='Close',command=close,relief='solid',font=('Arial',20))
    close_btn.place(x=150,rely=0.8,width=100,height=50)
    Setting.protocol("WM_DELETE_WINDOW",close)
    Setting.mainloop()

if __name__ == '__main__':
    #視窗初始化
    root = tk.Tk()
    root.title('Calculator')
    root.resizable(False, False)
    window_width = root.winfo_screenwidth()    # 取得螢幕寬度
    window_height = root.winfo_screenheight()  # 取得螢幕高度
    width = 800
    height = 600
    left = int((window_width - width)/2)       # 計算左上 x 座標
    top = int((window_height - height)/2)      # 計算左上 y 座標
    root.geometry(f'{width}x{height}+{left}+{top-20}')

    #變數初始化
    SPAT = tk.DoubleVar()
    SPAT_1 = tk.DoubleVar()
    SYL = tk.DoubleVar()
    SYL_1 = tk.DoubleVar()
    loss = tk.StringVar()
    loss.set('0.0%')
    parameter = tk.StringVar()
    files_amount = tk.IntVar()
    syl_display = tk.DoubleVar()
    syl_display1 = tk.DoubleVar()
    adj = tk.IntVar()
    adj.set(6)
    header_row = tk.IntVar()
    header_row.set(11)
    convert = tk.IntVar()

    
    ban_list = ['User Item']
    total_files = []
    
    #元件配置初始化
    
    #SPAT標題
    label_spat = tk.Label(root, text='Upper\n\n\nLower\n\n\nSigma\n\n\nLoss %', font=('Arial',14))
    label_spat.place(x=250,y=300)
    label = tk.Label(root, text="PAT",font=('Arial',20,'bold'))
    label.place(x=300,y=234,height=50,width=190)
    #SPAT按鈕
    btn = tk.Button(root,textvariable=SPAT, command=partial(copy,SPAT),font=('Arial',18),relief='solid',bd=2)
    btn.place(x=340,y=288,width=110,height=50)
    #SPAT按鈕_1
    btn_1 = tk.Button(root,textvariable=SPAT_1, command=partial(copy,SPAT_1),font=('Arial',18),relief='solid',bd=2)
    btn_1.place(x=340,y=360,width=110,height=50)
    #換算按鈕
    btn_2 = tk.Radiobutton(root,text='A to nA', variable=convert,value=1,command=AtonA,font=('Arial',18))
    btn_2.place(x=510,y=360,width=150,height=50)
    #換算按鈕
    btn_3 = tk.Radiobutton(root,text='ohm to mohm',variable=convert,value=2, command=ohmtomohm,font=('Arial',16))
    btn_3.place(x=510,y=288,width=150,height=50)
    #換算按鈕
    btn_4 = tk.Radiobutton(root,text='None',variable=convert,value=0, command=partial(spat,1),font=('Arial',16))
    btn_4.place(x=510,y=432,width=150,height=50)
    #convert
    convert_title = tk.Label(root,text='Convert',font=('Arial',20,'bold'))
    convert_title.place(x=500,y=234,height=50,width=190)


    #打開檔案按鈕
    openfilebtn = tk.Button(root,text='Open\nFiles',font=('Arial',18),command=loadfile,relief='solid',bd=2)
    openfilebtn.place(x=100,y=42,width=90,height=90)
    #打開資料夾按鈕
    openfilesbtn = tk.Button(root,text='Open\nDirectory',font=('Arial',14),command=loadfiles,relief='solid',bd=2)
    openfilesbtn.place(x=195,y=42,width=90,height=90)
    #clean按鈕
    clnbtn = tk.Button(root ,text='Clean',font=('Arial',20),command=clean,relief='solid',bd=2)
    clnbtn.place(x=100,y=138,width=190,height=90)
    #計算按鈕
    runframe = tk.LabelFrame(root,bd=6,bg='red',relief='flat')
    runframe.place(x=300,y=138,width=190,height=90)
    runbtn = tk.Button(runframe ,text='Calculate',font=('Arial',20,'bold'),command=calculate,relief='flat')
    runbtn.pack(fill='both',expand=1)
    #滾動條
    scollbar = tk.Scrollbar(root)
    scollbar.place(x=700,y=42,height=185)
    #listbox
    listbox = tk.Listbox(root ,listvariable=parameter,font=('Arial',10),selectmode='single',yscrollcommand=scollbar.set,justify='center',relief='solid',bd=2)
    listbox.place(x=500,y=42,width=200,height=185)
    listbox.bind('<<ListboxSelect>>',spat)
    #scollbar
    scollbar.config(command=listbox.yview)
    #檔案數量
    files_amount_frame = tk.LabelFrame(root,text='Files Count',relief='solid',bd=2,font=('Arial',17),labelanchor='n')
    files_amount_frame.place(x=300,y=30,width=190,height=100)
    files_amount_label = tk.Label(files_amount_frame,textvariable=files_amount, font=('Arial',40))
    files_amount_label.pack(fill='both',expand=1)
    #SPAT數值調整
    spinbox = tk.Spinbox(root,from_=0,to=50,font=('Arial',20),fg='#f00',justify='center',textvariable=adj,command=partial(spat,1))
    spinbox.place(x=340,y=432,width=110)
    #設定
    menubar = tk.Menu(root)
    menubar.add_command(label='Settings',command=settings)
    root.config(menu=menubar)
    #LOSS率
    losslabel = tk.Label(root ,textvariable=loss,font=('Arial',20))
    losslabel.place(x=340,y=486,width=110,height=50)

    root.mainloop()