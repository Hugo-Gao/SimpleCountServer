# coding=utf-8
from flask import Flask
import os

from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
basedir=os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'userConfigBase.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
userdb=SQLAlchemy(app)

class userInfoTable(userdb.Model):
    __tablename__='userInfo'
    id=userdb.Column(userdb.Integer,primary_key=True)
    username=userdb.Column(userdb.String,unique=True)
    password=userdb.Column(userdb.String)

    def __repr__(self):
        return 'table name is '+self.username