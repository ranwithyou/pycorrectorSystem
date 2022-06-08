import click
from flask_login import logout_user, login_required, login_user, UserMixin, LoginManager

from pycorrector1.deepcontext.infer import Inference
from pycorrector1.deepcontext import config
from flask import Flask, render_template, request, jsonify, redirect, flash, url_for
import re
import os
from flask_sqlalchemy import SQLAlchemy  # 导入扩展
app = Flask(__name__)
login_manager = LoginManager(app)  # 实例化扩展类
db = SQLAlchemy(app)  # 初始化扩展，传入程序实例 app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db')
app.config['SECRET_KEY'] = 'dev'

class User(db.Model, UserMixin):  # 表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(20))  # 管理员还是普通用户
    password = db.Column(db.String(10))  # 密码
    username = db.Column(db.String(20))  # 账号


@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    db.create_all()
    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.password = password  # 设置密码
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.password = password  # 设置密码
        db.session.add(user)

    db.session.commit()  # 提交数据库会话
    click.echo('Done.')


@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    return user  # 返回用户对象


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if len(username) == 0 or len(password) == 0 or len(username) > 20 or len(password) > 10:
            flash('Invalid input.')
            return redirect(url_for('initialization'))

        user = User.query.filter_by(username=username).first()
        # 验证用户名和密码是否一致
        if username == user.username and password == user.password:
            login_user(user)  # 登入用户
            flash('Login success.')
            return redirect(url_for('index'))  # 重定向到主页

        flash('Wrong username or password.')  # 如果验证失败，显示错误消息
        return redirect(url_for('initialization'))  # 重定向回登录页面


@app.route('/logout')
@login_required
def logout():
    logout_user()  # 登出用户
    flash('Goodbye.')
    return redirect(url_for('initialization'))  # 重定向回首页


@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password1 = request.form.get("password1")
        # 如果获取的数据为空
        if User.query.filter_by(username=username).first():
            return jsonify({"msg": "username already in use"})
        if len(username) == 0 or len(password) == 0 or len(password1) == 0 or password != password1 \
                or len(username) > 20 or len(password) > 10:
            flash('Invalid input.')  # 显示错误提示
            return redirect(url_for('register'))  # 重定向回注册页面
        user = User(name="ordinary user", username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('initialization'))  # 重定向回主页


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/')
def initialization():  # put application's code here
    return render_template('login.html')

@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/infer', methods=['GET', 'POST'])
def infer():
    data2 = []
    res = {}
    temp = {}
    res1 = {}
    if request.method == 'POST':
        data = request.form.get('input')
        data1 = re.split('[！。？]', str(data).strip('\n').strip('”').strip())
        for x in data1:
            if x != '':
                data2.append(x)
    inference = Inference(config.model_dir, config.vocab_path)
    # print(data2)
    for i in data2:
        r = inference.predict(i)
        res1.update({i: r})
    print(res1)
    return render_template("index.html", result=res1, inputs=data, color="white")


if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run(debug=True, host="0.0.0.0", port=8000)
