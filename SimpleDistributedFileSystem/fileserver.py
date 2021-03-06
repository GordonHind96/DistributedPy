from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flaskrun import flaskrun
import httplib2, urllib
import requests
import optparse
import json
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'fileserver.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)
default_host = '127.0.0.1'
default_port = '8000'
parser = optparse.OptionParser()
parser.add_option("-H", "--host",
                      help="Hostname of the Flask app " + \
                           "[default %s]" % default_host,
                      default=default_host)
parser.add_option("-P", "--port",
                      help="Port for the Flask app " + \
                           "[default %s]" % default_port,
                      default=default_port)

# Two options useful for debugging purposes, but
# a bit dangerous so not exposed in the help message.
parser.add_option("-d", "--debug",
                      action="store_true", dest="debug",
                      help=optparse.SUPPRESS_HELP)
options, _ = parser.parse_args()

'''
File class,
id: primary key
filename: name specified by user
flilecontents: contents specidied by user
'''
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(80))
    filecontents = db.Column(db.String(120))
    server = db.Column(db.Integer)
    version = db.Column(db.String(80))

    def __init__(self, filename, filecontents, server, version):
        self.filename = filename
        self.filecontents = filecontents
        self.server = server
        self.version = version
    def serialize(self):
        return{
            'id':self.id,
            'filename':self.filename,
            'filecontents':self.filecontents,
            'server':self.server,
            'version':self.version
        }
class FileSchema(ma.Schema):
    class Meta:
        fields = ('id','filename','filecontents','server','version')

file_schema = FileSchema()
files_schema = FileSchema(many = True)

#endpoint for users to create new file
@app.route("/", methods=["POST"])
def add_file():
    filename = request.json['filename']
    filecontents = request.json['filecontents']
    file_server = request.json['file_server']
    file_version = request.json['version']
    new_file = File(filename,filecontents,file_server,file_version)
    db.session.add(new_file)
    db.session.commit()
    return jsonify(new_file.serialize())

#endpoint to get file by id
@app.route("/<id>", methods=["GET"])
def get_file(id):
    print("going to get %s"% id)
    file = File.query.get(id)
    return file_schema.jsonify(file)

#endpoint to get all files saved on this server
@app.route("/s/<server_id>", methods=["GET"])
def get_files(server_id):
    all_files_on_server = File.query.filter_by(server = server_id).all()
    result = files_schema.dump(all_files_on_server)
    return jsonify(result.data)

#endpoint to update a file saved on this server
@app.route("/<id>",methods=["PUT"])
def file_update(id):
    file = File.query.get(id)
    lock_id = request.json['lock_id']
    if check_lock(lock_id,id) or file.version == 'primary':
        filename = request.json['filename']
        filecontents = request.json['filecontents']
        flag = request.json['update_flag']
        file.filename = filename
        file.filecontents = filecontents
        db.session.commit()
        if file.version == 'primary':
            update_secondarys(file.id,file.server)
        return file_schema.jsonify(file)
    responsePackage = {'response':'unable to get lock on file'}
    return jsonify(responsePackage)

#endpoint to remove a file save on the server
@app.route("/<id>", methods=["DELETE"])
def file_delete(id):
    file = File.query.get(id)
    db.session.delete(file)
    db.session.commit()
    return file_schema.jsonify(file)

#informs the directory server to update the secondarys
def update_secondarys(id,serv_id):
    file = File.query.get(id)
    update_data = {'filename':file.filename,'filecontents':file.filecontents,'server_id':serv_id}
    headers ={'Content-Type':'application/json'}
    r = requests.post("http://127.0.0.1:5000/update",headers=headers,data=json.dumps(update_data))

#informs the directory server of the fileservers location so that files can be retreived from it
def inform_directory(host, port):
    servinfo = {'host':options.host,'port':options.port}
    print(servinfo)
    headers ={'Content-Type':'application/json'}
    r = requests.post("http://"+host+":"+port+"/register",headers=headers, data=json.dumps(servinfo))

#checks that the file being edited has been locked
def check_lock(id,file_id):
    data = {'id': int(id), 'port': int(options.port),'file_id':int(file_id)}
    headers = {'Content-Type': 'application/json'}
    r = requests.post("http://127.0.0.1:6000/v", headers=headers, data=json.dumps(data))
    print(r.text)
    resJson = r.json()
    if resJson['valid'] == True:
        return True
    else:
        return False



inform_directory('127.0.0.1','5000')

app.run(
        debug=options.debug,
        host=options.host,
        port=int(options.port)
    )