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
| 用户表 | users | user_id, username, password, role |
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
