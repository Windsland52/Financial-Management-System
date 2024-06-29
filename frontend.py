import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, ttk
from PIL import Image, ImageTk
import requests

# URLs for backend API
LOCAL_URL = "http://127.0.0.1:5000"
REMOTE_URL = "http://43.143.217.242:5000"
# BASE_URL = LOCAL_URL
BASE_URL = REMOTE_URL
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
        # 设置窗口背景颜色  
        self.root.config(bg='lightblue')  

        # 添加标题标签  
        title_label = tk.Label(self.root, text="财务管理系统", font=("Helvetica", 24, "bold"), bg='lightblue', fg='navy')  
        title_label.pack(side=tk.TOP, fill=tk.X, pady=20) 

        # 添加一个用于显示用户面板的框架  
        self.user_panel_frame = tk.Frame(self.root, bg='white')  
        self.user_panel_frame.pack(fill=tk.X, expand=False, pady=0)  # 初始时不显示或只显示很小的高度

        # 创建一个父框架（可选，但有助于组织布局）  
        self.parent_frame = tk.Frame(self.root)  
        self.parent_frame.pack(fill=tk.BOTH, expand=True)

        # 创建登录表单的框架  
        self.frame = tk.Frame(self.parent_frame, bg='#87CEFA')
        self.frame.grid(row=0, column=0, sticky='nsew', padx=(self.root.winfo_width()+960) // 2, pady=(self.root.winfo_height()+350) // 2) 

        # 使用grid布局来居中登录表单内容（这里我们使用pack和anchor来实现居中）  
        # 注意：由于pack不支持直接居中，我们需要通过额外的Frame或使用place  
        # 但为了简单起见，这里我们使用grid在内部Frame中居中，然后将内部Frame pack到center_frame中  
        self.inner_frame = tk.Frame(self.frame)  
        self.inner_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)  
  
        # 设置grid的权重，使self.inner_frame扩展以填充self.frame  
        self.frame.rowconfigure(0, weight=1)  
        self.frame.columnconfigure(0, weight=1)  

        # 用户名标签和输入框
        self.username_label = tk.Label(self.inner_frame, text="Username:", bg='#87CEFA', fg='white', font=("Helvetica", 14))
        self.username_label.grid(row=0, column=0, sticky="e", pady=10)
        self.username_entry = tk.Entry(self.inner_frame, font=("Helvetica", 14))
        self.username_entry.grid(row=0, column=1, pady=10)

        # 密码标签和输入框
        self.password_label = tk.Label(self.inner_frame, text="Password:", bg='#87CEFA', fg='white', font=("Helvetica", 14))
        self.password_label.grid(row=1, column=0, sticky="e", pady=10)
        self.password_entry = tk.Entry(self.inner_frame, show="*", font=("Helvetica", 14))
        self.password_entry.grid(row=1, column=1, pady=10)

        # 登录按钮
        self.login_button = tk.Button(self.inner_frame, text="Login", command=self.attempt_login, font=("Helvetica", 14))
        self.login_button.grid(row=2, columnspan=2, pady=20)


        # 将回车键的按下事件绑定到on_enter_pressed函数  
        self.root.bind("<Return>", self.on_enter_pressed)

        # 使用grid的columnconfigure和rowconfigure来使self.inner_frame中的元素居中（实际上，pack+anchor或place可能更直接，但这里展示grid的用法）  
        # 注意：这里的居中更多是通过填充和权重来实现的视觉居中，而不是严格的水平/垂直居中  
        self.inner_frame.grid_columnconfigure(1, weight=1)  # 让输入框所在的列扩展  

        self.inner_frame.pack(expand=True)

        self.session = requests.Session()

    def attempt_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        response = self.session.post(LOGIN_URL, json={"username": username, "password": password})
        # print(response.text)
        data = response.json()
        if response.status_code == 200:  
            self.user_id = data['user_id']  
            role = data['role']
            # 更新用户面板以显示欢迎信息和返回按钮  
            self.update_user_panel(role)
  
            # 创建一个新的顶层窗口来显示用户面板  
            self.create_role_specific_window(role)  
  
            # 可选：隐藏登录表单（注意：这也会隐藏用户面板框架，因为它在登录表单下面）  
            self.parent_frame.pack_forget()
  
        else:  
            messagebox.showerror("Login Failed", data['message'])
    
    def update_user_panel(self, role):  
        # 清空用户面板框架中的现有内容（如果有的话）  
        for widget in self.user_panel_frame.winfo_children():  
            widget.destroy()
        self.user_panel_frame.pack(fill=tk.X, expand=True, pady=300) 
  
        # 添加欢迎标签  
        welcome_label = tk.Label(self.user_panel_frame, text=f"欢迎您，{role}。", font=("Helvetica", 20))  
        welcome_label.pack(side=tk.LEFT, padx=500)  
  
        # 添加退出登录按钮（这里假设登录表单总是在视图中）  
        # 如果登录表单会被隐藏，您可能需要在这里添加逻辑来重新显示它  
        logout_btn = tk.Button(self.user_panel_frame, text="EXIT",  
                       command=self.reset_user_panel,  
                       font=("Helvetica", 10, "bold"),  # 增加字体大小和加粗  
                       width=15,  # 文本宽度，但可能不是您想要的“放大”效果  
                       borderwidth=1,
                       padx=40,  # 增加水平填充  
                       pady=30)   # 增加垂直填充  
        logout_btn.pack(side=tk.RIGHT, padx=20)
  
        # 可选：调整用户面板框架的大小以适应新内容  
        self.user_panel_frame.config(height=50)  # 或者使用pack_propagate(False)和grid_rowconfigure/columnconfigure  
  
    def reset_user_panel(self):  
        # 清空用户面板框架中的现有内容（如果有的话）  
        for widget in self.user_panel_frame.winfo_children():  
            widget.destroy()
        self.user_panel_frame.pack_forget()  # 隐藏用户面板框架
        self.parent_frame.pack(fill=tk.BOTH, expand=True)  # 显示登录表单
        # 重置session
        self.session = requests.Session()

    def create_role_specific_window(self, role):
        if role == "employee":
            self.create_employee_widgets()
        elif role == "finance":
            self.create_finance_widgets()
        elif role == "admin":
            self.create_admin_widgets()

    def create_employee_widgets(self):
        # 创建新的窗口
        stat_window = tk.Toplevel(self.root)
        stat_window.title("员工面板") 
  
        # 薪资查看按钮  
        view_salary_btn = tk.Button(stat_window, text="查看当前薪资等级", font=("Helvetica", 12), command=self.view_salary, width=20)  
        view_salary_btn.grid(row=1, column=0, padx=10, pady=10)  
  
        # 薪资统计查看按钮  
        view_stats_btn = tk.Button(stat_window, text="查询薪资统计信息", font=("Helvetica", 12), command=self.view_salary_statistics, width=20)  
        view_stats_btn.grid(row=1, column=1, padx=10, pady=10)

    def create_finance_widgets(self):
        # 创建新的窗口
        stat_window = tk.Toplevel(self.root)
        stat_window.title("财务面板") 
  
        # 薪资查看按钮  
        view_salary_btn = tk.Button(stat_window, text="查看当前薪资等级", font=("Helvetica", 12), command=self.view_salary, width=20)  
        view_salary_btn.grid(row=1, column=0, padx=10, pady=10)  
  
        # 薪资统计查看按钮  
        view_stats_btn = tk.Button(stat_window, text="查询薪资统计信息", font=("Helvetica", 12), command=self.view_salary_statistics, width=20)  
        view_stats_btn.grid(row=1, column=1, padx=10, pady=10)

        # 薪资设置按钮  
        set_salary_btn = tk.Button(stat_window, text="设置薪资", font=("Helvetica", 12), command=self.set_salary, width=20)  
        set_salary_btn.grid(row=2, column=0, padx=10, pady=10)

        # 薪资报告上传按钮  
        upload_report_btn = tk.Button(stat_window, text="上传财务报表", font=("Helvetica", 12), command=self.submit_report, width=20)  
        upload_report_btn.grid(row=2, column=1, padx=10, pady=10)

    def create_admin_widgets(self):
        # 创建新的窗口
        stat_window = tk.Toplevel(self.root)
        stat_window.title("管理面板") 
  
        # 薪资查看按钮  
        view_salary_btn = tk.Button(stat_window, text="查看当前薪资等级", font=("Helvetica", 12), command=self.view_salary, width=20)  
        view_salary_btn.grid(row=1, column=0, padx=10, pady=10)  
  
        # 薪资统计查看按钮  
        view_stats_btn = tk.Button(stat_window, text="查询薪资统计信息", font=("Helvetica", 12), command=self.view_salary_statistics, width=20)  
        view_stats_btn.grid(row=1, column=1, padx=10, pady=10)

        # 设置权限按钮  
        set_permission_btn = tk.Button(stat_window, text="设置权限", font=("Helvetica", 12), command=self.set_permission, width=43)  
        set_permission_btn.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    def view_salary(self):
        response = requests.get(f"{SALARY_URL}/{self.user_id}")
        # print(response.text)
        print(self.session.params,self.session.headers,self.session.cookies)
        data = response.json()
        try:
            salary_info = f"最新薪资等级: {data['grade']}, 更新时间: {data['ts']}"
            messagebox.showinfo("查看薪资等级", salary_info)
        except:
            messagebox.showerror("Error", data['message'])

    def view_salary_statistics(self):
        # 创建新的窗口
        stat_window = tk.Toplevel(self.root)
        stat_window.title("薪资统计信息")

        # 时间类型选择框
        time_type_label = ttk.Label(stat_window, text="选择查询类型:")
        time_type_label.pack(pady=3)

        time_type = tk.StringVar()
        time_type_combo = ttk.Combobox(stat_window, textvariable=time_type)
        time_type_combo['values'] = ('月', '季度', '年')
        time_type_combo.current(0)  # 设置默认值
        time_type_combo.pack(pady=5)

        # 年份输入框
        year_label = ttk.Label(stat_window, text="年份:")
        year_label.pack(pady=5)

        year_entry = ttk.Entry(stat_window)
        year_entry.pack(pady=5)

        # 月份输入框（仅在选择月份/季度时可见）
        month_label = ttk.Label(stat_window, text="月份:")
        month_label.pack(pady=5)

        month_entry = ttk.Entry(stat_window)
        month_entry.pack(pady=5)

        # 触发选择类型更新
        time_type.trace_add('write', lambda *args: self.update_inputs(time_type, month_label, month_entry))

        # 创建获取统计数据按钮
        fetch_button = ttk.Button(stat_window, text="统计数据", command=lambda: self.fetch_statistics(time_type, year_entry, month_entry))
        fetch_button.pack(pady=20)

    def update_inputs(self, time_type, month_label, month_entry):
        selected_type = time_type.get()
        if selected_type == '月' or selected_type == '季度':
            month_label.pack(pady=5)
            month_entry.pack(pady=5)
        else:
            month_label.pack_forget()
            month_entry.pack_forget()

    def fetch_statistics(self, time_type, year_entry, month_entry):
        year = int(year_entry.get())
        selected_type = time_type.get()
        date_range = {"year": year}
        if selected_type == '月' or selected_type == '季度':
            month = int(month_entry.get())
            if selected_type == '月':
                option = "month"
                date_range["month"] = month
            else:
                option = "quarter"
                quarter = (month - 1) // 3 + 1
                date_range["quarter"] = quarter
        else:
            option = "year"
        response = self.session.post(f"{STATISTICS_URL}", json={"option": option, "date": date_range})
        try:
            data = response.json()
            if selected_type == '月':
                statistics_info = f"{year}年{month}月薪资：{data['salary']}元"
            elif selected_type == '季度':
                statistics_info = f"{year}年第{quarter}季度薪资：{data['salary']}元"
            else:
                statistics_info = f"{year}年总薪资：{data['salary']}元"
            messagebox.showinfo("薪资统计", statistics_info)
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
        
        response = self.session.post(SALARY_URL, json={
            "user_id": user_id, "salary_grade": salary_grade
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

    def get_user_id(self):
        return simpledialog.askstring("Input", "Enter User ID:")

    def get_salary_grade(self):
        return simpledialog.askstring("Input", "Enter Salary Grade:")

    def get_permission_level(self):
        return simpledialog.askstring("Input", "Enter Permission Level:")
    
    def on_enter_pressed(self, event):  
        self.attempt_login() 

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
