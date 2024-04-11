#import os
import tkinter as tk
from tkinter import filedialog
import polars as pl
#import multiprocessing
from glob import glob

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
        
        try:
            data_base = pl.concat([data_base,spat])
            bin_data_base = pl.concat([bin_data_base,bin_rd])
        except:
            data_base = spat
            bin_data_base = bin_rd
        
    print(data_base)
    print(bin_data_base)
    print(
        bin_data_base.group_by("Bin")
        .agg([pl.len().alias("count")])
        .with_columns((pl.col("count") / pl.sum("count")).alias("percent_count"))
    )

    Robust_Mean = data_base.median().item(0,0)
    Robust_Sigma = (data_base.quantile(0.75,"nearest").item(0,0) - data_base.quantile(0.25,"nearest").item(0,0)) / 1.35
    print(f'Robust_Mean: {Robust_Mean}')
    print(f'Robust_Sigma: {round(Robust_Sigma,3)}')

    SPAT.set(round(Robust_Mean + float(spinbox.get()) * Robust_Sigma , 3))
    SPAT_1.set(round(Robust_Mean - float(spinbox.get()) * Robust_Sigma , 3))
        
def clean():
    global total_files
    global listbox_status
    total_files = pl.DataFrame(None)
    parameter.set('')
    files_amount.set('檔案數量 : 0')
    listbox_status = False

def spat_c():
    root.clipboard_clear()
    root.clipboard_append(SPAT.get())

def spat_1_c():
    root.clipboard_clear()
    root.clipboard_append(SPAT_1.get())

def syl_c():
    root.clipboard_clear()
    root.clipboard_append(SYL.get())

def syl_1_c():
    root.clipboard_clear()
    root.clipboard_append(SYL_1.get())

def sbl_c():
    root.clipboard_clear()
    root.clipboard_append(SBL.get())

def sbl_1_c():
    root.clipboard_clear()
    root.clipboard_append(SBL_1.get())

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
    SBL = tk.DoubleVar()
    SBL_1 = tk.DoubleVar()
    parameter = tk.StringVar()
    files_amount = tk.StringVar()
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
    btn = tk.Button(root,textvariable=SPAT, command=spat_c,font=('Arial',20),relief='solid',bd=2)
    btn.place(relx=0.6,rely=0.6,width=100,height=50)
    #SPAT按鈕_1
    btn_1 = tk.Button(root,textvariable=SPAT_1, command=spat_1_c,font=('Arial',20),relief='solid',bd=2)
    btn_1.place(relx=0.8,rely=0.6,width=100,height=50)
    #SYL標題
    label1 = tk.Label(root, text="SYL", wraplength=300,font=('Arial',20))
    label1.place(relx=0.1,rely=0.7,width=100,height=50)
    #SYL按鈕
    btn1 = tk.Button(root,textvariable=SYL, command=syl_c,font=('Arial',20),relief='solid',bd=2)
    btn1.place(relx=0.3,rely=0.7,width=100,height=50)
    #SYL按鈕_1
    btn1_1 = tk.Button(root,textvariable=SYL_1, command=syl_1_c,font=('Arial',20),relief='solid',bd=2)
    btn1_1.place(relx=0.6,rely=0.7,width=100,height=50)
    #SBL標題
    label2 = tk.Label(root, text="SBL", wraplength=300,font=('Arial',20))
    label2.place(relx=0.1,rely=0.85,width=100,height=50)
    #SBL按鈕
    btn2 = tk.Button(root,textvariable=SBL, command=sbl_c,font=('Arial',20),relief='solid',bd=2)
    btn2.place(relx=0.3,rely=0.85,width=100,height=50)
    #SBL按鈕_1
    btn2_1 = tk.Button(root,textvariable=SBL_1, command=sbl_1_c,font=('Arial',20),relief='solid',bd=2)
    btn2_1.place(relx=0.6,rely=0.85,width=100,height=50)
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

    

    scollbar.config(command=listbox.yview)
    


    root.mainloop()

