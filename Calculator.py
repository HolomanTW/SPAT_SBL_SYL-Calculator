import tkinter as tk
from tkinter import filedialog
import polars as pl
from glob import glob
from functools import partial

def loadfiles():
    global listbox_status
    global total_files
    while True:
        folder_path = filedialog.askdirectory()
        files = (glob(rf'{folder_path}/*.csv'))
        
        if len(files) != 0:
            try:
                total_files = pl.concat([total_files,pl.DataFrame(files)])
            except:
                total_files = pl.DataFrame(files)
            
            #print(total_files)
            files_amount.set(f"檔案數量 : {total_files.height}")

            if listbox_status == False:
                rd = pl.scan_csv(total_files.row(0),has_header=True,skip_rows=11,n_rows=0)
                header = rd.collect()
                print('listbox')
                title = [x for x in header.columns if x not in ban_list]
                parameter.set(title)
                listbox_status = True
        else:
            break

def calculate():
    global bin_data_base
    for file in total_files.get_column('column_0'):
        rd = pl.scan_csv(file,has_header=True,skip_rows=11,skip_rows_after_header=5).filter(~pl.all_horizontal(pl.all().is_null()))
        n, = listbox.curselection()
        try:
            spat = rd.filter(Bin=1).select(listbox.get(n)).collect()
            spat = spat.cast(pl.Float64)
            
        except:
            spat = rd.filter(Bin=1).with_columns(pl.col(listbox.get(n)).str.strip_chars()).select(listbox.get(n)).collect()
            spat = spat.cast(pl.Float64)

        bin_rd = rd.select('Bin').collect()
        bin_p = bin_rd.group_by("Bin").agg([pl.len().alias("count")]).with_columns((pl.col("count") / pl.sum("count")).alias("percent")).with_columns(pl.lit(file).alias('file'))
        bin_pivot = bin_p.pivot(index='file',columns='Bin',values='percent')
        bin_pivot.drop_in_place('file')
        
        try:
            data_base = pl.concat([data_base,spat])
            bin_data_base = pl.concat([bin_data_base,bin_pivot],how='diagonal').fill_null(0)
        except:
            data_base = spat
            bin_data_base = bin_pivot
    #print(data_base)
    #print(bin_data_base)

    #SPAT計算
    Robust_Mean = data_base.median().item(0,0)
    Robust_Sigma = (data_base.quantile(0.75,"nearest").item(0,0) - data_base.quantile(0.25,"nearest").item(0,0)) / 1.35
    print(f'Robust_Mean: {Robust_Mean}')
    print(f'Robust_Sigma: {round(Robust_Sigma,3)}')

    #SYL計算
    SYL_Mean = bin_data_base['1'].mean() *100
    SYL_Sigma = bin_data_base['1'].std() *100

    #print(f'sylmean: {SYL_Mean}')
    #print(f'sylsigma: {SYL_Sigma}')
    #輸出SPAT
    SPAT.set(round(Robust_Mean + float(spinbox.get()) * Robust_Sigma , 3))
    SPAT_1.set(round(Robust_Mean - float(spinbox.get()) * Robust_Sigma , 3))
    #輸出SYL
    SYL.set(round(SYL_Mean - 3 * SYL_Sigma , 3))
    SYL_1.set(round(SYL_Mean - 4 * SYL_Sigma , 3))
    syl_display.set(f"{round(SYL_Mean,3)}      {round(SYL_Sigma,3)}")
    bin_data_base.drop_in_place('1')

        
def clean():
    global total_files
    global listbox_status
    total_files = pl.DataFrame(None)
    parameter.set('')
    SPAT.set(0.0)
    SPAT_1.set(0.0)
    SYL.set(0.0)
    SYL_1.set(0.0)
    syl_display.set('')
    bin_data_base.clear()
    files_amount.set('檔案數量 : 0')
    listbox_status = False

def sbl_window():
    window = tk.Toplevel()
    window.title('SBL')
    window.resizable(False, True)
    window_width = root.winfo_screenwidth()    # 取得螢幕寬度
    window_height = root.winfo_screenheight()  # 取得螢幕高度
    width = 500
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
    title = tk.Label(frame,text='Bin                3σ                 4σ                 Mean                 Sigma',font=('Arial',12))
    title.place(x=25,y=25)
    #print(sorted(bin_data_base.columns))
    for i,bin in enumerate(sorted(bin_data_base.columns)):
        Mean = bin_data_base[bin].mean() *100
        Sigma = bin_data_base[bin].std() *100
        SBL1 = round(Mean + 3 * Sigma , 3)
        SBL2 = round(Mean + 4 * Sigma , 3)
        frame_height = 65 + i * 65
        bin_label = tk.Label(frame,text=bin,font=('Arial',14))
        bin_label.place(x=25,y=frame_height)
        bin_btn0 = tk.Button(frame,text=SBL1,command=partial(copy_spe,SBL1),font=('Arial',14),relief='solid',bd=2)
        bin_btn0.place(x=85,y=frame_height)
        bin_btn1 = tk.Button(frame,text=SBL2,command=partial(copy_spe,SBL2),font=('Arial',14),relief='solid',bd=2)
        bin_btn1.place(x=185,y=frame_height)
        bin_label1 = tk.Label(frame,text=f'{round(Mean,3)}         {round(Sigma,3)}',font=('Arial',14))
        bin_label1.place(x=285,y=frame_height)

    canvas.config(scrollregion=(0,0,500,frame_height+70))
    scbar.config(command=canvas.yview)
    frame.config(width=500,height=frame_height+70)
    canvas.pack(fill='both',expand=True)
    canvas.create_window((0,0),window=frame,anchor='nw')
    window.mainloop()

def copy(type):
    root.clipboard_clear()
    root.clipboard_append(type.get())

def copy_spe(type):
    root.clipboard_clear()
    root.clipboard_append(type)


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
    root.geometry(f'{width}x{height}+{left}+{top}')

    #變數初始化
    SPAT = tk.DoubleVar()
    SPAT_1 = tk.DoubleVar()
    SYL = tk.DoubleVar()
    SYL_1 = tk.DoubleVar()

    parameter = tk.StringVar()
    files_amount = tk.StringVar()
    syl_display = tk.StringVar()
    adj = tk.IntVar()
    adj.set('6')
    files_amount.set("檔案數量 : 0")
    ban_list = ['X','Y','Time/mS','Bin','SiteNo','TestNo']
    listbox_status = False
    
    
    
    #元件配置初始化
    #SPAT標題
    label = tk.Label(root, text="SPAT=Mean±          Sigma", wraplength=300,font=('Arial',18))
    label.place(relx=0.1,rely=0.6,height=50)
    #SPAT按鈕
    btn = tk.Button(root,textvariable=SPAT, command=partial(copy,SPAT),font=('Arial',20),relief='solid',bd=2)
    btn.place(relx=0.6,rely=0.6,width=100,height=50)
    #SPAT按鈕_1
    btn_1 = tk.Button(root,textvariable=SPAT_1, command=partial(copy,SPAT_1),font=('Arial',20),relief='solid',bd=2)
    btn_1.place(relx=0.8,rely=0.6,width=100,height=50)
    #SYL標題
    label1 = tk.Label(root, text="SYL", wraplength=300,font=('Arial',20))
    label1.place(relx=0.07,rely=0.73,width=100,height=50)
    #SYL按鈕
    btn1 = tk.Button(root,textvariable=SYL, command=partial(copy,SYL),font=('Arial',20),relief='solid',bd=2)
    btn1.place(relx=0.22,rely=0.73,width=100,height=50)
    #SYL按鈕_1
    btn1_1 = tk.Button(root,textvariable=SYL_1, command=partial(copy,SYL_1),font=('Arial',20),relief='solid',bd=2)
    btn1_1.place(relx=0.42,rely=0.73,width=100,height=50)
    #SYL title
    label3 = tk.Label(root,text='3σ                         4σ                     Mean                   Sigma',font=('Arial',12))
    label3.place(relx=0.28,rely=0.69)
    #SYL標註
    label4 = tk.Label(root,textvariable=syl_display,font=('Arial',20))
    label4.place(relx=0.61,rely=0.74)
    #SBL標題
    sbl_btn = tk.Button(root, text="SBL", font=('Arial',20),command=sbl_window,relief='solid',bd=2)
    sbl_btn.place(relx=0.42,rely=0.85,width=100,height=50)
    
    #打開資料夾按鈕
    openfilesbtn = tk.Button(root,text='Open directory',font=('Arial',15),command=loadfiles,relief='solid',bd=2)
    openfilesbtn.place(relx=0.1,rely=0.1,width=150,height=70)
    #clean按鈕
    clnbtn = tk.Button(root ,text='Clean',font=('Arial',20),command=clean,relief='solid',bd=2)
    clnbtn.place(relx=0.1,rely=0.26,width=150,height=70)
    #計算按鈕
    runbtn = tk.Button(root ,text='Calculate',font=('Arial',20),command=calculate,relief='solid',bd=2)
    runbtn.place(relx=0.1,rely=0.42,width=460,height=50)
    #滾動條
    scollbar = tk.Scrollbar(root)
    scollbar.place(relx=0.87,rely=0.1,height=170)
    #listbox
    listbox = tk.Listbox(root ,listvariable=parameter,font=('Arial',10),selectmode='single',yscrollcommand=scollbar.set,justify='center')
    listbox.place(relx=0.45,rely=0.1,width=250,height=170)
    #檔案數量
    files_amount_dis = tk.Label(root,textvariable=files_amount,font=('Arial',17))
    files_amount_dis.place(relx=0.35,rely=0.51)
    #SPAT數值調整
    spinbox = tk.Spinbox(root,from_=0,to=50,font=('Arial',17),fg='#f00',justify='center',textvariable=adj)
    spinbox.place(relx=0.37,rely=0.62,width=50)

    
    #scollbar
    scollbar.config(command=listbox.yview)
    


    root.mainloop()

