import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar

def on_date_select():
    selected_date = cal.selection_get()
    print(type(selected_date))
    print("Selected Date:", selected_date)
    result_label.config(text=f"Selected Date: {selected_date}")

# 创建主窗口
root = tk.Tk()
root.title("Date Picker")

# 创建日历小部件
cal = Calendar(root, selectmode='day', year=2024, month=6, day=23)
cal.pack(pady=20)

# 创建选择按钮
select_button = ttk.Button(root, text="Select Date", command=on_date_select)
select_button.pack(pady=20)

# 创建显示选择日期的标签
result_label = ttk.Label(root, text="")
result_label.pack(pady=20)

# 运行主循环
root.mainloop()
