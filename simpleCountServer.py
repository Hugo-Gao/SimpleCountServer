# coding=utf-8
import json
from flask import Flask
from flask import request
from flask.ext.script import Manager
import os
from flask.ext.sqlalchemy import SQLAlchemy
from pip._vendor.requests.packages.urllib3 import response
from sqlalchemy import JSON
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy.orm import *
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
app = Flask(__name__)
basedir=os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'userConfigBase.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
engine = create_engine('sqlite:///'+os.path.join(basedir,'userConfigBase.sqlite'), echo=True)
metadata=MetaData(engine)
userdb=SQLAlchemy(app)
manager=Manager(app)
userName=''
# 初始化数据库连接:
engine = create_engine('sqlite:///'+os.path.join(basedir,'userConfigBase.sqlite'))
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)
@app.route('/')
def test():
    return 'success'

class userInfoTable(userdb.Model):
    __tablename__='userInfo'
    id=userdb.Column(userdb.Integer,primary_key=True)
    username=userdb.Column(userdb.String,unique=True)
    password=userdb.Column(userdb.String)
    def __repr__(self):
        return 'table name is '+self.username

#此方法处理用户登录 返回码为0无注册 返回码为1密码错误



class userBillListTable(userdb.Model):
    __tablename__='allBillList'
    id=userdb.Column(userdb.Integer,primary_key=True)
    billName=userdb.Column(userdb.String,unique=False)
    userName=userdb.Column(userdb.String,unique=False)
    tourists=userdb.Column(userdb.String,unique=False)
    extend_existing=True
    def __repr__(self):
        return self.billName

#检查用户登陆
@app.route('/user',methods=['POST'])
def check_user():
    userName=request.form['username']
    print str(userName)+"log success"
    haveregisted = userInfoTable.query.filter_by(username=request.form['username']).all()
    if haveregisted.__len__() is not 0: # 判断是否已被注册
        passwordRight = userInfoTable.query.filter_by(username=request.form['username'],password=request.form['password']).all()
        if passwordRight.__len__() is not 0:
            return '登录成功'
        else:
            return '1'
    else:
        return '0'


#此方法处理用户注册
@app.route('/register',methods=['POST'])
def register():
    userName=request.form['username']
    userdb.create_all()
    haveregisted = userInfoTable.query.filter_by(username=request.form['username']).all()
    if haveregisted.__len__() is not 0: # 判断是否已被注册
        return '0'
    userInfo=userInfoTable(username=request.form['username'],password=request.form['password'])
    userdb.session.add(userInfo)
    userdb.session.commit()
    return '注册成功'

#客户端将数据传上服务器，更新服务器上的数据
@app.route('/postdata',methods=['POST'])
def postData():
    userName=request.form['username']
    class userTable(userdb.Model):
        if userName is not '':
         __tablename__=userName
         __table_args__ = {"useexisting": True}
         id=userdb.Column(userdb.Integer,primary_key=True)
         name=userdb.Column(userdb.String)
         money=userdb.Column(userdb.Integer)
         describe=userdb.Column(userdb.String)
         pic=userdb.Column(userdb.BLOB)
         date=userdb.Column(userdb.String)
         oldpic=userdb.Column(userdb.BLOB)
         billname=userdb.Column(userdb.String)
         extend_existing=True
        else:
           print 'tableName is NUll'
    userdb.create_all()
    haveExisted=userTable.query.filter_by(date=request.form['date']).all()#判断数据库中是否有相同的数据了
    if len(haveExisted) is not 0:
        print 'already exist'+str(len(haveExisted))
        return '已经注册了'
    cName=request.form['name']
    cMoney=request.form['money']
    cDescribe=request.form['describe']
    cDate=request.form['date']
    cPicinfo=request.form['picinfo']
    cOldpicinfo=request.form['oldpicinfo']
    cBillName=request.form['billname']
    try:
        userData=userTable(name=cName,money=cMoney,describe=cDescribe,pic=cPicinfo,date=cDate,oldpic=cOldpicinfo,billname=cBillName)
        userdb.session.add(userData)
        userdb.session.commit()
    except:
        print '出问题了'
    return '1'


#客户端传送billlist到服务器
@app.route('/postBillList',methods=['POST','GET'])
def postBillList():
    userdb.create_all()
    userName=request.form['userName']
    billName=request.form['billName']
    tourists=request.form['touristsString']
    print '收到了'+userName+' '+billName+' '+tourists+' '
    haveExisted=userBillListTable.query.filter_by(billName=billName, userName=userName).all()
    if len(haveExisted) is not 0:
        print userName+" "+billName+"have already existed"
        return 0
    try:
        billListData=userBillListTable(userName=userName,billName=billName,tourists=tourists)
        userdb.session.add(billListData)
        userdb.session.commit()
    except:
        print 'postBillList出问题了'
    return 0

#客户端获取服务器上的帐单名数据
@app.route('/getbillsname',methods=['GET','POST'])
def getBillsName():
    userName=request.form['username']
    userdb.create_all()
    session=DBSession()
    data=dict()
    #查询该用户以前的账单名
    billNameList=session.query(userBillListTable).filter(userBillListTable.userName==userName).all()
    if (billNameList.__len__() is 0):
        return '新用户'
    pushbillNameList=list()
    for i in range(billNameList.__len__()):
        pushbillNameList.append(billNameList.__getitem__(i).billName.__str__())
        data[billNameList.__getitem__(i).billName.__str__()]=billNameList.__getitem__(i).tourists
    data['billsname']=pushbillNameList
    print data
    session.close()
    return json.dumps(data,ensure_ascii=False)


#客户端获取服务器上的bilBean
@app.route('/getdata',methods=['GET','POST'])
def getBillBean():
    userName=request.form['username']
    billName=request.form['billname']
    class userTable(userdb.Model):
        if userName is not '':
            __tablename__=userName
            __table_args__ = {"useexisting": True}
            id=userdb.Column(userdb.Integer,primary_key=True)
            name=userdb.Column(userdb.String)
            money=userdb.Column(userdb.Integer)
            describe=userdb.Column(userdb.String)
            pic=userdb.Column(userdb.BLOB)
            date=userdb.Column(userdb.String)
            oldpic=userdb.Column(userdb.BLOB)
            billname=userdb.Column(userdb.String)
            extend_existing=True
        else:
            print 'tableName is NUll'
        def __repr__(self):
            return self.id
    userdb.create_all()
    session=DBSession()
    data=dict()
    billBeanList=session.query(userTable).filter(userTable.billname==billName).all()
    if billBeanList.__len__() is 0:
        return '没有数据'
    for i in range(billBeanList.__len__()):
        bean=dict()
        bean['name']=billBeanList.__getitem__(i).name
        bean['money']=billBeanList.__getitem__(i).money
        bean['describe']=billBeanList.__getitem__(i).describe
        bean['pic']=billBeanList.__getitem__(i).pic
        bean['oldpic']=billBeanList.__getitem__(i).oldpic
        bean['date']=billBeanList.__getitem__(i).date
        bean['billname']=billBeanList.__getitem__(i).billname
        print str(i)+' '+billBeanList.__getitem__(i).date
        data[str(i+1)]=bean.copy()
    return json.dumps(data,ensure_ascii=False)

if __name__ == '__main__':
    #manager.run()
    app.run(host='172.27.35.1',port=8070)


#python simpleCountServer.py runserver --host 192.168.253.1