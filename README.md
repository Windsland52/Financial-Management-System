# 项目目标

开发一个财务管理系统，员工可以通过系统查询个人薪资等级和具体的工资，并能够实现按月、季度、年份进行工资的统计，以及通过提交财务报表，财务人员可以通过系统对不同用户的工资等级进行设置，管理员能够实现对不同用户权限的管理

# 项目结构

`backend.py` flask实现的后端

`frontend.py` tkinter实现的客户端

`requirements.txt` 依赖库

`README.md` 项目说明

`/reports` 财务报表存放处

`/flask_session` session存放处

`/dist/FMS财务管理系统.exe` 打包好的前端exe文件 

# 项目部署

- Python版本：3.11.9

## 后端部署

### 数据库

- 数据库：PostgreSQL(最新版安装时请不要选择中文，会出现`The database cluster initialisation failed`错误)
- 关系表
| 中文 | 表名 | 字段 |
| --- | --- | --- |
| 用户表 | user | user_id, username, password, role |
| 薪资等级表 | salary | user_id, ts, salary_grade, modified_by |
| 薪资关系表 | salary_relation | salary_grade, salary_amount |
另外俩表暂时不用。

```sql
-- 创建数据库
CREATE DATABASE finance_management;
CREATE USER username WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE finance_management TO postgres;
```

```python
# Database configuration(backend.py)
DATABASE_USER = os.getenv('DATABASE_USER', 'postgres')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'zhenxun_bot')
# 本地/远程均可
DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
DATABASE_PORT = os.getenv('DATABASE_PORT', '5432')
# 数据库名
DATABASE_NAME = os.getenv('DATABASE_NAME', 'finance_management')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'
```

### 服务器端

```bash
# conda(anoconda/miniconda)安装完成后，将scripts文件夹添加到环境变量PATH中，以便使用conda命令
# cmd进入项目目录，进行conda初始化，运行后重启终端
conda init
# 创建虚拟环境
conda create -n FMS python=3.11.9
# 激活虚拟环境
conda activate FMS
# 安装依赖（不安装conda的话从此处开始即可，记得pip换源）
pip install -r requirements.txt
# pip临时换源安装所需参数
-i https://pypi.tuna.tsinghua.edu.cn/simple
# 运行backend.py，完成数据库初始化，启动后端
python backend.py
```

## 前端部署

同[服务器端](#服务器端)。
### 可能的问题：
#### 后端部署在远程服务器，前端无法连接到后端

1. 检查前后端端口是否有问题
2. 后端部署在远程服务器，需要在防火墙开放端口，如5000端口

# 开发文档

## 后端

### 数据库的连接

```python
class User(db.Model):
    __tablename__ = 'user'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'admin', 'finance', 'employee'

class Salary(db.Model):
    __tablename__ = 'salary'
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False, primary_key=True)
    ts = db.Column(db.DateTime, nullable=False)
    salary_grade = db.Column(db.String(50), nullable=False)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

    # Establish a relationship with the User table for the modifier
    modifier = db.relationship('User', foreign_keys=[modified_by])

    # Optional: Establish a relationship with the User table for the user_id
    user = db.relationship('User', foreign_keys=[user_id])

class SalaryRelation(db.Model):
    __tablename__ = 'salary_relation'
    
    salary_grade = db.Column(db.String(50), primary_key=True)
    salary_amount = db.Column(db.Float, nullable=False)
    
# Create all tables
with app.app_context():
    db.create_all()
```

## 登录

```python
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    # if user and check_password_hash(user.password, data['password']):
    if user and user.password == data['password']:
        session['user_id'] = user.user_id
        session['role'] = user.role
        print('log session', dict(session))
        return jsonify({'message': 'Logged in successfully!', 'role': user.role, 'user_id': user.user_id})
    return jsonify({'message': 'Invalid credentials!'})
```

## 获取当前薪资等级

```python
@app.route('/salary/<int:user_id>', methods=['GET'])
def get_salary(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    if user is None:
        return jsonify({'message': 'User not found!'}), 404
    
    # Check for employee role and access permissions
    if user.role == 'employee' and user.user_id != user_id:
        return jsonify({'message': 'Access denied!'}), 403
    
    # Query for the latest salary entry
    latest_salary = Salary.query.filter_by(user_id=user_id).order_by(Salary.ts.desc()).first()
    
    if latest_salary is None:
        return jsonify({'message': 'No salary data found for the user!'}), 404
    
    return jsonify({'grade': latest_salary.salary_grade, 'ts': latest_salary.ts})
```

## 薪资统计

```python
@app.route('/salary/statistics', methods=['POST'])
def salary_statistics():
    data = request.get_json()
    user_id = session['user_id']
    # if session['role'] == 'employee' and session['user_id'] != int(user_id):
    #     return jsonify({'message': 'Access denied!'}), 403
    option = data['option']  # 'monthly', 'quarterly', 'yearly'
    date = data['date']
    year = date['year']


    user = User.query.filter_by(user_id=user_id).first()
    if user is None:
        return jsonify({'message': 'User not found!'}), 404
    print(data)
    # 加载 Excel 文件
    file_path = f'reports/salary-{year}.xlsx'
    if option =='month':
        month = date['month']
        try:
            df = pd.read_excel(file_path, sheet_name=f'{month}月')
        except Exception as e:
            return jsonify({'message': 'Failed to read Excel file', 'error': str(e)}), 400

        # 搜索名字所在的行
        name_to_search = user.username
        searched_row = df[df.iloc[:, 0] == name_to_search]
        if not searched_row.empty:
            # 获取该名字所在行的某列值（例如，第三列）
            col_index = 1  # 第三列的索引为2
            cell_value = searched_row.iloc[0, col_index]
            # 转换为基本数据类型
            cell_value = cell_value.item() if hasattr(cell_value, 'item') else cell_value
            return jsonify({'salary': cell_value})
        else:
            return jsonify({'message': 'Salary data not found for the user!'}), 404
    elif option == 'quarter':
        quarter = date['quarter']
        try:
            df = pd.read_excel(file_path, sheet_name='总表')
        except Exception as e:
            return jsonify({'message': 'Failed to read Excel file', 'error': str(e)}), 400

        # 搜索名字所在的行
        name_to_search = user.username
        searched_row = df[df.iloc[:, 0] == name_to_search]
        if not searched_row.empty:
            # 获取该名字所在行的某列值（例如，第三列）
            col_index = quarter  # 第三列的索引为2
            cell_value = searched_row.iloc[0, col_index]
            # 转换为基本数据类型
            cell_value = cell_value.item() if hasattr(cell_value, 'item') else cell_value
            return jsonify({'salary': cell_value})
        else:
            return jsonify({'message': 'Salary data not found for the user!'}), 404
    elif option == 'year':
        try:
            df = pd.read_excel(file_path, sheet_name='总表')
        except Exception as e:
            return jsonify({'message': 'Failed to read Excel file', 'error': str(e)}), 400

        # 搜索名字所在的行
        name_to_search = user.username
        searched_row = df[df.iloc[:, 0] == name_to_search]
        if not searched_row.empty:
            # 获取该名字所在行的某列值（例如，第三列）
            col_index = 5  # 第三列的索引为2
            cell_value = searched_row.iloc[0, col_index]
            # 转换为基本数据类型
            cell_value = cell_value.item() if hasattr(cell_value, 'item') else cell_value
            return jsonify({'salary': cell_value})
        else:
            return jsonify({'message': 'Salary data not found for the user!'}), 404
    else:
        return jsonify({'message': 'Invalid option!'}), 400
```

## 设置薪资等级（finance）

```python
@app.route('/salary', methods=['POST'])
@role_required('finance')
def set_salary():
    data = request.get_json()
    salary = Salary.query.filter_by(user_id=data['user_id']).first()
    if not salary:
        return jsonify({'message': 'People not found'}), 404

    salary.salary_grade = data['salary_grade']
    salary.modified_by = session['user_id']
    salary.ts = datetime.now().replace(microsecond=0)
    try:
        db.session.commit()
        return jsonify({'message': 'Salary updated successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update salary', 'error': str(e)}), 500
```

## 提交财务报表（finance）

```python
@app.route('/report', methods=['POST'])
@role_required('finance')
def submit_report():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    # 确保 file.filename 是一个有效的字符串
    if not isinstance(file.filename, str):
        return jsonify({'message': 'Invalid file type'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        print('File saved to:', filepath)
        # 检查文件是否存在
        if not os.path.exists(filepath):
            return jsonify({'message': 'Failed to save file'}), 400
        try:
            # 尝试使用 pandas 读取文件
            df = pd.read_excel(filepath)
            return jsonify({'message': 'File is uploaded successfully'}), 200
        except Exception as e:
            print('Error reading Excel file:', str(e))
            return jsonify({'message': 'Invalid Excel file', 'error': str(e)}), 400
    else:
        return jsonify({'message': 'Invalid file type'}), 400
```

## 设置权限（admin）

```python
@app.route('/permission', methods=['POST'])
@role_required('admin')
def set_permission():
    data = request.get_json()
    user_id = data.get('user_id')
    new_role = data.get('role')

    if not user_id or not new_role:
        return jsonify({'message': 'User ID and role are required'}), 400
    
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    user.role = new_role
    
    try:
        db.session.commit()
        return jsonify({'message': 'Role updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update role', 'error': str(e)}), 500
```

