# 项目目标

开发一个财务管理系统，员工可以通过系统查询个人薪资等级和具体的工资，并能够实现按月、季度、年份进行工资的统计，以及通过提交财务报表，财务人员可以通过系统对不同用户的工资等级进行设置，管理员能够实现对不同用户权限的管理

# 项目部署

- Python版本：3.11.9

## 后端部署

### 数据库

- 数据库：PostgreSQL(psql 15.1)
- 关系表（暂时）
| 架构模式 | 表名 | 字段 |
| --- |
| 用户表 | users | id, username, password, role, user_id |
| 工资表 | salary | id, user_id, salary_level, salary_amount, data |
另外俩表暂时不用。

```sql
-- 创建数据库
CREATE DATABASE finance_management;
CREATE USER username WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE finance_management TO username;
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
# 创建虚拟环境（可选、推荐）
conda -n FMS python=3.11.9
# 激活虚拟环境
conda activate FMS
# 安装依赖
pip install -r requirements.txt
# 运行backend.py，完成数据库初始化，启动后端
python backend.py
```

## 前端部署

同[服务器端](#服务器端)。

# TODO

- [ ] 数据库重构
- [ ] 员工通过系统查询个人按月、季度、年份的工资
- [ ] UI设计
- [ ] 系统安全性
- [ ] 返回到登录页面时，自动清除用户信息
- [ ] 代码规范