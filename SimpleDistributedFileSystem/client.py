import requests
import json

headers = {'Content-Type': 'application/json'}

'''
openfile
Takes: filename (string), mode (char) (either w, r)
if mode is w it gets the primary version of the file and pass the info on to read_write file
else mode is r and it gets the secondary version of the file, no lock on read required
'''
def openfile(filename, mode):
    if mode == 'w':
        getloc = requests.get("http://127.0.0.1:5000/w/" + filename)
        location = getloc.json()
        read_write_file(filename,location)
    elif mode =='r':
        getloc = requests.get("http://127.0.0.1:5000/r/" + filename)
        location = getloc.json()
        read_file(filename,location)
'''
Unlocks the file 
'''
def closefile(id):
    unlocker = requests.delete('http://127.0.0.:6000/'+str(id))

'''
Creates new file, prompts the user for input, opens the file in read_write mode following completion
'''
def write_file():
    filename = input("filename:")
    filecontents = input("filecontents")
    writepackage = {'filename':filename,'filecontents':filecontents}
    writer = requests.post("http://127.0.0.1:5000/",headers=headers,data=json.dumps(writepackage))
    openfile(filename,'w')

'''
Receives the filename and location info from the directory server
Locks the file and prompts the user for the new contents of the file
FIle is then closed by releasing the lock
'''
def read_write_file(filename, location):
    lockpackage = {'id': location['id'], 'host': location['host'], 'port': location['port']}
    locker = requests.post("http://127.0.0.1:6000/", headers=headers, data=json.dumps(lockpackage))
    lockinfo = locker.json()
    lock_id = lockinfo['id']
    getfile = requests.get('http://'+location['host']+':'+str(location['port'])+'/'+str(location['id']))
    getinfo = getfile.json()
    print(getinfo['filename'])
    print(getinfo['filecontents'])
    new_contents = input("what would you like it to say")
    update = {'filename':filename,'filecontents':new_contents,'lock_id':lock_id,'update_flag':'not set'}
    putter = requests.put('http://'+location['host']+':'+str(location['port'])+'/'+str(location['id']),headers=headers, data=json.dumps(update))
    print(putter.text)
    closefile(lock_id)

'''
Takes the filename and location and retrieves the filename and filecontents
'''
def read_file(filename, location):
    getfile = requests.get('http://' + location['host'] + ':' + str(location['port']) + '/' + str(location['id']))
    getinfo = getfile.json()
    print(getinfo['filename'])
    print(getinfo['filecontnets'])
