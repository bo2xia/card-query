import os
import logging
from datetime import datetime, timedelta
from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, PasswordField, SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange
import secrets

# 简化日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 Flask app - 生产环境配置
app = Flask(__name__)

# 环境配置
ENV = os.getenv('FLASK_ENV', 'development')
DEBUG = ENV == 'development'

app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///app.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    DEBUG=DEBUG
)
db = SQLAlchemy(app)

# 简化表单定义 - 去除复杂验证
class LoginForm:
    def __init__(self):
        self.account = None
        self.password = None

    def validate_on_submit(self):
        self.account = request.form.get('account', '').strip()
        self.password = request.form.get('password', '').strip()
        return bool(self.account and self.password)

class AccountForm:
    def __init__(self):
        self.account = None
        self.new_account = None
        self.password = None
        self.action = None

    def validate_on_submit(self):
        self.account = request.form.get('account', '').strip()
        self.new_account = request.form.get('new_account', '').strip()
        self.password = request.form.get('password', '').strip()
        self.action = request.form.get('action', '').strip()

        if self.action == 'add':
            return bool(self.new_account and self.password)
        elif self.action == 'modify_random':
            return bool(self.account)
        return False

class BatchGenerateForm:
    def __init__(self):
        self.account = None
        self.count = None
        self.max_query_count = None
        self.duration_hours = None

    def validate_on_submit(self):
        self.account = request.form.get('account', '').strip()
        self.count = request.form.get('count', '').strip()
        self.max_query_count = request.form.get('max_query_count', '').strip()
        self.duration_hours = request.form.get('duration_hours', '').strip()

        try:
            self.count = int(self.count) if self.count else 0
            self.max_query_count = int(self.max_query_count) if self.max_query_count else 0
            self.duration_hours = int(self.duration_hours) if self.duration_hours else 0
            return bool(self.account and self.count > 0 and self.max_query_count > 0 and self.duration_hours > 0)
        except ValueError:
            return False

class ChangePasswordForm:
    def __init__(self):
        self.current_password = None
        self.new_password = None
        self.confirm_password = None

    def validate_on_submit(self):
        self.current_password = request.form.get('current_password', '').strip()
        self.new_password = request.form.get('new_password', '').strip()
        self.confirm_password = request.form.get('confirm_password', '').strip()
        return bool(self.current_password and self.new_password and
                   self.new_password == self.confirm_password)

# 简化数据模型
class Admin(db.Model):
    __tablename__ = 'admins'
    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.String(128), nullable=False)

class Account(db.Model):
    __tablename__ = 'accounts'
    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Card(db.Model):
    __tablename__ = 'cards'
    card_key = db.Column(db.String(16), primary_key=True)
    username = db.Column(db.String(20), db.ForeignKey('accounts.username'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    first_used_at = db.Column(db.DateTime)
    query_count = db.Column(db.Integer, default=0)
    max_query_count = db.Column(db.Integer, default=10)
    duration_hours = db.Column(db.Integer, default=720)

# 简化助手函数
def generate_random_string(length: int = 16) -> str:
    return secrets.token_urlsafe(length)[:length]

def check_admin_credentials(account: str, password: str) -> bool:
    # 简化验证 - 去除复杂的锁定机制
    admin = Admin.query.filter_by(username=account).first()
    if admin and admin.password == password:  # 简化密码验证
        return True
    return False

def ensure_admin_session():
    if 'admin' not in session:
        return redirect(url_for('login'))
    return None

def flash_message(message: str, category: str = 'success') -> None:
    flash(message, category)

# 简化路由
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error='页面未找到'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error='服务器内部错误，请稍后重试'), 500

@app.route('/admin', methods=['GET'])
def admin():
    if redirect_response := ensure_admin_session():
        return redirect_response
    return render_template('admin.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        if check_admin_credentials(form.account, form.password):
            session['admin'] = form.account
            return redirect(url_for('admin'))
        flash_message('账号或密码错误', 'danger')
    return render_template('login.html', form=form)

@app.route('/admin/logout', methods=['GET'])
def logout():
    session.pop('admin', None)
    flash_message('已退出登录')
    return redirect(url_for('login'))

@app.route('/admin/accounts', methods=['GET', 'POST'])
def accounts():
    if redirect_response := ensure_admin_session():
        return redirect_response
    form = AccountForm()

    if request.method == 'POST' and form.validate_on_submit():
        if form.action == 'add':
            if Account.query.filter_by(username=form.new_account).first():
                flash_message('账号已存在', 'danger')
            else:
                try:
                    account = Account(
                        username=form.new_account,
                        password=form.password,  # 简化密码存储
                        created_at=datetime.utcnow()
                    )
                    db.session.add(account)
                    db.session.commit()
                    flash_message(f'账号 {form.new_account} 添加成功')
                except Exception as e:
                    db.session.rollback()
                    flash_message('数据库错误，请稍后重试', 'danger')
        elif form.action == 'modify_random':
            account = Account.query.filter_by(username=form.account).first()
            if account:
                new_password = generate_random_string(12)
                account.password = new_password
                db.session.commit()
                flash_message(f'账号 {form.account} 密码已重置为: {new_password}')
            else:
                flash_message('账号不存在', 'danger')

    # 简化账号列表显示
    accounts_list = Account.query.all()
    account_list = [
        {
            'index': i + 1,
            'account': account.username,
            'created_at': account.created_at.strftime('%Y-%m-%d %H:%M:%S') if account.created_at else '',
            'card_count': Card.query.filter_by(username=account.username).count()
        }
        for i, account in enumerate(accounts_list)
    ]
    return render_template('accounts.html', accounts=account_list, form=form)

@app.route('/admin/delete_account/<account>', methods=['POST'])
def delete_account(account: str):
    if redirect_response := ensure_admin_session():
        return redirect_response
    try:
        account_obj = Account.query.get(account)
        if account_obj:
            Card.query.filter_by(username=account).delete()
            db.session.delete(account_obj)
            db.session.commit()
            flash_message(f'账号 {account} 删除成功')
        else:
            flash_message('账号不存在', 'danger')
    except Exception as e:
        db.session.rollback()
        flash_message('数据库错误，请稍后重试', 'danger')
    return redirect(url_for('accounts'))

@app.route('/admin/cards', methods=['GET'])
def cards():
    if redirect_response := ensure_admin_session():
        return redirect_response

    # 简化卡密列表显示
    cards_list = Card.query.all()
    card_list = [
        {
            'index': i + 1,
            'card_key': card.card_key,
            'account': card.username,
            'created_at': card.created_at.strftime('%Y-%m-%d %H:%M:%S') if card.created_at else '',
            'first_used_at': card.first_used_at.strftime('%Y-%m-%d %H:%M:%S') if card.first_used_at else '未使用',
            'expiry_date': (card.created_at + timedelta(hours=card.duration_hours)).strftime('%Y-%m-%d %H:%M:%S') if card.created_at else '未知',
            'query_count': card.query_count,
            'max_query_count': card.max_query_count
        }
        for i, card in enumerate(cards_list)
    ]
    return render_template('cards.html', cards=card_list)

@app.route('/admin/delete_card/<card_key>', methods=['POST'])
def delete_card(card_key: str):
    if redirect_response := ensure_admin_session():
        return redirect_response
    try:
        card = Card.query.get(card_key)
        if card:
            db.session.delete(card)
            db.session.commit()
            flash_message(f'卡密 {card_key} 删除成功')
        else:
            flash_message('卡密不存在', 'danger')
    except Exception as e:
        db.session.rollback()
        flash_message('数据库错误，请稍后重试', 'danger')
    return redirect(url_for('cards'))

@app.route('/admin/batch_generate', methods=['GET', 'POST'])
def batch_generate():
    if redirect_response := ensure_admin_session():
        return redirect_response
    form = BatchGenerateForm()

    if request.method == 'POST' and form.validate_on_submit():
        try:
            cards = [
                Card(
                    card_key=generate_random_string(16),
                    username=form.account,
                    max_query_count=form.max_query_count,
                    duration_hours=form.duration_hours,
                    created_at=datetime.utcnow()
                ) for _ in range(form.count)
            ]
            for card in cards:
                db.session.add(card)
            db.session.commit()
            flash_message(f'成功生成 {form.count} 个卡密')
        except Exception as e:
            db.session.rollback()
            flash_message('数据库错误，请稍后重试', 'danger')

    # 获取账号列表供选择
    accounts = Account.query.all()
    return render_template('batch_generate.html', form=form, accounts=accounts)

@app.route('/admin/change_password', methods=['GET', 'POST'])
def change_password():
    if redirect_response := ensure_admin_session():
        return redirect_response
    form = ChangePasswordForm()

    if request.method == 'POST' and form.validate_on_submit():
        admin = Admin.query.filter_by(username=session['admin']).first()
        if admin and admin.password == form.current_password:
            admin.password = form.new_password
            db.session.commit()
            flash_message('密码修改成功')
            return redirect(url_for('admin'))
        else:
            flash_message('当前密码错误', 'danger')

    return render_template('change_password.html', form=form)

@app.route('/query', methods=['GET'])
def query():
    card_key = request.args.get('card_key')
    if not card_key:
        return render_template('query.html', error='请输入卡密')

    card = Card.query.get(card_key)
    if not card:
        return render_template('query.html', error='卡密无效')

    if card.query_count >= card.max_query_count:
        return render_template('query.html', error='查询次数已达上限')

    if card.first_used_at:
        expiry = card.first_used_at + timedelta(hours=card.duration_hours)
        if datetime.utcnow() > expiry:
            return render_template('query.html', error='卡密已过期')
    else:
        card.first_used_at = datetime.utcnow()

    card.query_count += 1
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return render_template('query.html', error='数据库错误，请稍后重试')

    account = Account.query.get(card.username)
    expiry_date = (card.first_used_at + timedelta(hours=card.duration_hours)).strftime('%Y-%m-%d %H:%M:%S')
    return render_template('query.html',
                          account=account.username,
                          password=account.password,
                          expiry_date=expiry_date,
                          query_count=card.query_count,
                          max_query_count=card.max_query_count)

# 初始化数据库
def init_db():
    max_retries = 5
    retry_count = 0

    while retry_count < max_retries:
        try:
            with app.app_context():
                # 测试数据库连接
                with db.engine.connect() as conn:
                    conn.execute(db.text('SELECT 1'))

                # 创建表
                db.create_all()

                # 创建默认管理员账号
                if not Admin.query.filter_by(username='admin').first():
                    admin = Admin(username='admin', password='admin123')
                    db.session.add(admin)
                    db.session.commit()
                    logger.info("默认管理员账号已创建: admin/admin123")

                logger.info("数据库初始化成功")
                return True

        except Exception as e:
            retry_count += 1
            logger.error(f"数据库初始化失败 (尝试 {retry_count}/{max_retries}): {e}")
            if retry_count < max_retries:
                import time
                time.sleep(5)  # 等待5秒后重试
            else:
                logger.error("数据库初始化最终失败")
                return False

if __name__ == '__main__':
    if init_db():
        port = int(os.getenv('PORT', 5000))
        logger.info(f"启动应用，端口: {port}, 调试模式: {DEBUG}")
        app.run(debug=DEBUG, host='0.0.0.0', port=port)
    else:
        logger.error("应用启动失败：数据库初始化失败")
        exit(1)