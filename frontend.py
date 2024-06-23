import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, ttk
from PIL import Image, ImageTk
import requests
import json
import os
import datetime

# URLs for backend API
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/login"
SALARY_URL = f"{BASE_URL}/salary"
STATISTICS_URL = f"{BASE_URL}/salary/statistics"
REPORT_URL = f"{BASE_URL}/report"
PERMISSION_URL = f"{BASE_URL}/permission"

class App:
    # login data
    user_id = 0
    def __init__(self, root):
        self.root = root
        self.root.title("Finance Management System")

        # 设置窗口大小
        self.root.geometry("1280x720")

        # 加载背景图片
        self.bg_image = Image.open("background.jpg")
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        # 创建背景标签
        self.bg_label = tk.Label(self.root, image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # 创建一个父框架
        self.parent_frame = tk.Frame(self.root)
        self.parent_frame.place(relx=0.9, rely=0.5, anchor="e")

        # 创建登录表单的框架
        self.frame = tk.Frame(self.parent_frame)
        self.frame.pack(padx=5, pady=5)

        # 设置半透明效果和背景色
        self.frame.config(bg='#87CEFA', bd=0, highlightthickness=0)

        # 用户名标签和输入框
        self.username_label = tk.Label(self.frame, text="Username:", bg='#87CEFA', fg='white', font=("Helvetica", 14))
        self.username_label.grid(row=0, column=0, sticky="e", pady=10)
        self.username_entry = tk.Entry(self.frame, font=("Helvetica", 14))
        self.username_entry.grid(row=0, column=1, pady=10)

        # 密码标签和输入框
        self.password_label = tk.Label(self.frame, text="Password:", bg='#87CEFA', fg='white', font=("Helvetica", 14))
        self.password_label.grid(row=1, column=0, sticky="e", pady=10)
        self.password_entry = tk.Entry(self.frame, show="*", font=("Helvetica", 14))
        self.password_entry.grid(row=1, column=1, pady=10)

        # 登录按钮
        self.login_button = tk.Button(self.frame, text="Login", command=self.login, font=("Helvetica", 14))
        self.login_button.grid(row=2, columnspan=2, pady=20)


        self.session = requests.Session()


    def create_login_widgets(self):
        self.clear_frame()

        tk.Label(self.frame, text="Username:").grid(row=0, column=0)
        tk.Label(self.frame, text="Password:").grid(row=1, column=0)

        self.username_entry = tk.Entry(self.frame)
        self.password_entry = tk.Entry(self.frame, show="*")

        self.username_entry.grid(row=0, column=1)
        self.password_entry.grid(row=1, column=1)

        tk.Button(self.frame, text="Login", command=self.login).grid(row=2, column=0, columnspan=2)

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        response = self.session.post(LOGIN_URL, json={"username": username, "password": password})
        data = response.json()
        self.user_id = data['user_id']
        if response.status_code == 200:
            role = data['role']
            self.create_role_widgets(role)
        else:
            messagebox.showerror("Login Failed", data['message'])

    def create_role_widgets(self, role):
        self.clear_frame()

        if role == "employee":
            self.create_employee_widgets()
        elif role == "finance":
            self.create_finance_widgets()
        elif role == "admin":
            self.create_admin_widgets()

    def create_employee_widgets(self):
        tk.Button(self.frame, text="View Salary", command=self.view_salary).grid(row=0, column=0)
        tk.Button(self.frame, text="View Salary Statistics", command=self.view_salary_statistics).grid(row=1, column=0)
        self.create_return_button()

    def create_finance_widgets(self):
        self.create_employee_widgets()
        tk.Button(self.frame, text="Set Salary", command=self.set_salary).grid(row=2, column=0)
        tk.Button(self.frame, text="Submit Report", command=self.submit_report).grid(row=3, column=0)
        self.create_return_button()

    def create_admin_widgets(self):
        self.create_employee_widgets()
        tk.Button(self.frame, text="Set Permission", command=self.set_permission).grid(row=2, column=0)
        self.create_return_button()

    def view_salary(self):
        # user_id = self.get_user_id()
        # if user_id is None:  # 用户取消输入
        #     return
        response = requests.get(f"{SALARY_URL}/{self.user_id}")
        # print(response.text)
        data = response.json()
        try:
            salary_info = f"最新薪资等级: {data['grade']}, 更新时间: {data['ts']}"
            messagebox.showinfo("查看薪资等级", salary_info)
        except:
            messagebox.showerror("Error", data['message'])

    def view_salary_statistics(self):
        # 创建新的窗口
        stat_window = tk.Toplevel(self.root)
        stat_window.title("View Salary Statistics")

        # 时间类型选择框
        time_type_label = ttk.Label(stat_window, text="Select Time Type:")
        time_type_label.pack(pady=5)

        time_type = tk.StringVar()
        time_type_combo = ttk.Combobox(stat_window, textvariable=time_type)
        time_type_combo['values'] = ('Month', 'Quarter', 'Year')
        time_type_combo.current(0)  # 设置默认值
        time_type_combo.pack(pady=5)

        # 年份输入框
        year_label = ttk.Label(stat_window, text="Year:")
        year_label.pack(pady=5)

        year_entry = ttk.Entry(stat_window)
        year_entry.pack(pady=5)

        # 月份输入框（仅在选择月份/季度时可见）
        month_label = ttk.Label(stat_window, text="Month:")
        month_label.pack(pady=5)

        month_entry = ttk.Entry(stat_window)
        month_entry.pack(pady=5)

        # 触发选择类型更新
        time_type.trace('w', lambda *args: self.update_inputs(time_type, month_label, month_entry))

        # 创建获取统计数据按钮
        fetch_button = ttk.Button(stat_window, text="Fetch Statistics", command=lambda: self.fetch_statistics(time_type, year_entry, month_entry))
        fetch_button.pack(pady=20)

    def update_inputs(self, time_type, month_label, month_entry):
        selected_type = time_type.get()
        if selected_type == 'Month' or selected_type == 'Quarter':
            month_label.pack(pady=5)
            month_entry.pack(pady=5)
        else:
            month_label.pack_forget()
            month_entry.pack_forget()

    def fetch_statistics(self, time_type, year_entry, month_entry):
        year = int(year_entry.get())
        selected_type = time_type.get()
        date_range = {"year": year}
        if selected_type == 'Month' or selected_type == 'Quarter':
            month = int(month_entry.get())
            if selected_type == 'Month':
                date_range["month"] = month
            else:
                quarter = (month - 1) // 3 + 1
                date_range["quarter"] = quarter

        response = self.session.post(f"{STATISTICS_URL}", json={"option": selected_type.lower(), "date": date_range})
        try:
            data = response.json()
            if selected_type == 'Month':
                statistics_info = f"{year}年{month}月薪资：{data['salary']}元"
            elif selected_type == 'Quarter':
                statistics_info = f"{year}年第{quarter}季度薪资：{data['salary']}元"
            else:
                statistics_info = f"{year}年总薪资：{data['salary']}元"
            messagebox.showinfo("Salary Statistics", statistics_info)
        except:
            messagebox.showerror("Error", data['message'])

    def submit_report(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xls *.xlsx")])
        if file_path:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = self.session.post(REPORT_URL, files=files)
                if response.status_code == 200:
                    messagebox.showinfo("Success", "File is uploaded successfully.")
                else:
                    error_message = response.json().get('message', 'Unknown error')
                    messagebox.showerror("Error", f"Failed to upload file: {error_message}")

    def set_salary(self):
        user_id = self.get_user_id()
        salary_grade = self.get_salary_grade()
        salary_date = self.get_salary_date()
        
        response = self.session.post(SALARY_URL, json={
            "user_id": user_id, "salary_grade": salary_grade, "date": salary_date
        })
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError as e:
            messagebox.showerror("Error", f"Failed to parse JSON: {e}")
            return

        if response.status_code == 200:
            messagebox.showinfo("Success", data['message'])
        else:
            messagebox.showerror("Error", data['message'])

    def set_permission(self):
        user_id = self.get_user_id()
        if user_id is None:
            return
        permission_level = self.get_permission_level()
        if permission_level is None:
            return
        response = self.session.post(PERMISSION_URL, json={"user_id": user_id, "role": permission_level})
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError as e:
            messagebox.showerror("Error", f"Failed to parse JSON: {e}")
            return
        if response.status_code == 200:
            messagebox.showinfo("Success", data['message'])
        else:
            messagebox.showerror("Error", data['message'])
    
    def create_report_widgets(self):
        # 添加上传按钮
        self.upload_button = tk.Button(self.frame, text="Upload Excel File", command=self.submit_report)
        self.upload_button.grid(row=1, column=0, pady=20)

    def create_return_button(self):
        # 创建返回登录界面的按钮
        return_button = tk.Button(self.frame, text="Return to Login", command=self.create_login_widgets)
        return_button.grid(row=3, column=0, columnspan=2, pady=10)

    def get_user_id(self):
        return simpledialog.askstring("Input", "Enter User ID:")

    def get_period(self):
        return simpledialog.askstring("Input", "Enter Period (monthly/quarterly/yearly):")

    def get_report_content(self):
        return simpledialog.askstring("Input", "Enter Report Content:")

    def get_report_date(self):
        return simpledialog.askstring("Input", "Enter Report Date (YYYY-MM-DD):")

    def get_salary_grade(self):
        return simpledialog.askstring("Input", "Enter Salary Grade:")

    def get_salary_amount(self):
        return simpledialog.askstring("Input", "Enter Salary Amount:")

    def get_salary_date(self):
        return simpledialog.askstring("Input", "Enter Salary Date (YYYY-MM-DD):")

    def get_permission_level(self):
        return simpledialog.askstring("Input", "Enter Permission Level:")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
