from flask import Flask, request, jsonify, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
import pandas as pd
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Database configuration
DATABASE_USER = os.getenv('DATABASE_USER', 'postgres')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'zhenxun_bot')
DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
DATABASE_PORT = os.getenv('DATABASE_PORT', '5432')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'finance_management')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SESSION_COOKIE_SECURE'] = False  # 仅在开发环境中设置为 False，生产环境中应设置为 True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_TYPE'] = 'filesystem'  # 确保会话存储在服务器端
app.config['UPLOAD_FOLDER'] = './reports/'
app.config['ALLOWED_EXTENSIONS'] = {'xls', 'xlsx'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)
CORS(app, supports_credentials=True)  # 允许发送凭据（如会话 cookie）

# 初始化会话
Session(app)

# Define models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'admin', 'finance', 'employee'
    user_id = db.Column(db.Integer, unique=True, nullable=False)

class Salary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    salary_grade = db.Column(db.String(50), nullable=False)
    salary_amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    report_content = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    permission_level = db.Column(db.String(50), nullable=False)

# Create all tables
with app.app_context():
    db.create_all()

# Define routes and handlers
# @app.route('/register', methods=['POST'])
# def register():
#     data = request.get_json()
#     hashed_password = generate_password_hash(data['password'], method='sha256')
#     new_user = User(username=data['username'], password=hashed_password, role=data['role'], user_id=data['user_id'])
#     db.session.add(new_user)
#     db.session.commit()
#     return jsonify({'message': 'New user created!'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    # if user and check_password_hash(user.password, data['password']):
    if user and user.password == data['password']:
        session['user_id'] = user.user_id
        session['role'] = user.role
        print('log session', dict(session))
        return jsonify({'message': 'Logged in successfully!', 'role': user.role, 'user_id': user.id})
    return jsonify({'message': 'Invalid credentials!'})

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print("Session in decorator:", dict(session))  # 打印调试信息
            if 'user_id' not in session or 'role' not in session:
                return jsonify({'message': 'Unauthorized'}), 401
            if session['role'] != role:
                return jsonify({'message': 'Permission denied'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/users', methods=['GET'])
@role_required('admin')
def get_users():
    users = User.query.all()
    return jsonify([user.username for user in users])

@app.route('/salary', methods=['POST'])
@role_required('finance')
def set_salary():
    data = request.get_json()
    salary = Salary.query.filter_by(user_id=data['user_id'], date=datetime.strptime(data['date'], '%Y-%m-%d').date()).first()
    if not salary:
        return jsonify({'message': 'Salary record not found'}), 404

    salary.salary_grade = data['salary_grade']
    
    try:
        db.session.commit()
        return jsonify({'message': 'Salary updated successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update salary', 'error': str(e)}), 500

@app.route('/salary/<int:user_id>', methods=['GET'])
def get_salary(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    if user.role == 'employee' and user.user_id != user_id:
        return jsonify({'message': 'Access denied!'}), 403
    
    salaries = Salary.query.filter_by(user_id=user_id).all()
    return jsonify([{'grade': s.salary_grade, 'amount': s.salary_amount, 'date': s.date} for s in salaries])

@app.route('/salary/statistics', methods=['GET'])
def salary_statistics():
    user_id = request.args.get('user_id')
    if session['role'] == 'employee' and session['user_id'] != int(user_id):
        return jsonify({'message': 'Access denied!'}), 403
    period = request.args.get('period')  # 'monthly', 'quarterly', 'yearly'

    if period == 'monthly':
        salaries = db.session.query(
            db.func.date_trunc('month', Salary.date).label('period'), 
            db.func.sum(Salary.salary_amount).label('total_amount')
        ).group_by('period').filter_by(user_id=user_id).all()
    elif period == 'quarterly':
        salaries = db.session.query(
            db.func.date_trunc('quarter', Salary.date).label('period'), 
            db.func.sum(Salary.salary_amount).label('total_amount')
        ).group_by('period').filter_by(user_id=user_id).all()
    elif period == 'yearly':
        salaries = db.session.query(
            db.func.date_trunc('year', Salary.date).label('period'), 
            db.func.sum(Salary.salary_amount).label('total_amount')
        ).group_by('period').filter_by(user_id=user_id).all()
    
    return jsonify([{'period': str(s.period), 'total_amount': s.total_amount} for s in salaries])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/report', methods=['POST'])
@role_required('finance')
def submit_report():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
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

# @app.route('/reports', methods=['GET'])
# @role_required('admin')
# def get_reports():
#     reports = Report.query.all()
#     return jsonify([{'user_id': r.user_id, 'content': r.report_content, 'date': r.date} for r in reports])

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

# @app.route('/permission/<int:user_id>', methods=['GET'])
# @role_required('admin')
# def get_permission(user_id):
#     permission = Permission.query.filter_by(user_id=user_id).first()
#     return jsonify({'user_id': permission.user_id, 'level': permission.permission_level})

if __name__ == '__main__':
    app.run(debug=True)
