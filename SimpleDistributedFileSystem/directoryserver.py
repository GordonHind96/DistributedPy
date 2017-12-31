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

#enpoint for fileserves to register with the directory
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

#endpoint to gracefully remove a fileserver(never used)
@app.route("/unregister/<id>", methods=["DELETE"])
def unregister_server(id):
    server = Server.query.get(id)
    db.session.delete(server)
    db.session.commit()
    #global numServers
    #numServers -= 1
    return server_schema.jsonify(server)

#Writes a file to every fileserver, one being the primary version, the others are secondary
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

#endpoint for getting a file for reading, returns a secondary version of the file
@app.route("/r/<filename>", methods=['GET'])
def get_file_locations(filename):
    global numServers
    response = 'could not find file with that name'
    for i in range(1, numServers+1):
        server = Server.query.get(i)
        r = requests.get("http://"+server.host+":"+ str(server.port)+"/s/"+str(i))
        print(r.text)
        resJson = r.json()
        for item in resJson:
            if item['filename'] == filename:
                response = 'item found but locked by another user'
                if not check_locked(item['id'],server.port):
                    if item['version]'] == 'secondary':
                        responsePackage ={'serverhost':server.host,'serverport':server.port,'fileid':item['id']}
                        return jsonify(responsePackage)
    responsePackage = {'response':response}
    return jsonify(responsePackage)

#endpoint for getting a file for writing, returns the primary version of the file
@app.route("/w/<filename>", methods=['GET'])
def get_file_locations(filename):
    global numServers
    response = 'could not find file with that name'
    for i in range(1, numServers+1):
        server = Server.query.get(i)
        r = requests.get("http://"+server.host+":"+ str(server.port)+"/s/"+str(i))
        print(r.text)
        resJson = r.json()
        for item in resJson:
            if item['filename'] == filename:
                response = 'item found but locked by another user'
                if not check_locked(item['id'],server.port):
                    if item['version'] == 'primary':
                        responsePackage ={'serverhost':server.host,'serverport':server.port,'fileid':item['id']}
                        return jsonify(responsePackage)
    responsePackage = {'response':response}
    return jsonify(responsePackage)

#endpoint for beginning updating of secondary files
@app.route("/update",methods=['POST'])
def update_files():
    filename = request.json['filename']
    filecontents = request.json['filecontents']
    server_id = request.json['server_id']
    for i in range(1, numServers+1):
        if i != server_id:
            server = Server.query.get(i)
            r = requests.get("http://"+server.host+":"+ str(server.port)+"/s/"+str(i))
            resJson = r.json()
            for item in resJson:
                if item['filename'] == filename:
                    requestLock = {'host': server.host, 'port': server.port, "id":item['id']}
                    headers = {'Content-Type': 'application/json'}
                    rs = requests.post("http://127.0.0.1:6000/", headers=headers, data=json.dumps(requestLock))
                    rjs = rs.json()
                    update_data = {'filename':filename,'filecontents':filecontents,'lock_id':rjs['id'],'update_flag':'from_primary'}
                    headers = {'Content-Type': 'application/json'}
                    re = requests.put("http://"+server.host+":"+ str(server.port)+"/"+str(item['id']),headers=headers,data=json.dumps(update_data))
                    rs = requests.delete("http://127.0.0.1:6000/"+str(rjs['id']))
                    return jsonify(re.json())
    return 200

#checks if file is locked
def check_locked(id, port):
    data = {'id':id,'port':port}
    headers ={'Content-Type':'application/json'}
    r = requests.post("http://127.0.0.1:6000/vf",headers = headers, data=json.dumps(data))
    resJson = r.json()
    if resJson['lock_status'] == True:
        return True
    else:
        return False
flaskrun(app)
