from flask import Flask,request,jsonify,abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flaskrun import flaskrun
import requests
import json
import os
from random import randint
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'directoryserver.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)
numServers = 2

'''
Directory class, keeps track of fileservers and the files on
each server
'''
class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.String(80))
    port = db.Column(db.Integer, unique=True)


    def __init__(self, host, port):
        self.host = host
        self.port = port

    def serialize(self):
        return {
            'id': self.id,
            'host': self.host,
            'port': self.port
        }
class ServerSchema(ma.Schema):
    class Meta:
        fields = ('id', 'host', 'port')
server_schema = ServerSchema()
servers_schema = ServerSchema(many=True)

@app.route("/register", methods=["POST"])
def register_server():
    host = request.json['host']
    port = request.json['port']
    print("receive request from %s :%s"%(host,port))
    new_server = Server(host,port)
    db.session.add(new_server)
    db.session.commit()
    #global numServers
    #numServers += 1
    return jsonify(new_server.serialize())

@app.route("/unregister/<id>", methods=["DELETE"])
def unregister_server(id):
    server = Server.query.get(id)
    db.session.delete(server)
    db.session.commit()
    #global numServers
    #numServers -= 1
    return server_schema.jsonify(server)

@app.route("/",methods=['POST'])
def write_file():
    global numServers
    filename = request.json['filename']
    filecontents = request.json['filecontents']
    headers = {'Content-Type': 'application/json'}
    responsePackage={'status':'fail'}
    version = 'primary'
    for i in range(1,numServers+1):
        server = Server.query.get(i)
        if i != 1:
            version = 'secondary'
        fileinfo = {'filename': filename, 'filecontents': filecontents,'version':version,'file_server':i}
        r = requests.post("http://" + server.host + ":" + str(server.port) + "/", headers=headers, data=json.dumps(fileinfo))
        resJson = r.json()
        responsePackage ={'serverhost':server.host,'serverport':server.port,'fileid':resJson['id'],'filename':resJson['filename'],'filecontents':resJson['filecontents']}

    return jsonify(responsePackage)

@app.route("/<filename>", methods=['GET'])
def get_file_locations(filename):
    global numServers
    for i in range(1, numServers+1):
        server = Server.query.get(i)
        r = requests.get("http://"+server.host+":"+ str(server.port)+"/s/"+str(i))
        print(r.text)
        resJson = r.json()
        for item in resJson:
            if item['filename'] == filename:
                if item['locked']==False:
                    responsePackage ={'serverhost':server.host,'serverport':server.port,'fileid':item['id']}
                    return jsonify(responsePackage)
    return abort(404)

@app.route("/update",methods=['POST'])
def update_files():
    filename = request.json['filename']
    filecontents = request.json['filecontents']
    for i in range(1, numServers+1):
        server = Server.query.get(i)
        r = requests.get("http://"+server.host+":"+ str(server.port)+"/s/"+str(i))
        print(r.text)
        resJson = r.json()
        for item in resJson:
            if item['filename'] == filename:
                update_data = {'filename':filename,'filecontents':filecontents,'update_flag':'from_primary'}
                headers = {'Content-Type': 'application/json'}
                r = requests.put("http://"+server.host+":"+ str(server.port)+"/"+item.id,headers=headers,data=json.dumps(update_data))
                return r.json()
    return 200

@app.route("/updatep",methods=['POST'])
def find_and_update_primary():
    filename = request.json['filename']
    filecontents = request.json['filecontents']
    for i in range(1, numServers + 1):
        server = Server.query.get(i)
        r = requests.get("http://" + server.host + ":" + str(server.port) + "/s/" + str(i))
        print(r.text)
        resJson = r.json()
        for item in resJson:
            if item['filename'] == filename and item['version'] == 'primary':
                update_data = {'filename': filename, 'filecontents': filecontents, 'update_flag': 'from_secondary'}
                headers = {'Content-Type': 'application/json'}
                r = requests.put("http://" + server.host + ":" + str(server.port) + "/" + item.id, headers=headers,
                                data=json.dumps(update_data))
                return r.json()
    return 200
flaskrun(app)
