#!/usr/bin/env python
#-*- acoding:utf-8 -*-

from flask import Flask,render_template#从文件/包flask中导入一个类Flask，render_template把Jinja2模板引擎集成到了flask中
from flask import request
from flask import redirect
from flask import abort
from flask import session
from flask import url_for
from flask import flash
from datetime import datetime
from flask.ext.script import Manager
from flask.ext.script import Shell
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import Required
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.mail import Mail
from flask.ext.mail import Message

import os

basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)#创建一个Flask对象
app.config['SECRET_KEY']='yangchao_wtf_key'#wtf防止跨站请求伪造攻击 flask-wtf
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///' + os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True


#邮件服务测试
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = '55617@163.com'
app.config['FLASK_ADMIN'] = os.environ.get('FLASKY_ADMIN')

app.config['MAIL_SERVER'] = 'smtp.163.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') 
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')


manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
mail = Mail(app)
#创建数据库迁移
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


class NameForm(Form):
    name=StringField('what is your name?', validators=[Required()])
    submit=SubmitField('submit')

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    def __repr__(self):
        return '<User %s>' % self.username
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    def __repr__(self):
        return '<Role %s>' % self.name
    users = db.relationship('User', backref='role', lazy='dynamic')


def send_email(to, template, subject, user):
    msg = Message(subject, sender='55617@163.com', recipients=[to])
    msg.body = render_template(template + '.txt', user=user)
    msg.html = render_template(template + '.html', user=user)
    mail.send(msg)

@app.route('/send')
def send():
    user = User(username = 'jack')
    template = '/mail/new_user'
    msg = Message('123', sender='55617@163.com', recipients=['861008761@qq.com'])
    msg.body = render_template(template + '.txt', user=user)
    msg.html = render_template(template + '.html', user=user)
    #msg.body = 'test'
    #msg.html = '<b>HTML</b> body'
    mail.send(msg)

@app.route('/')#修饰器
def index():
    #abort(404)#网页显示：Not Found
    #return redirect('http://www.baidu.com')#重定向需要使用完整URL
    #return '<h1>hello,world!</h1>'
    return render_template('index.html', current_time=datetime.utcnow(), language='zh-cn')

@app.route('/<name>',methods=['GET','POST'])#修饰器
def user(name):
    #name = None
    form = NameForm()
    if form.validate_on_submit():
        oldname = session.get('name')
        if oldname is not None and oldname != form.name.data:
            user = User(username = form.name.data)
            send_email('861008761@qq.com', '/mail/new_user', 'new User', user=user)
            flash('you have changed your name!')
                #
                #return redirect(url_for('user',name=session.get('name')))
            #flash('don\'t be shy,try again')
        session['name'] = form.name.data
        return redirect(url_for('user',name=session.get('name')))
    return render_template('user.html',name=name,form=form)

@app.route('/request')
def context():
    user_agent = request.headers.get('User_Agent')#从request的headers中截取浏览器内核信息
    return '<p>your browser is %s<p>' % user_agent

@app.route('/comments')
def comment():
    comments=['jack is bad','jack is dangerous','jack is hot']
    return render_template('comments.html',comments=comments)

@app.route('/comments_macro')
def comment_macro():
    comments=['the girl is bad','the girl is nice']
    return render_template('macro.html',comments=comments)

@app.route('/extends')
def extend():
    return render_template('/模板继承/extends.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500

def make_shell_context():
    return dict(app = app, db = db, User = User, Role = Role)
manager.add_command('shell', Shell(make_context = make_shell_context))

if __name__ == '__main__':
    manager.run()























    
