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
import os

basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)#创建一个Flask对象
app.config['SECRET_KEY']='yangchao_wtf_key'#wtf防止跨站请求伪造攻击 flask-wtf
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///' + os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)


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


@app.route('/')#修饰器
def index():
    #abort(404)#网页显示：Not Found
    #return redirect('http://www.baidu.com')#重定向需要使用完整URL
    #return '<h1>hello,world!</h1>'
    return render_template('index.html', current_time=datetime.utcnow(), language='zh-cn')

@app.route('/<name>',methods=['GET','POST'])#修饰器
def user(name):
    session['name'] = name
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.name.data).first()
        if user is not None:
            session['known'] = True
        else:
            user = User(username = form.name.data)
            db.session.add(user)
            #db.session.commit()#在py文件中没有这句话也可以直接写入数据库
            session['known'] = False
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('user', name=session.get('name')))#url_for需要参数 name ，所以其他参数可以省略，这个参数不可以
    return render_template('user.html',name=session.get('name'),form=form,known=session.get('known',False))

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
    return dict(app =app, db = db, User = User, Role = Role)
manager.add_command('shell', Shell(make_context = make_shell_context))

if __name__ == '__main__':
    manager.run()























    
