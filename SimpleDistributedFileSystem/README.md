# SIMPLE DISTRIBUTED FILE SYSTEM

## WHAT's DONE

### FileServer
* endpoints for creating a file
* endpoints for retrieving a specific file
* endpoints for retreiving all files
* endpoints for updating file
* endpoints for deleteing file

### Directory Server
* endpoints to write a file on the directory server and receive location info in return
* endpoints to request a file by name and have its location and id returned

### Lock Server
* endpoint for lock, calls lock in fileserver, returns lock id
* endpoint for unlock, calls unlock in fileserver, deletes lock
* users can only unlock a file if they have a lock id
* users can not lock a file that has been locked

## TODO
* check if file is locked in directory service before returning it
* replication
* Auth Server
* user accounts
* only users can access usertaged files
* groups and groupd access of files

### Bonus
* create a nice user interface
