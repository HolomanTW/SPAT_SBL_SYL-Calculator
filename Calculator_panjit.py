import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import polars as pl
from glob import glob
from functools import partial

def loadfiles():
    global listbox_status
    global total_files
    global rescancsv
    global recalculatesbl

    folder_path = filedialog.askdirectory()
        
    if folder_path != '':
        rescancsv = True
        recalculatesbl = True
        files = glob(f'{folder_path}/**/*[!a-z].csv',recursive=True)

        try:
            total_files.extend(files)
        except:
            total_files = files
        
        #print(total_files)
        files_amount.set(f"Files Count : {len(total_files)}")
        while listbox_status == False:
            rd = pl.scan_csv(total_files[0],has_header=True,skip_rows=header_row.get()-1,n_rows=0,truncate_ragged_lines=True).drop('')
            header = rd.collect()
            
            if 'Parameter' in header.columns:
                title = [x for x in header.columns if x not in ban_list]
                parameter.set(title)
                listbox_status = True
            else:
                messagebox.showerror('Error','找不到測項標題\n\n請重新選擇')
                settings()


        while True:
            bin_rd = pl.scan_csv(total_files[0],has_header=True,skip_rows=bin_row.get()-1,n_rows=0,truncate_ragged_lines=True)
            bin_header = bin_rd.collect()
            if 'Bin' in bin_header.columns:
                break
            else:
                messagebox.showerror('Error',"找不到 Bin 標題\n\n請重新選擇")
                settings()


def calculate():
    global percentage
    global rescancsv
    global recalculatesbl
    global limit_rd
    global rd
    global Robust_Mean
    global Robust_Sigma
    global MIN
    global MAX
    global spat_rd
    n, = listbox.curselection()
    listbox_parameter = listbox.get(n)

    if rescancsv ==True:
        rd = pl.scan_csv(total_files ,has_header=True,skip_rows=header_row.get()-1).drop('').filter(~pl.all_horizontal(pl.all().is_null())).filter((pl.col("Bin#") == '1') & (pl.col('Parameter') == 'PID-'))
        limit_rd = pl.scan_csv(total_files[0],has_header=True,skip_rows=header_row.get()-1,skip_rows_after_header=1,n_rows=3).drop('')
        rescancsv = False

    try:
        spat_rd = rd.select(listbox_parameter).cast(pl.Float64).collect()
    except:
        spat_rd = rd.with_columns(pl.col(listbox_parameter).str.strip_chars()).select(listbox_parameter).cast(pl.Float64).collect()
    
    Robust_Mean = spat_rd.median().item(0,0)
    Robust_Sigma = (spat_rd.quantile(0.75,"linear").item(0,0) - spat_rd.quantile(0.25,"linear").item(0,0)) / 1.35
    #取得原始上下限
    MIN_rd = limit_rd.filter(pl.col('Parameter') == 'Min').select(listbox_parameter).collect()   #問題
    MIN_rd = MIN_rd.item(0,0)
    if MIN_rd == None:
        MIN = MIN_rd
    else:
        try:
            MIN = float(MIN_rd)
        except:
            MIN = ''.join(filter(lambda x: x.isdigit() or x == '.' or x == '-',MIN_rd))


    MAX_rd = limit_rd.filter(pl.col('Parameter') == 'Max').select(listbox_parameter).collect()   #問題
    MAX_rd = MAX_rd.item(0,0)
    if MAX_rd == None:
        MAX = MAX_rd
    else:
        try:
            MAX = float(MAX_rd)
        except:
            MAX = ''.join(filter(lambda x: x.isdigit() or x == '.' or x == '-',MAX_rd))
    

    spat()

    if recalculatesbl == True:
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
        recalculatesbl = False

        #SYL計算
        SYL_Mean = percentage['1'].mean() *100
        SYL_Sigma = percentage['1'].std() *100
        
        #輸出SYL    
        SYL.set(round(SYL_Mean - 3 * SYL_Sigma , 3))
        SYL_1.set(round(SYL_Mean - 4 * SYL_Sigma , 3))
        syl_display.set(round(SYL_Mean,3))
        syl_display1.set(round(SYL_Sigma,3))
        with pl.Config(tbl_cols=-1,tbl_rows=-1):
            print(percentage)
        percentage.drop_in_place('1')
        sbl_btn.config(state=tk.NORMAL)
    
    
    #SPAT計算DEBUG

    print(f'Original Max:{MAX} Min:{MIN}')
    print(f'Robust Mean: {Robust_Mean}')
    print(f'Robust Sigma: {round(Robust_Sigma,3)}')
    #print(f'Q1:{data_base.quantile(0.25,"linear").item(0,0)}')
    #print(f'Q3:{data_base.quantile(0.75,"linear").item(0,0)}')
    #with pl.Config(tbl_cols=-1,tbl_rows=-1):
        #print(bin_data_base)




def spat():
    try:
        SPAT_upper_limit = round(Robust_Mean + float(spinbox.get()) * Robust_Sigma , 3)
        SPAT_lower_limit = round(Robust_Mean - float(spinbox.get()) * Robust_Sigma , 3)
        #print(f"SPAT max:{SPAT_upper_limit}  min:{SPAT_lower_limit}")
        #輸出SPAT
        if MAX == None:
            SPAT.set(SPAT_upper_limit)
            btn.config(fg='black')
        elif SPAT_upper_limit > MAX:
            SPAT.set(MAX)
            btn.config(fg='red')
        else:
            SPAT.set(SPAT_upper_limit)
            btn.config(fg='black')
        
        if MIN == None:
            SPAT_1.set(SPAT_lower_limit)
            btn_1.config(fg='black')
        elif SPAT_lower_limit < MIN:
            SPAT_1.set(MIN)
            btn_1.config(fg='red')
        else:
            SPAT_1.set(SPAT_lower_limit)
            btn_1.config(fg='black')

        count = spat_rd.count().item()
        loss_die = spat_rd.filter((pl.first() > SPAT_upper_limit) | (pl.first() < SPAT_lower_limit)).count().item()
        loss.set(f"{round((loss_die / count)*100,3)}%")
        print(f"total{count}")
        print(f'choose{loss_die}')

    except:
        pass
        
def clean():
    global total_files
    global listbox_status
    global percentage
    global rd
    global limit_rd
    global Robust_Mean
    global Robust_Sigma
    global MIN
    global MAX

    total_files = []
    parameter.set('')
    SPAT.set(0.0)
    SPAT_1.set(0.0)
    SYL.set(0.0)
    SYL_1.set(0.0)
    syl_display.set(0)
    syl_display1.set(0)
    files_amount.set('Files Count : 0')
    listbox_status = False
    sbl_btn.config(state=tk.DISABLED)
    loss.set('0.0%')

    try:
        del percentage
        del rd
        del limit_rd
        del Robust_Mean
        del Robust_Sigma
        del MIN
        del MAX
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
    width = 600
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
    files_amount = tk.StringVar()
    files_amount.set("Files Count : 0")
    syl_display = tk.DoubleVar()
    syl_display1 = tk.DoubleVar()
    adj = tk.IntVar()
    adj.set(6)
    header_row = tk.IntVar()
    header_row.set(19)
    bin_row = tk.IntVar()
    bin_row.set(14)
    
    ban_list = ['Parameter','X','Y','Bin#','Site#','B-CONT','C-CONT','E-CONT']
    listbox_status = False
    
    
    
    
    #元件配置初始化
    #canvas
    root_canvas = tk.Canvas(root,width=590,height=290)
    root_canvas.place(relx=0,rely=0.5)
    root_canvas.create_line(40,40,560,40,width=3,)
    root_canvas.create_line(40,130,560,130,width=3)
    root_canvas.create_line(40,220,560,220,width=3)
    
    #SPAT標題
    label_spat = tk.Label(root, text='Upper                       Lower                    Sigma                    LOSS %', font=('Arial',10))
    label_spat.place(relx=0.21,rely=0.57)
    label = tk.Label(root, text="SPAT",font=('Arial',18))
    label.place(relx=0.05,rely=0.61,height=50)
    #SPAT按鈕
    btn = tk.Button(root,textvariable=SPAT, command=partial(copy,SPAT),font=('Arial',18),relief='solid',bd=2)
    btn.place(relx=0.17,rely=0.61,width=100,height=50)
    #SPAT按鈕_1
    btn_1 = tk.Button(root,textvariable=SPAT_1, command=partial(copy,SPAT_1),font=('Arial',18),relief='solid',bd=2)
    btn_1.place(relx=0.37,rely=0.61,width=100,height=50)
    #SYL標題
    label1 = tk.Label(root, text="SYL", wraplength=300,font=('Arial',20))
    label1.place(relx=0.02,rely=0.76,width=100,height=50)
    #SYL按鈕
    btn1 = tk.Button(root,textvariable=SYL, command=partial(copy,SYL),font=('Arial',18),relief='solid',bd=2)
    btn1.place(relx=0.17,rely=0.76,width=100,height=50)
    #SYL按鈕_1
    btn1_1 = tk.Button(root,textvariable=SYL_1, command=partial(copy,SYL_1),font=('Arial',18),relief='solid',bd=2)
    btn1_1.place(relx=0.37,rely=0.76,width=100,height=50)
    #SYL title
    label3 = tk.Label(root,text='3σ                          4σ                        Mean                     Sigma',font=('Arial',10))
    label3.place(relx=0.23,rely=0.72)
    #SYL標註
    label4 = tk.Label(root,textvariable=syl_display,font=('Arial',20),anchor='center')
    label4.place(relx=0.55,rely=0.77,width=120)
    label5 = tk.Label(root,textvariable=syl_display1,font=('Arial',20),anchor='center')
    label5.place(relx=0.75,rely=0.77,width=120)
    #SBL視窗按鈕
    sbl_btn = tk.Button(root, text="SBL", font=('Arial',20),command=sbl_window,relief='solid',bd=2,state=tk.DISABLED)
    sbl_btn.place(relx=0.41,rely=0.89,width=100,height=50)    
    #打開資料夾按鈕
    openfilesbtn = tk.Button(root,text='Open directory',font=('Arial',15),command=loadfiles,relief='solid',bd=2)
    openfilesbtn.place(relx=0.1,rely=0.07,width=150,height=70)
    #clean按鈕
    clnbtn = tk.Button(root ,text='Clean',font=('Arial',20),command=clean,relief='solid',bd=2)
    clnbtn.place(relx=0.1,rely=0.23,width=150,height=70)
    #計算按鈕
    runbtn = tk.Button(root ,text='Calculate',font=('Arial',20,'bold'),command=calculate,relief='solid',bd=2)
    runbtn.place(relx=0.1,rely=0.4,width=480,height=50)
    #滾動條
    scollbar = tk.Scrollbar(root)
    scollbar.place(relx=0.87,rely=0.07,height=170)
    #listbox
    listbox = tk.Listbox(root ,listvariable=parameter,font=('Arial',10),selectmode='single',yscrollcommand=scollbar.set,justify='center')
    listbox.place(relx=0.45,rely=0.07,width=250,height=170)
    #scollbar
    scollbar.config(command=listbox.yview)
    #檔案數量
    files_amount_dis = tk.Label(root,textvariable=files_amount,font=('Arial',17))
    files_amount_dis.place(relx=0.37,rely=0.49)
    #SPAT數值調整
    spinbox = tk.Spinbox(root,from_=0,to=50,font=('Arial',20),fg='#f00',justify='center',textvariable=adj,command=spat)
    spinbox.place(relx=0.61,rely=0.62,width=50)
    #設定
    menubar = tk.Menu(root)
    menubar.add_command(label='Settings',command=settings)
    root.config(menu=menubar)
    #LOSS率
    losslabel = tk.Label(root ,textvariable=loss,font=('Arial',20))
    losslabel.place(relx=0.73,rely=0.61,width=150,height=50)



    
    root.mainloop()