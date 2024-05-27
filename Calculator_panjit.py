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
        

def loadfiles():
    global title
    global total_files
    retry = None

    folder_path = filedialog.askdirectory()
 
    if folder_path != '':
        files = glob(f'{folder_path}/**/*[!a-z].csv',recursive=True)

        try:
            total_files.extend(files)
        except:
            total_files = files
        
        #print(total_files)
        
        while True:
            header = pl.read_csv(total_files[0],has_header=True,skip_rows=header_row.get()-1,n_rows=0,truncate_ragged_lines=True).drop('')

            if 'Parameter' in header.columns:
                title = [x for x in header.columns if x not in ban_list and 'CONT' not in x and 'OPEN' not in x]
               
                break
            else:
                retry = messagebox.askretrycancel('Error','找不到測項標題\n\n請重新選擇')
                if retry == True:
                    settings()
                else:
                    total_files = []
                    break

        if retry == False:
            pass
        else:
            while True:
                bin_header = pl.read_csv(total_files[0],has_header=True,skip_rows=bin_row.get()-1,n_rows=0,truncate_ragged_lines=True)
                if 'Bin' in bin_header.columns:
                    files_amount.set(len(total_files))
                    test = threading.Thread(target=animation)
                    test.start()
                    root.mainloop()
                    break
                else:
                    retry_bin = messagebox.askretrycancel('Error',"找不到 Bin 標題\n\n請重新選擇")
                    if retry_bin == True:
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
    
    rd = pl.scan_csv(total_files ,has_header=True,skip_rows=header_row.get()-1).drop('').filter(~pl.all_horizontal(pl.all().is_null())).filter(pl.col('Parameter') == 'PID-')
    limit_rd = pl.read_csv(total_files[0],has_header=True,skip_rows=header_row.get()-1,skip_rows_after_header=1,n_rows=3).drop('')
    combine_forSPAT_rd = rd.filter(pl.col('Bin#') == '1').drop('Parameter').collect()

    '''che = []
    for file in total_files:
        check_rd = pl.scan_csv(file,has_header=True,skip_rows=7,n_rows=1,truncate_ragged_lines=True).select('RDWFODASK-D08-01-P0').cast(pl.Int64)
        che.append(check_rd)
    check = pl.collect_all(che)
    print(check)
    print(f'數量{len(check)}')
    combine = pl.concat(check).sum()
    print(combine)'''


    #轉換數據類型為Float
    try:
        spat_rd = combine_forSPAT_rd.cast(pl.Float64)
    except:
        spat_rd = combine_forSPAT_rd.with_columns(pl.all().str.strip_chars()).cast(pl.Float64)
    #計算SPAT的Robust Mean and Robust Sigma
    try:
        Robust_Mean = spat_rd.median()
        Robust_Sigma = (spat_rd.quantile(0.75,"linear") - spat_rd.quantile(0.25,"linear")) / 1.35
    
    except TypeError:
        messagebox.showerror('Error','無良率')


    for file in total_files:
        bin_rd = pl.read_csv(file ,has_header=True,skip_rows=bin_row.get()-1,skip_rows_after_header=1,n_rows=1,truncate_ragged_lines=True)
        bin_rd.drop_in_place('Bin')
        bin_rd.drop_in_place('')
        bin_rd = bin_rd.drop((i.name for i in bin_rd if (i.null_count() == 1)))
    
        try:
            bin_data_base = pl.concat([bin_data_base,bin_rd],how='diagonal').fill_null(0)
        except:
            bin_data_base = bin_rd
    bin_data_base_cast = bin_data_base.cast(pl.Int32)
    qty_sum = bin_data_base_cast.sum_horizontal()
    percentage = bin_data_base_cast / qty_sum


    #SYL計算
    SYL_Mean = percentage['1'].mean() *100
    SYL_Sigma = percentage['1'].std() *100
    
    #輸出SYL    
    SYL.set(round(SYL_Mean - 3 * SYL_Sigma , 3))
    SYL_1.set(round(SYL_Mean - 4 * SYL_Sigma , 3))
    syl_display.set(round(SYL_Mean,3))
    syl_display1.set(round(SYL_Sigma,3))
    percentage.drop_in_place('1')
    sbl_btn.config(state=tk.NORMAL)

    
    #SPAT計算DEBUG

    #print(f'Original Max:{MAX} Min:{MIN}')
    #print(f'Robust Mean: {Robust_Mean}')
    #print(f'Robust Sigma: {round(Robust_Sigma,3)}')
    #print(f'Q1:{data_base.quantile(0.25,"linear").item(0,0)}')
    #print(f'Q3:{data_base.quantile(0.75,"linear").item(0,0)}')
    #with pl.Config(tbl_cols=-1,tbl_rows=-1):
        #print(bin_data_base)



def spat(category):
    global SPAT_sigmaX
    global SPAT_lower_limit
    global SPAT_upper_limit
    n, = listbox.curselection()
    listbox_parameter = listbox.get(n)
    if category == 1:
        SPAT_sigmaX[n] = adj.get()
    else:
        adj.set(SPAT_sigmaX[n])

    #取得原始上下限
    MIN_rd = limit_rd.filter(pl.col('Parameter') == 'Min').select(listbox_parameter).item()   #問題
    if MIN_rd == None:
        MIN = MIN_rd
    else:
        try:
            MIN = float(MIN_rd)
        except:
            MIN = ''.join(filter(lambda x: x.isdigit() or x == '.' or x == '-',MIN_rd))

    MAX_rd = limit_rd.filter(pl.col('Parameter') == 'Max').select(listbox_parameter).item()   #問題
    if MAX_rd == None:
        MAX = MAX_rd
    else:
        try:
            MAX = float(MAX_rd)
        except:
            MAX = ''.join(filter(lambda x: x.isdigit() or x == '.' or x == '-',MAX_rd))

    upper_limit = Robust_Mean.select(listbox_parameter).item() + float(spinbox.get()) * Robust_Sigma.select(listbox_parameter).item()
    lower_limit = Robust_Mean.select(listbox_parameter).item() - float(spinbox.get()) * Robust_Sigma.select(listbox_parameter).item()
    #print(f"SPAT max:{SPAT_upper_limit}  min:{SPAT_lower_limit}")
    #輸出SPAT
    if MAX == None:
        SPAT.set(round(upper_limit,3))
        btn.config(fg='black')
    elif upper_limit > MAX:
        SPAT.set(MAX)
        btn.config(fg='red')
    else:
        SPAT.set(round(upper_limit,3))
        btn.config(fg='black')
    
    if MIN == None:
        SPAT_1.set(round(lower_limit,3))
        btn_1.config(fg='black')
    elif lower_limit < MIN:
        SPAT_1.set(MIN)
        btn_1.config(fg='red')
    else:
        SPAT_1.set(round(lower_limit,3))
        btn_1.config(fg='black')

    count = spat_rd.select(listbox_parameter).count().item()
    loss_die = spat_rd.select(listbox_parameter).filter((pl.first() > upper_limit) | (pl.first() < lower_limit)).count().item()
    loss.set(f"{round((loss_die / count)*100,3)}%")
    print(f"total{count}")
    print(f'choose{loss_die}')

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
    sbl_btn.config(state=tk.DISABLED)
    loss.set('0.0%')

    try:
        del percentage
        del limit_rd
        del Robust_Mean
        del Robust_Sigma
        del title
    except:
        pass


def sbl_window():
    window = tk.Toplevel()
    window.title('SBL')
    window.resizable(False, True)
    window_width = root.winfo_screenwidth()    # 取得螢幕寬度
    window_height = root.winfo_screenheight()  # 取得螢幕高度
    width = 600
    height = 500
    left = int((window_width - width)/2)       # 計算左上 x 座標
    top = int((window_height - height)/2)      # 計算左上 y 座標
    window.geometry(f'{width}x{height}+{left}+{top}')
    #滾動條
    def roll(event):
        canvas.yview_scroll(int(event.delta/-120),'units')
    window.bind('<MouseWheel>',roll)
    scbar = tk.Scrollbar(window,orient='vertical')
    scbar.pack(side='right',fill='y')
    
    canvas = tk.Canvas(window,yscrollcommand=scbar.set)
    frame = tk.Frame(canvas)
    #標題
    title = tk.Label(frame,text='Bin             Name                     3σ                   4σ                 Mean              Sigma',font=('Arial',12))
    title.place(x=25,y=25)
    frame_height = 0
    
    bin_name_rd = pl.read_csv(total_files[0] ,has_header=True,skip_rows=bin_row.get(),n_rows=0,truncate_ragged_lines=True).drop('')
    bin_name_rd.drop_in_place('Name')
    bin_name_rd.drop_in_place('PASS')
    bin_name = bin_name_rd.columns
    

    for i,bin in enumerate(percentage.columns):
        Mean = percentage[bin].mean() *100
        Sigma = percentage[bin].std() *100
        SBL1 = round(Mean + 3 * Sigma , 3)
        SBL2 = round(Mean + 4 * Sigma , 3)
        frame_height = 65 + i * 65
        bin_label = tk.Label(frame,text=bin,font=('Arial',14))
        bin_label.place(x=25,y=frame_height+5)
        bin_btn0 = tk.Button(frame,text=SBL1,command=partial(copy_spe,SBL1),font=('Arial',14),relief='solid',bd=2)
        bin_btn0.place(x=200,y=frame_height,width=75)
        bin_btn1 = tk.Button(frame,text=SBL2,command=partial(copy_spe,SBL2),font=('Arial',14),relief='solid',bd=2)
        bin_btn1.place(x=300,y=frame_height,width=75)
        bin_label1 = tk.Label(frame,text=bin_name[i],font=('Arial',12),wraplength=100)
        bin_label1.place(x=80,y=frame_height+5)
        bin_label2 = tk.Label(frame,text=f'{round(Mean,3)}         {round(Sigma,3)}',font=('Arial',14))
        bin_label2.place(x=400,y=frame_height+5)

    canvas.config(scrollregion=(0,0,600,frame_height+70))
    scbar.config(command=canvas.yview)
    frame.config(width=600,height=frame_height+70)
    canvas.pack(fill='both',expand=True)
    canvas.create_window((0,0),window=frame,anchor='nw')
    window.mainloop()

def copy(type):
    root.clipboard_clear()
    root.clipboard_append(type.get())

def copy_spe(type):
    root.clipboard_clear()
    root.clipboard_append(type)

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
    bin_header_row = tk.Label(Setting,text='bin標題 row 定位',font=(10))
    bin_header_row.place(relx=0.1,rely=0.3)
    bin_header_row_spinbox = tk.Spinbox(Setting,from_=0,to=100,font=('Arial',17),fg='#f00',justify='center',textvariable=bin_row)
    bin_header_row_spinbox.place(relx=0.5,rely=0.3,width=50)

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
    header_row.set(19)
    bin_row = tk.IntVar()
    bin_row.set(14)
    
    ban_list = ['Parameter','X','Y','Bin#','Site#','B-CONT','C-CONT','E-CONT','OPEN/SHORT']

    
    #元件配置初始化
    
    #SPAT標題
    label_spat = tk.Label(root, text='Upper\n\n\nLower\n\n\nSigma\n\n\nLoss %', font=('Arial',14))
    label_spat.place(x=50,y=300)
    label = tk.Label(root, text="SPAT",font=('Arial',20,'bold'))
    label.place(x=100,y=234,height=50,width=190)
    #SPAT按鈕
    btn = tk.Button(root,textvariable=SPAT, command=partial(copy,SPAT),font=('Arial',18),relief='solid',bd=2)
    btn.place(x=140,y=288,width=110,height=50)
    #SPAT按鈕_1
    btn_1 = tk.Button(root,textvariable=SPAT_1, command=partial(copy,SPAT_1),font=('Arial',18),relief='solid',bd=2)
    btn_1.place(x=140,y=360,width=110,height=50)

    #SYL標題
    label1 = tk.Label(root, text="SYL", wraplength=300,font=('Arial',20,'bold'))
    label1.place(x=300,y=234,width=190,height=50)
    #SYL按鈕
    btn1 = tk.Button(root,textvariable=SYL, command=partial(copy,SYL),font=('Arial',18),relief='solid',bd=2)
    btn1.place(x=340,y=288,width=110,height=50)
    #SYL按鈕_1
    btn1_1 = tk.Button(root,textvariable=SYL_1, command=partial(copy,SYL_1),font=('Arial',18),relief='solid',bd=2)
    btn1_1.place(x=340,y=360,width=110,height=50)
    #SYL title
    label3 = tk.Label(root,text='Mean\n\n\nSigma',font=('Arial',14))
    label3.place(x=280,y=432)
    #SYL標註
    label4 = tk.Label(root,textvariable=syl_display,font=('Arial',20),anchor='center')
    label4.place(x=340,y=426,width=110,height=50)
    label5 = tk.Label(root,textvariable=syl_display1,font=('Arial',20),anchor='center')
    label5.place(x=340,y=486,width=110,height=50)
    #SBL標題
    label6 = tk.Label(root,text='SBL', wraplength=300,font=('Arial',20,'bold'))
    label6.place(x=500,y=234,width=190,height=50)
    #SBL視窗按鈕
    sbl_btn = tk.Button(root, text="SBL", font=('Arial',20),command=sbl_window,relief='solid',bd=2,state=tk.DISABLED)
    sbl_btn.place(x=550,y=288,width=100,height=50)    
    #打開資料夾按鈕
    openfilesbtn = tk.Button(root,text='Open directory',font=('Arial',18),command=loadfiles,relief='solid',bd=2)
    openfilesbtn.place(x=100,y=42,width=190,height=90)
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
    spinbox.place(x=140,y=432,width=110)
    #設定
    menubar = tk.Menu(root)
    menubar.add_command(label='Settings',command=settings)
    root.config(menu=menubar)
    #LOSS率
    losslabel = tk.Label(root ,textvariable=loss,font=('Arial',20))
    losslabel.place(x=140,y=486,width=110,height=50)

    root.mainloop()