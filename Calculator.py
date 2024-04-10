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
            print(f'檔案數量:{total_files.height}')

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
    global total_files
    global data_base
    for file in total_files.get_column('column_0'):
        rd = pl.scan_csv(file,has_header=True,skip_rows=11,skip_rows_after_header=5).filter(Bin = 1)
        n, = listbox.curselection()
        try:
            show = rd.select(listbox.get(n)).collect()
            show = show.cast(pl.Float64)
        except:
            show = rd.with_columns(pl.col(listbox.get(n)).str.strip_chars()).select(listbox.get(n)).collect()
            show = show.cast(pl.Float64)
       
        #print(type(show))
        #print(listbox.get(n))
        try:
            data_base = pl.concat([data_base,show])
        except:
            data_base = show
    print(data_base)
    Robust_Mean = data_base.median().item(0,0)
    Robust_Sigma = (data_base.quantile(0.75,"nearest").item(0,0) - data_base.quantile(0.25,"nearest").item(0,0)) / 1.35
    print(f'Robust_Mean: {Robust_Mean}')
    print(f'Robust_Sigma: {Robust_Sigma}')
    SPAT.set(Robust_Mean)
        


def spat_c():
    root.clipboard_clear()
    root.clipboard_append(SPAT.get())

if __name__ == '__main__':
    #視窗初始化
    root = tk.Tk()
    root.title('Calculator')
    root.resizable(False, False)
    window_width = root.winfo_screenwidth()    # 取得螢幕寬度
    window_height = root.winfo_screenheight()  # 取得螢幕高度
    width = 500
    height = 500
    left = int((window_width - width)/2)       # 計算左上 x 座標
    top = int((window_height - height)/2)      # 計算左上 y 座標
    root.geometry(f'{width}x{height}+{left}+{top}')

    #變數初始化
    SPAT = tk.StringVar()
    SPAT.set('hihixd')
    parameter = tk.StringVar()
    ban_list = ['X','Y','Time/mS','Bin','SiteNo','TestNo']
    listbox_status = False
    
    
    #元件配置初始化
    #SPAT標題
    label = tk.Label(root, text="SPAT", wraplength=300,font=('Arial',20))
    label.place(relx=0.1,rely=0.7,width=100,height=50)
    #SPAT按鈕
    btn = tk.Button(root,textvariable=SPAT, command=spat_c,font=('Arial',20))
    btn.place(relx=0.3,rely=0.7,width=100,height=50)
    #打開資料夾按鈕
    openfilesbtn = tk.Button(root,text='Open directory',font=('Arial',15),command=loadfiles,relief='solid',bd=2)
    openfilesbtn.place(relx=0.1,rely=0.1,width=150,height=70)
    #clean按鈕
    clnbtn = tk.Button(root ,text='Clean',font=('Arial',20),relief='solid',bd=2)
    clnbtn.place(relx=0.1,rely=0.3,width=150,height=70)
    #計算按鈕
    runbtn = tk.Button(root ,text='Calculate',font=('Arial',20),command=calculate,relief='solid',bd=2)
    runbtn.place(relx=0.1,rely=0.5,width=410,height=50)
    #滾動條
    scollbar = tk.Scrollbar(root)
    scollbar.place(relx=0.9,rely=0.1,height=170)
    #listbox
    listbox = tk.Listbox(root ,listvariable=parameter,font=('Arial',10),selectmode='single',yscrollcommand=scollbar.set,justify='center')
    listbox.place(relx=0.45,rely=0.1,width=225,height=170)
    

    scollbar.config(command=listbox.yview)
    


    root.mainloop()

