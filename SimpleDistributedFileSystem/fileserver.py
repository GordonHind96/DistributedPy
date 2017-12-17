from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'fileserver.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)

'''
File class,
id: primary key
filename: name specified by user
flilecontents: contents specidied by user
'''
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(80), unique=True)
    filecontents = db.Column(db.String(120))

    def __init__(self, filename, filecontents):
        self.filename = filename
        self.filecontents = filecontents
    def serialize(self):
        return{
            'id':self.id,
            'filename':self.filename,
            'filecontents':self.filecontents
        }
class FileSchema(ma.Schema):
    class Meta:
        fields = ('id','filename','filecontents')

file_schema = FileSchema()
files_schema = FileSchema(many = True)

#endpoint for users to create new file
@app.route("/", methods=["POST"])
def add_file():
    filename = request.json['filename']
    filecontents = request.json['filecontents']
    new_file = File(filename,filecontents)
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
@app.route("/", methods=["GET"])
def get_files():
    all_files = File.query.all()
    result = files_schema.dump(all_files)
    return jsonify(result.data)

#endpoint to update a file saved on this server
@app.route("/<id>",methods=["PUT"])
def file_update(id):
    file = File.query.get(id)
    filename = request.json['filename']
    filecontents = request.json['filecontents']
    file.filename = filename
    file.filecontents = filecontents
    db.session.commit()
    return file_schema.jsonify(file)

#endpoint to remove a file save on the server
@app.route("/<id>", methods=["DELETE"])
def file_delete(id):
    file = File.query.get(id)
    db.session.delete(file)
    db.session.commit()
    return file_schema.jsonify(file)
if __name__== '__main__':
    app.run(debug=True)