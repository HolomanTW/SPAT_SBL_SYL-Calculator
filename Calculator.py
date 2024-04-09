import os
import tkinter as tk
from tkinter import filedialog

import polars as pl
#import multiprocessing
from glob import glob

def loadfiles():
    global listbox_status
    global total_files
    folder_path = filedialog.askdirectory()
    files = (glob(rf'{folder_path}/*.csv'))
    #print(f'檔案數量:{len(files)}')

    
    try:
        total_files = pl.concat([total_files,pl.DataFrame(files)])
        print('ok')
    except:
        total_files = pl.DataFrame(files)
    
    print(total_files)
    print(total_files[0])

    if listbox_status == False:
        rd = pl.scan_csv(files[0],has_header=True,skip_rows=11,n_rows=0)#.filter(Bin = 1)
        show = rd.collect()
        print(show)
        title = [x for x in show.columns if x not in ban_list]
        parameter.set(title)
        listbox_status = True


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
    label = tk.Label(root, text="SPAT", wraplength=300,font=('Arial',20))
    label.place(relx=0.1,rely=0.6,width=100,height=50)

    btn = tk.Button(root,textvariable=SPAT, command=spat_c,font=('Arial',20))
    btn.place(relx=0.3,rely=0.6,width=100,height=50)

    openfilesbtn = tk.Button(root,text='Open directory',font=('Arial',15),command=loadfiles,relief='solid',bd=2)
    openfilesbtn.place(relx=0.1,rely=0.1,width=150,height=70)

    clnbtn = tk.Button(root ,text='Clean',font=('Arial',20),relief='solid',bd=2)
    clnbtn.place(relx=0.1,rely=0.3,width=150,height=70)

    listbox = tk.Listbox(root ,listvariable=parameter)
    listbox.place(relx=0.5,rely=0.1)
    


    root.mainloop()

