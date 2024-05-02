import polars as pl
#import tkinter as tk
from glob import glob
import time

'''
root = tk.Tk()
root.title('SBL')
root.resizable(False, True)
window_width = root.winfo_screenwidth()    # 取得螢幕寬度
window_height = root.winfo_screenheight()  # 取得螢幕高度
width = 500
height = 200
left = int((window_width - width)/2)       # 計算左上 x 座標
top = int((window_height - height)/2)      # 計算左上 y 座標
root.geometry(f'{width}x{height}+{left}+{top}')

scbar = tk.Scrollbar(root,orient='vertical')
scbar.pack(side='right',fill='y')

canvas = tk.Canvas(root,scrollregion=(0,0,450,500),yscrollcommand=scbar.set,relief='solid',bd=2)
#canvas.create_line(100,10,100,700,width=20,dash=(10,5))

frame  = tk.Frame(canvas,relief='solid',bd=5,width=500,height=200)
bin_label = tk.Label(frame,text='bin',font=('Arial',14))
bin_label.place(x=25,y=65)
bin_btn0 = tk.Button(frame,text='SBL1',font=('Arial',14),relief='solid',bd=2)
bin_btn0.place(x=85,y=65)
bin_btn1 = tk.Button(frame,text='SBL2',font=('Arial',14),relief='solid',bd=2)
bin_btn1.place(x=185,y=65)
bin_label1 = tk.Label(frame,text='0.000         0.000',font=('Arial',14))
bin_label1.place(x=285,y=65)

scbar.config(command=canvas.yview)

canvas.pack(fill='both',expand=True)
canvas.create_window((0,0),window=frame,anchor='nw')

root.mainloop()


'''
start = time.perf_counter()
files = glob(f'C:/Users/92403/Desktop/test/H3N/**/*[!a-z].csv',recursive=True)
for f in files:
    rd = pl.read_csv(f ,has_header=True,skip_rows=13,skip_rows_after_header=1,n_rows=1,truncate_ragged_lines=True).select('1')

    try:
        bin_data_base = pl.concat([bin_data_base,rd],how='diagonal').fill_null(0)
    except:
        bin_data_base = rd
bin_data_base1=bin_data_base.cast(pl.Int32)
print(bin_data_base1.sum())

end0 = time.perf_counter()
print(f'scan done {end0-start}')
'''
data_base=rd.drop('').filter((pl.col("Bin#") == '1') & (pl.col('Parameter') == 'PID-')).select('IDSS_Post').cast(pl.Float64)
data1 = data_base.median().collect().item(0,0)
data2 = data_base.quantile(0.25,'linear').collect().item(0,0)
data3 = data_base.quantile(0.5,'linear').collect().item(0,0)
data4 = data_base.quantile(0.75,'linear').collect().item(0,0)

data = data_base.median().item(0,0)
data1 = data_base.quantile(0.25,'linear').item(0,0)
data2 = data_base.quantile(0.5,'linear').item(0,0)
data3 = data_base.quantile(0.75,'linear').item(0,0)'''

'''
for file in files:
    rd = pl.scan_csv(file ,has_header=True,skip_rows=18,truncate_ragged_lines=True)
    spat = rd.drop('').filter((pl.col("Bin#") == '1') & (pl.col('Parameter') == 'PID-')).collect()
    try:
        data_base = pl.concat([data_base,spat])
    except:
        data_base = spat
'''


#bin_rd = bin_rd[[s.name for s in bin_rd if not (s.null_count() == bin_rd.height)]]
#rd = rd.drop(i.name for i in rd if (i.null_count() == 2))

#print(bin_rd.sum_horizontal())

#new = spat.cast(pl.Float64)
#bin_rd = bin_rd.cast(pl.Int32)




