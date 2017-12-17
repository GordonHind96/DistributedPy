from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flaskrun import flaskrun
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'directoryserver.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)

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
    return jsonify(new_server.serialize())

@app.route("/unregister/<id>", methods=["DELETE"])
def unregister_server(id):
    server = Server.query.get(id)
    db.session.delete(server)
    db.session.commit()
    return server_schema.jsonify(server)
flaskrun(app)
