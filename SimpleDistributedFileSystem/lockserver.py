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
    host = request.json['host']
    port = request.json['port']
    file_id = request.json['id']
    r = requests.put("http://" + host + ":" + port + "/lock/" + file_id)
    res = r.json()
    if res['lock_status'] == 'locked':
        new_lock = Lock(host,port,file_id)
        db.session.add(new_lock)
        db.session.commit()
        return jsonify(new_lock.serialize())
    else:
        return jsonify(res)

@app.route('/<id>', methods=['DELETE'])
def unlock(id):
    lock = Lock.query.get(id)
    if lock:
        r = requests.put("http://" + lock.host + ":" + str(lock.port) + "/unlock/" + str(lock.file_id))
        res = r.json()
        if res['lock_status'] == 'unlocked':
            db.session.delete(lock)
            db.session.commit()
            return lock_schema.jsonify(lock)
        else:
            return jsonify(res)

flaskrun(app)



