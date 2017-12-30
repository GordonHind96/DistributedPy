import requests
import json

headers = {'Content-Type': 'application/json'}

def write_file(filename, filecontents):
    writepackage = {'filename':filename,'filecontents':filecontents}
    writer = requests.post("http://127.0.0.1:5000/",headers=headers,data=json.dumps(writepackage))
    read_write_file(filename)

def read_write_file(filename):
    getloc = requests.get("http://127.0.0.1:5000/w/"+filename)
    location = getloc.json()
    lockpackage = {'id':location['id'],'host':location['host'],'port':location['port']}
    locker = requests.post("http://127.0.0.1:6000/",headers=headers,data=json.dumps(lockpackage))
    lockinfo = locker.json()
    lock_id = lockinfo['id']
    getfile = requests.get('http://'+location['host']+':'+str(location['port'])+'/'+str(location['id']))
    getinfo = getfile.json()
    print(getinfo['filename'])
    print(getinfo['filecontnets'])
    new_contents = input("what would you like it to say")
    update = {'filename':filename,'filecontents':new_contents,'lock_id':lock_id,'update_flag':'not set'}
    putter = requests.put('http://'+location['host']+':'+str(location['port'])+'/'+str(location['id']),headers=headers, data=json.dumps(update))
    print(putter.text)
    unlocker = requests.delete('http://127.0.0.:6000/'+str(lock_id))

def read_file(filename):
    getloc = requests.get("http://127.0.0.1:5000/r/" + filename)
    location = getloc.json()
    lockpackage = {'id': location['id'], 'host': location['host'], 'port': location['port']}
    locker = requests.post("http://127.0.0.1:6000/", headers=headers, data=json.dumps(lockpackage))
    lockinfo = locker.json()
    lock_id = lockinfo['id']
    getfile = requests.get('http://' + location['host'] + ':' + str(location['port']) + '/' + str(location['id']))
    getinfo = getfile.json()
    print(getinfo['filename'])
    print(getinfo['filecontnets'])
