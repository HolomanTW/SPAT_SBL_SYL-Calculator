import os
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import polars as pl
import multiprocessing
from glob import glob

def loadfiles():
    folder_path = filedialog.askdirectory()
    files = glob(rf'{folder_path}/*.csv')
    print(len(files))
    for file in files:
        rd = pl.read_csv(file,has_header=True,skip_rows=11,skip_rows_after_header=5)
        rd2 = pl.scan_csv(file,has_header=True,skip_rows=11,skip_rows_after_header=5,).filter("Bin" > 1)
        show = rd2.collect()
        print(show)
        print(show.null_count())
        break

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

    #元件配置初始化
    label = tk.Label(root, text="SPAT", wraplength=300,font=('Arial',20))
    label.place(relx=0.1,rely=0.4,width=100,height=50)

    btn = tk.Button(root,textvariable=SPAT, command=spat_c,font=('Arial',20))
    btn.place(relx=0.25,rely=0.4,width=100,height=50)

    openfilesbtn = tk.Button(root,text='Open directory',command=loadfiles,relief='solid',bd=2)
    openfilesbtn.place(relx=0.5,rely=0.1,width=200,height=100)


    root.mainloop()

