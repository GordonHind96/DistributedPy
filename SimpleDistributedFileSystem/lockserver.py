from flask import Flask,request,jsonify,abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
from flaskrun import flaskrun
import requests
import json
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'lockserver.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)

'''
Lock class, contains info on the location of a locked file, when it was locked, (by who)
'''
class Lock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.String(80))
    port = db.Column(db.Integer)
    locked_at = db.Column(db.DATETIME)
    file_id = db.Column(db.Integer)

    def __init__(self,host,port,file_id):
        self.host = host
        self.port = port
        self.file_id = file_id
        self.locked_at = datetime.now()
    def serialize(self):
        return {
            'id': self.id,
            'locked_at': self.locked_at,
            'host': self.host,
            'port':self.port,
            'file_id':self.file_id
        }
class LockSchema(ma.Schema):
    class Meta:
        fields = ('id','locked_at','host','port','file_id')

lock_schema = LockSchema()
locks_schema = LockSchema(many = True)

@app.route('/',methods=['POST'])
def lock():
    print("lock called")
    host = request.json['host']
    port = request.json['port']
    file_id = request.json['id']
    new_lock = Lock(host,port,file_id)
    db.session.add(new_lock)
    db.session.commit()
    return jsonify(new_lock.serialize())


@app.route('/<id>', methods=['DELETE'])
def unlock(id):
    lock = Lock.query.get(id)
    if lock:
        db.session.delete(lock)
        db.session.commit()
        return lock_schema.jsonify(lock)
    else:
        res = {'response':'no lock with that id'}
        return jsonify(res)
@app.route('/v',methods=['POST'])
def validate_lock_id():
    lock_id = request.json['id']
    lock = Lock.query.get(lock_id)
    if lock is None:
        response = {"valid": False}
        return jsonify(response)
    if lock.file_id == request.json['file_id'] and lock.port == request.json['port']:
        response = {"valid":True}
        return jsonify(response)
    response = {"valid":False}
    return jsonify(response)

@app.route('/vf',methods=['POST'])
def check_file_locked():
    file = request.json['id']
    port = request.json['port']
    lock = Lock.query.filter_by(file_id = file,port = port).first()
    if lock is None:
        response = {'lock_status':False}
        return jsonify(response)
    response = {'lock_status':True}
    return jsonify(response)

flaskrun(app)



